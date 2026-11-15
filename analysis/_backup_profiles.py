"""Inspect the original's own .cyb backup: which keys a Profile actually carries.

Read-only evidence: `%APPDATA%\\Cybersole\\Backups\\*.cyb` is written by the ORIGINAL (never by the
replica), so its key set is trustworthy in a way settings.json is not (see AGENTS.md §2.2).

Why not tools/*.py: replica/tools/live_schema_diff.py compares the replica's model against the
replica's own output; this script reads the original's backup instead, which is the point.

Usage: python analysis/_backup_profiles.py
"""
import glob
import io
import json
import os

root = os.path.expandvars(r'%APPDATA%\Cybersole')
path = sorted(glob.glob(os.path.join(root, 'Backups', '*.cyb')))[-1]
data = json.load(io.open(path, encoding='utf-8', errors='replace'))
print('backup:', os.path.basename(path))
print('top-level keys:', ', '.join(sorted(data)))
for section in ('profiles', 'profileGroups', 'proxies', 'proxyGroups'):
    rows = data.get(section)
    if not isinstance(rows, list) or not rows:
        continue
    print('\n== %s  (%d row(s))' % (section, len(rows)))
    first = rows[0]
    if isinstance(first, dict):
        for key in sorted(first):
            value = first[key]
            kind = type(value).__name__
            preview = '' if isinstance(value, (dict, list)) else repr(value)[:40]
            print('   %-22s %-6s %s' % (key, kind, preview))
        nested = {k: v for k, v in first.items() if isinstance(v, dict)}
        for key, value in nested.items():
            print('   nested %s -> %s' % (key, ', '.join(sorted(value))))
