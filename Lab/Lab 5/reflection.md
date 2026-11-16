# Lab 5: Static Code Analysis — Reflection

**Name:** Harsh Mannan
**SRN:** PES2UG24CS183
**Repository:** L5_52_course_enrollment_system

---

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** Most of the Flake8 and Pylint style findings were mechanical. Removing the unused `math` import (F401), changing `== None` to `is None` (E711), adding the missing final newline (W292), wrapping long lines (E501) and renaming camelCase functions to snake_case (C0103) each took a one-line change. They did not change behaviour, and the tool gives the exact line and the expected form. Swapping `hashlib.md5` for `hashlib.sha256` and `random.randint` for `secrets.randbelow` were similarly direct one-for-one replacements.

**Hardest:** The `eval()` call (Bandit B307) was the hardest security fix because it could not simply be deleted. The function's contract was "pass a string expression", so I had to redesign the interface to take a numeric `discount_percent`, add validation (0–100), update the caller in `main()`, and confirm the output stayed the same (450.0 for a 25% discount on CS303). The `global` statement (W0603) and the mutable default argument (W0102) also needed some thought about how state flows through the program, rather than a text substitution.

The hardest issues overall were the **logic bugs that no tool reported**. `dropCourse("CS202")` reopened a closed course and created a seat even though no one was enrolled, so the program printed "Open courses: 3" instead of 2. Drops also never refunded tuition, seats could go negative, and a student could enrol twice. Fixing these meant understanding what the program is supposed to do and adding a per-course `students` list, which is a design change that no tool could suggest.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

Yes, a few findings were debatable rather than real defects:

- **Pylint C0103 on `total_tuition`:** Pylint assumes any module-level name assigned at the top level is a *constant* and wants `UPPER_CASE`. `total_tuition` is mutable running state, not a constant, so renaming it to `TOTAL_TUITION` would have been misleading. The real problem was the use of `global`, which I fixed by keeping the value in a `ledger` dict.
- **Bandit B324 (MD5):** This depends on context. If the hash were only a non-security identifier (like a cache key), MD5 with `usedforsecurity=False` would be acceptable and the warning would be a false positive. Since a student-identifying hash could be relied on for integrity, I treated it as a real issue and switched to SHA-256.
- **Bandit B105 (hard-coded password):** Bandit reported this with only *Medium confidence* because it matches on variable names and string contents. Here it was a true positive, since the token was a real secret and was even printed. But the same rule often fires on harmless strings such as `password_label = "Password"`.

The opposite problem, **false negatives**, was more important in this lab: all three tools reported a clean result even while the enrolment logic was wrong. Static analysis cannot know the business rules.

### 3. How would you integrate static analysis tools into your actual software development workflow?

- **In the editor:** Enable Pylint and Flake8 in VS Code or PyCharm so warnings appear while typing, when they are cheapest to fix.
- **Pre-commit hooks:** Use the `pre-commit` framework to run Flake8, Pylint and Bandit (plus a formatter such as Black) on staged files, so badly formatted or insecure code is blocked before it is committed.
- **Continuous Integration:** Add a GitHub Actions job that runs on every push and pull request, for example `flake8 .`, `pylint --fail-under=9.5 src/` and `bandit -r src/ -ll`. The build fails if style errors appear, if the Pylint score drops below the threshold, or if Bandit finds Medium or High severity issues. Upload the reports as build artifacts so reviewers can see them.
- **Shared configuration:** Keep a project-wide config (`.pylintrc`/`pyproject.toml`, `.flake8`, `.bandit`) under version control so everyone uses the same rules. Disable rules that don't fit the project there, with a justification, rather than with scattered inline `# noqa` / `# nosec` comments.
- **Alongside tests and review:** As this lab showed, the tools do not catch logic errors, so they should complement unit tests (for example, tests for "dropping a non-enrolled student does nothing") and human code review, not replace them.

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Measured results:** Pylint went from **4.00/10 to 10.00/10**, Bandit from **6 issues (2 High, 1 Medium, 3 Low) to none**, and Flake8 from **12 issues to 0**.
- **Security:** The program no longer runs shell commands built from user input, no longer executes arbitrary code through `eval()`, no longer keeps or prints a secret token in source code, and uses a strong hash and a cryptographically secure OTP generator.
- **Robustness:** The shared mutable default `audit_trail=[]` no longer leaks entries between calls. The roster file is always closed and written as UTF-8 because of the `with` block. Errors are no longer silently swallowed: an unknown course ID is reported and returns `False`. Importing the module no longer runs the demo, because of the `if __name__ == "__main__":` guard.
- **Correctness:** After the logic fixes, the program reports the right number of open courses (2), refunds tuition on a drop, never lets seat counts go negative, and rejects duplicate enrolments.
- **Readability and maintainability:** Consistent snake_case names, a docstring on every function, lines that fit on screen, f-strings, and a simplified `check_course_status` make the code much easier to read and change. Each function now clearly states what it returns and when it fails.
