"""
    Shared fixtures and test configuration found here
"""
import pytest

from sudan.annotation import Annotation

@pytest.fixture
def annotation(pytestconfig) -> Annotation:
    ann = pytestconfig.rootpath / 'tests' / 'test_annotation'
    fna = pytestconfig.rootpath / 'tests' / 'coli-complete-genome.fna'
    return Annotation.initialze(ann, fna)
