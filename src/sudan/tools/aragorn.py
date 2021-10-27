import re

from logging import getLogger
from pathlib import Path
from typing import Dict, Generator
from typing import List
from typing import NamedTuple
from Bio.SeqFeature import SeqFeature

from sudan.annotation import Annotation, Features


log = getLogger('sudan.aragorn')


def run(annotation: Annotation) -> Path:
    pass


class TrnaRecord(NamedTuple):
    num: str
    name: str
    pos: str
    nums: str
    codon: str


def deeplen(iterable):
    return sum(map(len, iterable.values()))


def parse(prog_out: Generator[str, None, None]) -> Features:
    re_coords = re.compile(r'(c)?\[-?(\d+),(\d+)\]')

    contig_id = None
    features = {}

    for line in map(str.strip, prog_out):
        if line.startswith('>'):
            contig_id = line[1:]
            features[contig_id] = []
            continue

        data = line.split()
        if len(data) != 5 or not re.match(r'\d+', data[0]):
            continue

        record = TrnaRecord(*data)

        if '?' in record.name:
            log.debug(f'tRNA {record.pos} is a pseudo/wacky gene - skipping')
            continue

        match = re_coords.match(record.pos)
        if not match:
            log.debug(f'Invalid position format {record}')
        revcom, start, end = match.groups()

        start = int(start)
        end = int(end)
        strand = -1 if revcom else +1

        if start > end:
            log.debug(f'tRNA {record.pos} has start > end - skipping.')
            continue

        start = max(start, 1)
        min(end, len(context.CONTIG[contig_id].seq))

        if abs(end-start) > MAX_TRNA_LEN:
            log.debug(f'tRNA {record.pos} is too big (>{MAX_TRNA_LEN}) - skipping.')
            continue

        tool = 'Aragorgn:' + aragorn.version

        ftype = 'tRNA'
        product = record.name + record.codon
        gene = {}

        if 'tmRNA' in record.name:
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
            id=f'{record.num} {product}',
            type=ftype,
            strand=strand,
            qualifiers=qualifiers
        ))

    log.info(f'Found {deeplen(features)} tRNAs')
    return features
