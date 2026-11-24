# Audit and corrections relative to the submitted notebook and report

The assignment brief, submitted notebook and report were reviewed together. The modular implementation changes the following conventions:

1. **Observation window:** the assignment asks for 252 trading days. The submitted parameter table used a 300-day window. The corrected run uses 252 observation days, keeps maturity at 300 days, and generates an additional MPOR segment only to observe close-out following late-window defaults.
2. **MPOR:** the report's derivation page appears to describe MPOR as 300 days, while its parameter table and submitted code use 10 days. The corrected base case consistently uses 10 days.
3. **Close-out collateral:** the submitted loss function treated the last daily change in MTM as “last VM”. The corrected model uses the last successfully settled VM balance, because the collateral account is reset to current MTM at each settlement.
4. **Default-day VM:** no VM exchange is made on the day A defaults. The last successful settlement is prior to default; an unpaid margin call is not counted as collateral.
5. **Full MPOR close-out:** the submitted notebook capped close-out at the last simulated day. The corrected simulation extends the price process beyond the observation window by MPOR days.
6. **Fire-sale cost:** the submitted code computed the cost of a theoretical liquidation before checking available assets. The corrected model charges only for assets actually sold; if assets are insufficient, it sells all remaining assets and defaults on the residual call.
7. **Initial IM funding:** when a higher IM multiplier exceeds available cash, the corrected fire-sale model sells assets at inception to fund IM; if assets are insufficient, the investor defaults at day zero.
8. **Weekly VM:** VM is accumulated between settlement dates and the latest successful settlement mark is held consistently for close-out.
9. **Procyclical IM:** both IM top-ups and releases are recognized. The submitted code only accumulated positive top-ups and did not symmetrically release excess IM when volatility fell.
10. **Systemic haircut:** the discount uses the previous day's share of investors selling assets, as specified by the assignment, and is capped at 50%.

These corrections materially change simulation results. The submitted report's values are preserved only as historical reference; corrected results are recalculated under the new conventions and are not intended to reproduce the original report.