import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from review_signal import detect_language, score  # noqa: E402

EN_REPLY = "Thank you for your feedback. We are sorry and our team will contact you shortly."
DE_REVIEW = "Meine Bestellung kam zwei Wochen zu spät und niemand hat geantwortet."
DE_REPLY = "Vielen Dank für Ihr Feedback. Unser Team wird sich in Kürze bei Ihnen melden."


def row(i, review, reply, domain="acme.example"):
    return {"company": "Acme", "domain": domain, "review_id": f"R{i}",
            "review_text": review, "reply_text": reply}


def test_short_text_is_not_classified():
    assert detect_language("ok thanks") is None


def test_detects_common_languages():
    assert detect_language(DE_REVIEW) == "de"
    assert detect_language(EN_REPLY) == "en"


def test_mismatch_makes_company_qualified():
    rows = [row(i, DE_REVIEW, EN_REPLY) for i in range(5)]
    (stats,) = score(rows)
    assert stats.mismatches == 5
    assert stats.tier == "qualified"
    assert stats.unserved_langs["de"] == 5


def test_matching_replies_are_deprioritized():
    rows = [row(i, DE_REVIEW, DE_REPLY) for i in range(6)]
    (stats,) = score(rows)
    assert stats.mismatch_rate == 0
    assert stats.tier == "deprioritize"


def test_too_few_replies_is_insufficient_data():
    rows = [row(i, DE_REVIEW, EN_REPLY) for i in range(3)] + [row(9, DE_REVIEW, "")]
    (stats,) = score(rows)
    assert stats.replies == 3
    assert stats.tier == "insufficient-data"


def test_ranking_puts_qualified_first():
    good = [row(i, DE_REVIEW, DE_REPLY, "good.example") for i in range(6)]
    gap = [row(i, DE_REVIEW, EN_REPLY, "gap.example") for i in range(6)]
    results = score(good + gap)
    assert results[0].domain == "gap.example"
