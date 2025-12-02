from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_helpers.helpers.string import string_to_pascal_case
from wexample_helpers_git.helpers.git import (
    git_tag_exists,
    git_tag_annotated,
)
from wexample_wex_addon_app.workdir.framework_packages_suite_workdir import (
    FrameworkPackageSuiteWorkdir,
)
from wexample_wex_addon_dev_php.workdir.php_workdir import PhpWorkdir

if TYPE_CHECKING:
    from wexample_filestate.config_value.readme_content_config_value import (
        ReadmeContentConfigValue,
    )


class PhpPackageWorkdir(PhpWorkdir):
    def _get_readme_content(self) -> ReadmeContentConfigValue | None:
        from wexample_wex_addon_dev_php.config_value.php_package_readme_config_value import (
            PhpPackageReadmeContentConfigValue,
        )

        return PhpPackageReadmeContentConfigValue(workdir=self)

    def _get_suite_package_workdir_class(self) -> type[FrameworkPackageSuiteWorkdir]:
        from wexample_wex_addon_dev_php.workdir.php_packages_suite_workdir import (
            PhpPackagesSuiteWorkdir,
        )

        return PhpPackagesSuiteWorkdir

    def get_package_import_name(self) -> str:
        """Get the full package import name with vendor prefix."""
        return f"{string_to_pascal_case(self.get_vendor_name())}\\{string_to_pascal_case(self.get_project_name())}"

    def _publish(self, force: bool = False) -> None:
        """Add a Packagist-friendly tag (vX.Y.Z) in addition to default tagging."""
        tag = f"v{self.get_project_version()}"
        cwd = self.get_path()

        if git_tag_exists(tag, cwd=cwd, inherit_stdio=False) and not force:
            self.log(f"Tag {tag} already exists, skipping creation (use --force to re-tag).")
        else:
            git_tag_annotated(tag, f"Release {tag}", cwd=cwd, inherit_stdio=True)

        # Uses git repo to deploy packages.
        self.push_changes(
            remote_name=self.search_app_or_suite_runtime_config(
                "php.packagist.deployment_remote_name",
                default=None
            ).get_str_or_none()
        )

    def get_package_name(self) -> str:
        from wexample_helpers.helpers.string import string_to_kebab_case

        return f"{string_to_kebab_case(self.get_vendor_name())}/{string_to_kebab_case(self.get_project_name())}"
