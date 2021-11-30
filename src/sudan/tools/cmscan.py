from logging import getLogger
from pathlib import Path
from typing import Generator
from Bio.SeqFeature import SeqFeature
from Bio.SeqFeature import FeatureLocation
from subprocess import PIPE
from BCBio import GFF

from sudan.tools import run_tool
from sudan.annotation import Annotation, Features
from sudan.utilities import deeplen

log = getLogger('sudan.cmscan')

StrGenerator = Generator[str, None, None]

def run(annotation: Annotation) -> Path:
    cpu = annotation.cfg.cpus
    dbsize = annotation.total_bp * 2 / 10e6
    cmdb = f'{annotation.dbdir}/cm/{annotation.cfg.kingdom}' #cmpress
    cmpress_cmd = f'cmpress {cmdb}'

    delete_db = f'rm {cmdb}.i1*'
    run_tool(delete_db)

    run_tool(cmpress_cmd)

    out = annotation.basedir / 'cmscan.out'
    print(cmdb)
    
    cmd = f"cmscan -Z {dbsize} --cut_ga --rfam --nohmmonly --fmt 2 --cpu {cpu}" + \
          f" --verbose --tblout {out} --noali {cmdb} {annotation.source_fasta}"
    run_tool(cmd)
    annotation.tool_out[annotation.tools.cmscan.name] = out
    return out

def parse(annotation: Annotation, prog_out: StrGenerator) -> Features:
    infernal = annotation.tools.cmscan
    toolname = f"infernal:" + str(infernal.version)
    features = {}
    for line in map(str.strip, prog_out):
        if line.startswith('#'):
            continue

        data = line.split()
        if len(data) < 2 or not data[2].startswith('RF'):
            continue

        contig_id = data[3]
        if not contig_id in annotation[contig_id]:
            continue

        # Overlaps with a higher scoring match
        if len(data) > 19 and data[19] == '=':
            continue

        if contig_id not in features:
            features[contig_id] = []

        qualifiers = {
            'product': data[1],
            'inference': f'COORDINATES:profile:{toolname}',
            'accession': data[2],
            'note': ' '.join(data[26:]),
            'score': float(data[16])
        }

        start = min(map(int, [data[9], data[10]]))
        end = max(map(int, [data[9], data[10]]))
        strand = -1 if data[11] == '-' else +1

        features[contig_id].append(SeqFeature(
            FeatureLocation(start, end, strand),
            id=f'{data[0]} {data[1]}',
            type='misc_RNA',
            strand=strand,
            qualifiers=qualifiers,
        ))

    log.info(f'Found {deeplen(features)} ncRNAs')
    return features
