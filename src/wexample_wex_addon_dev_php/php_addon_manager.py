from __future__ import annotations

from typing import Any

from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager


class PhpAddonManager(AbstractAddonManager):
    @classmethod
    def get_package_module(cls) -> Any:
        import wexample_wex_addon_dev_php

        return wexample_wex_addon_dev_php
