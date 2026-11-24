# OTC Derivatives Margining & Systemic Liquidity Risk

**Collaborative university research | Quantitative risk management | OTC derivatives | Initial and variation margin | Fire sales | Systemic liquidity**

> Educational Monte Carlo model. This is not a regulatory margin engine, production counterparty-risk model, investment recommendation or validated loss forecast.

## Research question

Can bilateral margin requirements reduce a dealer's counterparty exposure while increasing liquidity pressure on an investor, causing forced asset sales and endogenous default? How do initial-margin calibration, variation-margin frequency, the margin period of risk (MPOR), collateral eligibility and procyclical recalibration affect this trade-off?

## Project overview

This project models a stylized OTC forward between two institutions:

- **Institution A — Investor:** long a forward, holds limited cash and illiquid assets, and can default from an exogenous shock or inability to meet margin calls.
- **Institution B — Dealer:** takes the opposite side and is assumed always solvent.

The project derives one-sided 99% delta-normal initial margin, simulates arithmetic-Brownian asset-price paths over a 252-trading-day observation window, tracks variation-margin calls, and estimates close-out losses after the MPOR. The extended model adds fire sales, eligible illiquid collateral, procyclical initial margin and a lagged aggregate fire-sale haircut.

## Selected results from the corrected research implementation

The corrected implementation was previously run with 20,000 Monte Carlo paths, a 252-day observation window, 10-day MPOR and fixed random seeds.

- **99% initial margin:** $9,268.39.
- **Unlimited-cash exogenous default frequency:** 1.03%.
- **Limited-cash investor default frequency:** 21.92%.
- **Paths with fire sales:** 56.12%.
- **Mean realized fire-sale cost per path:** $552.26.

| Setup | Investor default | Fire-sale cost / path | Mean dealer loss / path |
|---|---:|---:|---:|
| Daily VM, limited cash and fire sales | 21.92% | $552.26 | $10.91 |
| Weekly VM (5 trading days) | 20.39% | $516.29 | $51.12 |
| Eligible illiquid collateral for VM | 3.00% | $0.00 | $0.61 |

These are outputs from a stylized simulation under selected parameters, not empirical default forecasts. See [complete results and interpretation](docs/SIMULATION_RESULTS.md).

## Repository map

- `src/otc_margining.py` — reusable model, collateral, liquidity and loss functions.
- `run_analysis.py` — reproducible core scenarios, policy experiments, data outputs and figures.
- `notebooks/` — four focused walkthroughs of the assignment.
- `figures/` — generated simulation figures.
- `outputs/` — CSV/JSON scenario summaries.
- `docs/` — methodology, audit, results and source review.
- `tests/` — unit and simulation sanity checks.

## Run locally

```bash
python -m pip install -r requirements.txt
python run_analysis.py
python -m pytest -q
```

No external market data are required: the assignment uses simulated price paths and parametric exogenous defaults. The analysis is self-contained.

## Key modelling conventions

- Forward MTM to A: \(V_t=Q(S_t-K)\).
- Initial margin: \(IM=z_{0.99}Q\sigma_s\sqrt{MPOR/252}\), with dollar volatility \(\sigma_s=20\%\times S_0\).
- Daily default probability is calibrated so the one-year cumulative default probability equals the chosen annual PD.
- VM stops on the default day. At close-out, B holds IM actually posted plus the last successfully settled VM balance.
- Fire-sale losses are charged only on assets actually sold; insufficient proceeds trigger liquidity default.
- Policy comparisons use common price paths and exogenous default dates where possible to reduce Monte Carlo noise.

## Technical notes and limitations

The assignment specifies a stylized arithmetic-Brownian forward. The implementation assumes an always-solvent dealer, independent investor exogenous defaults, simplified collateral and close-out mechanics, and fixed haircut conventions. The systemic extension makes the fire-sale discount depend on the previous day's aggregate selling fraction, but does not model correlated defaults or common asset-price returns. Results are parameter- and seed-dependent.

The revised implementation corrects several inconsistencies in the submitted notebook/report, including the observation horizon, default-day VM settlement, MPOR close-out horizon, realized fire-sale costs, initial IM funding and release of excess procyclical IM. See [model audit](docs/MODEL_AUDIT.md).

## Group-project context

This work originated as a university group assignment and is presented as collaborative research, not as an individually completed project. The public-facing repository omits student numbers, personal identifiers and the original group roster. See [contribution context](CONTRIBUTIONS.md).

## Licensing

No open-source licence is included. Reuse permissions should be agreed by the relevant contributors. Public visibility does not grant rights to third-party content. See [licensing note](LICENSE_NOT_INCLUDED.md).

**Educational use only — not regulatory advice or investment advice.**