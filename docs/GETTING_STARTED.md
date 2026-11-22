# Getting started (everyone, about 15 minutes)

Do these once. Then work at your own pace on your part.

## 1. Send your GitHub username

Post it in the group chat. You'll get an invite to the team repo; accept it from your email or
github.com/notifications. **Don't wait for it**: step 2 works without the invite.

## 2. Get the code

**Already accepted the invite?**
```bash
git clone https://github.com/andreaneenu/lr-replication.git
cd lr-replication
```

**No invite yet?** Open https://github.com/andreaneenu/lr-replication, click **Fork** (top right), then:
```bash
git clone https://github.com/YOUR-USERNAME/lr-replication.git
cd lr-replication
git remote add upstream https://github.com/andreaneenu/lr-replication.git
```
When your invite arrives later you can keep using your fork; nothing breaks.

## 3. Set up Python (inside the `lr-replication` folder)

Needs Python 3.10+ and git.

```bash
python -m venv .venv
```
Activate it:
- Windows (PowerShell): `.venv\Scripts\activate`
  (if PowerShell blocks it, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)
- Mac/Linux: `source .venv/bin/activate`

Then:
```bash
pip install -e ".[dev]"
python -m lrrep.fake
python -m pytest
```
You should see about **14 passed, 8 skipped**. The skipped tests belong to parts nobody has built
yet; yours switch on once you write your functions.

(`make` commands in the README are shortcuts for these; Windows users can ignore `make`.)

## 4. Set up your agent

- Get the paper PDF from the team's shared folder and put it in `docs/paper/` (it's gitignored, so it
  is never pushed).
- **Claude Code or another coding agent:** open it in the `lr-replication` folder and say:
  > I'm Member N. Read CLAUDE.md and my brief, then tell me my next task.

  It reads [CLAUDE.md](../CLAUDE.md), knows your files, the branch naming and the rules.
- **Claude in the browser instead?** Start a chat, upload the paper PDF plus `CLAUDE.md`,
  `docs/members/member-N.md` and `docs/CONTRACTS.md`, and say which member you are.

## 5. Read the plan and your brief

[PLAN.md](PLAN.md) (5 minutes: goal, scope, roles, who waits on whom), then

your brief `docs/members/member-N.md`: what you own, what you deliver, a suggested day-by-day checklist,
and what "done" means. Member numbers and names: [TEAM.md](TEAM.md).

---

## How we work (short version)

- **Your own pace.** The day labels in the briefs are a suggested pace, not deadlines.
- **Waiting on someone?** Build and test on fake data (`python -m lrrep.fake` made every file), and
  message the member whose file you need directly (who owns what: [CONTRACTS.md](CONTRACTS.md),
  names: [TEAM.md](TEAM.md)). If you're the one others wait on, tell them roughly when it'll be ready.
- **Never push to `main`.** One branch per task, named `m<N>/<topic>`:
  ```bash
  git switch -c m3/svd-betas
  ```
- **Edit only your own files** (table in [CLAUDE.md](../CLAUDE.md)). Shared files change only by agreement.
- **Never commit data.** The repo is public and CRSP data is licensed. Real data lives in the shared folder.
- **Done with a piece?** Push your branch and open a pull request into `andreaneenu/lr-replication`
  `main`. Your review partner ([CONTRIBUTING.md](../CONTRIBUTING.md)) takes a look, then it gets merged.
- **Stay in sync:** `git pull upstream main` (or `git pull origin main` if you cloned the team repo directly).
- **Leave a note** in `docs/status/member-N.md` when you stop, so others (and your agent) know where you are.
