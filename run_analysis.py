from __future__ import annotations
import json
from dataclasses import replace
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from src.otc_margining import ModelConfig,simulate_prices,simulate_default_days,simulate_liquidity,summarize_simulation

OUT=ROOT/"outputs"; FIG=ROOT/"figures"
for folder in (OUT,FIG): folder.mkdir(parents=True,exist_ok=True)

cfg=ModelConfig(paths=20000,horizon=252,maturity=300,mpor=10,seed=42)
prices=simulate_prices(cfg,seed=100,extra_days=cfg.mpor)
exog_default_day=simulate_default_days(cfg,seed=200)

results={}; scenarios={}
for name,kwargs in [
    ("unlimited_cash_daily_vm",{"mode":"unlimited"}),
    ("fire_sale_daily_vm",{"mode":"fire_sale"}),
    ("weekly_vm",{"mode":"fire_sale","vm_frequency":5}),
    ("eligible_illiquid_vm_collateral",{"mode":"eligible_collateral"}),
]:
    result=simulate_liquidity(prices,exog_default_day,cfg,**kwargs)
    scenarios[name]=result
    results[name]=summarize_simulation(result,cfg)
    results[name]["exogenous_default_rate"]=float(np.mean(exog_default_day<=cfg.horizon))

im_rows=[]
for k in [1.0,1.5,2.0,2.5]:
    result=simulate_liquidity(prices,exog_default_day,cfg,mode="fire_sale",im_multiplier=k)
    sm=summarize_simulation(result,cfg)
    im_rows.append({"IM multiplier":k,"IM ($)":cfg.initial_margin(multiplier=k),
                    "Default rate":sm["default_rate"],"Liquidity default rate":sm["liquidity_default_rate"],
                    "Fire-sale cost/path":sm["mean_fire_sale_cost_per_path"],
                    "Positive-loss probability":sm["probability_positive_loss"],
                    "Dealer mean loss":sm["mean_dealer_loss"],"Conditional dealer P99 loss":sm["conditional_p99"]})

mpor_rows=[]
for m in [10,5,3]:
    p_m=simulate_prices(cfg,seed=100,extra_days=m)
    result=simulate_liquidity(p_m,exog_default_day,cfg,mode="fire_sale",mpor=m)
    sm=summarize_simulation(result,cfg)
    mpor_rows.append({"MPOR (days)":m,"IM ($)":cfg.initial_margin(mpor=m),
                      "Default rate":sm["default_rate"],"Liquidity default rate":sm["liquidity_default_rate"],
                      "Fire-sale cost/path":sm["mean_fire_sale_cost_per_path"],
                      "Positive-loss probability":sm["probability_positive_loss"],
                      "Dealer mean loss":sm["mean_dealer_loss"],"Conditional dealer P99 loss":sm["conditional_p99"]})

reg_cfg=replace(cfg,annual_vol=.15)
reg_prices,vol_states=simulate_prices(reg_cfg,seed=300,extra_days=cfg.mpor,regime_switch=True,low_vol=.15,high_vol=.30)
reg_defaults=simulate_default_days(cfg,seed=200)
fixed=simulate_liquidity(reg_prices,reg_defaults,reg_cfg,mode="fire_sale")
dynamic=simulate_liquidity(reg_prices,reg_defaults,reg_cfg,mode="fire_sale",volatility_states=vol_states)
results["procyclical_fixed_15pct_IM"]=summarize_simulation(fixed,reg_cfg)
results["procyclical_dynamic_IM"]=summarize_simulation(dynamic,reg_cfg)
results["procyclical_dynamic_IM"]["high_vol_day_share"]=float(np.mean(vol_states[:,:cfg.horizon+1]>=.30))
results["procyclical_dynamic_IM"]["mean_im_held_at_end"]=float(np.mean(dynamic["im_held_at_end"]))

systemic=simulate_liquidity(prices,exog_default_day,cfg,mode="fire_sale",systemic_h0=.10,systemic_theta=2.0)
results["systemic_haircut"]=summarize_simulation(systemic,cfg)

summary={"configuration":{"paths":cfg.paths,"observation_horizon_days":cfg.horizon,
    "contract_maturity_days":cfg.maturity,"mpor_days":cfg.mpor,"seed_prices":100,
    "seed_default_times":200,"S0":cfg.s0,"K":cfg.strike,"Q":cfg.position,
    "annual_volatility":cfg.annual_vol,"annual_exogenous_PD":cfg.annual_pd,
    "initial_cash":cfg.initial_cash,"illiquid_assets":cfg.illiquid_assets,
    "fire_sale_haircut":cfg.fire_sale_haircut,"initial_margin_99pct":cfg.initial_margin()},
    "scenarios":results,"initial_margin_policy":im_rows,"mpor_policy":mpor_rows}
(OUT/"simulation_summary.json").write_text(json.dumps(summary,indent=2))
pd.DataFrame(im_rows).to_csv(OUT/"initial_margin_policy.csv",index=False)
pd.DataFrame(mpor_rows).to_csv(OUT/"mpor_policy.csv",index=False)
rows=[{"Scenario":key,**{k:v for k,v in sm.items() if isinstance(v,(int,float))}} for key,sm in results.items()]
pd.DataFrame(rows).to_csv(OUT/"scenario_summary.csv",index=False)

