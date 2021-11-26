import logging

from distutils.sysconfig import get_python_lib
from pathlib import Path

import sudan
from sudan.annotation import Annotation, Features
from sudan.tools import aragorn, barrnap, cmscan, minced, prodigal, run_tool
from sudan.cli import parse_args

FORMAT = '[%(levelname)-5s][%(name)12s] %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('sudan')



class Config:

    FORMAT_FASTA = 'fasta'
    MIN_CONTIG_LEN = 200
    MAX_TRNA_LEN = 500

    kingdom = 'Bacteria'
    



def get_db_path():
    DB_NAME = 'sudan_db'
    db_dir = Path(get_python_lib()) / DB_NAME
    if not db_dir.is_dir():
        db_dir = Path(__file__).parent / DB_NAME 

    if not db_dir.is_dir():
        logger.error(f'{db_dir} is not a database dir, something wrong!')

    return db_dir
       



def main():
    print('Hello, World! This is sudan main function. It is perfectly empty.')
    print(f'Although we found a database dir in {get_db_path()}')
    args = parse_args()
    annotation = Annotation.initialze(Path(args.output_dir), Path(args.input_file))
    annotation.kingdom = args.kingdom
    out = aragorn.run(annotation)
    with open(out, 'r') as fd:
        features = aragorn.parse(annotation, fd)
    annotation.add_features(features)    
    out = barrnap.run(annotation)
    with open(out, 'r') as fd:
        features = barrnap.parse(annotation, fd)
    annotation.add_features(features)
    out = cmscan.run(annotation)
    with open(out, 'r') as fd:
        features = cmscan.parse(annotation, fd)
    annotation.add_features(features)   
    out = minced.run(annotation)
    with open(out, 'r') as fd:
        features = minced.parse(annotation, fd)
    annotation.add_features(features)
    out = prodigal.run(annotation)
    with open(out, 'r') as fd:
        features = prodigal.parse(annotation, prodigal.run(annotation))
    annotation.add_features(features)

    faa_name = Path(annotation.basedir) / 'out.faa' #change it
    with open(faa_name, 'w') as file:
      count = 0
      for sid in annotation.records.keys():
        for f in annotation.features(sid):
            if f.type == 'CDS':
                count += 1
                file.write(f'>{sid}_{count}_{f.location.end}_{f.location.end}\n')
                feature_s = f.extract(annotation.records[sid])
                file.write(f'{feature_s.translate(table=11).seq}\n') #add gcode

        databases = []
    # https://isfinder.biotoul.fr/
    # if there is an IS (Insertion Sequence) database we use that first
    IS_db = f"{annotation.dbdir}/kingdom/{annotation.kingdom}/IS"
    if Path(IS_db).is_file():
        databases.append({
            'db': 'IS',
            'db_path': Path(IS_db),
            'src': 'similar to AA sequence:ISfinder:',
            'fmt': 'blast',
            'mincov': 90,
            'evalue': 1e-30  # IS families are quite specific
        })

    # https://www.ncbi.nlm.nih.gov/bioproject/PRJNA313047
    # if there is an AMR (antimicrobial resitance) database we use that early on
    AMR_db = f"{annotation.dbdir}/kingdom/{annotation.kingdom}/AMR"
    if Path(AMR_db).is_file():
        databases.append({
            'db': 'AMR',
            'db_path': Path(AMR_db),
            'scr': 'similar to AA sequence:BARRGD:',
            'fmt': 'blast',
            'mincov': 90,
            'evalue': 1e-300   # need to exact alleles (~ MIN_DBL, 0.0 not accepted)
        })

    # primary data source is a curated subset of uniprot (evidence <= 1 per Phylum)
    databases.append({
    'db': 'sprot',
    'db_path': Path(annotation.dbdir) / 'kingdom'/ annotation.kingdom /'sprot',
    'scr': 'similar to AA sequence:UniProtKB:',
    'fmt': 'blast',
    'mincov': 80,
    'evalue': 1e-9
    })

    for name in ('sprot', 'IS', 'AMR'):
        fasta = f'{annotation.dbdir}/kingdom/{annotation.kingdom}/{name}'
        if Path(fasta).is_file():
            run_tool(f"makeblastdb -hash_index -dbtype prot -in {fasta} -logfile /dev/null")
    
    for db in databases:
        cmd = f"blastp -query {Path('/home/marina/sudan') / faa_name} -db {db['db_path']}" + \
              f" -evalue {db['evalue']} -qcov_hsp_perc {db['mincov']} -num_threads 1" + \
              f" -num_alignments 1 -seg no -outfmt '6 qseqid stitle saccver pident length" + \
              f" mismatch gapopen qstart qend sstart send evalue bitscore'" + \
              f" -out {annotation.basedir / db['db']}"
        run_tool(cmd)