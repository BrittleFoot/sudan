from logging import getLogger
from BCBio import GFF
from typing import Generator
from pathlib import Path

from sudan.tools import run_tool
from sudan.annotation import Annotation, Features
from sudan.utilities import deeplen

log = getLogger('sudan.prodigal')

StrGenerator = Generator[str, None, None]


def _gcode(kingdom):
    if kingdom == 'Archaea':
        return 11
    elif kingdom == 'Bacteria':
        return 11
    elif kingdom == 'Mitochondria':
        return 5
    elif kingdom == 'Viruses':
        return 1


def run(ann: Annotation) -> Path:
    out = ann.basedir / 'prodigal.out.gff'

    is_single_genome = ann.total_bp >= 100000 and not ann.cfg.metagenome
    prodigal_mode = 'single' if is_single_genome else 'meta' 
    
    #to add -g gcode, it depends on kingdom
    kingdom = ann.cfg.kingdom
    run_tool(
        f'prodigal -i {ann.source_fasta} -g {_gcode(kingdom)} '
        f'-c -m -p {prodigal_mode} -f gff -q -o {out}'
    )
    ann.tool_out[ann.tools.prodigal.name] = out
    return out

def parse(annotation: Annotation, prog_out: StrGenerator) -> Features:
    features = {}
    for record in GFF.parse(prog_out):
        features[record.id] = record.features
    log.info(f'Found {deeplen(features)} CDS')

    return features

