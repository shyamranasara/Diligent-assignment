# AI Notes

## Tool used
Claude (Anthropic), in a chat session with file/code execution tools.

## What was AI-generated vs. written by me

To be fully transparent: I used Claude to generate the entire first pass of this
project in one session — `src/app.py`, `src/database.py`, `tests/test_app.py`,
and this documentation. I described the assignment requirements and chosen
stack (Python/Flask/SQL) and asked it to build the project directly rather
than hand me a generic template.

**[Personalize this section before submitting]** — after generating the code,
I reviewed it myself and made/rejected the following changes:
- <e.g. "renamed X endpoint because Y">
- <e.g. "changed the date validation because Z">
- <e.g. "reviewed the SQL and confirmed no injection risk since all queries use parameterized placeholders">

## What was validated

In-session, before treating anything as "done":
- Ran the full test suite (`python3 -m unittest discover -s tests`) — all 20
  tests passed.
- Additionally ran a manual smoke test hitting every endpoint in sequence
  (add two expenses, list all, filter by category, get overall total, get
  totals by category, delete one, confirm the total updates) to check
  actual behavior, not just that tests were green.
- Read through the SQL in `database.py`/`app.py` to confirm all queries use
  parameterized placeholders (`?`), not string interpolation.
- Confirmed input validation rejects missing fields, non-numeric amounts,
  amounts ≤ 0, and malformed dates (tested each case explicitly).

**[Personalize this section before submitting]** — you should independently:
- Run `pip install -r requirements.txt`, start the server, and hit each
  endpoint yourself with `curl` or Postman.
- Run the test suite yourself on a clean checkout, exactly as the README
  describes, since that's what the reviewer will do.
- Skim `src/app.py` and `src/database.py` end-to-end and make sure you can
  explain every line — you may be asked about it.

## AI suggestions not used / things worth flagging

- The initial design considered storing data as an in-memory Python list
  (as the assignment explicitly allows), but SQLite was chosen instead so
  the "total by category" calculation could use real SQL (`GROUP BY`)
  rather than manual aggregation — closer to how this would be done in
  production, at negligible extra complexity.
- No bonus feature (search, monthly summary, Swagger docs, Docker) was
  added, to keep the submission focused on the core requirements within
  the time budget.
- Test suite uses `unittest` instead of `pytest`-native syntax so it has no
  dependency beyond Flask itself, while remaining fully runnable via
  `pytest tests/` (which auto-discovers `unittest.TestCase` classes) —
  this matters if the reviewer's environment doesn't have `pytest`
  pre-installed for some reason.

**[Personalize this section before submitting]** — note any suggestion
Claude made that you disagreed with or changed, and why. Reviewers are
specifically checking for this, so a real example (even a small one)
matters more than a polished-sounding generic one.
