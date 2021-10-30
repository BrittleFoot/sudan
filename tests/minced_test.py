import pytest

from sudan.annotation import Annotation
from sudan.tools.minced import run, parse


def test_run(annotation: Annotation):
    out = run(annotation)

    with open(out, 'r') as fd:
        features = parse(annotation, fd)
        annotation.add_features(features)

        assert annotation.features_count == 1