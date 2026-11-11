"""Assure one AI agent end to end: run three open-source tools over its configuration, its
runtime log and its model gateway, then merge their evidence into one OSCAL bundle and one report.

    python assure.py --out assurance

Set SOURCE_DATE_EPOCH for byte-identical output (CI does).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCENARIO = 'scenario'  # relative and forward-slash: tools record input paths as given
AS_OF = '2026-10-12'
NS = uuid.UUID('5f0c3a52-61f4-4c1e-9a3e-2d4b9c6e7a10')

# (folder, question it answers, tool, command, report, OSCAL file) per layer.
LAYERS = [
    ('access', 'What is the agent allowed to do?', 'agent-access-review',
     ['agent_access_review', 'scan', f'{SCENARIO}/agents.yaml', f'{SCENARIO}/.mcp.json', '--as-of', AS_OF,
      '--fail-on', 'never'],
     'access-review.md', 'oscal/assessment-results.json'),
    ('runtime', 'What did it actually do?', 'multiagent-flight-recorder',
     ['agent_flight_recorder', 'report', '--log', f'{SCENARIO}/runtime/flight.jsonl',
      '--pubkey', f'{SCENARIO}/runtime/demo-signing.pub', '--fail-on', 'never'],
     'flight-report.md', 'oscal/assessment-results.json'),
    ('gateway', 'Is the path its model calls take controlled?', 'ai-gateway-audit',
     ['ai_gateway_audit', 'scan', f'{SCENARIO}/gateway', '--as-of', AS_OF, '--fail-on', 'never'],
     'gateway-audit.md', 'oscal/assessment-results.json'),
]
RANK = {'not-satisfied': 0, 'satisfied': 1}


def run_layer(out: Path, folder: str, cmd: list) -> None:
    args = [sys.executable, '-m', *map(str, cmd), '--out', str(out / folder)]
    done = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    if done.returncode:
        sys.exit(f'{cmd[0]} failed:\n{done.stdout}\n{done.stderr}')


def rebase(node, src: Path, dst: Path):
    """Point evidence links written relative to src at the same files from dst."""
    if isinstance(node, dict):
        return {k: (os.path.relpath((src / v).resolve(), dst).replace(os.sep, '/')
                    if k == 'href' and not v.startswith(('#', 'http')) else rebase(v, src, dst))
                for k, v in node.items()}
    if isinstance(node, list):
        return [rebase(v, src, dst) for v in node]
    return node


def now() -> str:
    epoch = os.environ.get('SOURCE_DATE_EPOCH')
    t = datetime.fromtimestamp(int(epoch), timezone.utc) if epoch else datetime.now(timezone.utc)
    return t.isoformat().replace('+00:00', 'Z')


def build(out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    results, controls = [], defaultdict(dict)
    for folder, question, tool, cmd, _, oscal in LAYERS:
        run_layer(out, folder, cmd)
        path = out / folder / oscal
        ar = json.loads(path.read_text(encoding='utf-8'))['assessment-results']
        for res in ar['results']:
            res = rebase(res, path.parent, out / 'oscal')
            res['title'] = f'{question} ({tool})'
            res.setdefault('props', []).append({'name': 'layer', 'value': folder})
            results.append(res)
            for f in res['findings']:
                cid = f['target']['target-id']
                state = f['target']['status']['state']
                checks = f['title'].split(': ', 1)[-1]
                prev = controls[cid].get(folder)
                if prev is None or RANK[state] < RANK[prev[0]]:
                    controls[cid][folder] = (state, checks)

    bundle = {'assessment-results': {
        'uuid': str(uuid.uuid5(NS, '|'.join(r['uuid'] for r in results))),
        'metadata': {'title': 'AI assurance: Acme Release Agent (configuration, runtime, gateway)',
                     'last-modified': now(), 'version': '1', 'oscal-version': '1.1.2'},
        'import-ap': {'href': '#'},
        'results': results,
    }}
    (out / 'oscal').mkdir(exist_ok=True)
    (out / 'oscal' / 'assessment-results.json').write_text(json.dumps(bundle, indent=2) + '\n', encoding='utf-8', newline='\n')
    write_report(out, controls)
    write_manifest(out)
    return bundle


def control_key(cid: str):
    """'ac-2.3' sorts as ('ac', 2, 3), right after 'ac-2'."""
    fam, _, rest = cid.partition('-')
    base, _, enh = rest.partition('.')
    return fam, int(base), int(enh or 0)


def control_label(cid: str) -> str:
    """OSCAL 'ac-2.3' is written AC-2(3) in NIST SP 800-53."""
    base, _, enh = cid.upper().partition('.')
    return f'{base}({enh})' if enh else base


def write_report(out: Path, controls: dict) -> None:
    mark = {'satisfied': 'pass', 'not-satisfied': '**FAIL**'}
    failing = sum(any(s == 'not-satisfied' for s, _ in c.values()) for c in controls.values())
    multi = sum(len(c) > 1 for c in controls.values())
    lines = ['# AI assurance report: Acme Release Agent', '',
             f'Review date {AS_OF}. One agent, assessed at three layers by three tools. '
             f'**{len(controls)} NIST SP 800-53 controls** have evidence, **{multi}** of them from more than '
             f'one layer; **{failing}** are not satisfied.', '',
             '| Layer | Question | Tool | Report |', '|---|---|---|---|']
    for folder, question, tool, _, report, _ in LAYERS:
        lines.append(f'| {folder} | {question} | `{tool}` | [{report}]({folder}/{report}) |')
    lines += ['', '## Controls across layers', '',
              'Each cell is that layer\'s result for the control and the checks behind it. '
              'A control is satisfied overall only when every layer that tested it passes.', '',
              '| NIST 800-53 | Configuration | Runtime | Gateway | Overall |', '|---|---|---|---|---|']
    for cid in sorted(controls, key=control_key):
        cells = []
        for folder, *_ in LAYERS:
            hit = controls[cid].get(folder)
            cells.append(f'{mark[hit[0]]} ({hit[1]})' if hit else '')
        overall = 'not-satisfied' if any(s == 'not-satisfied' for s, _ in controls[cid].values()) else 'satisfied'
        lines.append(f'| {control_label(cid)} | ' + ' | '.join(cells) + f' | {mark[overall]} |')
    lines += ['', 'The merged OSCAL assessment results are in [`oscal/assessment-results.json`]'
              '(oscal/assessment-results.json): one result per layer, with every evidence link pointing at the '
              'hashed file it came from. [`manifest.sha256`](manifest.sha256) hashes every file in this bundle.']
    (out / 'assurance-report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')


def write_manifest(out: Path) -> None:
    rows = [f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out).as_posix()}'
            for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'manifest.sha256']
    (out / 'manifest.sha256').write_text('\n'.join(rows) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out', default='assurance', type=Path)
    a = ap.parse_args()
    build(a.out.resolve())
    print(f'Report: {a.out / "assurance-report.md"}\nOSCAL:  {a.out / "oscal" / "assessment-results.json"}')
