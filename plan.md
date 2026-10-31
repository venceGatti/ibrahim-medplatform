1. **Fix missing dependency in Github Actions CI:**
   - The user explicitly provided a CI failure log showing `ModuleNotFoundError: No module named 'psutil'` in `medclient/sidecar-python/src/api/agentic_routes.py`. The user asked me to "analyze the above information and fix the errors causing these CI failures". I added `psutil==6.1.1` to `medclient/sidecar-python/requirements.txt` to fix the CI.

2. **Verify locally:**
   - Use `cat medclient/sidecar-python/requirements.txt` to confirm `psutil` is added.

3. **Run tests:**
   - Run tests using `cd medclient/sidecar-python && python -m pytest tests/` to confirm tests pass locally. Tests passed!

4. **Pre-commit and submit:**
   - Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
   - Commit and submit the changes.
