"""usage: python hidden_check.py <workspace>   hidden behavior check + mutant score for test 3 (runs the model code unsandboxed)"""
import os, shutil, subprocess, sys, tempfile

WS = os.path.abspath(sys.argv[1])
REF = r'''
import re
_U = {"d": 86400, "h": 3600, "m": 60, "s": 1}
_P = re.compile(r"\s*(?:([0-9]+)d)?\s*(?:([0-9]+)h)?\s*(?:([0-9]+)m)?\s*(?:([0-9]+)s)?\s*", re.I)
def parse_duration(text):
    if not isinstance(text, str):
        raise TypeError("text")
    m = _P.fullmatch(text)
    if not m or not any(g is not None for g in m.groups()):
        raise ValueError(text)
    return sum(int(g) * u for g, u in zip(m.groups(), _U.values()) if g is not None)
def format_duration(seconds):
    if isinstance(seconds, bool) or not isinstance(seconds, int):
        raise TypeError("seconds")
    if seconds < 0:
        raise ValueError("seconds")
    out = ""
    for n, u in _U.items():
        q, seconds = divmod(seconds, u)
        if q:
            out += "%d%s" % (q, n)
    return out or "0s"
'''
MUTANTS = [
    ("day = 23 hours", '"d": 86400', '"d": 82800'),
    ("case sensitive", ", re.I)", ")"),
    ("empty text allowed", "or not any(g is not None for g in m.groups())", "or False"),
    ("trailing junk allowed", "_P.fullmatch(text)", "_P.match(text)"),
    ("wrong error type in parse", 'raise TypeError("text")', 'raise ValueError("text")'),
    ("zero formats as empty", 'out or "0s"', "out"),
    ("negative allowed", "if seconds < 0", "if False"),
    ("bool allowed in format", "isinstance(seconds, bool) or ", ""),
]
CODE = r'''
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
from duration import parse_duration as p, format_duration as f
bad = []
def eq(fn, a, want):
    try: got = fn(a)
    except Exception as e: got = type(e).__name__
    if got != want: bad.append("%s(%r) -> %r, expected %r" % (fn.__name__, a, got, want))
def err(fn, a, E):
    try: got = fn(a)
    except E: return
    except Exception as e: got = type(e).__name__
    bad.append("%s(%r) -> %r, expected %s" % (fn.__name__, a, got, E.__name__))
OK = [("45s",45),("1h30m",5400),("2d 3h",183600),("1D2H3M4S",93784),("  5m  ",300),("90m",5400),("0s",0),("1h  1s",3601),("007s",7)]
BAD = ["","   ","5","m","1h1h","30m1h","1x","-5m","1.5h","1h,5m","5 m","1h foo","1h5"]
FMT = [(0,"0s"),(45,"45s"),(5400,"1h30m"),(86400,"1d"),(93784,"1d2h3m4s"),(3601,"1h1s"),(864000,"10d")]
for a, w in OK: eq(p, a, w)
for a in BAD: err(p, a, ValueError)
for a in (None, 5, b"5m", ["5m"]): err(p, a, TypeError)
for a, w in FMT: eq(f, a, w)
err(f, -1, ValueError)
for a in (1.5, "5", None, True): err(f, a, TypeError)
for n in range(0, 200000, 977): eq(p, f(n), n)
total = len(OK)+len(BAD)+4+len(FMT)+1+4+len(range(0,200000,977))
print("BEHAVIOR: %d/%d" % (total-len(bad), total))
for b in bad[:15]: print("  FAIL", b)
'''
def run(args, cwd):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    try:
        r = subprocess.run([sys.executable] + args, cwd=cwd, env=env, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return 99, "timeout"

code, out = run(["-c", CODE, WS], tempfile.gettempdir())
print(out.strip())
tf = os.path.join(WS, "test_duration.py")
if not os.path.exists(tf):
    sys.exit("TESTS: test_duration.py missing")
code, out = run(["test_duration.py"], WS)
print("OWN TESTS:", "pass" if code == 0 and "PASS" in out else "FAIL\n" + out[-500:])

def with_impl(src):
    d = tempfile.mkdtemp()
    try:
        shutil.copy(tf, d)
        open(os.path.join(d, "duration.py"), "w").write(src)
        c, o = run(["test_duration.py"], d)
        return c == 0 and "PASS" in o
    finally:
        shutil.rmtree(d, ignore_errors=True)
if not with_impl(REF):
    sys.exit("TESTS: reject a correct implementation, so the mutant score would be meaningless")
caught = 0
for name, a, b in MUTANTS:
    assert REF.count(a) == 1, name
    hit = not with_impl(REF.replace(a, b))
    caught += hit
    print("  %s mutant: %s" % ("caught" if hit else "MISSED", name))
print("TEST STRENGTH: %d/%d" % (caught, len(MUTANTS)))
