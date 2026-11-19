"""The reachability oracle: does a method body actually reach the published image?

R1261 predicted, and R1262 confirmed, that editing a step method's body leaves the artifact's byte size completely
unchanged. That turns a question which had been answered by string probing -- and answered wrongly four times -- into
a measurement: change one method, republish, and compare.

    python analysis/reach_oracle.py record            # after a publish: note size, pdata, and the src digest
    python analysis/reach_oracle.py compare           # what changed since the last record
    python analysis/reach_oracle.py probe <file.cs>   # what to do: read, edit, publish, compare

The oracle cannot say *why* a method is trimmed, only whether it is. That is deliberate: R1242 tried to explain the
why with three instruments and failed, while one size comparison settles the whether in a single publish.
"""
import hashlib
import io
import json
import os
import subprocess
import sys

STATE = 'analysis/reach_oracle.json'
ARTIFACT = 'replica/.publish-aot/Cybersole.Ui.exe'


def src_digest():
    h = hashlib.sha256()
    count = 0
    for root, _dirs, files in os.walk('replica/src'):
        for name in sorted(files):
            if not name.endswith('.cs'):
                continue
            path = os.path.join(root, name)
            h.update(path.replace(os.sep, '/').encode('utf-8'))
            h.update(io.open(path, 'rb').read())
            count += 1
    return h.hexdigest(), count


def pdata_count():
    out = subprocess.run([sys.executable, 'python', os.path.join('tools', 'metrics_report.py'), '--skip-tests'],
                         capture_output=True, text=True, cwd='replica')
    for line in (out.stdout or '').splitlines():
        if 'pdata' in line and 'replica' in line:
            for token in line.replace('{', ' ').replace('}', ' ').replace(',', ' ').split():
                if token.replace(',', '').isdigit() and len(token) > 3:
                    pass
    return None


def load():
    if not os.path.exists(STATE):
        return []
    return json.load(io.open(STATE, encoding='utf-8'))


def artifact_identity():
    """Size is not enough: R1265 changed a method body and the size stayed identical while the hash moved."""
    if not os.path.exists(ARTIFACT):
        return None, None
    h = hashlib.sha256()
    h.update(io.open(ARTIFACT, 'rb').read())
    return os.path.getsize(ARTIFACT), h.hexdigest()


def record(note):
    digest, files = src_digest()
    size, art_sha = artifact_identity()
    rows = load()
    row = {'artifact_size': size, 'artifact_sha256': art_sha, 'src_files': files,
           'src_sha256': digest, 'note': note}
    prev = rows[-1] if rows else None
    rows.append(row)
    io.open(STATE, 'w', encoding='utf-8', newline='\n').write(json.dumps(rows, indent=2, ensure_ascii=False))
    print('recorded: size=%s sha=%s src_files=%d' % (size, (art_sha or '')[:16], files))
    if prev:
        src_moved = digest != prev['src_sha256']
        art_moved = art_sha != prev.get('artifact_sha256')
        print('vs previous: size %+d, src %s, artifact %s'
              % ((size or 0) - (prev['artifact_size'] or 0),
                 'changed' if src_moved else 'same',
                 'changed' if art_moved else 'same'))
        if src_moved and art_moved:
            print('=> the source and the artifact both moved: what changed reaches the image')
        elif src_moved and not art_moved:
            print('=> the source moved and the artifact did not: what changed is NOT in the image')
    return 0


def compare():
    rows = load()
    if len(rows) < 2:
        print('need at least two records; run record after each publish')
        return 1
    a, b = rows[-2], rows[-1]
    print('previous: size=%s sha=%s' % (a['artifact_size'], (a.get('artifact_sha256') or '')[:16]))
    print('current : size=%s sha=%s' % (b['artifact_size'], (b.get('artifact_sha256') or '')[:16]))
    print('delta   : size %+d, artifact %s, src %s'
          % ((b['artifact_size'] or 0) - (a['artifact_size'] or 0),
             'changed' if a.get('artifact_sha256') != b.get('artifact_sha256') else 'same',
             'changed' if a['src_sha256'] != b['src_sha256'] else 'same'))
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 0
    if argv[0] == 'record':
        return record(argv[1] if len(argv) > 1 else '')
    if argv[0] == 'compare':
        return compare()
    print(__doc__)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
