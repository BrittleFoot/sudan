import logging

from distutils.sysconfig import get_python_lib
from pathlib import Path


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