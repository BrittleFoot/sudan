import re

from logging import getLogger
from pathlib import Path
from typing import Dict, Generator
from typing import List
from typing import NamedTuple
from Bio.SeqFeature import SeqFeature
from Bio.SeqFeature import FeatureLocation

from sudan import Config
from sudan.tools import run_tool
from sudan.annotation import Annotation, Features


log = getLogger('sudan.aragorn')

StrGenerator = Generator[str, None, None]


def run(annotation: Annotation) -> Path:
    out = annotation.basedir / 'aragorn.out'
    run_tool(f'aragorn -l -gc11 -w {annotation.source_fasta} -o {out}')

    annotation.tool_out[annotation.tools.aragorn.name] = out
    return out


class TrnaRecord(NamedTuple):
    num: str
    name: str
    pos: str
    nums: str
    codon: str


def deeplen(iterable):
    return sum(map(len, iterable.values()))


def parse(annotation: Annotation, prog_out: StrGenerator) -> Features:
    aragorn = annotation.tools.aragorn
    re_coords = re.compile(r'(c)?\[-?(\d+),(\d+)\]')

    contig_id = None
    features = {}

    for line in map(str.strip, prog_out):
        if line.startswith('>end'):
            break

        if line.startswith('>'):
            contig_id = line[1:]
            features[contig_id] = []
            continue

        data = line.split()
        if len(data) != 5 or not re.match(r'\d+', data[0]):
            continue

        _, name, pos, _, codon = data

        if '?' in name:
            log.debug(f'tRNA {pos} is a pseudo/wacky gene - skipping')
            continue

        match = re_coords.match(pos)
        if not match:
            log.debug(f'Invalid position format {pos}')
        revcom, start, end = match.groups()

        start = int(start)
        end = int(end)
        strand = -1 if revcom else +1

        if start > end:
            log.debug(f'tRNA {pos} has start > end - skipping.')
            continue

        start = max(start, 1)
        min(end, len(annotation[contig_id].seq))

        if abs(end-start) > Config.MAX_TRNA_LEN:
            log.debug(
                f'tRNA {pos} is too big '
                f'(>{Config.MAX_TRNA_LEN}) - skipping.'
            )
            continue

        tool = 'Aragorgn:' + str(aragorn.version)

        ftype = 'tRNA'
        product = name + codon
        gene = {}

        if 'tmRNA' in name:
            ftype = 'tmRNA'
            product = 'transfer-messenger RNA, SsrA'
            gene = {'gene': 'ssrA'}

        qualifiers = {
            'product': product,
            'inference': f'COORDINATES:profile:{tool}'
        }
        qualifiers.update(gene)

        features[contig_id].append(SeqFeature(
            FeatureLocation(start, end, strand),
            id=f'{product}',
            type=ftype,
            strand=strand,
            qualifiers=qualifiers
        ))

    log.info(f'Found {deeplen(features)} tRNAs')
    return features
