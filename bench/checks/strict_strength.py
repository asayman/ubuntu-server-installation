"""usage: python strict_strength.py <workspace>

Mutant score with a strict pass rule: exit 0, no output line mentions FAIL, last line is exactly PASS.
WARNING: runs the workspace's test_duration.py on your machine, unsandboxed."""
import ast, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "hidden_check.py"), encoding="utf-8").read()
ns = {}
for node in ast.parse(src).body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") in ("REF", "MUTANTS"):
        ns[node.targets[0].id] = ast.literal_eval(node.value)
REF, MUTANTS = ns["REF"], ns["MUTANTS"]
tf = os.path.join(sys.argv[1], "test_duration.py")


def ok(impl):
    d = tempfile.mkdtemp()
    try:
        shutil.copy(tf, d)
        open(os.path.join(d, "duration.py"), "w").write(impl)
        try:
            r = subprocess.run([sys.executable, "-B", "test_duration.py"], cwd=d, capture_output=True, text=True, timeout=30)
        except subprocess.TimeoutExpired:
            return False
        lines = [l.strip() for l in (r.stdout + r.stderr).splitlines() if l.strip()]
        return r.returncode == 0 and not any("FAIL" in l.upper() for l in lines) and bool(lines) and lines[-1] == "PASS"
    finally:
        shutil.rmtree(d, ignore_errors=True)


if not ok(REF):
    sys.exit("STRICT STRENGTH: n/a, tests reject a correct implementation")
missed = [n for n, a, b in MUTANTS if ok(REF.replace(a, b))]
print("STRICT STRENGTH: %d/%d" % (len(MUTANTS) - len(missed), len(MUTANTS)), "missed: " + ", ".join(missed) if missed else "")
