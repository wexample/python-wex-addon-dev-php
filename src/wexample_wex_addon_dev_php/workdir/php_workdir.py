from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_addon_app.workdir.code_base_workdir import CodeBaseWorkdir

if TYPE_CHECKING:
    from wexample_config.const.types import DictConfig
    from wexample_filestate.option.children_file_factory_option import (
        ChildrenFileFactoryOption,
    )


class PhpWorkdir(CodeBaseWorkdir):
    def get_dependencies(self) -> list[str]:
        # TODO search in composer.json
        return []

    def prepare_value(self, raw_value: DictConfig | None = None) -> DictConfig:
        from wexample_filestate.const.disk import DiskItemType
        from wexample_helpers.helpers.array import array_dict_get_by

        raw_value = super().prepare_value(raw_value=raw_value)

        # Ensure a composer.json file exists for any PHP package project
        children = raw_value["children"]

        children.append(
            {
                "name": "composer.json",
                "type": DiskItemType.FILE,
                "should_exist": True,
            }
        )

        # Add rules to .gitignore
        array_dict_get_by("name", ".gitignore", children).setdefault(
            "should_contain_lines", []
        ).extend(
            [
                ".php-cs-fixer.cache",
                ".scannerwork",
                "/vendor",
            ]
        )

        return raw_value

    def _create_php_file_children_filter(self) -> ChildrenFileFactoryOption:
        from wexample_filestate.const.disk import DiskItemType
        from wexample_filestate.option.children_filter_option import (
            ChildrenFilterOption,
        )
        from wexample_filestate_php.file.php_file import PhpFile

        return ChildrenFilterOption(
            pattern={
                "class": PhpFile,
                "name_pattern": r"^.*\.php$",
                "type": DiskItemType.FILE,
                "python": [],
            },
            recursive=True,
        )
