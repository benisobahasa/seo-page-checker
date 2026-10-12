import pytest

from app.analyzer import RULES, analyze_html, grade_for
from tests.factories import build_page


def finding(result, rule_id):
    return next(f for f in result.findings if f.rule_id == rule_id)


def test_good_page_scores_100():
    result = analyze_html(build_page())
    assert result.score == 100
    assert result.grade == "A"
    assert result.failed == 0


def test_rule_weights_sum_to_100_and_ids_are_unique():
    assert sum(r.weight for r in RULES) == 100
    assert len({r.id for r in RULES}) == len(RULES)


def test_missing_title_fails_both_title_rules():
    result = analyze_html(build_page(title=None))
    assert not finding(result, "title_present").passed
    assert not finding(result, "title_length").passed
    assert result.stats.title is None


@pytest.mark.parametrize(
    ("length", "expected"),
    [(29, False), (30, True), (60, True), (61, False)],
)
def test_title_length_boundaries(length, expected):
    result = analyze_html(build_page(title="a" * length))
    assert finding(result, "title_length").passed is expected


@pytest.mark.parametrize(
    ("length", "expected"),
    [(69, False), (70, True), (160, True), (161, False)],
)
def test_description_length_boundaries(length, expected):
    result = analyze_html(build_page(description="a" * length))
    assert finding(result, "meta_description_length").passed is expected


def test_missing_description_fails_both_description_rules():
    result = analyze_html(build_page(description=None))
    assert not finding(result, "meta_description_present").passed
    assert not finding(result, "meta_description_length").passed


@pytest.mark.parametrize("count", [0, 2, 3])
def test_h1_must_appear_exactly_once(count):
    result = analyze_html(build_page(h1_count=count))
    assert not finding(result, "single_h1").passed
    assert result.stats.h1_count == count


def test_skipped_heading_level_is_detected():
    result = analyze_html(build_page(extra_body="<h4>Too deep</h4>"))
    check = finding(result, "heading_order")
    assert not check.passed
    assert "h2 to h4" in check.message


def test_images_missing_alt_are_counted_but_empty_alt_is_allowed():
    extra = '<img src="a.png"><img src="b.png" alt=""><img src="c.png">'
    result = analyze_html(build_page(extra_body=extra))
    assert result.stats.image_count == 4  # 1 from the template + 3 extra
    assert result.stats.images_missing_alt == 2
    assert not finding(result, "images_alt").passed


def test_noindex_is_detected_even_with_other_directives():
    result = analyze_html(build_page(robots="NOINDEX, nofollow"))
    assert not finding(result, "indexable").passed


def test_missing_lang_viewport_and_canonical_are_reported():
    result = analyze_html(build_page(lang=None, viewport=False, canonical=False))
    assert not finding(result, "lang_attribute").passed
    assert not finding(result, "viewport_meta").passed
    assert not finding(result, "canonical_present").passed


def test_word_count_ignores_script_style_and_head():
    plain = analyze_html(build_page(body_words=10))
    noisy_extra = "<script>" + "x " * 100 + "</script><style>" + "y " * 100 + "</style>"
    noisy = analyze_html(build_page(body_words=10, extra_body=noisy_extra))
    assert noisy.stats.word_count == plain.stats.word_count


def test_thin_content_fails_word_count_rule():
    result = analyze_html(build_page(body_words=20))
    assert not finding(result, "word_count").passed


def test_title_whitespace_is_normalized():
    result = analyze_html(build_page(title="  Hello \n   World  "))
    assert result.stats.title == "Hello World"


@pytest.mark.parametrize(
    "garbage",
    ["<<<>>>", "<div", "<!-- unclosed", "<title>unclosed", "\x00\x01\x02", "plain text only"],
)
def test_malformed_input_never_crashes(garbage):
    result = analyze_html(garbage)
    assert 0 <= result.score <= 100


@pytest.mark.parametrize(
    ("score", "grade"),
    [
        (100, "A"),
        (90, "A"),
        (89, "B"),
        (75, "B"),
        (74, "C"),
        (60, "C"),
        (59, "D"),
        (40, "D"),
        (39, "F"),
        (0, "F"),
    ],
)
def test_grade_boundaries(score, grade):
    assert grade_for(score) == grade
