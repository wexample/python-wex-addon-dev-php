from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.item.file.json_file import JsonFile
from wexample_helpers.decorator.base_class import base_class
from wexample_helpers.helpers.debug import debug_dump

if TYPE_CHECKING:
    from wexample_wex_addon_app.workdir.code_base_workdir import CodeBaseWorkdir


@base_class
class PhpComposerJsonFile(JsonFile):
    def add_dependency(
            self, package_name: str, version: str, operator: str = "", optional: bool = False, group: None|str = None
    ) -> bool:
        """
        Add or update a Composer dependency.
        Returns True if the dependency list changed.
        """

        group_key = "require-dev" if group == "dev" else "require"
        version = f"{operator}{version}"

        config = self.read_config()

        # Ensure group exists
        deps = config.search(path=group_key, default={}).to_dict_or_none()

        old_version = deps.get(package_name)

        # If version is unchanged → nothing to do
        if old_version == version:
            return False

        # Apply change
        deps[package_name] = version

        config_updated = {}
        config_updated[group_key] = deps

        debug_dump(group_key)

        config.update_nested(data=config_updated)
        self._content_cache_config = config

        self.write_config(config)

        return True

    def get_dependencies_versions(
        self, optional: bool = False, group: str = "dev"
    ) -> dict[str, str]:
        # Default values is not well managed in nested config value, for now.
        require = self.read_config().search(path="require")

        if not require:
            return {}

        return require.to_dict()

    def dumps(self, content: dict | None = None) -> str:
        import json

        content = content or self.read_parsed()

        package = self.find_package_workdir()
        if package:
            content["version"] = package.get_project_version()

        return json.dumps(content or {}, ensure_ascii=False, indent=2)

    def find_package_workdir(self) -> CodeBaseWorkdir | None:
        from wexample_wex_addon_app.workdir.code_base_workdir import CodeBaseWorkdir

        return self.find_closest(CodeBaseWorkdir)
