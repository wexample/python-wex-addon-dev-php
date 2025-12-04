from __future__ import annotations

from wexample_filestate.result.file_state_result import FileStateResult
from wexample_wex_addon_dev_javascript.workdir.javascript_workdir import JavascriptWorkdir
from wexample_wex_addon_dev_php.workdir.php_workdir import PhpWorkdir


class SymfonyWorkdir(PhpWorkdir):
    def libraries_sync(self) -> None:
        super().libraries_sync()

        self.log('Syncing Javascript...')

        workdir_javascript = JavascriptWorkdir.create_from_path(
            path=self.get_path()
        )

        workdir_javascript.libraries_sync()

    def apply(
            self,
            **kwargs,
    ) -> FileStateResult:
        result = super().apply(**kwargs)

        workdir_javascript = JavascriptWorkdir.create_from_path(
            path=self.get_path()
        )

        workdir_javascript.apply(
            **kwargs
        )

        return result
