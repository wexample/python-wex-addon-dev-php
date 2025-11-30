from __future__ import annotations

from wexample_wex_addon_app.workdir.framework_packages_suite_workdir import (
    FrameworkPackageSuiteWorkdir,
)

from wexample_wex_addon_dev_php.workdir.php_workdir import PhpWorkdir


class PhpPackageWorkdir(PhpWorkdir):
    def _get_suite_package_workdir_class(self) -> type[FrameworkPackageSuiteWorkdir]:
        from wexample_wex_addon_dev_php.workdir.php_packages_suite_workdir import (
            PhpPackagesSuiteWorkdir,
        )

        return PhpPackagesSuiteWorkdir
