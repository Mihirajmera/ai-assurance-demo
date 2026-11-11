import hashlib
import json
import os
from pathlib import Path

import pytest

import assure


@pytest.fixture(scope='module')
def out(tmp_path_factory):
    os.environ['SOURCE_DATE_EPOCH'] = '1791763200'
    path = tmp_path_factory.mktemp('bundle')
    assure.build(path)
    return path


def bundle(out):
    return json.loads((out / 'oscal' / 'assessment-results.json').read_text(encoding='utf-8'))['assessment-results']


def hrefs(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == 'href' and not v.startswith(('#', 'http')):
                yield v
            else:
                yield from hrefs(v)
    elif isinstance(node, list):
        for v in node:
            yield from hrefs(v)


def test_one_result_per_layer(out):
    layers = [p['value'] for r in bundle(out)['results'] for p in r['props'] if p['name'] == 'layer']
    assert layers == ['access', 'runtime', 'gateway']


def test_every_evidence_link_resolves(out):
    links = list(hrefs(bundle(out)['results']))
    assert links, 'expected evidence links in the merged results'
    for href in links:
        assert (out / 'oscal' / href).resolve().is_file(), href


def test_finding_uuids_are_unique(out):
    ids = [f['uuid'] for r in bundle(out)['results'] for f in r['findings']]
    assert len(ids) == len(set(ids))


def test_manifest_matches_files(out):
    for line in (out / 'manifest.sha256').read_text(encoding='utf-8').splitlines():
        digest, name = line.split('  ', 1)
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == digest, name


def test_report_rolls_up_across_layers(out):
    report = (out / 'assurance-report.md').read_text(encoding='utf-8')
    # SI-7 fails at runtime (tool description changed) and at the gateway (image not pinned by digest).
    assert '| SI-7 |  | **FAIL** (AFR-06) | **FAIL** (GWA-07) | **FAIL** |' in report
    assert '| AC-2(3) |' in report


def test_output_is_reproducible(out, tmp_path):
    assure.build(tmp_path)
    assert (tmp_path / 'manifest.sha256').read_text() == (out / 'manifest.sha256').read_text()


def test_committed_sample_is_current(out):
    sample = Path(assure.ROOT) / 'sample-output' / 'manifest.sha256'
    assert sample.read_text(encoding='utf-8') == (out / 'manifest.sha256').read_text(encoding='utf-8'), \
        'regenerate: SOURCE_DATE_EPOCH=1791763200 python assure.py --out sample-output'
