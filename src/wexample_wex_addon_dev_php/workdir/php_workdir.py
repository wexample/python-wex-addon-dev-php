from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate_php.option.php.phpcs_fixer_option import PhpcsFixerOption
from wexample_helpers.decorator.base_class import base_class
from wexample_wex_addon_ai.workdir.mixin.with_ai_workdir_mixin import (
    WithAiWorkdirMixin,
)
from wexample_wex_addon_app.workdir.code_base_workdir import CodeBaseWorkdir

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig
    from wexample_config.options_provider.abstract_options_provider import (
        AbstractOptionsProvider,
    )
    from wexample_filestate.option.children_file_factory_option import (
        ChildrenFileFactoryOption,
    )

    from wexample_wex_addon_dev_php.file.php_composer_json_file import (
        PhpComposerJsonFile,
    )


@base_class
class PhpWorkdir(WithAiWorkdirMixin, CodeBaseWorkdir):
    def get_app_config_file(self, reload: bool = True) -> PhpComposerJsonFile:
        from wexample_wex_addon_dev_php.file.php_composer_json_file import (
            PhpComposerJsonFile,
        )

        config_file = self.find_by_type(PhpComposerJsonFile)
        # Read once to populate content with file source.
        config_file.read_text(reload=reload)
        return config_file

    def get_dependencies_versions(self) -> dict[str, str]:
        return self.get_app_config_file().get_dependencies_versions()

    def get_main_code_file_extension(self) -> str:
        from wexample_filestate_php.const.php_file import PHP_FILE_EXTENSION

        return PHP_FILE_EXTENSION

    def get_options_providers(self) -> list[type[AbstractOptionsProvider]]:
        from wexample_filestate_php.options_provider.php_options_provider import (
            PhpOptionsProvider,
        )

        options = super().get_options_providers()

        options.append(PhpOptionsProvider)

        return options

    def get_package_name(self) -> str:
        from wexample_helpers.helper.string import string_to_kebab_case

        return f"{string_to_kebab_case(self.get_vendor_name())}/{string_to_kebab_case(self.get_project_name())}"

    def has_tests(self) -> bool:
        # Only real PHPUnit test classes count; the tests/ directory itself
        # may be empty scaffolding.
        tests_path = self.get_path() / "tests"
        if not tests_path.is_dir():
            return False
        return any(tests_path.rglob("*Test.php"))

    def prepare_value(self, raw_value: DictConfig | None = None) -> DictConfig:
        from wexample_filestate.const.disk import DiskItemType

        from wexample_wex_addon_dev_php.file.php_composer_json_file import (
            PhpComposerJsonFile,
        )

        raw_value = super().prepare_value(raw_value=raw_value)

        self.append_agents(config=raw_value)

        # Ensure a composer.json file exists for any PHP package project
        children = raw_value["children"]

        children.append(
            {
                "class": PhpComposerJsonFile,
                "name": "composer.json",
                "type": DiskItemType.FILE,
                "should_exist": True,
            }
        )

        self.add_gitignore_rules(
            children,
            ".php-cs-fixer.cache",
            ".scannerwork",
            "/vendor",
            section="PHP",
        )

        children.extend(
            [
                {
                    "name": "tests",
                    "type": DiskItemType.DIRECTORY,
                    "should_exist": True,
                    "children": [
                        self._create_php_file_children_filter(),
                    ],
                },
                {
                    "name": "src",
                    "type": DiskItemType.DIRECTORY,
                    "should_exist": True,
                    "children": [
                        self._create_php_file_children_filter(),
                    ],
                },
            ]
        )

        return raw_value

    def test_run(self, format: str | None = None) -> None:
        phpunit = self.get_path() / "vendor" / "bin" / "phpunit"
        if not phpunit.exists():
            raise RuntimeError(
                f"{self.get_package_name()} has tests but vendor/bin/phpunit "
                "is missing; run composer install in the package."
            )
        self.shell_run_for_app(cmd=[str(phpunit)])

    def _create_php_file_children_filter(self) -> ChildrenFileFactoryOption:
        from wexample_filestate.const.disk import DiskItemType
        from wexample_filestate.option.children_filter_option import (
            ChildrenFilterOption,
        )
        from wexample_filestate_php.file.php_file import PhpFile

        return ChildrenFilterOption(
            pattern={
                "class": PhpFile,
                "type": DiskItemType.FILE,
                "php": [PhpcsFixerOption.get_name()],
            },
            name_pattern=r"^.*\.php$",
            recursive=True,
        )
