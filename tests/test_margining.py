import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.otc_margining import (
    ModelConfig, simulate_default_days, simulate_liquidity, simulate_prices
)


def test_initial_margin_is_delta_normal_var():
    cfg = ModelConfig(paths=100)
    expected = 2.3263478740408408 * cfg.position * 20.0 * np.sqrt(10 / 252)
    assert np.isclose(cfg.initial_margin(), expected)


def test_default_intensity_matches_annual_probability():
    cfg = ModelConfig(paths=100)
    assert np.isclose(1 - (1 - cfg.daily_pd) ** cfg.trading_days, cfg.annual_pd)


def test_price_simulation_contains_observation_and_mpor_days():
    cfg = ModelConfig(paths=20, horizon=252, mpor=10)
    assert simulate_prices(cfg, seed=7).shape == (20, 263)


def test_basic_simulation_outputs_are_well_formed():
    cfg = ModelConfig(paths=500, horizon=40, mpor=10)
    prices = simulate_prices(cfg, seed=11)
    default_days = simulate_default_days(cfg, seed=12)
    for mode in ("unlimited", "fire_sale", "eligible_collateral"):
        result = simulate_liquidity(prices, default_days, cfg, mode=mode)
        assert result["defaulted"].shape == (cfg.paths,)
        assert result["losses"].shape == (cfg.paths,)
        assert np.all(result["losses"] >= 0)
        assert np.all(result["fire_sale_cost"] >= 0)
    eligible = simulate_liquidity(prices, default_days, cfg, mode="eligible_collateral")
    assert np.all(eligible["fire_sale_cost"] == 0)


def test_all_project_notebooks_are_valid_json():
    notebook_dir = ROOT / "notebooks"
    paths = sorted(notebook_dir.glob("*.ipynb"))
    assert len(paths) == 5
    for path in paths:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        assert notebook["nbformat"] >= 4
        assert notebook["cells"]
