import pytest

from sudan.annotation import Annotation
from sudan.tools.barrnap import run, parse

@pytest.fixture
def annotation(pytestconfig) -> Annotation:
    ann = pytestconfig.rootpath / 'tests' / 'test_annotation'
    fna = pytestconfig.rootpath / 'tests' / 'coli-complete-genome.fna'
    return Annotation.initialze(ann, fna)


def test_run(annotation: Annotation):
    out = run(annotation)

    with open(out, 'r') as fd:
        features = parse(annotation, fd)
        annotation.add_features(features)

        assert annotation.features_count == 22