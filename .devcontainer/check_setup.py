"""Post-create check: is the environment able to solve, and is the licence present?

Run automatically when the Codespace is built. It never prints the licence
contents - only whether the solver can be initialised with it.
"""
import os
import sys

print("=" * 64)
lic = os.environ.get("XPAUTH_PATH", "")
print(f"XPAUTH_PATH = {lic or '(unset)'}")

if not lic or not os.path.exists(lic):
    print("\nLICENCE NOT FOUND. The licence is deliberately NOT in this repository")
    print("(it is a credential and .gitignore excludes it). To finish setup:")
    print("  1. drag xpauth.xpr into the workspace root in the VS Code explorer")
    print("  2. re-run:  python .devcontainer/check_setup.py")
    print("The repository is fully usable without it for everything except solving.")
    sys.exit(0)

try:
    import numpy as np
    import xpress as xp
except ImportError as exc:
    print(f"\nimport failed: {exc}\nrun: pip install -r requirements.txt")
    sys.exit(1)

print(f"xpress {xp.__version__} | optimizer {xp.getVersion()}")
p = xp.problem()
p.controls.outputlog = 0
v = p.addVariables(3, lb=0, ub=1, name="v")
p.addConstraint(xp.Sum(v) == 1)
p.setObjective(xp.Dot([1.0, 2.0, 3.0], v), sense=xp.maximize)
p.optimize()
print(f"smoke test: objective = {p.getObjVal():.1f} (expected 3.0)")
print("\nlicence OK — the pipeline can run. See README.md for the script order.")
print("=" * 64)
