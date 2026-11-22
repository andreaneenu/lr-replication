# CLAUDE.md: instructions for coding agents in this repo

This repo is a 7-person, 6-day group replication of Lopez-Lira & Roussanov (2023),
"Do Common Factors Really Explain the Cross-Section of Stock Returns?". Each human member
owns one stage of a pipeline. You are working for ONE member at a time.

## 1. First thing in every session: who am I working for?

The user will say something like "I'm Member 3" or give their name.
- If they give a name, look it up in `docs/TEAM.md` to get the member number.
- If you cannot tell, ask: "Which member are you (1-7)?" Do nothing else until you know.

Then read, in this order, before writing any code:
1. `docs/members/member-<N>.md`: your role, files you own, day-by-day tasks, definition of done.
2. `docs/CONTRACTS.md`: the exact format of every file you read or write.
3. `docs/status/member-<N>.md`: where this member left off.
4. The paper section listed in your member file. A summary is in `docs/PAPER_NOTES.md`; the
   PDF, if present, is in `docs/paper/` (not committed if the course forbids sharing it).

Then tell the user in 3-5 lines: what you understand the next task to be, which files you will
touch, and how you will test it. Start once they agree (or right away if they said "go").

## 2. Branches and commits

- Never commit to `main`. Work on a branch named `m<N>/<short-topic>`, e.g. `m3/svd-betas`.
  Start it from an up-to-date main:
  `git switch main && git pull && git switch -c m3/svd-betas`
- Commit small and often. Message format: `m<N>: <what changed>` (e.g. `m3: add Figure 1`).
- Before opening a PR, bring main in: `git fetch origin && git rebase origin/main`
  (or `git merge origin/main` if the member prefers). Resolve conflicts only in files you own;
  if a conflict is in someone else's file, stop and tell the user.
- Open a PR with `gh pr create --fill` (or on github.com) using the PR template. Never merge your
  own PR; never force-push to `main`.
- Details: `CONTRIBUTING.md`.

## 3. Ownership: what you may edit

Edit ONLY the paths your member owns (listed at the top of their member file and in
`.github/CODEOWNERS`). In particular:

| Member | Owns |
| --- | --- |
| 1 | `src/lrrep/{config,contracts,io,fake,stats,timing,pipeline}.py`, `src/lrrep/portfolios/solver.py`, `tests/test_shared.py`, `config.yaml`, root docs, `.github/`, `report/` (final edit) |
| 2 | `src/lrrep/data/crsp.py`, `tests/test_member_2.py` |
| 3 | `src/lrrep/betas/`, `tests/test_member_3.py` |
| 4 | `src/lrrep/portfolios/factor_exposure.py`, `src/lrrep/tests_ap/fama_macbeth.py`, `tests/test_member_4.py` |
| 5 | `src/lrrep/forecast/`, `tests/test_member_5.py` |
| 6 | `src/lrrep/portfolios/main_portfolios.py`, `tests/test_member_6.py` |
| 7 | `src/lrrep/data/external_factors.py`, `src/lrrep/tests_ap/alphas.py`, `src/lrrep/report/`, `tests/test_member_7.py`, `slides/` |

Everyone may edit: their own `docs/status/member-<N>.md`, their own section file in `report/sections/`,
their own row in `docs/DEVIATIONS.md`, and new helper modules inside their own folder.

Shared files (`contracts.py`, `config.yaml`, `io.py`, `solver.py`, `stats.py`, `docs/CONTRACTS.md`)
change ONLY through a separate PR labelled `contract-change`, approved by Member 1 and by every
member who reads the affected file. If you think one needs to change, tell the user and draft the
PR; do not slip the change into a feature PR.

## 4. How to work

- Setup once: `python -m venv .venv && source .venv/bin/activate && make setup && make fake`.
- Build against FAKE data first (`--fake`, `load(name, fake=True)`). Real data arrives on day 2
  in the shared folder; point `LRREP_DATA_DIR` at it. Never wait for another member: their file
  already exists in `data/fake/`.
- Read and write contract files only through `lrrep.io.load` / `lrrep.io.save` (save validates
  the contract). Read settings only from `lrrep.config.CFG`; never hard-code windows, K, dates.
- Use the shared helpers instead of re-implementing them: `lrrep.portfolios.solver` (pure-play
  weights), `lrrep.stats` (Sharpe, Newey-West, subperiods), `lrrep.timing` (look-ahead tests).
- Run your stage: `python -m lrrep.pipeline --stage <stage> --fake`. Stages and owners: `make status`.
- Tests: your `tests/test_member_<N>.py` tests are skipped until your functions exist, then must
  pass. Add tests for anything non-obvious. Run `make test && make lint` before every PR.
- Results: small CSV tables go to `results/tables/`, figures to `results/figures/`, both via
  `lrrep.io.save_table` / `lrrep.io.figure_path`. These ARE committed (from real-data runs only).

## 5. Rules that protect the result

1. **Timing.** A row dated month t may only use information available at the end of month t.
   Predictive files are indexed by formation month t and predict the return in t+1. Every
   predictive function gets a look-ahead test (`lrrep.timing.assert_no_lookahead`).
2. **No data in git.** Never commit anything under `data/` (except `data/README.md`), raw
   downloads, WRDS credentials, or `.env`. CRSP is licensed: it lives only in the shared drive.
3. **Reproducible.** Seed from `CFG["seed"]`. No notebooks as the source of a result: the
   pipeline must regenerate every table and figure. Notebooks are fine for exploring in
   `notebooks/<member>/` (gitignored outputs).
4. **Honest deviations.** Any choice that differs from the paper goes in `docs/DEVIATIONS.md`
   with why and its likely effect.
5. **Fake numbers are never reported.** Fake data only checks that code runs and signs are sensible.

## 6. Keep the team informed

At the end of each work session, update `docs/status/member-<N>.md` (done / next / blocked / files
delivered) and commit it on your branch. When you deliver a real data file, post in the team chat:
"Member N: <file> delivered to the shared folder, <rows> rows, <date range>".

## 7. Definition of done for any task

Code in owned paths, tests pass (`make test`), lint clean (`make lint`), stage runs on fake data,
contract validated on save, status file updated, PR open with the template filled in.
