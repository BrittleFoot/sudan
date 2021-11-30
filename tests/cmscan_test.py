import pytest

from sudan.annotation import Annotation
from sudan.tools.cmscan import run, parse


def test_run(annotation: Annotation):
    out = run(annotation)
    print(out)

    with open(out, 'r') as fd:
        features = parse(annotation, fd)
        from pprint import pprint
        print(features)
        annotation.add_features(features)

        assert annotation.features_count == 264