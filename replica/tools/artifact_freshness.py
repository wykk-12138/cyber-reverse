"""Is the .publish-aot artifact the one the current source would produce?

WHY THIS EXISTS: criterion (c) asks for an artifact-level comparison that can be recomputed, and func_count.py does
exactly that -- original against .publish-aot. But a comparison is only about the current code if the artifact was built
from it, and nothing checked that. R932 found the published executable dated 2026-11-16 11:49 with sixty-four source
files totalling twenty thousand lines changed after it, so every figure derived from it -- including the function ratio
the objective's first clause is measured by -- described a build more than a day old. A stale figure is not a wrong
figure, but quoting it without knowing it is stale is the mistake, and the fix is to make staleness visible in the same
table that carries the number.

This is a timestamp comparison and nothing more. It cannot tell whether a change altered the output -- a comment edit
marks the artifact stale while changing nothing. That is the correct direction to err: a false alarm costs a publish,
a missed one costs a figure quoted about code that no longer exists.
"""

import io
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARTIFACT = os.path.join(ROOT, ".publish-aot", "Cybersole.Ui.exe")
SOURCE = os.path.join(ROOT, "src")


def newest_source():
    """The newest .cs under src, and how many files postdate the artifact."""
    if not os.path.isdir(SOURCE):
        return None, 0, 0

    newest, newest_path, newer, newer_lines = 0.0, None, 0, 0
    touched = []
    for dirpath, dirnames, filenames in os.walk(SOURCE):
        dirnames[:] = [d for d in dirnames if d not in ("obj", "bin")]
        for name in filenames:
            if not name.endswith(".cs"):
                continue
            p = os.path.join(dirpath, name)
            try:
                m = os.path.getmtime(p)
            except OSError:
                continue
            if m > newest:
                newest, newest_path = m, p
            if os.path.exists(ARTIFACT) and m > os.path.getmtime(ARTIFACT):
                newer += 1
                touched.append(p)
                try:
                    with io.open(p, encoding="utf-8", errors="replace") as fh:
                        newer_lines += sum(1 for _ in fh)
                except OSError:
                    pass
    return newest_path, newer, newer_lines, touched


def dirty_among(paths):
    """
    How many of these files differ from HEAD.

    R1183: mutation-check.py rewrites every mutation target and restores it, which updates mtime while the
    bytes go back to exactly what was committed. Before this, each mutation run therefore left the artifact
    looking stale by seventeen files for the rest of the session - a false alarm that cost three rounds of
    wondering. Touching a file is not changing it, so the two are counted apart, and a file that really did
    change still marks the artifact stale.
    """
    if not paths:
        return 0
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--"] + paths,
                             cwd=ROOT, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return len(paths)          # cannot tell: stay on the cautious side
    if out.returncode != 0:
        return len(paths)
    return sum(1 for line in out.stdout.split("\n") if line.strip())


def main():
    if not os.path.exists(ARTIFACT):
        print("publish artifact: absent")
        print("publish artifact state: missing -- func_count's replica figure cannot be produced")
        return 1

    art = os.path.getmtime(ARTIFACT)
    newest_path, newer, newer_lines, touched = newest_source()

    dirty = dirty_among(touched)

    print("publish artifact: %s" % os.path.relpath(ARTIFACT, ROOT))
    print("publish artifact mtime: %s" % _stamp(art))
    # R1211: size and a content digest, printed as provenance rather than as a change detector. I added them to
    # answer "did this rebuild change the executable", and then calibrated that question and lost the answer:
    # publishing the same unchanged tree twice produced 39e8fd73... and 847757a0..., so this build is not
    # reproducible and two digests are not comparable across builds. What the report can still say is which
    # artifact was on disk at a given time; what it cannot say is whether a source change reached it. For that,
    # the usable signals are the .pdata count and section mass, or a marker string the new source introduces.
    try:
        import hashlib
        _size = os.path.getsize(ARTIFACT)
        _h = hashlib.sha256()
        with open(ARTIFACT, 'rb') as _f:
            for _chunk in iter(lambda: _f.read(1 << 20), b''):
                _h.update(_chunk)
        print("publish artifact size: %d bytes" % _size)
        print("publish artifact sha256: %s" % _h.hexdigest())
    except OSError as _e:
        print("publish artifact size/sha256: unavailable (%s)" % _e)
    if newest_path:
        print("newest source: %s (%s)" % (os.path.relpath(newest_path, ROOT), _stamp(os.path.getmtime(newest_path))))
    print("source files newer than the artifact: %d" % newer)
    print("lines in those files: %d" % newer_lines)
    print("of those, changed against HEAD: %d" % dirty)
    print("publish artifact state: %s" % ("stale" if dirty else "current"))

    if dirty:
        print("")
        print("  The function ratio in METRICS.md comes from this artifact. While it is stale that ratio describes an")
        print("  older build, so it must be labelled as such wherever it is quoted rather than presented as current.")
    elif newer:
        print("")
        print("  %d files are newer but unchanged against HEAD: mutation-check rewrites and restores its" % newer)
        print("  targets, which updates mtime without changing a byte. Nothing to rebuild.")
    return 0


def _stamp(t):
    import datetime
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    sys.exit(main())