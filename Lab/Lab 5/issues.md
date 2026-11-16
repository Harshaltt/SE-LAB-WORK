# Lab 5: Static Code Analysis — Issue Table

**Name:** Harsh Mannan
**SRN:** PES2UG24CS183
**Repository:** L5_52_course_enrollment_system
**File analysed:** `course_enrollment_system.py`

Line numbers refer to the **original** file (before any fixes).

## Summary of results

| Tool   | Before                                        | After               |
|--------|-----------------------------------------------|---------------------|
| Pylint | 4.00/10 (36 messages)                         | **10.00/10**        |
| Bandit | 6 issues (2 High, 1 Medium, 3 Low)            | **No issues identified** |
| Flake8 | 12 issues                                     | **0 issues** (`flake8 --count` reports 0) |

Reports are in `reports/before/` and `reports/after/`.

## Issues found and how they were fixed

High and medium severity issues are listed first.

| # | Issue | Type | Line(s) | Tool / Code | Description | Fix Approach |
|---|-------|------|---------|-------------|-------------|--------------|
| 1 | Shell command injection | Security (High) | 63 | Bandit B605 | `os.system("echo ... " + filename)` passes a caller-controlled filename to the shell. A name like `x; rm -rf ~` would run arbitrary commands. | Removed the shell call; the confirmation is printed with `print()`. |
| 2 | Weak MD5 hash | Security (High) | 52 | Bandit B324 | `hashlib.md5()` is cryptographically broken (collisions are practical) and should not be used to identify students. | Replaced with `hashlib.sha256()`. |
| 3 | Use of `eval()` | Security (Medium) | 47 | Bandit B307, Pylint W0123 | `eval(discount_expr)` executes any string passed in, which allows arbitrary code execution. | Changed the API to take a numeric `discount_percent`, validated to be in 0–100, and computed `base_fee * (1 - discount_percent / 100)`. |
| 4 | Mutable default argument | Bug | 15 | Pylint W0102 | `audit_trail=[]` is created once and shared by every call, so audit entries leak between unrelated calls. | Default changed to `None`; a new list is created inside the function. |
| 5 | Bare `except` with `pass` | Bug / Security (Low) | 31–32 | Bandit B110, Flake8 E722, Pylint W0702 | Every exception (even `KeyboardInterrupt`) was silently swallowed, which hides errors such as an unknown course ID. | Catch only `KeyError` and report the unknown course; the function returns `False`. |
| 6 | Hard-coded secret, printed to console | Security (Low) | 75, 84 | Bandit B105 | The registrar token was stored in source code (visible in git history) and printed in plain text. | Read from the `REGISTRAR_AUTH_TOKEN` environment variable; only print whether a token is present (`True`/`False`). |
| 7 | Insecure random for OTP | Security (Low) | 56 | Bandit B311 | `random.randint()` is a predictable PRNG and is not suitable for one-time passwords. | Used `1000 + secrets.randbelow(9000)` (cryptographically secure, still 4 digits). |
| 8 | `global` statement | Code quality | 12, 16 | Pylint W0603, C0103 | Mutating a module global with `global total_tuition` makes state hard to track and test. | Tuition kept in a module-level `ledger` dict that is updated without `global`. |
| 9 | File not closed safely, no encoding | Bug | 60–62 | Pylint R1732, W1514 | If `write()` raised, the file would never be closed; the encoding depended on the platform. | `with open(filename, "w", encoding="utf-8") as roster_file:`. |
| 10 | Unused import | Style | 4 | Flake8 F401, Pylint W0611 | `math` was imported but never used. | Removed the import. |
| 11 | Unused variables | Code quality | 36, 46, 68 | Flake8 F841, Pylint W0612 | `lab_fee` was never used, `base_fee` was unused because of `eval`, and the loop variable `cid` was unused. | Removed `lab_fee`; `base_fee` is now used in the formula; the loop uses `.values()`. |
| 12 | Comparison to `None` with `==` | Style | 37 | Flake8 E711, Pylint C0121 | `== None` can be overridden by `__eq__`; identity is the correct check. | Changed to `is None`. |
| 13 | Parameter shadows global | Code quality | 66 | Pylint W0621 | The parameter `courses` hid the global `courses` dict. | Renamed the parameter to `course_catalog`. |
| 14 | Non-PEP 8 names | Style | 15, 27, 35, 45, 51, 55, 59, 66 | Pylint C0103 | Functions used camelCase (`enrollStudent`, `dropCourse`, …). | Renamed to snake_case (`enroll_student`, `drop_course`, …). |
| 15 | Missing docstrings | Documentation | 1 and every function | Pylint C0114, C0116 | There was no module docstring and no function docstrings. | Added a module docstring and a docstring for every function. |
| 16 | Lines too long | Style | 7, 8, 9, 15, 23, 79 | Flake8 E501, Pylint C0301 | Lines of up to 135 characters exceeded the 79-character PEP 8 limit. | Wrapped the dict entries, the function signature, the message and the call. |
| 17 | Over-complex if/else | Code quality | 39–42 | Pylint R1703, R1705 | `if x: return True else: return False` is redundant. | `return not courses[course_id]["is_closed"]`. |
| 18 | Old-style `%` formatting | Style | 23 | Pylint C0209 | `%` string formatting is less readable than f-strings. | Converted to an f-string. |
| 19 | No newline at end of file | Style | 87 | Flake8 W292, Pylint C0304 | The file did not end with a newline. | Added the final newline. |
| 20 | `main()` runs on import | Code quality | 87 | Not flagged | Importing the module ran the whole demo and wrote a file. | Wrapped in `if __name__ == "__main__":`. |

