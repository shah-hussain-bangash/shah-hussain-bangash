"""Offline file-consistency checks; no claim of physical or source authenticity."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


def require(condition, message):
    if not condition:
        raise ValueError(message)


def file_at(root, relative):
    path = root / relative
    resolved = path.resolve()
    require(resolved.is_relative_to(root.resolve()), 'Path escapes evidence checkout')
    require(path.is_file() and not path.is_symlink(), 'Missing or linked file: ' + str(relative))
    return path


def load(root, relative):
    return json.loads(file_at(root, relative).read_text(encoding='utf-8'))


def verify(root):
    root = Path(root)
    prefix = Path('docs/edgeops')
    visual = load(root, prefix/'visual-capture-manifest.json')
    brief = load(root, prefix/'brief-manifest.json')
    ci = load(root, prefix/'ci-evidence.json')
    commit = ci['commit']
    require(re.fullmatch(r'[0-9a-f]{40}', commit), 'Invalid application commit')
    require(visual['source_commit'] == brief['source_application_commit'] == commit,
            'Evidence application commits disagree')
    for record in (visual, brief):
        require(record['physical_acceptance_verified'] is False,
                'Historical synthetic record cannot establish physical acceptance')
    require(ci['physical_status']['physical_acceptance_verified'] is False,
            'CI snapshot cannot establish physical acceptance')
    require(brief['production_ready'] is False and ci['physical_status']['production_ready'] is False,
            'Software evidence cannot establish production readiness')
    records = [*visual['images'], {**brief, 'path':brief['file']}]
    video_manifest = prefix/'video-capture-manifest.json'
    if (root/video_manifest).is_file():
        video = load(root, video_manifest)
        require(video['schema'] == 'edgeops.synthetic-video-evidence.v1', 'Invalid video manifest')
        require(re.fullmatch(r'[0-9a-f]{40}', video['source_application_commit']),
                'Invalid video source commit')
        require(video['physical_acceptance_verified'] is False and video['production_ready'] is False,
                'Synthetic video cannot establish physical acceptance')
        require(video['capture_checks']['maintenance_status'] == 'draft'
                and video['capture_checks']['execution_enabled'] is False
                and video['capture_checks']['source_snapshot_matches'] is True,
                'Video capture claims disagree with the declared synthetic workflow')
        records.append({**video, 'path':video['file']})
    pack_manifest = prefix/'arrival-pack-manifest.json'
    if (root/pack_manifest).is_file():
        pack = load(root, pack_manifest)
        require(pack['schema'] == 'edgeops.hardware-preparation-pack-evidence.v1', 'Invalid pack manifest')
        require(re.fullmatch(r'[0-9a-f]{40}', pack['source_application_commit']), 'Invalid pack source commit')
        require(pack['pack_format'] == 'edgeops-arrival-pack-v2'
                and type(pack['hardware_categories']) is int and pack['hardware_categories'] == 30
                and type(pack['received_count_verified']) is int and pack['received_count_verified'] == 0,
                'Pack scope or receipt claim differs')
        for key in ('physical_acceptance_verified', 'equipment_authorized', 'production_ready'):
            require(pack[key] is False, 'Preparation pack cannot establish physical acceptance')
        report = load(root, prefix/pack['verification_report'])
        require(report['archive_sha256'] == pack['sha256']
                and report['pack_format'] == pack['pack_format']
                and report['file_consistency'] == 'passed'
                and type(report['files_checked']) is int and report['files_checked'] == 32
                and type(report['hardware_categories']) is int and report['hardware_categories'] == 30
                and type(report['received_count_verified']) is int and report['received_count_verified'] == 0,
                'Pack verification report disagrees with artifact')
        for key in ('physical_acceptance_verified', 'hardware_connected', 'equipment_authorized',
                    'production_ready', 'source_authenticity_verified', 'signature_verified'):
            require(report[key] is False, 'Pack report cannot establish physical authority')
        records.append({**pack, 'path':pack['file']})
    for record in records:
        raw = file_at(root, prefix/record['path']).read_bytes()
        require(type(record['bytes']) is int and len(raw) == record['bytes'],
                'Artifact size differs: ' + record['path'])
        require(hashlib.sha256(raw).hexdigest() == record['sha256'],
                'Artifact SHA-256 differs: ' + record['path'])
        git_sha = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(git_sha == record['git_blob_sha'], 'Artifact Git identity differs: ' + record['path'])
    require(ci['checks'], 'Missing historical CI records')
    require(len({r['workflow'] for r in ci['checks']}) == len(ci['checks']), 'Duplicate CI workflow')
    for check in ci['checks']:
        require(check['head_sha'] == commit and check['status'] == 'completed'
                and check['conclusion'] == 'success', 'Inconsistent historical CI result')
        expected = 'https://github.com/'+ci['repository']+'/actions/runs/'+str(check['run_id'])
        require(check['url'] == expected, 'CI run URL differs from recorded repository/ID')
    documents = [root/'README.md', *sorted((root/prefix).glob('*.md'))]
    count = 0
    for document in documents:
        text = document.read_text(encoding='utf-8')
        require(sum(line.startswith('```') for line in text.splitlines()) % 2 == 0,
                'Unclosed Markdown fence: ' + document.name)
        targets = re.findall(r'\]\(([^)]+)\)', text) + re.findall(r'src="([^"]+)"', text)
        for target in targets:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue  # External availability and authenticity are not tested offline.
            linked_path = document.parent/unquote(parsed.path) if parsed.path else document
            relative = linked_path.relative_to(root)
            linked = file_at(root, relative)
            if parsed.fragment and linked.suffix == '.md':
                headings = re.findall(r'^#{1,6}\s+(.+)$', linked.read_text(encoding='utf-8'), re.M)
                slugs = {re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings}
                require(unquote(parsed.fragment) in slugs, 'Missing heading: ' + target)
            count += 1
    return {'file_consistency':'passed', 'artifacts_checked':len(records),
            'historical_ci_records_checked':len(ci['checks']), 'local_links_checked':count,
            'external_links_checked':False, 'source_authenticity_verified':False,
            'physical_acceptance_verified':False, 'production_ready':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.root), indent=2))
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, 'Evidence verification failed: '+str(error)+'\n')


if __name__ == '__main__':
    main()

