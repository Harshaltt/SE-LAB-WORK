# Lab 7: Fuzz Testing

Property-based fuzz testing of `visa_application.py` with Hypothesis and pytest, followed by hardening all three functions against malformed input.

| File | Description |
|------|-------------|
| `visa_application.py` | Fixed (hardened) module |
| `test_visa_application.py` | 9 Hypothesis tests: robustness, structured fuzzing, correctness |
| `PES2UG24CS183_Harsh_Mannan_Lab7_FuzzTesting.pdf` | Report with steps, screenshots and bugs found |

Original repo: [SETAPESU26/L6_L7_52_visa_application](https://github.com/SETAPESU26/L6_L7_52_visa_application)

## Run

```bash
pip install hypothesis pytest
python -m pytest test_visa_application.py   # 9 passed
python visa_application.py
```

Against the original buggy code: 6 failed, 3 passed. After the fixes: 9 passed.
