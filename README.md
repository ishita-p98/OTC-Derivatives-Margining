# OTC Derivatives Margining & Systemic Liquidity Risk

**Collaborative university research | Quantitative risk management | OTC derivatives | Initial and variation margin | Fire sales | Systemic liquidity**

> Educational Monte Carlo model. This is not a regulatory margin engine, production counterparty-risk model, investment recommendation or validated loss forecast.

## Research question

Can bilateral margin requirements reduce a dealer's counterparty exposure while increasing liquidity pressure on an investor, causing forced asset sales and endogenous default? How do initial-margin calibration, variation-margin frequency, the margin period of risk (MPOR), collateral eligibility and procyclical recalibration affect this trade-off?

## Project overview

The model represents a stylized OTC forward between two institutions:

- **Institution A - Investor:** long a forward, holds limited cash and illiquid assets, and can default from an exogenous shock or inability to meet margin calls.
- **Institution B - Dealer:** takes the opposite side and is assumed always solvent.

The analysis derives one-sided 99% delta-normal initial margin, simulates arithmetic-Brownian asset-price paths over a 252-trading-day observation window, tracks variation-margin calls, and estimates close-out losses after the MPOR. Extensions add fire sales, eligible illiquid collateral, procyclical initial margin and a lagged aggregate fire-sale haircut.

## Start here

- [Main submitted research notebook](notebooks/01_margining_simulation_submission.ipynb) - the complete original implementation, retained as a single notebook for provenance.
- [Methodology](docs/METHODOLOGY.md) - model setup, equations and conventions.
- [Model audit and corrections](docs/MODEL_AUDIT.md) - differences identified between assignment, submission and revised simulation.
- [Simulation results](docs/SIMULATION_RESULTS.md) - corrected-run tables and caveats.
- [Source review](docs/SOURCE_REVIEW.md) - overview of assignment requirements and submitted materials.
- [Publication status](docs/PUBLICATION_STATUS.md) - anonymization and release notes.
- [Contribution context](CONTRIBUTIONS.md) - acknowledgement of the collaborative university project.

## Selected results from the corrected research implementation

A separate corrected implementation was previously run with 20,000 Monte Carlo paths, a 252-day observation window and a 10-day MPOR.

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

## Repository structure

- `notebooks/` - original research notebook and notebook guide.
- `docs/` - methodology, audit, results and source review.
- `data/` - no external data required; model inputs are parameterized.
- `tests/` - notebook JSON and Python syntax integrity checks.
- `index.html` - existing project overview page retained for compatibility.

## Run and inspect

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Open [the research notebook](notebooks/01_margining_simulation_submission.ipynb) in Jupyter and run its cells in order. A lightweight structural test can be run with:

```bash
python -m pytest -q
```

## Key modelling conventions

- Forward MTM to A: \(V_t=Q(S_t-K)\).
- Initial margin: \(IM=z_{0.99}Q\sigma_s\sqrt{MPOR/252}\), with dollar volatility \(\sigma_s=20\%\times S_0\).
- Daily default probability is calibrated so the one-year cumulative probability equals the selected annual PD.
- VM stops on the default day. At close-out, B holds IM actually posted plus the last successfully settled VM balance.
- Fire-sale losses are charged only on assets actually sold; insufficient proceeds trigger liquidity default.
- The corrected implementation uses common price paths and exogenous default dates where possible for policy comparisons.

## Model limitations

The model assumes arithmetic-Brownian price dynamics, an always-solvent dealer, independent investor exogenous defaults and simplified collateral/close-out treatment. The systemic extension makes the fire-sale discount depend on the previous day's aggregate selling fraction, but does not model correlated defaults or common asset-price returns. Outcomes depend on the selected parameters and random seed.

The revised implementation changes several timing and accounting conventions in the submitted notebook/report. The detailed results below are from the corrected local analysis package and should not be confused with the original notebook's stored outputs. They have not been calibrated to real-world portfolios or regulatory standards.

## Group-project context

This work originated as a university group assignment and is presented as collaborative research, not as an individually completed project. The public-facing repository omits student numbers, personal identifiers and the original group roster.

## Licensing

No open-source licence is included. Reuse permissions should be agreed by the relevant contributors. Public visibility does not grant rights to third-party content. See [licensing note](LICENSE_NOT_INCLUDED.md).

**Educational use only - not regulatory advice or investment advice.**
