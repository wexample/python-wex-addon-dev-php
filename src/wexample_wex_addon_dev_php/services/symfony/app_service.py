from __future__ import annotations

from wexample_filestate.const.disk import DiskItemType
from wexample_wex_addon_app.service.app_service import AppService as BaseAppService

_D = DiskItemType.DIRECTORY

# php-fpm in the Alpine-based images runs as www-data uid 82, NOT the Debian
# 33. Symfony must be able to write its runtime dirs as that user. Declared
# here so rectify keeps them owned by 82 and stops them from flipping back to
# the host uid (e.g. after own/this, a git checkout or a fresh image deploy),
# which surfaces as a 500 with nothing written to var/log.
_SYMFONY_WEB_OWNER = "82:82"

_WORKDIR_CONTRIBUTION: dict = {
    "children": [
        {
            "name": "var",
            "type": _D,
            "should_exist": True,
            "mode": {
                "owner": _SYMFONY_WEB_OWNER,
                "recursive": True,
            },
        },
    ]
}


class AppService(BaseAppService):
    def get_workdir_contribution(self, workdir) -> dict:
        return _WORKDIR_CONTRIBUTION
