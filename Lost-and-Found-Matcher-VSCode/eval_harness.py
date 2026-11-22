"""Small rule tests for score_pair. Run: python eval_harness.py"""
from lost_and_found_matcher import score_pair

def report(item, colour=None, brand=None, place=None, date="2026-11-10"):
    return {
        "id": "TEST", "date": date, "item": item,
        "colour": colour, "brand": brand, "place": place
    }

tests = [
    (
        "Same bottle colour, brand and place",
        report("bottle", "black", "Milton", "library"),
        report("bottle", "black", "Milton", "library", "2026-11-11"),
        "Likely"
    ),
    (
        "Same item, colour only",
        report("bottle", "black"),
        report("bottle", "black"),
        "Possible"
    ),
    (
        "Different colours must be rejected",
        report("wallet", "brown"),
        report("wallet", "black"),
        None
    ),
    (
        "More than 30 days must be rejected",
        report("bag", "blue", date="2026-09-01"),
        report("bag", "blue", date="2026-11-10"),
        None
    ),
    (
        "Other is not automatically matched",
        report("other", "green"),
        report("other", "green"),
        None
    ),
]

passed = 0
for number, (name, lost, found, expected) in enumerate(tests, start=1):
    result = score_pair(lost, found)
    got = result["classification"] if result else None
    ok = got == expected
    passed += int(ok)
    print(f"{number}. {name}: expected={expected}, got={got} -> {'PASS' if ok else 'FAIL'}")

print(f"\n{passed}/{len(tests)} tests passed.")
