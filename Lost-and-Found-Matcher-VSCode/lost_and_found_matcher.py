"""
Lost and Found Matcher
Reads lost.csv and found.csv, extracts report details with Gemini,
validates facts, scores pairs in Python, and writes four output files.
"""

import csv
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
PROMPT_FILE = BASE_DIR / "system_prompt.txt"

# These are the 10 colour values used in this starter version.
# Confirm the official list with your faculty if one was given in class.
ALLOWED_ITEMS = {
    "phone", "wallet", "id_card", "bottle", "bag", "earphones",
    "keys", "umbrella", "calculator", "watch", "spectacles", "other"
}
ALLOWED_COLOURS = {
    "black", "blue", "red", "green", "white",
    "brown", "silver", "gold", "grey", "yellow"
}
# Based on the campus places appearing in the supplied sample reports.
# Add any other officially permitted campus places if needed.
ALLOWED_PLACES = {
    "library", "canteen", "computer lab",
    "science lab", "auditorium", "sports ground"
}
MODEL_NAME = "gemini-3.8-flash"


def read_report(filename):
    """Read id, date and description from a CSV file."""
    file_path = BASE_DIR / filename
    reports = []

    with file_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        required_columns = {"id", "date", "description"}

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError(
                f"{filename} must contain columns: id,date,description"
            )

        for row in reader:
            report = {
                "id": row["id"].strip(),
                "date": row["date"].strip(),
                "description": row["description"].strip()
            }
            datetime.strptime(report["date"], "%Y-%m-%d")
            reports.append(report)

    return reports


def load_prompt():
    """Read the LLM instructions from system_prompt.txt."""
    return PROMPT_FILE.read_text(encoding="utf-8")


