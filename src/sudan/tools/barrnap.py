from logging import getLogger
from pathlib import Path
from typing import Dict, Generator
from typing import List
from typing import NamedTuple
from Bio.SeqFeature import SeqFeature


from BCBio import GFF
from sudan.tools import run_tool
from sudan.utilities import IOWrapper
from sudan.annotation import Annotation, Features

log = getLogger('sudan.barrnap')

StrGenerator = Generator[str, None, None]

def run(annotation: Annotation) -> Path:
    out = annotation.basedir / 'barrnap.out'
    run_tool(f'barrnap --kingdom bac --threads 8 --quiet {annotation.source_fasta} > {out}')
# why only bac kingdom? euk arc bac mito (default 'bac')
    annotation.tool_out[annotation.tools.barrnap.name] = out
    return out

def deeplen(iterable):
    return sum(map(len, iterable.values()))

def parse(annotation: Annotation, prog_out: StrGenerator) -> Features:
    barrnap = annotation.tools.barrnap
    features = {}
    for record in GFF.parse(IOWrapper(map(str.strip, prog_out))):
        features[record.id] = record.features

    log.info(f'Found {deeplen(features)} rRNAs')

    # Q: do we need rnammer alternative rrna annotation?
    return features


    