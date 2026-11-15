"""For the 13 suspicious namespace matches, how many contract members does the replica type actually have? (R582b)

The namespace screen flags "same name, unrelated part of the program" but that is coarse: 13 of 65 were flagged and
most still look like legitimate renames (`Webhook` -> `Webhooks`, `Controls` -> `Views.Controls`).

Member coverage is the evidence that separates them. For each flagged pair, count how many of the members the
contract binds on that type appear inside the replica declaration:

    100 %   the replica type has every member the contract binds  -> almost certainly the same type, moved
      0 %   none of them                                          -> a candidate different type
    middle  needs a human read

## Why the body includes the declaration head

The first version took only the `{...}` body. Three of the thirteen are **positional records**:

    public sealed record ComboBoxToken(string Text);
    public sealed record ComboBoxGroupHeader(string Name);
    public sealed record Notification(NotificationKind Kind, string Title, string Body);

Their members live in the parameter list and there is no brace body at all, so the first version reported "none
present" for all three — my tool's blind spot, not a fact about the types. This version starts the captured text at
the declaration keyword and runs to the brace close, or to the `;` when there is no body.

That is the same positional-record blind spot `bind_scope.DECL` has (R580), which is worth noting: I built a tool
with the defect I had just documented.

Coverage is a **name** count. It does not show that the members mean the same thing, and it cannot see members the
replica adds. Read-only.
"""

import glob
import io
import json
import os
import re

REPO = r"D:\projects\cyber-reverse\replica"
BIND = os.path.join(REPO, "docs", "xaml_bindings.json")

NS = re.compile(r"^\s*namespace\s+([\w.]+)", re.M)
DECL = re.compile(r"\b(?:class|interface|record|struct|enum)\s+(\w+)")


def bodies():
    """(namespace, name) -> declaration text, including positional parameters."""
    out = {}
    for path in glob.glob(os.path.join(REPO, "src", "**", "*.cs"), recursive=True):
        text = io.open(path, encoding="utf-8", errors="replace").read()
        m = NS.search(text)
        ns = m.group(1) if m else ""
        for d in DECL.finditer(text):
            start = d.start()
            brace = text.find("{", d.end())
            semi = text.find(";", d.end())
            if brace >= 0 and (semi < 0 or brace < semi):
                depth, i = 0, brace
                while i < len(text):
                    if text[i] == "{":
                        depth += 1
                    elif text[i] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    i += 1
                out[(ns, d.group(1))] = text[start:i + 1]
            elif semi >= 0:
                out[(ns, d.group(1))] = text[start:semi + 1]
            else:
                out[(ns, d.group(1))] = text[start:start + 400]
    return out


FLAGGED = [
    ("Cybersole.CaptchaProviders.CaptchaProvider", "Cybersole.Core.Settings"),
    ("Cybersole.Elements.Element", "Cybersole.Core.Models"),
    ("Cybersole.Models.Notification", "Cybersole.Services"),
    ("Cybersole.Models.State", "Cybersole.Stores.Scripts"),
    ("Cybersole.ProxyTesters.ProxyTester", "Cybersole.Services"),
    ("Cybersole.SmartActions.SmartAction", "Cybersole.Core.Models"),
    ("Cybersole.Ui.Controls.ComboBoxEdit", "Cybersole.Ui.Views.Controls"),
    ("Cybersole.Ui.Controls.ComboBoxGroupHeader", "Cybersole.Ui.Views.Controls"),
    ("Cybersole.Ui.Controls.ComboBoxToken", "Cybersole.Ui.Views.Controls"),
    ("Cybersole.Ui.Views.Accounts.GroupGrid", "Cybersole.Ui.Views.Common"),
    ("Cybersole.Ui.Views.Profiles.Modals.ExpressionExample", "Cybersole.Core.Expressions"),
    ("Cybersole.Ui.Views.TimeSpanOption", "Cybersole.Core.Models"),
    ("Cybersole.Webhook.IWebhook", "Cybersole.Core.Webhooks"),
]


def main():
    binds = json.load(io.open(BIND, encoding="utf-8"))
    body = bodies()

    print("%-52s %-8s %-6s %s" % ("contract type", "members", "found", "verdict"))
    print("-" * 112)

    same, diff, partial = [], [], []

    for full, actual_ns in FLAGGED:
        members = list(binds.get(full) or [])
        simple = full.split(".")[-1].split("`")[0]
        text = body.get((actual_ns, simple))
        if text is None:
            print("%-52s %-8d %-6s %s" % (full, len(members), "?", "declaration not found"))
            continue

        found = [m for m in members if re.search(r"\b" + re.escape(m) + r"\b", text)]
        pct = 100.0 * len(found) / max(1, len(members))
        if pct >= 99.9:
            verdict = "SAME (all bound members present)"
            same.append(full)
        elif pct <= 0.1:
            verdict = "DIFFERENT (none present): " + ", ".join(members[:4])
            diff.append(full)
        else:
            missing = [m for m in members if m not in found]
            verdict = "PARTIAL — missing: " + ", ".join(missing[:4])
            partial.append(full)
        print("%-52s %-8d %-6d %s" % (full, len(members), len(found), verdict[:70]))

    print()
    print("same     : %d" % len(same))
    print("partial  : %d  %s" % (len(partial), ", ".join(p.split('.')[-1] for p in partial)))
    print("different: %d  %s" % (len(diff), ", ".join(p.split('.')[-1] for p in diff)))


if __name__ == "__main__":
    main()
