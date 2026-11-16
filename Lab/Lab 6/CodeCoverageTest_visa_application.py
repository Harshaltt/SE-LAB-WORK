"""
Lab 6 - Code (line) coverage tests for visa_application.py
SRN : PES2UG24CS183
Name: HARSH MANNAN

Goal: execute every line of visa_application.py at least once.
Run:
    coverage run -m pytest CodeCoverageTest_visa_application.py
    coverage report -m
"""
import pytest
from visa_application import visa_fee, documents_complete, application_status


# ---------------------------------------------------------------- visa_fee
def test_within_included_entries():
    # tourist includes 1 entry -> no extra -> fee 0  (covers the early return)
    assert visa_fee("tourist", 1, "normal", "B") == 0


def test_unknown_visa_type_raises():
    # covers: raise ValueError("unknown visa type")
    with pytest.raises(ValueError, match="unknown visa type"):
        visa_fee("diplomatic", 1, "normal", "B")


def test_negative_entries_raises():
    # covers: raise ValueError("invalid entries")
    with pytest.raises(ValueError, match="invalid entries"):
        visa_fee("tourist", -1, "normal", "B")


def test_normal_speed_small_extra():
    # student includes 2, 3 entries -> 1 extra at normal rate 40
    assert visa_fee("student", 3, "normal", "B") == 40


def test_group_a_express_many_extra_entries():
    # business includes 3, group A adds 1 -> 4 included
    # 10 entries -> 6 extra (> 5) -> express 100 + 20 + 10 = 130 per entry
    assert visa_fee("business", 10, "express", "A") == 6 * 130


# ------------------------------------------------------ documents_complete
def test_documents_complete():
    assert documents_complete(3, 2, False) is True


def test_renewal_needs_one_form():
    # covers the is_renewal branch
    assert documents_complete(1, 0, True) is True


def test_too_few_photos():
    # covers: if photos < 2: return False
    assert documents_complete(3, 1, False) is False


# ------------------------------------------------------ application_status
def test_express_open():
    # express cutoff 10, not peak -> 10 days left is "open"
    assert application_status(10, True, False) == "open"


def test_normal_peak_closing():
    # normal cutoff 30 + 15 (peak) = 45; 40 days -> >= 30 -> "closing"
    assert application_status(40, False, True) == "closing"


def test_normal_closed():
    # normal cutoff 30; 5 days -> below 15 -> "closed"
    assert application_status(5, False, False) == "closed"
