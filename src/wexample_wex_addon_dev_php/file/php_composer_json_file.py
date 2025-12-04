from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.item.file.json_file import JsonFile
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_wex_addon_app.workdir.code_base_workdir import CodeBaseWorkdir


@base_class
class PhpComposerJsonFile(JsonFile):
    def add_dependency_from_string(
            self,
            package_name: str,
            version: str,
            operator: str = "",
            optional: bool = False,
            group: None | str = None,
    ) -> bool:
        """
        Add or update a Composer dependency using raw package name + version.
        Returns True if the dependency list changed.
        """
        # Composer group
        group_key = "require-dev" if group == "dev" else "require"

        # Composer uses simple version constraints (no pip-style operators)
        constraint = f"{operator}{version}".strip()

        config = self.read_config()

        # Extract or create dependency dictionary
        deps_node = config.search(path=group_key, default={})
        deps = deps_node.to_dict() if deps_node else {}

        old = deps.get(package_name)

        # No change needed
        if old == constraint:
            return False

        # Apply change
        deps[package_name] = constraint

        config.update_nested({group_key: deps})
        self.write_config(config)

        return True


    def get_dependencies_versions(
            self, optional: bool = False, group: str = "dev"
    ) -> dict[str, str]:
        # Default values is not well managed in nested config value, for now.
        require = self.read_config().search(path="require")

        if not require:
            return {}

        return require.get_dict_or_default(default={})

    def dumps(self, content: dict | None = None) -> str:
        content = content or self.read_parsed()

        workdir = self.get_parent_item()
        content["name"] = workdir.get_package_name()
        content["version"] = workdir.get_project_version()

        return super().dumps(content or {})
