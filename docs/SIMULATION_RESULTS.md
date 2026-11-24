# Simulation results and interpretation

**Run configuration:** 20,000 Monte Carlo paths; 252-trading-day observation window; 10-day MPOR; maturity parameter 300 days; fixed seeds for prices and default times. Price paths are simulated through the additional MPOR close-out window.

**Important:** These are results from a corrected, stylized implementation of the assignment. They are not directly comparable to the submitted report because timing, collateral and fire-sale accounting conventions were corrected. They are not regulatory estimates.

## Initial margin

The 99% one-sided delta-normal initial margin is **$9,268.39**, using $S_0=100$, $Q=1,000$, annual dollar volatility $\sigma_s=20.00$ and a 10-day MPOR:

\[
IM=z_{0.99}Q\sigma_s\sqrt{MPOR/252}.
\]

## Core scenarios

| Scenario | Investor default | Liquidity default | Paths with fire sales | Mean fire-sale cost / path | Mean dealer loss | Positive dealer loss | Conditional P99 loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| Unlimited cash, daily VM | 1.03% | 0.00% | 0.00% | $0 | $0.12 | 0.01% | $1,388 |
| Limited cash, daily VM + fire sales | 21.92% | 20.98% | 56.12% | $552.26 | $10.91 | 0.68% | $6,493 |
| Weekly VM (5-day) | 20.39% | 19.45% | 52.83% | $516.29 | $51.12 | 2.29% | $7,766 |
| Eligible illiquid collateral for VM | 3.00% | 1.98% | 0.00% | $0 | $0.61 | 0.05% | $2,168 |

“Default” means exogenous default or failure to meet a modelled margin call during the observation window. “Liquidity default” is the latter component. Dealer loss is close-out exposure after IM and the last successfully settled VM collateral. Conditional P99 is calculated only among simulations with strictly positive dealer losses; the unconditional distribution contains a point mass at zero.

## Policy experiments

### Initial-margin multiplier

| Multiplier $k$ | IM ($) | Investor default | Liquidity default | Fire-sale cost / path | Positive dealer loss | Conditional P99 dealer loss |
|---:|---:|---:|---:|---:|---:|---:|
| 1.0 | $9,268 | 21.92% | 20.98% | $552 | 0.68% | $6,493 |
| 1.5 | $13,903 | 31.41% | 30.55% | $752 | 0.04% | $2,989 |
| 2.0 | $18,537 | 43.65% | 42.88% | $984 | 0.00% | $0 |
| 2.5 | $23,171 | 58.00% | 57.39% | $1,231 | 0.00% | $0 |

Higher IM protects the dealer but consumes more of A's cash, increases fire-sale needs and raises liquidity-driven default. A zero positive-loss observation in this finite simulation is not proof of zero underlying risk.

### MPOR

| MPOR | IM ($) | Investor default | Liquidity default | Fire-sale cost / path | Positive dealer loss | Conditional P99 dealer loss |
|---:|---:|---:|---:|---:|---:|---:|
| 10 days | $9,268 | 21.92% | 20.98% | $552 | 0.68% | $6,493 |
| 5 days | $6,554 | 17.86% | 16.89% | $453 | 0.86% | $5,298 |
| 3 days | $5,077 | 15.62% | 14.66% | $405 | 1.22% | $4,579 |

Shorter MPOR reduces IM and leaves more liquidity available to A. That benefit must be considered alongside dealer close-out exposure, which can increase as the collateral horizon shortens.

## Procyclical IM and systemic feedback

The procyclical experiment compares fixed through-the-cycle IM using 15% annual volatility with dynamic IM moving between 15% and 30% after daily price declines beyond 2% of $S_0$.

| Measure | Fixed 15% IM | Dynamic 15%/30% IM |
|---|---:|---:|
| Investor default | 8.97% | 14.16% |
| Liquidity default | 7.97% | 13.18% |
| Mean fire-sale cost / path | $300.79 | $452.99 |
| Mean dealer loss | $6.52 | $17.52 |

The high-volatility state accounts for 1.96% of path-days. Under this parameterization, dynamic spot IM increases investor defaults relative to fixed through-the-cycle IM.

The systemic extension sets $h_t=h_0(1+\theta f_{t-1})$, where $f_{t-1}$ is the fraction of investors fire-selling in the previous period, with a 50% cap. The recorded run gives mean effective haircut 10.46%, maximum 10.72%, and default frequency 22.06%, versus 21.92% under the fixed-haircut baseline. This modest change is specific to the chosen parameters and does not imply the absence of systemic feedback.

## Interpretation and limitations

- Price evolution is arithmetic Brownian motion with zero drift and constant dollar volatility, as specified in the assignment. It may generate negative prices in sufficiently extreme paths; this is a stylized short-horizon assumption.
- Annual default probability is converted into a constant daily hazard so the one-year cumulative probability equals the selected annual PD.
- On a default day, no new VM is exchanged. Dealer collateral includes IM held and the last successfully settled VM balance.
- The observation window is 252 trading days, as stated in the assignment. An additional MPOR segment is simulated only to complete close-out for defaults near the end of the window; contractual maturity is set to 300 days.
- Fire-sale cost is booked on assets actually sold. If available assets are insufficient, remaining assets are sold and the investor defaults with the residual margin call unpaid.
- The eligible-collateral experiment assumes haircut-adjusted value is stable through close-out. It omits collateral market-value volatility and wrong-way risk.
- Defaults are independent across investors; the systemic extension links haircuts through aggregate sales, but not asset-price returns or counterparty defaults.
- These are one-seed Monte Carlo estimates. Sampling error, parameter risk and structural model risk remain material. They are not empirically calibrated default probabilities or regulatory capital estimates.