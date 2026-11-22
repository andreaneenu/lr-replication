# How we work together

Seven people, six days, one repo. The rules below keep merges painless.

## Getting the code: fork (default) or direct push

The repo is public, so nobody needs an invite to start.

- **Not invited (default): fork workflow.** On GitHub, click **Fork** on the team repo, then:
  ```bash
  git clone https://github.com/<you>/lr-replication.git && cd lr-replication
  git remote add upstream https://github.com/<owner>/lr-replication.git
  ```
  Push branches to your fork (`origin`) and open pull requests into the team repo's `main`.
- **Invited later (optional):** you can push branches straight to the team repo instead of your fork.
  Everything else stays the same.

Below, `upstream` means the team repo. If you cloned the team repo directly, read `upstream` as `origin`.

## The short version

1. One branch per task, named `m<N>/<topic>` (`m3/svd-betas`, `m6/table6`, `m7/factors-download`).
2. Edit only the files you own (see the table in `CLAUDE.md` and `.github/CODEOWNERS`).
3. Open a pull request into `main` early (as a draft is fine). It merges when CI is green and one
   reviewer approves.
4. Pull `main` into your branch at least twice a day.
5. Shared files change only through a `contract-change` PR.

## Branches

| Branch | Purpose | Who merges |
| --- | --- | --- |
| `main` | Always runs: `make test` passes and `make run-fake` works | Member 1 or the reviewer, after approval |
| `m<N>/<topic>` | One member's task | Squash-merged into `main` by PR |
| `contracts/<topic>` | A change to a shared file (contracts, config, solver, io, stats) | Member 1, after every affected reader approves |
| `report/<section>` | Writing (optional: report text can also go on your feature branch) | Reviewer |

Keep branches short-lived: merge at least once a day. A branch older than a day collects conflicts.

## Commits

Format: `m<N>: <imperative summary>`, e.g. `m5: add yearly random forest forecasts`.
Small commits; never commit data, credentials, or large outputs (`.gitignore` blocks most).

## Staying in sync with main

```bash
git fetch upstream
git rebase upstream/main      # or: git merge upstream/main   (pick one style per person; both are fine)
make test
git push --force-with-lease origin <your-branch>   # only after a rebase, only on YOUR branch
```

Starting a new task:
```bash
git switch main && git pull upstream main && git push origin main   # keep your fork's main current
git switch -c m3/<topic>
```

Conflicts should be rare because everyone owns different files. If one appears in a file you
don't own, don't resolve it by guessing: ask its owner.

## Pull requests

- Title: `m<N>: <what>`. Fill in the template (what, how tested, contract impact, deviations).
- Open it with `gh pr create --repo <owner>/lr-replication --fill` or the "Compare & pull request" button on your fork.
- CI runs `ruff` and `pytest` on fake data. It must be green. For a first-time contributor's PR,
  GitHub waits until the repo owner clicks **Approve and run workflows** once.
- Reviews: your partner reviews and comments "LGTM" (non-collaborators' approvals don't count toward
  GitHub's required approvals, so the owner merges after the partner's LGTM).
- Reviewer pairs:

| Author | Reviewer | Why |
| --- | --- | --- |
| Member 2 | Member 3 | Member 3 consumes the CRSP files |
| Member 3 | Member 4 | Member 4 consumes betas first |
| Member 4 | Member 6 | Same solver, same portfolio logic |
| Member 5 | Member 6 | Member 6 consumes the forecasts |
| Member 6 | Member 7 | Member 7 tests the portfolios |
| Member 7 | Member 5 | Cross-check of statistics |
| Member 1 | Member 2 | Shared code (any member may step in) |

  Member 1 may approve any PR when the paired reviewer is unavailable.
- Merge method: **Squash and merge**, then delete the branch.

## Changing a contract or a shared file

1. Branch `contracts/<topic>`; change `src/lrrep/contracts.py` AND `docs/CONTRACTS.md` together
   (and `fake.py`, so the fake files still match).
2. Label the PR `contract-change`, list the affected readers, @-mention them.
3. Merge only after Member 1 and every affected reader approve. Then announce it in the team chat:
   everyone pulls main and re-runs `make fake`.

## Public repo: what must never be pushed

The repo is public. Never commit CRSP or any WRDS data, raw downloads, credentials (`.pgpass`, `.env`),
or the paper PDF. `.gitignore` blocks these; never override it with `git add -f`. If something slips in,
tell Member 1 immediately: deleting it in a new commit is not enough, the history must be rewritten.

## Sharing data files

- Real data: the shared drive folder (`LRREP_DATA_DIR`). Write your file there with
  `lrrep.io.save` (it validates the contract), then post in the chat:
  `Member N: <file> delivered, <rows> rows, <first>-<last> month`.
- Never overwrite another member's file in the shared folder.
- If you re-deliver a file, bump a note in your status file with the date and what changed.

## Pace and coordination

- Everyone works at their own pace. The day labels in the briefs are a suggested pace, not deadlines.
- **If your work waits on another member's file**, keep building on fake data and message that member
  directly to ask when it'll be ready. Owners of each file: docs/CONTRACTS.md; names: docs/TEAM.md.
- **If others wait on you**, tell them roughly when your file will be ready, and deliver a partial
  version (for example a short sample period) early if you can.
- Pull requests are reviewed by your partner when they can; the repo owner merges approved ones.
- Leave a note in `docs/status/member-<N>.md` whenever you stop working.

## Report and slides

Each member writes their section in `report/sections/<NN>-<topic>.md` (Markdown, figures linked
from `results/figures/`). Member 1 assembles and edits `report/report.md` on day 5-6.
Member 7 owns `slides/`; each member sends 1-2 slides' worth of content by day 5.
