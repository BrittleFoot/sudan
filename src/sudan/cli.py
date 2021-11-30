from dataclasses import dataclass
import argparse as ap

from os.path import isfile


def file(arg):
    if isfile(arg):
        return arg
    raise ValueError(arg)


@dataclass
class Arguments:
    input_file: str = ''
    output_dir: str = 'sudan_output'
    kingdom: str = 'Bacteria'
    metagenome: int = 0
    noanno: bool = False
    cpus: int = 8
    hmms: str = ''
    proteins: str = ''
    usegenus: int = 0
    compliant: int = 0


def parse_args() -> Arguments:
    arp = ap.ArgumentParser(
        'sudadn',
        usage='use it wisely',
        description='annotates marvelously',
    )

    def flag(*name_or_flags, help=None):
        return arp.add_argument(*name_or_flags, action='store_true', help=help)

    arp.add_argument('input-file', type=file)
    arp.add_argument('--output-dir', '-o', default='sudan_output')
    arp.add_argument('--kingdom', '-k', default='Bacteria', 
        choices=['Archaea', 'Bacteria', 'Mitochondria', 'Viruses'],
        help='Choose one: Archaea, Bacteria, Mitochondria, Viruses')
    arp.add_argument('--metagenome', default=0, help='Improve gene predictions for highly fragmented genomes')
    arp.add_argument('--noanno', default=False)
    arp.add_argument('--cpus', default=8)
    arp.add_argument('--hmms', default='')
    arp.add_argument('--proteins', default='')
    arp.add_argument('--usegenus', default=0)
    arp.add_argument('--compliant', default=0)

    arp.add_argument('--verboose', '-v', action='count', default=0)

    return Arguments(**arp.parse_args())


def main():
    a = parse_args()
    print(a)



if __name__ == '__main__':
    main()