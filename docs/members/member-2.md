# Member 2: CRSP data, earnings dates, summary statistics

**Owns:** `src/lrrep/data/crsp.py`, `tests/test_member_2.py`.
**Writes:** `crsp_daily`, `crsp_monthly`, `market`, `earnings_dates`; `results/tables/summary_stats.csv`.
**Read by:** Members 3 (daily), 4, 5, 6, 7. You are on the critical path for days 1-2.
**Paper:** Section 3.1 (Data). **Report:** section 5 (data sources + summary statistics table).

## Start here

```bash
pip install wrds          # or: pip install -e ".[wrds]"
python -c "import wrds; db = wrds.Connection()"   # creates ~/.pgpass on first login; never commit it
python -m pytest tests/test_member_2.py           # skipped until build_monthly exists
```
First check which CRSP format your account has (legacy `crsp.msf`/`crsp.dsf` or CIZ `crsp.msf_v2`/`crsp.dsf_v2`)
and the **last month available**. Write both in `docs/status/member-2.md` and tell Member 1 (it sets the extension's end date).

## Day by day (suggested pace)

Work at your own pace. If you need another member's file before it's ready, keep going on fake data and message them.

- [ ] **Day 1** Confirm WRDS access (CRSP and Compustat). No access? Tell Member 1 at once; someone else may have it.
- [ ] **Day 1** `pull_monthly`, `pull_risk_free_and_market`, `build_monthly` (make the test pass), 1965 to the **latest available month** (the extension needs data past 2021).
- [ ] **Day 2** Deliver a 1990-1994 slice early, then the full `crsp_daily`, `crsp_monthly`, `market`.
- [ ] **Day 3** `pull_earnings_dates` (Compustat `fundq.rdq` linked to permno) → `earnings_dates` for Member 4's cash-flow news test.
- [ ] **Day 3** `summary_stats` table for the report (stocks per month, returns, size, by decade).
- [ ] **Day 4** Data checks (no duplicate keys, returns within [-1, 10], no gaps for live stocks); help Member 5 merge characteristics on permno-month if needed.
- [ ] **Day 5** Report section 5 draft (sources, filters, summary statistics, universe chart `results/figures/universe.png`); deviation rows 6-7 in `docs/DEVIATIONS.md`.
- [ ] **Day 6-7** Your 1-2 slides (data and sample); rehearsal.

## Spec details

- Delisting: `ret_total = (1+ret)(1+dlret) - 1`; if `ret` is missing and `dlret` exists, use `dlret`.
- `in_universe` at t: shrcd in {10, 11}, exchcd in {1, 2, 3}, `me_t >= p20`, the 20th percentile of `me` among NYSE (exchcd == 1) stocks at t.
- Keep all daily rows of permnos ever in the universe (Member 3 needs trailing 12-month windows).
- Earnings dates: link with `ccmxpf_lnkhist` (linktype LU/LC, linkprim P/C, rdq inside the link dates).

## Definition of done

Four files in the shared folder via `lrrep.io.save` (validated), through the latest month; test passes;
summary statistics table; chat message with rows and date ranges.

## Pitfalls

- CRSP price is negative when it's a bid-ask average: always `abs(prc)`.
- Share and exchange codes change over time: use the record valid on that date.
- Keep out-of-universe stock-months (flag them False); others need their returns.
