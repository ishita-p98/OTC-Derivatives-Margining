"""Stylized OTC derivatives margining simulation.

Arithmetic-Brownian prices, exogenous investor default, daily/weekly VM,
fire sales, eligible illiquid collateral, MPOR close-out, procyclical IM and
lagged system-wide fire-sale discounts. Educational model only.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Optional
import numpy as np


@dataclass(frozen=True)
class ModelConfig:
    s0: float = 100.0
    strike: float = 100.0
    position: float = 1000.0
    annual_vol: float = 0.20
    annual_pd: float = 0.01
    initial_cash: float = 20000.0
    illiquid_assets: float = 15000.0
    fire_sale_haircut: float = 0.10
    collateral_haircut: float = 0.10
    mpor: int = 10
    horizon: int = 252
    maturity: int = 300
    trading_days: int = 252
    confidence: float = 0.99
    paths: int = 100000
    seed: int = 42

    @property
    def dt(self):
        return 1.0 / self.trading_days

    @property
    def sigma_dollar(self):
        return self.annual_vol * self.s0

    @property
    def daily_pd(self):
        intensity = -np.log1p(-self.annual_pd)
        return float(1.0 - np.exp(-intensity / self.trading_days))

    def initial_margin(self, mpor=None, multiplier=1.0, annual_vol=None):
        m = self.mpor if mpor is None else int(mpor)
        vol = self.annual_vol if annual_vol is None else float(annual_vol)
        z = 2.3263478740408408
        return float(multiplier*z*self.position*(vol*self.s0)*np.sqrt(m/self.trading_days))


def simulate_prices(cfg, seed=None, horizon=None, extra_days=None, regime_switch=False,
                    drop_trigger=-0.02, low_vol=0.15, high_vol=0.30):
    """Return paths [n_paths, horizon + extra_days + 1]; extra days cover MPOR close-out."""
    rng=np.random.default_rng(cfg.seed if seed is None else seed)
    h=cfg.horizon if horizon is None else int(horizon)
    e=cfg.mpor if extra_days is None else int(extra_days)
    n_days=h+e
    prices=np.empty((cfg.paths,n_days+1),dtype=np.float32)
    prices[:,0]=cfg.s0
    vols=np.full((cfg.paths,n_days+1),cfg.annual_vol,dtype=np.float32) if regime_switch else None
    for t in range(n_days):
        if regime_switch:
            v=vols[:,t].astype(np.float64)
            ds=v*cfg.s0*np.sqrt(cfg.dt)*rng.standard_normal(cfg.paths)
            prices[:,t+1]=prices[:,t]+ds
            vols[:,t+1]=np.where(ds/cfg.s0<drop_trigger,high_vol,low_vol)
        else:
            ds=cfg.sigma_dollar*np.sqrt(cfg.dt)*rng.standard_normal(cfg.paths)
            prices[:,t+1]=prices[:,t]+ds
    return (prices,vols) if regime_switch else prices


def simulate_default_days(cfg,seed=None):
    """First exogenous default day (1-indexed); horizon+1 means no default."""
    rng=np.random.default_rng(cfg.seed+1 if seed is None else seed)
    d=rng.geometric(cfg.daily_pd,size=cfg.paths)
    return np.where(d<=cfg.horizon,d,cfg.horizon+1).astype(np.int32)


def _closeout_losses(values,default_day,last_vm_value,im_held,mpor,horizon):
    idx=np.minimum(default_day+mpor,values.shape[1]-1)
    closeout_value=values[np.arange(values.shape[0]),idx]
    vm_collateral=np.maximum(-last_vm_value,0.0)
    loss=np.maximum(0.0,-closeout_value-vm_collateral-im_held)
    loss=np.where(default_day<=horizon,loss,0.0)
    return loss,closeout_value,vm_collateral


def summarize_losses(losses):
    positive=losses[losses>0]
    return {
        "probability_positive_loss":float(np.mean(losses>0)),
        "mean_unconditional_loss":float(np.mean(losses)),
        "mean_conditional_loss":float(positive.mean()) if positive.size else 0.0,
        "conditional_p95":float(np.quantile(positive,.95)) if positive.size else 0.0,
        "conditional_p99":float(np.quantile(positive,.99)) if positive.size else 0.0,
        "maximum_loss":float(losses.max(initial=0.0)),
    }


def simulate_liquidity(prices,exogenous_default_day,cfg,*,im_multiplier=1.0,mpor=None,
                       vm_frequency=1,mode="fire_sale",collateral_haircut=None,
                       systemic_h0=None,systemic_theta=0.0,volatility_states=None):
    """Pathwise settlement, liquidity/default and close-out simulation.

    On default day no VM is exchanged. Collateral at default is IM held plus
    the last successfully settled VM balance; failed margin calls are not collateral.
    """
    if mode not in {"unlimited","fire_sale","eligible_collateral"}:
        raise ValueError("invalid mode")
    if vm_frequency<1: raise ValueError("vm_frequency must be >=1")
    m=cfg.mpor if mpor is None else int(mpor)
    n=prices.shape[0]; horizon=cfg.horizon
    vals=cfg.position*(prices.astype(np.float64)-cfg.strike)
    default_day=np.full(n,horizon+1,dtype=np.int32)
    im0=np.full(n,cfg.initial_margin(m,im_multiplier),dtype=np.float64)
    cash=np.full(n,cfg.initial_cash,dtype=np.float64)
    assets=np.full(n,cfg.illiquid_assets,dtype=np.float64)
    im_held=im0.copy()
    fire_cost=np.zeros(n); fire_events=np.zeros(n,dtype=np.int32)
    eligible_effective=np.zeros(n); eligible_face=np.zeros(n)
    liq_default=np.zeros(n,dtype=bool)
    initial_shortfall=np.maximum(im0-cash,0.0)
    initial_default=np.zeros(n,dtype=bool)
    if mode=="fire_sale" and np.any(initial_shortfall>0):
        gross=initial_shortfall/(1-cfg.fire_sale_haircut)
        sold=np.minimum(gross,assets); proceeds=sold*(1-cfg.fire_sale_haircut)
        fire_cost+=sold*cfg.fire_sale_haircut
        fire_events+=(sold>0).astype(np.int32)
        assets-=sold; cash+=proceeds
        initial_default=proceeds+1e-10<initial_shortfall
    elif mode=="eligible_collateral":
        initial_default=initial_shortfall>1e-10
    if mode=="eligible_collateral": cash-=np.minimum(im0,cfg.initial_cash)
    elif mode=="unlimited": cash=np.maximum(cash-im0,0.0)
    else: cash-=im0
    default_day[initial_default]=0
    liq_default[initial_default]=True
    im_held[initial_default]=0.0
    last_vm_mark=vals[:,0].copy()
    im_topups=np.zeros(n)
    prev_h=cfg.fire_sale_haircut if systemic_h0 is None else systemic_h0
    systemic_haircut_path=np.full(horizon+1,np.nan)
    systemic_haircut_path[0]=prev_h if systemic_h0 is not None else np.nan
    systemic_seller_fraction=np.zeros(horizon+1)

    for t in range(1,horizon+1):
        selling_today=np.zeros(n,dtype=bool)
        new_exog=(exogenous_default_day==t)&(default_day>horizon)
        default_day[new_exog]=t
        active=default_day>horizon
        if not active.any(): break
        required_im=im0
        if volatility_states is not None:
            vol_now=volatility_states[:,t].astype(np.float64)
            required_im=2.3263478740408408*cfg.position*(vol_now*cfg.s0)*np.sqrt(m/cfg.trading_days)
            delta_im=required_im-im_held
        else: delta_im=np.zeros(n)
        is_settlement=(t%vm_frequency==0)
        if not is_settlement and volatility_states is None: continue
        vm_change=vals[:,t]-last_vm_mark
        need_vm=np.where(is_settlement&active&(vm_change<0),-vm_change,0.0)
        receive_vm=is_settlement&active&(vm_change>0)
        cash[receive_vm]+=vm_change[receive_vm]
        if mode=="eligible_collateral" and np.any(receive_vm):
            release_eff=np.minimum(eligible_effective[receive_vm],vm_change[receive_vm])
            hc=cfg.collateral_haircut if collateral_haircut is None else collateral_haircut
            release_face=release_eff/(1-hc)
            ids=np.flatnonzero(receive_vm)
            eligible_effective[ids]-=release_eff
            eligible_face[ids]-=release_face
            assets[ids]+=release_face
        need_im=np.where(active,np.maximum(delta_im,0.0),0.0)
        release_im=np.where(active,np.maximum(-delta_im,0.0),0.0)
        im_topups[active]+=need_im[active]
        cash[active]+=release_im[active]
        demand=need_vm+need_im
        needs_pay=active&(demand>0)
        if needs_pay.any():
            available=cash[needs_pay]; due=demand[needs_pay]
            can_cash=available>=due
            ids=np.flatnonzero(needs_pay)
            cash_ids=ids[can_cash]; cash[cash_ids]-=due[can_cash]
            short_ids=ids[~can_cash]
            if short_ids.size:
                shortfall=due[~can_cash]-available[~can_cash]
                if mode=="unlimited":
                    cash[short_ids]=available[~can_cash]-due[~can_cash]
                elif mode=="eligible_collateral":
                    hc=cfg.collateral_haircut if collateral_haircut is None else collateral_haircut
                    face_needed=shortfall/(1-hc)
                    face_used=np.minimum(face_needed,assets[short_ids])
                    effective=face_used*(1-hc)
                    assets[short_ids]-=face_used
                    eligible_face[short_ids]+=face_used
                    eligible_effective[short_ids]+=effective
                    cash[short_ids]=0.0
                    fail=effective+1e-10<shortfall
                    failed=short_ids[fail]
                    default_day[failed]=t; liq_default[failed]=True
                else:
                    haircut=cfg.fire_sale_haircut if systemic_h0 is None else prev_h
                    gross=shortfall/(1-haircut)
                    sold=np.minimum(gross,assets[short_ids])
                    proceeds=sold*(1-haircut)
                    fire_cost[short_ids]+=sold*haircut
                    fire_events[short_ids]+=(sold>0).astype(np.int32)
                    assets[short_ids]-=sold
                    selling_today[short_ids]=sold>0
                    cash[short_ids]=0.0
                    fail=proceeds+1e-10<shortfall
                    failed=short_ids[fail]
                    default_day[failed]=t; liq_default[failed]=True
                successful=active.copy()
                successful[short_ids]=~((default_day[short_ids]==t)&liq_default[short_ids])
                if volatility_states is not None: im_held[successful]=required_im[successful]
                if is_settlement: last_vm_mark[successful]=vals[successful,t]
        else:
            if is_settlement: last_vm_mark[active]=vals[active,t]
            if volatility_states is not None: im_held[active]=required_im[active]
        if systemic_h0 is not None:
            frac=float(np.mean(selling_today))
            systemic_seller_fraction[t]=frac
            prev_h=min(systemic_h0*(1+systemic_theta*frac),.50)
            systemic_haircut_path[t]=prev_h

    losses,closeout_value,vm_collateral=_closeout_losses(vals,default_day,last_vm_mark,im_held,m,horizon)
    return {
        "default_day":default_day,"defaulted":default_day<=horizon,"liquidity_default":liq_default,
        "cash_end":cash,"illiquid_assets_end":assets,"fire_sale_cost":fire_cost,
        "fire_sale_events":fire_events,"eligible_collateral_face":eligible_face,
        "eligible_collateral_effective":eligible_effective,"im_held_at_end":im_held,
        "last_vm_mark":last_vm_mark,"vm_collateral_at_default":vm_collateral,
        "closeout_value":closeout_value,"losses":losses,"im_topups_total":im_topups,
        "systemic_haircut_path":systemic_haircut_path,"systemic_seller_fraction":systemic_seller_fraction,
    }


def summarize_simulation(result,cfg):
    out={
        "default_rate":float(np.mean(result["defaulted"])),
        "liquidity_default_rate":float(np.mean(result["liquidity_default"])),
        "fire_sale_path_rate":float(np.mean(result["fire_sale_events"]>0)),
        "mean_fire_sale_cost_per_path":float(np.mean(result["fire_sale_cost"])),
        "mean_fire_sale_cost_per_selling_path":float(result["fire_sale_cost"][result["fire_sale_cost"]>0].mean()) if np.any(result["fire_sale_cost"]>0) else 0.0,
        "mean_fire_sale_events_per_path":float(np.mean(result["fire_sale_events"])),
        "mean_dealer_loss":float(np.mean(result["losses"])),
        "p99_dealer_loss_unconditional":float(np.quantile(result["losses"],.99)),
    }
    out.update(summarize_losses(result["losses"]))
    hp=result.get("systemic_haircut_path")
    if hp is not None and np.isfinite(hp).any():
        out["mean_systemic_haircut"]=float(np.nanmean(hp))
        out["max_systemic_haircut"]=float(np.nanmax(hp))
        out["mean_daily_seller_fraction"]=float(np.mean(result["systemic_seller_fraction"][1:]))
    return out


def theoretical_initial_margin(cfg,mpor=None,multiplier=1.0,annual_vol=None):
    return cfg.initial_margin(mpor=mpor,multiplier=multiplier,annual_vol=annual_vol)


def to_config_dict(cfg):
    return asdict(cfg)
