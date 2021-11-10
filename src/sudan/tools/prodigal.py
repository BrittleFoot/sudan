from logging import getLogger
from BCBio import GFF
from typing import Generator
from pathlib import Path

from sudan.tools import run_tool
from sudan.annotation import Annotation, Features
from sudan.utilities import deeplen

log = getLogger('sudan.prodigal')

StrGenerator = Generator[str, None, None]

def run(annotation: Annotation) -> Path:
    out = annotation.basedir / 'prodigal.out.gff'
    #$prodigal_mode = ($totalbp >= 100000 && !$metagenome) ? 'single' : 'meta'; Have to add metagenome option!
    prodigal_mode = 'single' if annotation.total_bp >= 100000 else 'meta' 
    #to add -g gcode, it depends on kingdom
    run_tool(f'prodigal -i {annotation.source_fasta} -g 11 -c -m -p {prodigal_mode} -f gff -q -o {out}')
    annotation.tool_out[annotation.tools.prodigal.name] = out
    return out

def parse(annotation: Annotation, prog_out: StrGenerator) -> Features:
    features = {}
    for record in GFF.parse(prog_out):
        features[record.id] = record.features
    log.info(f'Found {deeplen(features)} CDS')

    return features

