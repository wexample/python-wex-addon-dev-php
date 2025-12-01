from __future__ import annotations

from wexample_filestate.item.file.json_file import JsonFile
from wexample_helpers.decorator.base_class import base_class


@base_class
class PhpComposerJsonFile(JsonFile):
    def get_dependencies_versions(
            self, optional: bool = False, group: str = "dev"
    ) -> dict[str, str]:
        return self.read_config().search(path="require", default=[]).to_dict()
