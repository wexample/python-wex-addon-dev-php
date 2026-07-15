from __future__ import annotations

from wexample_filestate.result.file_state_result import FileStateResult
from wexample_helpers.decorator.base_class import base_class
from wexample_wex_addon_dev_javascript.workdir.javascript_workdir import (
    JavascriptWorkdir,
)

from wexample_wex_addon_dev_php.workdir.php_workdir import PhpWorkdir


@base_class
class SymfonyWorkdir(PhpWorkdir):
    def apply(
        self,
        **kwargs,
    ) -> FileStateResult:
        result = super().apply(**kwargs)

        workdir_javascript = JavascriptWorkdir.create_from_path(
            path=self.get_path(), io=self.io
        )

        return workdir_javascript.apply(result=result, **kwargs)

    # NOTE: package.json library syncing is handled natively by PhpWorkdir's
    # dependency manifests (get_dependency_manifests), no facade needed here.
