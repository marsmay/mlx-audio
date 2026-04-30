import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: requires MLX models, takes 30s+")
