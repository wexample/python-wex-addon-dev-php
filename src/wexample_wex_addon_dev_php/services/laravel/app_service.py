from __future__ import annotations

from wexample_filestate.const.disk import DiskItemType
from wexample_wex_addon_app.service.app_service import AppService as BaseAppService

_D = DiskItemType.DIRECTORY

# Apache in the wexample/php-8.2 image (Alpine-based) runs as www-data uid 82,
# NOT the Debian 33. Laravel must be able to write its runtime dirs as that
# user. Declared here so app/start's rectify keeps them owned by 82 and stops
# them from flipping back to the host uid (e.g. after own/this or a git
# checkout), which is what caused the recurring "could not be opened in append
# mode: Permission denied" on storage/logs.
_LARAVEL_WEB_OWNER = "82:82"


class AppService(BaseAppService):
    def get_workdir_contribution(self, workdir) -> dict:
        return {
            "children": [
                {
                    "name": "storage",
                    "type": _D,
                    "should_exist": True,
                    "mode": {
                        "owner": _LARAVEL_WEB_OWNER,
                        "recursive": True,
                    },
                },
                {
                    "name": "bootstrap",
                    "type": _D,
                    "should_exist": True,
                    "children": [
                        {
                            "name": "cache",
                            "type": _D,
                            "should_exist": True,
                            "mode": {
                                "owner": _LARAVEL_WEB_OWNER,
                                "recursive": True,
                            },
                        },
                    ],
                },
            ]
        }
