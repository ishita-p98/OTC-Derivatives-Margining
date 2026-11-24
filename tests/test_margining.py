from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.otc_margining import ModelConfig,simulate_prices,simulate_default_days,simulate_liquidity


def test_initial_margin_matches_delta_normal_formula():
    cfg=ModelConfig(paths=1000)
    expected=2.3263478740408408*cfg.position*20.0*np.sqrt(10/252)
    assert abs(cfg.initial_margin()-expected)<1e-8


def test_daily_default_probability_aggregates_to_annual_pd():
    cfg=ModelConfig(paths=200000)
    assert abs(1-(1-cfg.daily_pd)**cfg.trading_days-cfg.annual_pd)<1e-10
    observed=np.mean(simulate_default_days(cfg,seed=123)<=cfg.horizon)
    assert abs(observed-cfg.annual_pd)<.003


def test_price_paths_include_full_mpor_closeout_extension():
    cfg=ModelConfig(paths=50,horizon=252,mpor=10)
    assert simulate_prices(cfg,seed=10).shape==(50,263)


def test_unlimited_cash_has_no_liquidity_defaults():
    cfg=ModelConfig(paths=2000)
    result=simulate_liquidity(simulate_prices(cfg),simulate_default_days(cfg),cfg,mode="unlimited")
    assert result["liquidity_default"].sum()==0
    assert np.all(result["defaulted"]==(simulate_default_days(cfg)<=cfg.horizon))


def test_fire_sale_cost_is_nonnegative_and_only_when_assets_sold():
    cfg=ModelConfig(paths=5000)
    result=simulate_liquidity(simulate_prices(cfg),simulate_default_days(cfg),cfg,mode="fire_sale")
    assert np.all(result["fire_sale_cost"]>=0)
    assert np.all((result["fire_sale_cost"]==0)|(result["fire_sale_events"]>0))
    assert np.all(result["losses"]>=0)


def test_eligible_collateral_policy_has_no_fire_sale_cost():
    cfg=ModelConfig(paths=3000)
    result=simulate_liquidity(simulate_prices(cfg),simulate_default_days(cfg),cfg,mode="eligible_collateral")
    assert np.all(result["fire_sale_cost"]==0)
    assert np.all(result["eligible_collateral_effective"]>=0)


def test_insufficient_inception_resources_trigger_default():
    cfg=ModelConfig(paths=1000,initial_cash=1000,illiquid_assets=100)
    result=simulate_liquidity(simulate_prices(cfg),simulate_default_days(cfg),cfg,mode="fire_sale")
    assert np.all(result["default_day"]==0)


def test_systemic_haircut_is_lagged_and_capped():
    cfg=ModelConfig(paths=2500)
    result=simulate_liquidity(simulate_prices(cfg),simulate_default_days(cfg),cfg,mode="fire_sale",systemic_h0=.10,systemic_theta=2)
    h=result["systemic_haircut_path"]
    assert h[0]==.10
    assert np.nanmax(h)<=.50
    assert np.nanmin(h)>=.10
    assert np.nanmax(h)>.10
