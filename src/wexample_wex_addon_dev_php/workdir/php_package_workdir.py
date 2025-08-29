from __future__ import annotations

from wexample_config.const.types import DictConfig
from wexample_wex_addon_dev_php.workdir.php_workdir import PhpWorkdir
from wexample_filestate.const.disk import DiskItemType

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