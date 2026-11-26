"""usage: python ascii_check.py <workspace>   spec: digits must be ASCII, so each input must raise ValueError"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
from duration import parse_duration as p
bad = []
for x in ("\u0665s", "1h\u0663m", "\uff15m", "\u096bs"):
    try: bad.append("%s -> %r" % (ascii(x), p(x)))
    except ValueError: pass
    except Exception as e: bad.append("%s -> %s" % (ascii(x), type(e).__name__))
print("ASCII DIGITS:", "pass" if not bad else "FAIL " + "; ".join(bad))
