import math

from hypothesis import given, settings, strategies as st
from visa_application import parse_application, processing_average, payable_fee

# Run more examples than the default and disable the per-example deadline
# so that slow machines do not cause flaky failures.
settings.register_profile("lab7", max_examples=300, deadline=None)
settings.load_profile("lab7")


# ---------------------------------------------------------------------------
# Part 1: Robustness - random text (or None) must never crash a function
# ---------------------------------------------------------------------------

@given(st.text() | st.none())
def test_parse_application_no_crash(s):
    try:
        parse_application(s)
    except Exception as e:
        assert False, f"parse_application crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_processing_average_no_crash(s):
    try:
        processing_average(s)
    except Exception as e:
        assert False, f"processing_average crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_payable_fee_no_crash(s):
    try:
        payable_fee(s)
    except Exception as e:
        assert False, f"payable_fee crashed with: {e!r} for input {s!r}"


# ---------------------------------------------------------------------------
# Part 2: Structured fuzzing - inputs that look almost valid, to reach the
# deeper logic. Results must be either None (rejected) or a sane value.
# ---------------------------------------------------------------------------

# "visa:entries" built from arbitrary text, integers and separators
application_like = st.builds(
    lambda visa, entries: f"{visa}:{entries}",
    st.text(max_size=15),
    st.one_of(st.integers(), st.text(max_size=5)),
) | st.lists(st.text(max_size=8), min_size=1, max_size=4).map(":".join)


@given(application_like)
def test_parse_application_returns_valid_result(s):
    result = parse_application(s)
    if result is not None:
        visa, entries = result
        assert isinstance(visa, str) and visa != "", f"empty visa type for {s!r}"
        assert isinstance(entries, int) and entries >= 1, (
            f"invalid number of entries {entries!r} for {s!r}"
        )


# comma separated values: integers (incl. negative), empty items and junk
days_like = st.lists(
    st.one_of(st.integers(), st.just(""), st.text(max_size=4)),
    max_size=10,
).map(lambda items: ",".join(str(i) for i in items))


@given(days_like)
def test_processing_average_returns_valid_result(s):
    result = processing_average(s)
    if result is not None:
        assert isinstance(result, int), f"non-integer average {result!r} for {s!r}"
        assert result >= 0, f"negative processing days {result!r} for {s!r}"


# "fee|discount" built from floats (incl. nan / inf / negatives) and text
amount = st.one_of(
    st.floats(allow_nan=True, allow_infinity=True),
    st.integers(),
    st.sampled_from(["nan", "inf", "-inf", "1e309", "1_000", " "]),
    st.text(max_size=5),
)
fee_like = st.builds(lambda fee, disc: f"{fee}|{disc}", amount, amount) | st.lists(
    st.text(max_size=6), min_size=1, max_size=4
).map("|".join)


@given(fee_like)
def test_payable_fee_returns_valid_result(s):
    result = payable_fee(s)
    if result is not None:
        assert isinstance(result, float), f"non-float fee {result!r} for {s!r}"
        assert math.isfinite(result), f"non-finite fee {result!r} for {s!r}"
        assert result >= 0, f"negative fee {result!r} for {s!r}"


# ---------------------------------------------------------------------------
# Part 3: Correctness - valid inputs must still give the expected answer
# (makes sure the input validation does not break normal behaviour)
# ---------------------------------------------------------------------------

VISA_TYPES = ["tourist", "student", "business", "work", "transit", "e-visa", "work permit"]


@given(
    st.sampled_from(VISA_TYPES),
    st.integers(min_value=1, max_value=99),
    st.sampled_from(["", " ", "  "]),
)
def test_parse_application_valid_input(visa, entries, pad):
    text = f"{pad}{visa}{pad}:{pad}{entries}{pad}"
    assert parse_application(text) == (visa.title(), entries)


@given(st.lists(st.integers(min_value=0, max_value=365), min_size=1, max_size=50))
def test_processing_average_valid_input(days):
    csv = ",".join(str(d) for d in days)
    assert processing_average(csv) == sum(days) // len(days)


@given(
    st.integers(min_value=0, max_value=100_000_000),
    st.integers(min_value=0, max_value=100_000_000),
)
def test_payable_fee_valid_input(fee_paise, discount_paise):
    fee, discount = fee_paise / 100, discount_paise / 100
    text = f"{fee_paise // 100}.{fee_paise % 100:02d}|{discount_paise // 100}.{discount_paise % 100:02d}"
    expected = max(fee * 1.18 - discount, 0)
    assert math.isclose(payable_fee(text), expected, abs_tol=0.01)
