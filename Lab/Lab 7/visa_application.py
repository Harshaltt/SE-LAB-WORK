"""Visa application helpers (hardened after fuzz testing).

Every function validates its input and returns None for anything it cannot
process safely, instead of raising an exception or returning a nonsensical
value (empty visa type, negative counts, NaN, infinity, ...).
"""
import math
import re

GST_RATE = 1.18
MAX_INPUT_LENGTH = 1000            # reject absurdly long inputs (DoS protection)
MAX_ENTRIES = 99                   # allowed number of entries on a visa: 1..99
MAX_PROCESSING_DAYS = 365          # allowed processing time per record: 0..365
MAX_DAY_VALUES = 100               # maximum number of CSV values
MAX_AMOUNT = 10_000_000            # maximum fee / discount amount

# ASCII-only patterns: int()/float() would otherwise accept things such as
# '٣' (Arabic-Indic digit), '1_000', '+5', 'nan', 'inf' or '1e309'.
_VISA_TYPE_RE = re.compile(r"[A-Za-z]+(?:[ \-][A-Za-z]+)*")
_INT_RE = re.compile(r"[0-9]{1,6}")
_AMOUNT_RE = re.compile(r"[0-9]{1,9}(?:\.[0-9]{1,2})?")


def _is_valid_text(value):
    return isinstance(value, str) and len(value) <= MAX_INPUT_LENGTH


def parse_application(text):
    if not _is_valid_text(text):
        return None

    parts = text.split(':')
    if len(parts) != 2:                            # '', 'tourist', 'a:b:c'
        return None

    visa, entries = parts[0].strip(), parts[1].strip()
    if not _VISA_TYPE_RE.fullmatch(visa):          # empty / symbols / unicode
        return None
    if not _INT_RE.fullmatch(entries):             # empty, '-5', '1_0', 'abc'
        return None

    entries = int(entries)
    if not 1 <= entries <= MAX_ENTRIES:            # 0 entries is meaningless
        return None

    return visa.title(), entries


def processing_average(days_csv):
    if not _is_valid_text(days_csv):
        return None

    items = [item.strip() for item in days_csv.split(',')]
    if len(items) > MAX_DAY_VALUES:
        return None

    values = []
    for item in items:
        if not _INT_RE.fullmatch(item):            # '', '1,,2', '-5', 'ten'
            return None
        day = int(item)
        if day > MAX_PROCESSING_DAYS:
            return None
        values.append(day)

    if not values:                                 # avoid ZeroDivisionError
        return None

    return sum(values) // len(values)


def payable_fee(text):
    if not _is_valid_text(text):
        return None

    parts = text.split('|')
    if len(parts) != 2:                            # '', '6000', '1|2|3'
        return None

    fee_text, discount_text = parts[0].strip(), parts[1].strip()
    if not (_AMOUNT_RE.fullmatch(fee_text) and _AMOUNT_RE.fullmatch(discount_text)):
        return None                                # 'nan', 'inf', '-100', '1e309'

    fee, discount = float(fee_text), float(discount_text)
    if fee > MAX_AMOUNT or discount > MAX_AMOUNT:
        return None

    total = fee * GST_RATE - discount
    if not math.isfinite(total):
        return None

    return round(max(total, 0.0), 2)               # always a float, never negative


def _read(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def main():
    print("==== Running parse_application ====")
    user_input = _read("Enter visa type:entries (e.g. tourist:2): ")
    result = parse_application(user_input)
    if result is None:
        print("Invalid input: expected <visa type>:<entries 1-99>, e.g. tourist:2")
    else:
        print("Visa Type and Entries:", result)

    print("\n==== Running processing_average ====")
    user_input = _read("Enter processing days as CSV (e.g. 5,10,21): ")
    result = processing_average(user_input)
    if result is None:
        print("Invalid input: expected comma separated whole days (0-365), e.g. 5,10,21")
    else:
        print("Average Processing Days:", result)

    print("\n==== Running payable_fee ====")
    user_input = _read("Enter fee|discount (e.g. 6000|500): ")
    result = payable_fee(user_input)
    if result is None:
        print("Invalid input: expected <fee>|<discount> as non-negative amounts, e.g. 6000|500")
    else:
        print("Payable Fee:", result)


if __name__ == "__main__":
    main()
