# Running Playwright Tests

To run Playwright tests, use `pytest` with the `pytest-playwright` plugin. Tests are written in Python.

```bash
# Run all tests
pytest tests/

# Run a specific test file
pytest tests/test_login.py

# Run in headed mode (shows the browser)
pytest tests/ --headed

# Run with slow motion (milliseconds between actions)
pytest tests/ --slowmo=500

# Run a specific test by name
pytest tests/ -k "test_login_success"

# Run with verbose output
pytest tests/ -v
```

# Debugging Playwright Tests

To debug a failing Playwright test, set the `PWDEBUG=cli` environment variable. This pauses the test at the start and prints the debugging instructions.

**IMPORTANT**: run the command in the background and check the output until "Debugging Instructions" is printed. Make sure to stop the command after you have finished.

Once instructions containing a session name are printed, use `playwright-cli` to attach the session and explore the page.

```bash
# Run the test with CLI debugger
$env:PWDEBUG="cli" ; pytest tests/test_login.py

# ...
# ... debugging instructions for "tw-abcdef" session ...
# ...

# Attach to the test
playwright-cli attach tw-abcdef
```

Keep the test running in the background while you explore and look for a fix.
The test is paused at the start, so you should step over or pause at a particular location
where the problem is most likely to be.

Every action you perform with `playwright-cli` generates corresponding Playwright Python code.
This code appears in the output and can be copied directly into the test. Most of the time, a specific locator or an expectation should be updated, but it could also be a bug in the app. Use your judgement.

After fixing the test, stop the background test run. Rerun to check that test passes.