## Logic bugs not flagged by any tool

These were found by running the program and reading its output, as the README suggests.

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 21 | Drop creates phantom seats / reopens closed course | Logic bug | 27–30, 77 | `dropCourse("CS202")` ran when nobody was enrolled. CS202 went from 0 seats and closed to 1 seat and open, so the output said **"Open courses: 3"** when the correct answer is 2. | Each course now tracks a `students` list. `drop_course(course_id, student_name)` succeeds only if that student is enrolled. |
| 22 | Tuition never refunded on drop | Logic bug | 27–30 | Dropping a course freed a seat but left the fee in `total_tuition`, so revenue was overstated. | The course fee is subtracted from `ledger["total_tuition"]` on a successful drop. |
| 23 | Seats can go negative | Logic bug | 17–21 | Enrolment only checked `is_closed`. A course with 0 seats that was not marked closed accepted students and went to -1 seats. | Enrolment also requires `seats > 0`. |
| 24 | Duplicate enrolment | Logic bug | 15–24 | The same student could enrol in the same course twice, using two seats and paying twice. | Enrolment is rejected if the student is already in the course's `students` list. |

## Program output: before vs after

**Before**
```
Is CS101 open: True
Scholarship Fee: 450.0
Student Hash: ca0dd2213c84d8f39db03e28aa0a0554
Enrollment OTP: 2082
Course roster exported to: course_roster.txt
Open courses: 3                                         <- wrong (CS202 should still be closed)
Registrar Token active: REGISTRAR_PORTAL_ROOT_SECRET_2026   <- secret leaked
```

**After**
```
Kritika is not enrolled in CS202
Dropped CS202: False
Is CS101 open: True
Scholarship Fee: 450.0
Student Hash: 408e35a829bb7946854e886da530276b25ac52c7af6c6f7815392a907c1c6a5d
Enrollment OTP: 1452
Course roster exported to: course_roster.txt
Open courses: 2
Total tuition collected: 500.0
Registrar Token active: False
```
(The OTP is random, so it differs on every run.)

## Commits

| Commit | Purpose |
|--------|---------|
| Add baseline static analysis reports (before fixes) | Saved the `before` reports |
| **Fix security issues reported by Bandit** | Issues 1, 2, 3, 5, 6, 7 |
| **Fix PEP 8 style issues reported by Flake8** | Issues 10, 11, 12, 16, 19 |
| **Fix code quality issues reported by Pylint** | Issues 4, 8, 9, 13, 14, 15, 17, 18, 20 |
| Fix logic bugs not detected by the static analysis tools | Issues 21–24 |
| Add issue table, reflection and after reports | Documentation |
