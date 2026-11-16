"""
Lab 6 - Branch coverage tests for visa_application.py
SRN : PES2UG24CS183
Name: HARSH MANNAN

Goal: make every decision (if / elif) in visa_application.py evaluate to
both True and False at least once, including boundary values.
Run:
    coverage run --branch -m pytest BranchCoverageTest_visa_application.py
    coverage report -m
"""
import pytest
from visa_application import visa_fee, documents_complete, application_status


# =============================================================== visa_fee
# Decision 1: visa_type not in INCLUDED_ENTRIES  (True / False)
def test_unknown_visa_type_raises():
    with pytest.raises(ValueError, match="unknown visa type"):
        visa_fee("diplomatic", 1, "normal", "B")


def test_visa_type_is_case_sensitive():
    with pytest.raises(ValueError, match="unknown visa type"):
        visa_fee("Tourist", 1, "normal", "B")


# Decision 2: entries < 0  (True / False, boundary at 0)
def test_negative_entries_raises():
    with pytest.raises(ValueError, match="invalid entries"):
        visa_fee("tourist", -1, "normal", "B")


def test_zero_entries_is_valid_and_free():
    assert visa_fee("tourist", 0, "normal", "B") == 0


# Decision 3: nationality_group == "A" and visa_type != "student"
#   True                -> group A, non-student  (extra entry included)
#   False (left side)   -> group B
#   False (right side)  -> group A but student (no extra entry)
def test_group_a_non_student_gets_extra_included_entry():
    # tourist 1 + 1 (group A) = 2 included -> 2 entries are free
    assert visa_fee("tourist", 2, "normal", "A") == 0


def test_group_b_no_extra_included_entry():
    # tourist 1 included -> 2 entries -> 1 extra at 40
    assert visa_fee("tourist", 2, "normal", "B") == 40


def test_group_a_student_gets_no_bonus():
    # student 2 included, no bonus -> 3 entries -> 1 extra at 40
    assert visa_fee("student", 3, "normal", "A") == 40


# Decision 4: extra <= 0  (True / False, boundary at extra == 0 and 1)
def test_extra_exactly_zero_is_free():
    assert visa_fee("business", 3, "express", "B") == 0


def test_extra_exactly_one_is_charged():
    assert visa_fee("business", 4, "express", "B") == 100


# Decision 5: speed == "express"  (True / False)
# Decision 6: extra > 5           (True / False, boundary at 5 and 6)
# Decision 7: nested speed == "express" inside extra > 5  (True / False)
@pytest.mark.parametrize(
    "visa_type, entries, speed, group, expected",
    [
        # extra <= 5, normal  -> rate 40
        ("tourist", 6, "normal", "B", 5 * 40),          # extra = 5 (boundary)
        # extra <= 5, express -> rate 100
        ("tourist", 6, "express", "B", 5 * 100),        # extra = 5 (boundary)
        # extra > 5, normal   -> rate 40 + 20 = 60   (nested if False)
        ("tourist", 7, "normal", "B", 6 * 60),          # extra = 6 (boundary)
        # extra > 5, express  -> rate 100 + 20 + 10 = 130 (nested if True)
        ("tourist", 7, "express", "B", 6 * 130),        # extra = 6 (boundary)
        # any non-"express" speed is treated as normal
        ("business", 5, "priority", "B", 2 * 40),
        # combined: group A business, many entries, express
        ("business", 10, "express", "A", 6 * 130),
    ],
)
def test_fee_rate_branches(visa_type, entries, speed, group, expected):
    assert visa_fee(visa_type, entries, speed, group) == expected


# ===================================================== documents_complete
# Decision 1: is_renewal (True / False)
# Decision 2 (inside renewal): forms_filed >= 1 (True / False)
def test_renewal_with_one_form_is_complete():
    assert documents_complete(1, 0, True) is True


def test_renewal_with_no_forms_is_incomplete():
    assert documents_complete(0, 5, True) is False


# Decision 3: photos < 2 (True / False, boundary at 1 and 2)
def test_new_application_one_photo_is_incomplete():
    assert documents_complete(3, 1, False) is False


def test_new_application_zero_photos_is_incomplete():
    assert documents_complete(5, 0, False) is False


# Decision 4: forms_filed >= 3 (True / False, boundary at 2 and 3)
def test_documents_complete():
    assert documents_complete(3, 2, False) is True


def test_new_application_two_forms_is_incomplete():
    assert documents_complete(2, 2, False) is False


# ===================================================== application_status
# Decision 1: is_express      (True / False)  -> cutoff 10 / 30
# Decision 2: is_peak_season  (True / False)  -> +15
# Decision 3: days_left >= cutoff             -> "open"
# Decision 4: days_left >= cutoff - 15        -> "closing" / "closed"
@pytest.mark.parametrize(
    "days_left, is_express, is_peak, expected",
    [
        # normal, off-peak: cutoff 30
        (30, False, False, "open"),       # exactly at cutoff
        (29, False, False, "closing"),    # just below cutoff
        (15, False, False, "closing"),    # exactly cutoff - 15
        (14, False, False, "closed"),     # just below cutoff - 15
        # normal, peak: cutoff 45
        (45, False, True, "open"),
        (44, False, True, "closing"),
        (30, False, True, "closing"),
        (29, False, True, "closed"),
        # express, off-peak: cutoff 10
        (10, True, False, "open"),
        (9, True, False, "closing"),
        (-5, True, False, "closing"),     # exactly cutoff - 15 = -5
        (-6, True, False, "closed"),      # just below cutoff - 15
        # express, peak: cutoff 25
        (25, True, True, "open"),
        (24, True, True, "closing"),
        (10, True, True, "closing"),
        (9, True, True, "closed"),
    ],
)
def test_application_status_branches(days_left, is_express, is_peak, expected):
    assert application_status(days_left, is_express, is_peak) == expected
