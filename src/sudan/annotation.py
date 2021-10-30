import re

from typing import Dict
from typing import List
from typing import Generator
from logging import getLogger
from pathlib import Path
from Bio import SeqIO 
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature

from sudan import Config
from sudan.tools import Toolkit


log = getLogger('init')


Features = Dict[str, List[SeqFeature]]


class Annotation:
    def __init__(self, basedir: Path, records: Dict[str, SeqRecord], total_bp):
        self.basedir = basedir
        self.total_bp = total_bp
        self.records = records
        self.tools = Toolkit()
        self.tool_out = {}
        self.all_rna = []

        self.source_fasta = basedir / 'source.fasta'
        SeqIO.write(records.values(), self.source_fasta, Config.FORMAT_FASTA)
        log.info(f'Writing source fasta to {self.source_fasta}')

    def __getitem__(self, seq_id: str) -> SeqRecord:
        return self.records[seq_id]

    def features(self, seq_id) -> List[SeqFeature]:
        return self[seq_id].features

    def add_features(self, features: Features):
        for id, fs in features.items():
            features = self[id].features
            for feature in fs:
                features.append(feature)

    @property
    def features_count(self) -> int:
        return sum(len(seq.features) for seq in self.records.values())

    @classmethod
    def initialze(cls, on_base_dir: Path, from_fasta_file: Path):
        on_base_dir.mkdir(parents=True, exist_ok=True)
        log.info(f'Initializing annotation in {on_base_dir}')

        seqs = SeqIO.parse(from_fasta_file, Config.FORMAT_FASTA)
        records, total_bp = _prepare_sequences(seqs)
        return cls(on_base_dir, records, total_bp)


def _rename(id):
    if '|' in id:
        old_id = id
        id = old_id.replace('|', '_')
        log.debug(f'Changing illegal name {old_id} to {id}')

    return id


GAPS = re.compile(r'[*-]')
WACKY = re.compile(r'[^ACTG]')


def _normalize_sequence(seq: Seq) -> Seq:
    seq = str(seq.upper())
    seq, n = GAPS.subn('', seq)
    if n > 0:
        log.debug(f'Removed {n} gaps/pads')

    seq, n = WACKY.subn('N', seq)
    if n > 0:
        log.debug(f'Replaced {n} wacky IUPAC with N')

    return Seq(seq)


def _prepare_sequences(seq_iterator: Generator[SeqRecord, None, None]):
    ncontig = 0
    total_bp = 0
    records = {}
    for contig in seq_iterator:
        if len(contig.seq) < Config.MIN_CONTIG_LEN:
            log.debug(f'Skipping short contig {contig.id}')
            continue

        ncontig += 1

        contig.id = _rename(contig.id)
        
        if contig.id in records:
            raise ValueError(f'Duplicate id in sequence file {contig.id}')

        contig.seq = _normalize_sequence(contig.seq)


        contig.description = ''
        total_bp += len(contig.seq)

        contig.annotations['molecule_type'] = 'DNA'
        records[contig.id] = contig

    if ncontig <= 0:
        e = f'FASTA file {input} contains no suitable sequence entries'
        raise ValueError(e)

    log.info(f'Total {total_bp} BP read')

    return records, total_bp
