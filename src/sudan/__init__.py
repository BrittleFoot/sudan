import logging


FORMAT = '[%(levelname)-5s][%(name)12s] %(message)s'
logging.basicConfig(format=FORMAT)



class Config:

    FORMAT_FASTA = 'fasta'
    MIN_CONTIG_LEN = 200
    MAX_TRNA_LEN = 500




def main():
    print('Hello, World! This is sudan main function. It is perfectly empty.')