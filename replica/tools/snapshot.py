"""Snapshot the replica's sources, or restore one file from a past snapshot.

WHY THIS TOOL EXISTS, and why it grew a restore mode:

Taking snapshots was already here; recovering from one was not. R911 deleted six thousand characters of StoreFlow.cs
by using an anchor that ran past the block it meant to remove, and then could not find the snapshot because the
directory name had been remembered as tools/.snapshot-backup when it is tools/.snapshots. The file came back through
git checkout instead, which worked, and which was luck: the damage was in the working tree and uncommitted, so a
commit between the damage and the recovery would have made git useless too.

Misremembering one directory name is the same as having no snapshot. So recovery is a command now, and the listing
prints the directories it will actually use.

    python tools/snapshot.py                      take a snapshot
    python tools/snapshot.py --list               show the snapshots, newest last
    python tools/snapshot.py --restore <stamp> <relpath>
                                                  put one file back from that snapshot
    python tools/snapshot.py --restore <stamp>    put every file back from that snapshot

The restore checks that the destination exists inside the tree before writing, so a mistyped relative path cannot
create a file somewhere unexpected.
"""

import datetime
import io
import os
import shutil
import sys

ROOT = r"D:\projects\cyber-reverse\replica"
SNAPS = os.path.join(ROOT, "tools", ".snapshots")


def take():
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = os.path.join(SNAPS, stamp)
    count = 0
    for dirpath, _dirnames, filenames in os.walk(os.path.join(ROOT, "src")):
        if f"{os.sep}obj{os.sep}" in dirpath or f"{os.sep}bin{os.sep}" in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".cs"):
                continue
            src = os.path.join(dirpath, fn)
            out = os.path.join(dest, os.path.relpath(src, ROOT))
            os.makedirs(os.path.dirname(out), exist_ok=True)
            shutil.copy2(src, out)
            count += 1
    print("snapshot", stamp, "->", count, "files")


def stamps():
    if not os.path.isdir(SNAPS):
        return []
    return sorted(d for d in os.listdir(SNAPS) if os.path.isdir(os.path.join(SNAPS, d)))


def listing():
    names = stamps()
    if not names:
        print("no snapshots in " + SNAPS)
        return
    total = 0
    for n in names:
        held = sum(len(fs) for _dp, _dn, fs in os.walk(os.path.join(SNAPS, n)))
        total += held
        print("  %-18s %5d files" % (n, held))
    size = sum(os.path.getsize(os.path.join(dp, f))
               for dp, _dn, fs in os.walk(SNAPS) for f in fs)
    print("%d snapshots, %d files, %.1f MB, in %s" % (len(names), total, size / (1024.0 * 1024.0), SNAPS))


def restore(stamp, rel=None):
    base = os.path.join(SNAPS, stamp)
    if not os.path.isdir(base):
        sys.exit("no such snapshot: " + stamp + " (run --list)")

    targets = [rel] if rel else [
        os.path.relpath(os.path.join(dp, f), base)
        for dp, _dn, fs in os.walk(base) for f in fs
    ]

    written = 0
    for r in targets:
        src = os.path.join(base, r)
        if not os.path.isfile(src):
            print("  not in that snapshot: " + r)
            continue
        dst = os.path.normpath(os.path.join(ROOT, r))
        if not dst.startswith(os.path.normpath(ROOT) + os.sep):
            print("  refused, outside the tree: " + r)
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
        written += 1
    print("restored %d file(s) from %s" % (written, stamp))


def main(argv):
    if "--list" in argv:
        listing()
    elif "--restore" in argv:
        i = argv.index("--restore")
        rest = argv[i + 1:]
        if not rest:
            sys.exit("--restore needs a snapshot stamp; run --list")
        restore(rest[0], rest[1] if len(rest) > 1 else None)
    else:
        take()


if __name__ == "__main__":
    main(sys.argv[1:])