from logging import getLogger
from BCBio import GFF
from typing import Generator
from pathlib import Path

from sudan.tools import run_tool
from sudan.annotation import Annotation, Features
from sudan.utilities import deeplen

log = getLogger('sudan.minced')

StrGenerator = Generator[str, None, None]

def run(annotation: Annotation) -> Path:
    out = annotation.basedir / 'minced.out.gff'
    minced = annotation.tools.minced
    if not minced.have:
        log.warning('Skipping search for CRISPR repeats. Install minced to enable.')
        return
    run_tool(f'minced -gff {annotation.source_fasta} {out}')
    annotation.tool_out[annotation.tools.barrnap.name] = out
    return out

def parse(annotation: Annotation, prog_out: StrGenerator) -> Features:
    features = {}
    for record in GFF.parse(prog_out):
        features[record.id] = []
        for feature in record.features:
            n_repears = feature.qualifiers['score'][0]
            feature.qualifiers['note'] = f'CRISPR with {n_repears} repeat units'
            if 'rpt_family' not in feature.qualifiers:
                features.qualifiers['rpt_family'] = 'CRISPR'
            if 'rpt_type' not in feature.qualifiers:
                features.qualifiers['rpt_type'] = 'direct'

            features[record.id].append(feature)
            annotation.all_rna.append(feature)

    log.info(f'Found {deeplen(features)} CRISPR repeats')
    return features