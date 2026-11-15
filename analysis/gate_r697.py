"""R697: gate `func_compare.py --export-only` on auto_analysis_ready.

BLOCKERS §44/§45 recorded that a function count taken mid-analysis is wrong, and §129 (R694) showed the same trap is
*stable*: 136,798/187,328 = 0.730 at R433 and 136,989/187,732 = 0.730 at R694, 260 rounds apart. Both entries were
report-only -- the inventory in `analysis/trap_entry_inventory.py` found no operational entry point for that family.

`export()` already fetched `server_health` and returned it without looking at it. This makes the readiness flag a hard
gate, so the trap cannot be repeated by anyone who runs the command -- which is the only place it was ever repeated.
"""

import io
import subprocess

PATH = r"D:\projects\cyber-reverse\analysis\func_compare.py"

OLD = '''def export(url, dest, label):
    client = Client(url)
    client.initialize()
    health = client.call("server_health")
'''

NEW = '''def _ready(health):
    """auto_analysis_ready from a server_health reply that may arrive as dict or JSON text."""
    if isinstance(health, str):
        try:
            health = json.loads(health)
        except json.JSONDecodeError:
            return None
    if isinstance(health, dict):
        # the plugin may nest the payload one level down
        if "auto_analysis_ready" in health:
            return health["auto_analysis_ready"]
        for v in health.values():
            if isinstance(v, dict) and "auto_analysis_ready" in v:
                return v["auto_analysis_ready"]
    return None


def export(url, dest, label):
    client = Client(url)
    client.initialize()
    health = client.call("server_health")

    # R697: refuse to export from an instance whose auto-analysis has not finished.
    # Port-open is not readiness -- the plugin answers while functions are still being recognised, and the partial
    # count is *stable* (wrong/right = 0.730 at both R433 and R694, 260 rounds apart), so two identical samples prove
    # nothing. This gate is the operational entry point for BLOCKERS 44/45, which until R697 lived only in a report.
    ready = _ready(health)
    if ready is not True:
        raise SystemExit(
            "%s: auto_analysis_ready is %r -- refusing to export.\\n"
            "  Port-open is not readiness; functions are still being recognised.\\n"
            "  Wait first:  python analysis/wait_ready.py <port> <timeout>\\n"
            "  Background:  BLOCKERS 44/45 and 129, PARITY_PRODUCT section 8, IDA_STARTUP_CHECKLIST."
            % (label, ready))
'''


def main():
    text = io.open(PATH, encoding="utf-8").read()
    if "R697" in text:
        print("already patched")
        return
    if OLD not in text:
        print("MISS anchor")
        return
    text = text.replace(OLD, NEW, 1)
    import ast
    ast.parse(text)
    io.open(PATH, "w", encoding="utf-8").write(text)
    print("patched: export() now gates on auto_analysis_ready")

    subprocess.run(["git", "add", "-A"], cwd=r"D:\projects\cyber-reverse", check=False)
    r = subprocess.run(
        ["git", "-c", "user.name=dsh", "-c", "user.email=dsh@local", "commit", "-q", "-m",
         "R697: refuse to export a function inventory from an instance that is still analysing\n\n"
         "export() already fetched server_health and ignored it. Now auto_analysis_ready must be true\n"
         "or the export aborts with the reason and the wait command. BLOCKERS 44/45 recorded this trap\n"
         "and had no operational entry point; the trap is stable (0.730 wrong/right at both R433 and R694)\n"
         "so two agreeing samples do not prove correctness."],
        cwd=r"D:\projects\cyber-reverse", capture_output=True, text=True)
    print("commit rc=%d %s" % (r.returncode, (r.stdout or r.stderr).strip()[:180]))


if __name__ == "__main__":
    main()
