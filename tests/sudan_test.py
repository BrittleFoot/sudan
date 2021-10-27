import pytest

import sudan
 
from pathlib import Path

from sudan.annotation import Annotation


@pytest.fixture
def test_annotation(pytestconfig) -> Path:
    return pytestconfig.rootpath / 'tests' / 'test_annotation'


@pytest.fixture
def coli_fasta(pytestconfig) -> Path:
    return pytestconfig.rootpath / 'tests' / 'coli-complete-genome.fna'


@pytest.fixture
def annotation(coli_fasta, test_annotation) -> Annotation:
    return Annotation.initialze(test_annotation, coli_fasta)


def test_prepare_annotation(annotation: Annotation):
    assert annotation.features_count == 0
    assert len(annotation.records) == 3
    assert annotation.total_bp == 5594605


def test_aragorn(annotation: Annotation):
    assert annotation.tools.aragorn.have

    


if __name__ == '__main__':
    pytest.main()