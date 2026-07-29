from __future__ import annotations

from wexample_filestate.item.file.json_file import JsonFile
from wexample_helpers.decorator.base_class import base_class
from wexample_wex_addon_app.item.file.mixin.app_dependencies_config_file_mixin import (
    AppDependenciesConfigFileMixin,
)


@base_class
class PhpComposerJsonFile(AppDependenciesConfigFileMixin, JsonFile):
    def add_dependency(
        self,
        # In composer, no operator says ==
        operator: str = "",
        **kwargs,
    ) -> bool:
        return super().add_dependency(operator=operator, **kwargs)

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
        constraint = (f"{operator}{version}" if operator else version).strip()

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

    def dumps(self, content: dict | None = None) -> str:
        content = content or self.read_parsed()

        workdir = self.get_parent_item()
        content["name"] = workdir.get_package_name()
        content["version"] = workdir.get_setup_version()

        return super().dumps(content)

    def get_dependencies_versions(
        self, optional: bool = False, group: str = "dev"
    ) -> dict[str, str]:
        # Default values is not well managed in nested config value, for now.
        require = self.read_config().search(path="require")

        if not require:
            return {}

        # Use to_dict_or_none() (not get_dict_or_default) so nested ConfigValue
        # wrappers are unwrapped to native str — matches the dict[str, str] signature.
        return require.to_dict_or_none() or {}

    def set_private_registry_packages(self, package_names: list[str]) -> bool:
        """Bound every custom composer registry to the private packages.

        A custom registry holding some (possibly stale) versions of a
        publicly-published package is canonical for it and masks the newer
        versions available on packagist; the `only` filter keeps each
        registry to its own perimeter.
        """
        # Cross-ecosystem callers pass every private package; npm scoped
        # names (@vendor/name) can never be composer packages.
        package_names = [n for n in package_names if not n.startswith("@")]
        if not package_names:
            return False

        parsed = self.read_parsed()
        repositories = parsed.get("repositories")
        if isinstance(repositories, dict):
            entries = repositories.values()
        elif isinstance(repositories, list):
            entries = repositories
        else:
            return False

        only = sorted(package_names)
        changed = False
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("type") != "composer":
                continue
            # Only forge package registries (gitlab-style URL) host our
            # private packages; other composer repositories (packagist
            # mirrors, nova.laravel.com…) serve unrelated packages and must
            # not be restricted.
            if "/packages/composer" not in entry.get("url", ""):
                continue
            if entry.get("only") != only:
                entry["only"] = only
                changed = True

        if changed:
            self.write_parsed()
        return changed
