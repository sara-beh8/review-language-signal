"""
review-language-signal: turn public review replies into a prospecting signal.

A company that answers customer reviews in a different language than the
customer wrote in is showing a visible multilingual-support gap. This script
finds those companies in a set of reviews and ranks them as prospects, with
example reviews to open the conversation.

Usage:
    python review_signal.py data/sample_reviews.csv --out prospects.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from langdetect import DetectorFactory, LangDetectException, detect

DetectorFactory.seed = 0  # make language detection deterministic

MIN_CHARS = 20            # shorter texts are too unreliable to classify
MIN_REPLIES = 5           # below this, a company has too little evidence
QUALIFIED_RATE = 0.30     # mismatch rate that makes a company a qualified prospect
WATCH_RATE = 0.10         # mismatch rate that puts a company on the watch list


@dataclass
class CompanyStats:
    company: str
    domain: str
    reviews: int = 0
    replies: int = 0
    classified: int = 0
    mismatches: int = 0
    customer_langs: Counter = field(default_factory=Counter)
    reply_langs: Counter = field(default_factory=Counter)
    unserved_langs: Counter = field(default_factory=Counter)
    examples: list = field(default_factory=list)

    @property
    def mismatch_rate(self) -> float:
        return self.mismatches / self.classified if self.classified else 0.0

    @property
    def tier(self) -> str:
        if self.classified < MIN_REPLIES:
            return "insufficient-data"
        if self.mismatch_rate >= QUALIFIED_RATE:
            return "qualified"
        if self.mismatch_rate >= WATCH_RATE:
            return "watch"
        return "deprioritize"


def detect_language(text: str) -> str | None:
    """Return an ISO 639-1 code, or None if the text is too short or unclear."""
    text = (text or "").strip()
    if len(text) < MIN_CHARS:
        return None
    try:
        return detect(text)
    except LangDetectException:
        return None


def load_reviews(path: str) -> list[dict]:
    required = {"company", "domain", "review_id", "review_text", "reply_text"}
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if rows and not required.issubset(rows[0].keys()):
        missing = required - set(rows[0].keys())
        sys.exit(f"Input is missing columns: {', '.join(sorted(missing))}")
    return rows


def score(rows: list[dict]) -> list[CompanyStats]:
    companies: dict[str, CompanyStats] = {}
    for row in rows:
        key = row["domain"].lower()
        stats = companies.setdefault(key, CompanyStats(row["company"], row["domain"]))
        stats.reviews += 1

        reply = (row.get("reply_text") or "").strip()
        if not reply:
            continue
        stats.replies += 1

        customer_lang = detect_language(row["review_text"])
        reply_lang = detect_language(reply)
        if customer_lang is None or reply_lang is None:
            continue

        stats.classified += 1
        stats.customer_langs[customer_lang] += 1
        stats.reply_langs[reply_lang] += 1
        if customer_lang != reply_lang:
            stats.mismatches += 1
            stats.unserved_langs[customer_lang] += 1
            if len(stats.examples) < 2:
                stats.examples.append(
                    f"{row['review_id']}: customer wrote in {customer_lang}, "
                    f"company replied in {reply_lang}"
                )

    order = {"qualified": 0, "watch": 1, "deprioritize": 2, "insufficient-data": 3}
    return sorted(
        companies.values(),
        key=lambda s: (order[s.tier], -s.mismatch_rate, -s.classified),
    )


def fmt_langs(counter: Counter) -> str:
    return " ".join(f"{lang}:{n}" for lang, n in counter.most_common())


def write_prospects(results: list[CompanyStats], path: str) -> None:
    fields = [
        "tier", "company", "domain", "reviews", "replies", "classified_replies",
        "mismatches", "mismatch_rate", "customer_languages", "reply_languages",
        "unserved_languages", "evidence",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for s in results:
            writer.writerow([
                s.tier, s.company, s.domain, s.reviews, s.replies, s.classified,
                s.mismatches, f"{s.mismatch_rate:.0%}", fmt_langs(s.customer_langs),
                fmt_langs(s.reply_langs), fmt_langs(s.unserved_langs),
                " | ".join(s.examples),
            ])


def print_summary(results: list[CompanyStats]) -> None:
    print(f"{'tier':<18}{'company':<24}{'mismatch':>9}  unserved languages")
    for s in results:
        print(f"{s.tier:<18}{s.company:<24}{s.mismatch_rate:>8.0%}  {fmt_langs(s.unserved_langs) or '-'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    parser.add_argument("reviews_csv", help="CSV of reviews and company replies")
    parser.add_argument("--out", default="prospects.csv", help="where to write the ranked prospect list")
    args = parser.parse_args()

    results = score(load_reviews(args.reviews_csv))
    write_prospects(results, args.out)
    print_summary(results)
    print(f"\nWrote {len(results)} companies to {args.out}")


if __name__ == "__main__":
    main()
