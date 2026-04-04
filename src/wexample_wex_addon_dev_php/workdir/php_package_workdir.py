from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_helpers.helpers.string import string_to_pascal_case
from wexample_helpers_git.helpers.git import (
    git_tag_annotated,
    git_tag_exists,
)
from wexample_wex_addon_app.workdir.framework_packages_suite_workdir import (
    FrameworkPackageSuiteWorkdir,
)
from wexample_wex_addon_app.workdir.mixin.with_runner_workdir_mixin import (
    WithRunnerWorkdirMixin,
)

from wexample_wex_addon_dev_php.workdir.php_workdir import PhpWorkdir

if TYPE_CHECKING:
    from wexample_filestate.config_value.readme_content_config_value import (
        ReadmeContentConfigValue,
    )
    from wexample_filestate.utils.search_result import SearchResult
    from wexample_runner.runner_config import RunnerConfig


class PhpPackageWorkdir(WithRunnerWorkdirMixin, PhpWorkdir):
    def get_runners(self) -> dict[str, RunnerConfig]:
        from pathlib import Path

        from wexample_helpers.helpers.shell import shell_run
        from wexample_runner.runner_config import RunnerConfig

        git_root = shell_run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=self.get_path(),
            capture=True,
        ).stdout.strip()

        dockerfile_path = (
            Path(__file__).parent.parent / "resources" / "docker" / "Dockerfile.roave"
        )

        return {
            "roave": RunnerConfig(
                dockerfile=dockerfile_path,
                image_name="wex-php-roave",
                mount_path=git_root,
                container_workdir="/var/www/html",
                ephemeral=False,
            )
        }

    def _classify_version_bump(self, last_tag: str) -> str:
        from wexample_helpers.const.types import (
            UPGRADE_TYPE_INTERMEDIATE,
            UPGRADE_TYPE_MAJOR,
            UPGRADE_TYPE_MINOR,
        )
        from wexample_helpers_git.helpers.git import git_has_changes_since_tag

        if not git_has_changes_since_tag(last_tag, "src", cwd=self.get_path()):
            return UPGRADE_TYPE_MINOR

        try:
            package_rel = str(
                self.get_path().resolve().relative_to(
                    self.get_runners()["roave"].mount_path
                )
            )

            self.log(f"Running roave backward compatibility check from {last_tag}...")
            result = self.runner_exec(
                "roave",
                f"cd /var/www/html/{package_rel} && roave-backward-compatibility-check --from={last_tag}",
            )

            if result.is_success():
                self.log("No breaking changes detected.")
                return UPGRADE_TYPE_INTERMEDIATE
            else:
                self.log(f"Breaking changes detected.")
                return UPGRADE_TYPE_MAJOR

        except Exception as e:
            self.log(f"Breaking changes detected: {e}")
            return UPGRADE_TYPE_MAJOR

    def _get_critical_directories(self) -> list[str]:
        return ["src"]

    def get_package_import_name(self) -> str:
        """Get the full package import name with vendor prefix."""
        return f"{string_to_pascal_case(self.get_vendor_name())}\\{string_to_pascal_case(self.get_project_name())}"

    def search_imports_in_codebase(
        self, searched_package: PhpPackageWorkdir
    ) -> list[SearchResult]:
        """Find PHP `use`/qualified references to the given package."""
        import re

        pkg = re.escape(searched_package.get_package_import_name())
        pattern = rf"(?m)^\s*use\s+{pkg}(?:\\\\[\w]+)*\s*;|{pkg}(?:\\\\[\w]+)*"
        return self.search_in_codebase(pattern, regex=True, flags=re.MULTILINE)

    def search_in_codebase(
        self, string: str, *, regex: bool = False, flags: int = 0
    ) -> list[SearchResult]:
        from wexample_filestate.utils.search_result import SearchResult
        from wexample_filestate_php.file.php_file import PhpFile

        found: list[SearchResult] = []

        def _search(item: PhpFile) -> None:
            found.extend(
                SearchResult.create_for_all_matches(
                    string, item, regex=regex, flags=flags
                )
            )

        self.for_each_child_of_type_recursive(callback=_search, class_type=PhpFile)

        return found

    def _get_readme_content(self) -> ReadmeContentConfigValue | None:
        from wexample_wex_addon_dev_php.config_value.php_package_readme_config_value import (
            PhpPackageReadmeContentConfigValue,
        )

        return PhpPackageReadmeContentConfigValue(workdir=self)

    def _get_suite_workdir_class(self) -> type[FrameworkPackageSuiteWorkdir]:
        from wexample_wex_addon_dev_php.workdir.php_packages_suite_workdir import (
            PhpPackagesSuiteWorkdir,
        )

        return PhpPackagesSuiteWorkdir

    def _publish(self, force: bool = False) -> None:
        """Add a Packagist-friendly tag (vX.Y.Z) in addition to default tagging."""
        tag = f"v{self.get_project_version()}"
        cwd = self.get_path()

        if git_tag_exists(tag, cwd=cwd, inherit_stdio=False):
            self.log(f"Tag {tag} already exists, skipping creation.")
        else:
            git_tag_annotated(tag, f"Release {tag}", cwd=cwd, inherit_stdio=True)

        # Uses git repo to deploy packages.
        self.push_to_deployment_remote()
