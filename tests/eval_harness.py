"""Five-pair evaluation harness. No API key or third-party package required."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import score_pair

def report(rid, date, item, colour=None, brand=None, place=None, text="sample report"):
    return {"id": rid, "date": date, "item": item, "colour": colour,
            "brand": brand, "place": place, "report": text}

cases = [
    ("same colour + same place => likely",
     report("L1","2026-10-01","phone","black",None,"library"),
     report("F1","2026-10-01","phone","black",None,"library"), "likely"),
    ("same brand only => possible",
     report("L2","2026-10-01","watch",None,"Casio",None),
     report("F2","2026-10-02","watch",None,"Casio",None), "possible"),
    ("colour conflict => none",
     report("L3","2026-10-01","bottle","blue"),
     report("F3","2026-10-01","bottle","red"), "none"),
    ("different item => none",
     report("L4","2026-10-01","phone","black"),
     report("F4","2026-10-01","wallet","black"), "none"),
    (">30 days apart => none",
     report("L5","2026-08-01","umbrella","red",None,"hostel"),
     report("F5","2026-10-01","umbrella","red",None,"hostel"), "none"),
]

def main():
    passed = 0
    print("LOST AND FOUND MATCHER — EVALUATION HARNESS")
    for name, lost, found, expected in cases:
        result = score_pair(lost, found)
        actual = result["level"] if result else "none"
        ok = actual == expected
        passed += int(ok)
        print(f"{'PASS' if ok else 'FAIL'} | {name} | expected={expected} actual={actual}")
    print(f"Result: {passed}/{len(cases)} passed")
    if passed != len(cases):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
