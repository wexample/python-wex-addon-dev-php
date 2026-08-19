from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.common.abstract_addon_manager import AbstractAddonManager

if TYPE_CHECKING:
    from typing import Any


class PhpAddonManager(AbstractAddonManager):
    @classmethod
    def get_package_module(cls) -> Any:
        import wexample_wex_addon_dev_php

        return wexample_wex_addon_dev_php

    def get_workdir_types(self) -> dict[str, type]:
        from wexample_wex_addon_dev_php.workdir.php_package_workdir import (
            PhpPackageWorkdir,
        )
        from wexample_wex_addon_dev_php.workdir.php_packages_suite_workdir import (
            PhpPackagesSuiteWorkdir,
        )
        from wexample_wex_addon_dev_php.workdir.php_symfony_workdir import (
            PhpSymfonyWorkdir,
        )
        from wexample_wex_addon_dev_php.workdir.php_workdir import PhpWorkdir

        return {
            "php": PhpWorkdir,
            "php-package": PhpPackageWorkdir,
            "php-packages-suite": PhpPackagesSuiteWorkdir,
            "php-symfony": PhpSymfonyWorkdir,
        }
