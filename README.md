# Replicating Lopez-Lira & Roussanov (2023)

Group project replicating **"Do Common Factors Really Explain the Cross-Section of Stock
Returns?"** (Alejandro Lopez-Lira and Nikolai Roussanov, February 2023 version).

**The claim we test:** stock characteristics predict returns, but not because they measure
exposure to common risk factors. A long-short portfolio built from return forecasts and
hedged against all 50 latent factors still earns a high Sharpe ratio (paper Table 6: 2.31
hedged vs 0.84 unhedged vs 0.52 market, 1974-2021), which contradicts the Arbitrage Pricing Theory.

**Our scope:** a 6-day, 7-person replication of the core result with documented
simplifications. See [docs/PLAN.md](docs/PLAN.md) and [docs/DEVIATIONS.md](docs/DEVIATIONS.md).

## Quick start (every member)

```bash
git clone <repo-url> && cd lr-replication
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
make setup        # pip install -e ".[dev]"
make fake         # synthetic data for every file, so you can start immediately
make test         # shared tests pass; your member tests are skipped until you build them
make status       # pipeline stages and their owners
```

Then open [docs/members/](docs/members/) and read your file. If you use a coding agent
(Claude Code or similar), start it in this folder and say **"I'm Member N"**: it will read
[CLAUDE.md](CLAUDE.md) and your member file and pick up where you left off.

No `make`? Use the commands inside the [Makefile](Makefile), e.g. `python -m lrrep.fake`.

## How the pieces fit

```
Member 2  CRSP data ──► crsp_daily ──► Member 3  SVD betas ──► betas_svd ─┬─► Member 4  factor-exposure portfolios (Table 2), Fama-MacBeth (Table 8)
          crsp_monthly, market ─────────────────────────────────────────┤
Member 5  characteristics ──► chars_clean ──► forecasts ──► mu_hat ──────┴─► Member 6  hedged vs unhedged portfolios (Table 6, Figs 6-9)
Member 7  external factors ──► factors_ext ──────────────────────────────────► Member 7  alphas (Table 10), paper-vs-ours comparison, slides
Member 1  contracts, fake data, solver, pipeline, integration, report edit
```

Every arrow is a Parquet file with a fixed format: [docs/CONTRACTS.md](docs/CONTRACTS.md).

| Member | Stage | Code | Main outputs |
| --- | --- | --- | --- |
| 1 | Lead, integration | `pipeline.py`, `solver.py`, shared modules | one-command run, report |
| 2 | CRSP data | `data/crsp.py` | `crsp_daily`, `crsp_monthly`, `market` |
| 3 | SVD betas | `betas/svd.py` | `betas_svd`, `eigen`, Figure 1 |
| 4 | Factor portfolios, Fama-MacBeth | `portfolios/factor_exposure.py`, `tests_ap/fama_macbeth.py` | Table 2, Table 8 |
| 5 | Characteristics, forecasts | `forecast/` | `chars_clean`, `mu_hat` |
| 6 | Main portfolios | `portfolios/main_portfolios.py` | Table 6, Figures 6-9 |
| 7 | External factors, alphas, slides | `data/external_factors.py`, `tests_ap/alphas.py`, `report/comparison.py` | Table 10, comparison table, slides |

Names and GitHub handles: [docs/TEAM.md](docs/TEAM.md).

## Data

Data never goes in git (CRSP is licensed). It lives in a shared drive folder that each
member syncs locally; set `LRREP_DATA_DIR` to that folder. Layout: [data/README.md](data/README.md).

```bash
export LRREP_DATA_DIR="$HOME/Library/CloudStorage/OneDrive-GeorgiaInstituteofTechnology/lr-data"   # example
```

## Running

```bash
python -m lrrep.pipeline --stage betas --fake     # one stage on fake data
python -m lrrep.pipeline --all --fake --keep-going
python -m lrrep.pipeline --all                    # final real-data run (Member 1, day 4)
```

Results land in `results/tables/*.csv` and `results/figures/*.png` (committed).

## Working together

Branches `m<N>/<topic>`, pull requests into `main`, one review, CI must pass.
Full rules: [CONTRIBUTING.md](CONTRIBUTING.md). Daily status: [docs/status/](docs/status/).

## Repo setup (repo owner, once)

1. On GitHub, create a **private** repository (e.g. `lr-replication`). Do not add a README there.
2. Push this folder:
   ```bash
   git init -b main && git add . && git commit -m "m1: initial scaffold"
   git remote add origin git@github.com:<owner>/lr-replication.git && git push -u origin main
   ```
3. Settings → Collaborators: invite all 6 teammates with Write access.
4. Settings → Branches → add a rule (or ruleset) for `main`: require a pull request with 1 approval,
   require the `tests` status check to pass, block force pushes.
5. Fill in `docs/TEAM.md` and the GitHub handles in `.github/CODEOWNERS`.
6. Create the shared data folder (Georgia Tech OneDrive/Box/Google Drive), share it with the team,
   and post its link in the team chat (not in the repo).