def extract_json(client, system_prompt, report):
    """Ask the LLM to analyse one report and return JSON."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=(
            system_prompt
            + "\n\nAnalyse this report. Return only the required JSON object.\n"
            + "Report: "
            + report["description"]
        )
    )

    raw_text = (response.text or "").strip()
    # Remove a code fence if the model unexpectedly adds one.
    raw_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text)
    return json.loads(raw_text)


def is_valid(data):
    """Check required fields and allowed values in the JSON response."""
    required = {"item", "colour", "brand", "place", "summary"}

    if not isinstance(data, dict) or not required.issubset(data):
        return False

    if data["item"] not in ALLOWED_ITEMS:
        return False
    if data["colour"] is not None and data["colour"] not in ALLOWED_COLOURS:
        return False
    if data["place"] is not None and data["place"] not in ALLOWED_PLACES:
        return False
    if data["brand"] is not None and not isinstance(data["brand"], str):
        return False
    if not isinstance(data["summary"], str):
        return False
    if len(data["summary"].split()) > 8:
        return False

    return True


def check_facts(data, original_report):
    """Keep colour, brand and place only if supported by original text."""
    text = original_report.lower()
    checked = data.copy()

    for field in ("colour", "brand", "place"):
        value = checked[field]
        if value is not None and value.lower() not in text:
            checked[field] = None

    return checked


def safe_fallback(report):
    """Use a cautious fallback if the LLM call or JSON validation fails."""
    words = report["description"].split()
    return {
        "item": "other",
        "colour": None,
        "brand": None,
        "place": None,
        "summary": " ".join(words[:8])
    }


def analyse_reports(client, prompt, reports, label):
    """Extract, validate and fact-check every report once."""
    analysed = []

    for report in reports:
        try:
            details = extract_json(client, prompt, report)
            if not is_valid(details):
                raise ValueError("LLM JSON failed validation")
            details = check_facts(details, report["description"])
            status = "AI"
        except Exception as error:
            print(f"Warning: {report['id']} used safe fallback: {error}")
            details = safe_fallback(report)
            status = "Fallback"

        analysed.append({**report, **details, "extraction_status": status})
        print(f"{label} {report['id']}: {details['item']} ({status})")

    return analysed


def score_pair(lost, found):
    """Return a suggested match, or None when a hard rule rejects it."""
    if lost["item"] == "other" or found["item"] == "other":
        return None

    if lost["item"] != found["item"]:
        return None

    lost_date = datetime.strptime(lost["date"], "%Y-%m-%d")
    found_date = datetime.strptime(found["date"], "%Y-%m-%d")

    if abs((lost_date - found_date).days) > 30:
        return None

    # A mismatch is a hard rejection only when both values are known.
    for field in ("colour", "brand"):
        if lost[field] and found[field] and lost[field].lower() != found[field].lower():
            return None

    score = 0
    reasons = ["Same item type"]

    if lost["colour"] and found["colour"] and lost["colour"] == found["colour"]:
        score += 2
        reasons.append(f"Same colour (+2): {lost['colour']}")

    if lost["brand"] and found["brand"] and lost["brand"].lower() == found["brand"].lower():
        score += 2
        reasons.append(f"Same brand (+2): {lost['brand']}")

    if lost["place"] and found["place"] and lost["place"] == found["place"]:
        score += 1
        reasons.append(f"Same place (+1): {lost['place']}")

    if score == 0:
        return None

    classification = "Likely" if score >= 3 else "Possible"

    return {
        "lost_id": lost["id"],
        "found_id": found["id"],
        "lost_date": lost["date"],
        "found_date": found["date"],
        "item_type": lost["item"],
        "lost_colour": lost["colour"] or "",
        "found_colour": found["colour"] or "",
        "lost_brand": lost["brand"] or "",
        "found_brand": found["brand"] or "",
        "lost_place": lost["place"] or "",
        "found_place": found["place"] or "",
        "score": score,
        "classification": classification,
        "reasons": "; ".join(reasons),
        "multiple_claim_alert": ""
    }


def find_matches(lost_reports, found_reports):
    """Compare every lost report with every found report."""
    suggestions = []

    for lost in lost_reports:
        for found in found_reports:
            result = score_pair(lost, found)
            if result is not None:
                suggestions.append(result)

    suggestions.sort(key=lambda row: row["score"], reverse=True)

    claims_per_found = Counter(row["found_id"] for row in suggestions)
    for row in suggestions:
        if claims_per_found[row["found_id"]] > 1:
            row["multiple_claim_alert"] = "YES"
        else:
            row["multiple_claim_alert"] = "NO"

    return suggestions


def write_csv(filename, rows, fieldnames):
    """Write rows into a CSV file inside outputs folder."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / filename

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_reports(lost_reports, found_reports, matches):
    """Create matches.csv, no_match.csv, unclaimed.csv and summary.txt."""
    match_fields = [
        "lost_id", "found_id", "lost_date", "found_date", "item_type",
        "lost_colour", "found_colour", "lost_brand", "found_brand",
        "lost_place", "found_place", "score", "classification",
        "reasons", "multiple_claim_alert"
    ]
    write_csv("matches.csv", matches, match_fields)

    matched_lost = {row["lost_id"] for row in matches}
    matched_found = {row["found_id"] for row in matches}

    no_match = [
        {"id": row["id"], "date": row["date"], "description": row["description"]}
        for row in lost_reports if row["id"] not in matched_lost
    ]
    unclaimed = [
        {"id": row["id"], "date": row["date"], "description": row["description"]}
        for row in found_reports if row["id"] not in matched_found
    ]

    basic_fields = ["id", "date", "description"]
    write_csv("no_match.csv", no_match, basic_fields)
    write_csv("unclaimed.csv", unclaimed, basic_fields)

    multiple = defaultdict(list)
    for row in matches:
        multiple[row["found_id"]].append(row["lost_id"])

    likely_count = sum(row["classification"] == "Likely" for row in matches)
    possible_count = sum(row["classification"] == "Possible" for row in matches)

    lines = [
        "LOST AND FOUND MATCHER - SUMMARY",
        "================================",
        "",
        f"Total lost reports: {len(lost_reports)}",
        f"Total found reports: {len(found_reports)}",
        f"Suggested pairs: {len(matches)}",
        f"Likely matches: {likely_count}",
        f"Possible matches: {possible_count}",
        f"Lost reports with no suggestion: {len(no_match)}",
        f"Unclaimed found items: {len(unclaimed)}",
        "",
        "MULTIPLE-CLAIM ALERTS",
        "---------------------"
    ]

    alerts = {item: ids for item, ids in multiple.items() if len(ids) > 1}
    if alerts:
        for found_id, lost_ids in alerts.items():
            lines.append(f"{found_id} is suggested for: {', '.join(lost_ids)}")
    else:
        lines.append("No multiple-claim alerts.")

    lines += [
        "",
        "OWNERSHIP VERIFICATION",
        "----------------------",
        "A suggested match is not proof of ownership.",
        "The help desk must ask the claimant for an additional detail",
        "that does not appear in either report before returning an item.",
        "",
        "Note: The help desk makes the final ownership decision."
    ]

    (OUTPUT_DIR / "summary.txt").write_text("\n".join(lines), encoding="utf-8")

    print("\nFour output files were created in the outputs folder.")


def main():
    load_dotenv(BASE_DIR / ".env")

    lost_reports = read_report("lost.csv")
    found_reports = read_report("found.csv")

    print(f"Loaded {len(lost_reports)} lost reports.")
    print(f"Loaded {len(found_reports)} found reports.")

    if len(lost_reports) < 10 or len(found_reports) < 10:
        print("Reminder: the project specification requires at least 10 reports in each input CSV.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add your key to the local .env file."
        )

    client = genai.Client(api_key=api_key)
    try:
        prompt = load_prompt()
        lost_analysed = analyse_reports(client, prompt, lost_reports, "LOST")
        found_analysed = analyse_reports(client, prompt, found_reports, "FOUND")
        matches = find_matches(lost_analysed, found_analysed)
        write_reports(lost_analysed, found_analysed, matches)
    finally:
        client.close()


if __name__ == "__main__":
    main()
