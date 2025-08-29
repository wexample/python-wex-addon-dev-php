from __future__ import annotations

from wexample_config.const.types import DictConfig
from wexample_filestate.const.disk import DiskItemType
from wexample_wex_addon_dev_php.workdir.php_workdir import PhpWorkdir


class PhpPackageWorkdir(PhpWorkdir):
    def prepare_value(self, raw_value: DictConfig | None = None) -> DictConfig:
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

        return raw_value

    def get_dependencies(self) -> list[str]:
        return []

    def get_package_name(self) -> str:
        return self.get_project_name()
