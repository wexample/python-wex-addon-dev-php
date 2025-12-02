from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_filestate.item.file.json_file import JsonFile
from wexample_helpers.decorator.base_class import base_class

if TYPE_CHECKING:
    from wexample_wex_addon_app.workdir.code_base_workdir import CodeBaseWorkdir


@base_class
class PhpComposerJsonFile(JsonFile):
    def add_dependency(
            self,
            package_name: str,
            version: str,
            operator: str = "",
            optional: bool = False,
            group: None | str = None,
    ) -> bool:
        """
        Add or update a Composer dependency.
        Returns True if the dependency list changed.
        """

        # Composer group
        group_key = "require-dev" if group == "dev" else "require"

        # Composer does not use operators like pip (==, >=, etc.)
        # So operator is simply prepended if provided.
        constraint = f"{operator}{version}".strip()

        config = self.read_config()

        # Extract or create dependency dictionary
        deps_node = config.search(path=group_key, default={})
        deps = deps_node.to_dict() if deps_node else {}

        old = deps.get(package_name)

        # Nothing changes
        if old == constraint:
            return False

        # Apply change
        deps[package_name] = constraint

        # Sort alphabetically for deterministic output
        deps = {k: deps[k] for k in sorted(deps.keys())}

        # Write back into config
        config.set(path=group_key, value=deps)
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
