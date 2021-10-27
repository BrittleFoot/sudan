import pytest

from sudan.annotation import Annotation


@pytest.fixture
def annotation(pytestconfig) -> Annotation:
    ann = pytestconfig.rootpath / 'tests' / 'test_annotation'
    fna = pytestconfig.rootpath / 'tests' / 'coli-complete-genome.fna'
    return Annotation.initialze(ann, fna)


def test_prepare_annotation(annotation: Annotation):
    assert annotation.features_count == 0
    assert len(annotation.records) == 3
    assert annotation.total_bp == 5594605


def test_aragorn(annotation: Annotation):
    assert annotation.tools.aragorn.have

    


if __name__ == '__main__':
    pytest.main()