# Member 2: CRSP data

**Owns:** `src/lrrep/data/crsp.py`, `tests/test_member_2.py`.
**Writes:** `crsp_daily`, `crsp_monthly`, `market` (formats: `docs/CONTRACTS.md`).
**Read by:** Members 3 (daily), 4, 5, 6, 7 (monthly, market). You are on the critical path on day 1-2.
**Paper:** Section 3.1 (Data).

## Start here

```bash
pip install wrds          # or: pip install -e ".[wrds]"
python -c "import wrds; db = wrds.Connection()"   # creates ~/.pgpass on first login; never commit it
make test                 # tests/test_member_2.py is skipped until build_monthly exists
```
First check which CRSP format your account has (legacy `crsp.msf`/`crsp.dsf` or CIZ `crsp.msf_v2`/`crsp.dsf_v2`)
and write it in `docs/status/member-2.md` and `docs/DEVIATIONS.md` row 7.

## Day by day

- [ ] **Day 1 (morning)** Confirm WRDS access. If you don't have it, tell Member 1 immediately and ask the GT library; someone else may have it.
- [ ] **Day 1** `pull_monthly`: monthly returns, price, shares, share and exchange codes (valid on that date), delisting returns, 1965-2021.
- [ ] **Day 1** `pull_risk_free_and_market`: Ken French F-F factors (monthly and daily); convert percent to decimals.
- [ ] **Day 1** `build_monthly` (make `tests/test_member_2.py` pass): delisting-adjusted `ret`, `exret`, `me = |prc|*shrout/1000`, NYSE 20th-percentile size filter → `in_universe`.
- [ ] **Day 2 (by noon)** Deliver a 1990-1994 slice of all three files to the shared folder so others test on real data.
- [ ] **Day 2** `pull_daily` (year by year, only permnos ever in the universe) and `build_daily`; deliver full `crsp_daily`, `crsp_monthly`, `market` by end of day 2.
- [ ] **Day 2** Sample stats for the report: stocks in universe per year (save `results/tables/sample_stats.csv`).
- [ ] **Day 3** Help Member 5 merge Chen-Zimmermann signals on permno-month; data sanity checks (no duplicate keys, returns within [-1, 10], no gaps for live stocks).
- [ ] **Day 4** Figure: number of stocks in universe over time (`results/figures/universe.png`); write `report/sections/02-data.md`.
- [ ] **Day 5** Finalize data section; fill deviation rows 6-7.

## Spec details

- Delisting: `ret_total = (1+ret)(1+dlret) - 1`; if `ret` is missing and `dlret` exists, use `dlret`.
- `in_universe` at t: shrcd in {10, 11}, exchcd in {1, 2, 3}, and `me_t >= p20` where p20 is the 20th percentile of `me` among exchcd == 1 stocks at t.
- `crsp_daily` must include each universe stock's days for the 12 months BEFORE each month it is in the universe (Member 3 needs the trailing window). Simplest: keep all days for permnos ever in the universe.
- Months as month-end timestamps; `permno` int64; returns decimals.

## Definition of done

Three files in the shared folder, saved with `lrrep.io.save` (contract validated), dated 1965-01 to 2021-12;
test passes; sample stats table; chat message with rows and date ranges.

## Pitfalls

- CRSP price is negative when it's a bid-ask average: always use `abs(prc)`.
- Share and exchange codes change over time: use the record valid on that date, not the latest.
- Don't drop a stock-month just because it's out of the universe: keep it with `in_universe = False` (others need its returns).