plt.rcParams.update({"font.size":10,"axes.titleweight":"bold","figure.dpi":130})
days=np.arange(cfg.horizon+1)
fig,ax=plt.subplots(figsize=(9,4.6))
for i in range(45): ax.plot(days,prices[i,:cfg.horizon+1],alpha=.24,lw=.7)
ax.plot(days,prices[:,:cfg.horizon+1].mean(axis=0),lw=2,label="Cross-sectional mean")
ax.axhline(cfg.strike,color="black",ls="--",lw=1,label="Forward strike")
ax.set(xlabel="Trading day",ylabel="Underlying price ($)",title="Arithmetic Brownian motion: sample paths")
ax.legend(frameon=False);fig.tight_layout();fig.savefig(FIG/"01_price_paths.png",bbox_inches="tight");plt.close(fig)

keys=["unlimited_cash_daily_vm","fire_sale_daily_vm","weekly_vm","eligible_illiquid_vm_collateral"]
names=["Unlimited cash","Fire-sale liquidity","Weekly VM","Eligible illiquid VM collateral"]
vals=[results[k]["default_rate"]*100 for k in keys]
fig,ax=plt.subplots(figsize=(8,4.2));bars=ax.bar(names,vals)
ax.set_ylabel("Defaulted paths (%)");ax.set_title("Investor default frequency by margining setup")
ax.tick_params(axis="x",rotation=12)
for bar,value in zip(bars,vals): ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+.5,f"{value:.1f}%",ha="center",fontsize=9)
fig.tight_layout();fig.savefig(FIG/"02_default_frequency.png",bbox_inches="tight");plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.5))
for key,label in [("unlimited_cash_daily_vm","Unlimited cash"),("fire_sale_daily_vm","Fire-sale liquidity")]:
    positive=scenarios[key]["losses"];positive=positive[positive>0]
    if positive.size: ax.hist(positive,bins=45,density=True,alpha=.48,label=label)
ax.set(xlabel="Dealer loss ($), conditional on positive loss",ylabel="Density",title="Dealer loss distribution")
ax.legend(frameon=False);fig.tight_layout();fig.savefig(FIG/"03_dealer_loss_distribution.png",bbox_inches="tight");plt.close(fig)

imdf=pd.DataFrame(im_rows)
fig,ax1=plt.subplots(figsize=(8,4.5))
ax1.plot(imdf["IM multiplier"],100*imdf["Default rate"],marker="o",lw=2,label="Investor default rate")
ax1.set(xlabel="Initial-margin multiplier k",ylabel="Investor default rate (%)",title="Higher initial margin: dealer protection vs investor liquidity")
ax2=ax1.twinx();ax2.plot(imdf["IM multiplier"],imdf["Conditional dealer P99 loss"],marker="s",lw=2,label="Conditional dealer P99 loss")
ax2.set_ylabel("Conditional dealer P99 loss ($)")
l1,l2=ax1.get_legend_handles_labels();r1,r2=ax2.get_legend_handles_labels()
ax1.legend(l1+r1,l2+r2,loc="best",frameon=False);fig.tight_layout();fig.savefig(FIG/"04_initial_margin_tradeoff.png",bbox_inches="tight");plt.close(fig)

mpdf=pd.DataFrame(mpor_rows)
fig,ax1=plt.subplots(figsize=(8,4.5))
ax1.plot(mpdf["MPOR (days)"],100*mpdf["Default rate"],marker="o",lw=2,label="Investor default rate")
ax1.set(xlabel="MPOR (trading days)",ylabel="Investor default rate (%)",title="MPOR, initial margin and liquidity outcomes")
ax2=ax1.twinx();ax2.plot(mpdf["MPOR (days)"],mpdf["IM ($)"],marker="s",lw=2,label="Initial margin")
ax2.set_ylabel("Initial margin ($)")
l1,l2=ax1.get_legend_handles_labels();r1,r2=ax2.get_legend_handles_labels()
ax1.legend(l1+r1,l2+r2,frameon=False);fig.tight_layout();fig.savefig(FIG/"05_mpor_sensitivity.png",bbox_inches="tight");plt.close(fig)

fig,ax=plt.subplots(figsize=(8,4.2))
ax.hist(vol_states[:,:cfg.horizon+1].ravel(),bins=[.10,.20,.25,.35],rwidth=.8)
ax.set(xlabel="Annualized volatility regime",ylabel="Path-days",title="Regime-switching volatility observations")
fig.tight_layout();fig.savefig(FIG/"06_volatility_regimes.png",bbox_inches="tight");plt.close(fig)

values=[results["fire_sale_daily_vm"]["default_rate"]*100,results["systemic_haircut"]["default_rate"]*100]
fig,ax=plt.subplots(figsize=(7,4))
bars=ax.bar(["Fixed 10% haircut","Lagged systemic haircut"],values)
ax.set(ylabel="Investor default rate (%)",title="Systemic fire-sale haircut feedback")
for bar,value in zip(bars,values): ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+.3,f"{value:.2f}%",ha="center")
fig.tight_layout();fig.savefig(FIG/"07_systemic_feedback.png",bbox_inches="tight");plt.close(fig)
print(json.dumps({"IM_99":cfg.initial_margin(),"scenarios":results,"IM_policy":im_rows,"MPOR_policy":mpor_rows},indent=2))
