from logging import getLogger
from pathlib import Path
from typing import Dict, Generator
from typing import List
from BCBio import GFF


from sudan.tools import run_tool
from sudan.utilities import deeplen
from sudan.annotation import Features
from sudan.annotation import Annotation


log = getLogger('sudan.barrnap')

StrGenerator = Generator[str, None, None]

def _mode(kingdom):
    if kingdom == 'Archaea':
        return 'arc'
    elif kingdom == 'Bacteria':
        return 'bac'
    elif kingdom == 'Mitochondria':
        return 'mito'
    else:
        return ''


def run(annotation: Annotation) -> Path:
    out = annotation.basedir / 'barrnap.out.gff'

    # todo: parametrize kingdom, threads, etc using sudan.Config
    mode = _mode(annotation.cfg.kingdom)
    thr = annotation.cfg.cpus
    run_tool(f'barrnap --kingdom {mode} --threads {thr} --quiet {annotation.source_fasta} > {out}')
    
    annotation.tool_out[annotation.tools.barrnap.name] = out
    return out


def parse(annotation: Annotation, prog_out: StrGenerator) -> Features:
    barrnap = annotation.tools.barrnap
    features = {}
    for record in GFF.parse(prog_out):
        features[record.id] = record.features

    log.info(f'Found {deeplen(features)} rRNAs')

    # Q: do we need rnammer alternative rrna annotation?
    return features


    