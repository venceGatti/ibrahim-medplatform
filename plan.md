1. **Fix Python import error in Medfactory tests:**
   - The CI is failing because running `pytest medfactory/tests -v` throws `ModuleNotFoundError: No module named 'medfactory'`.
   - The user explicitly gave me a CI failure log that points exactly to `test_medfactory.py` failing with this error. I will fix it by adding a `conftest.py` file to `medfactory/tests/` to prepend the root directory to `sys.path`.

2. **Verify fix locally:**
   - I ran `python -m pytest medfactory/tests -v` locally and confirmed that the tests now pass.

3. **Pre-commit and submit:**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
   - Add, commit, and submit the changes.
