# Model methodology

## Contract and mark-to-market

Institution A is long a forward on an asset, with position size $Q$ and strike $K$. The assignment defines $V_t=Q(S_t-K)$. Institution B is the always-solvent dealer. A can default exogenously, and in the augmented model can also default after exhausting liquidity.

## Price process and initial margin

The underlying follows arithmetic Brownian motion:

\[
\Delta S_t=\sigma_s\sqrt{\Delta t}Z_t,\qquad Z_t\sim N(0,1).
\]

Therefore, the MTM change has standard deviation $Q\sigma_s\sqrt{\Delta t}$. For one-sided confidence level $\alpha=99\%$:

\[
IM=z_{0.99}Q\sigma_s\sqrt{MPOR/252}.
\]

With $S_0=K=100$, $Q=1,000$, annual dollar volatility $\sigma_s=20$ and MPOR 10 days, the computed IM is $9,268.39.

## Exogenous default

Given annual default probability $PD$, annual intensity is $\lambda=-\ln(1-PD)$. Daily event probability is $1-\exp(-\lambda/252)$. A geometric waiting-time draw simulates the first exogenous default day.

## Variation margin and liquidity

At each VM settlement date, the change in MTM since the last successful settlement is exchanged. If A owes VM, cash is used first. In the fire-sale model, any remaining shortfall is met by selling gross asset value $x=shortfall/(1-h)$, so realized deadweight cost is $hx$. If remaining assets cannot cover the shortfall, A defaults and all remaining assets are sold. Failed margin calls are not treated as settled collateral.

In the eligible-collateral policy, illiquid assets can be pledged to meet VM shortfalls with haircut $h_{col}$; the collateral is returned when the VM liability subsequently reduces. The model assumes the haircut-adjusted value of pledged assets is stable through close-out.

## Dealer close-out loss

If A defaults at day $t$, the position closes at $t+MPOR$. Price paths are extended by MPOR days so close-out is observed even for defaults near the end of the 252-day observation window. The last successful VM settlement is the collateral balance at default. For a long investor, the investor-posted amount is $\max(-V_{last},0)$. Dealer loss is:

\[
L_B=\max\{0,-V_{t+MPOR}-IM_{held}-\max(-V_{last},0)\}.
\]

## Policy and systemic extensions

The implementation compares IM multipliers $k$, daily versus five-day VM, MPOR values 10/5/3 days, and eligible illiquid collateral. A procyclical experiment compares fixed 15% through-the-cycle IM with dynamic IM based on 15%/30% volatility regimes. The systemic extension changes the fire-sale discount to:

\[
h_t=\min(h_0(1+\theta f_{t-1}),50\%),
\]

where $f_{t-1}$ is the previous day's fraction of investors forced to sell assets.