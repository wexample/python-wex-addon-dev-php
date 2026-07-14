from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command
from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE

from wexample_wex_addon_dev_php.const.tags import DomainTag

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext
    from wexample_wex_addon_app.service.app_service import AppService

# In-container layout convention shared by the local dev composes: the app is
# served from APP_DIR and each locally-developed vendor suite is mounted under
# VENDOR_DEV_DIR/<vendor> (see the `local_packages` env config section).
_APP_DIR = "/var/www/html"
_VENDOR_DEV_DIR = "/var/www/vendor-dev"

# The laravel images ship a /usr/bin/composer wrapper pinned to an older PHP
# binary; invoking the phar through PATH php guarantees the runtime version.
_COMPOSER = "php /usr/bin/composer.phar"


@command(
    type=COMMAND_TYPE_SERVICE,
    description="Wire locally-developed composer packages into vendor/ (local env only)",
    tags=[
        DomainTag.LANGUAGE_PHP,
        EffectTag.WRITE,
        AudienceTag.AGENT_SAFE,
        ScopeTag.APP,
        ScopeTag.CONTAINER,
        ScopeTag.LOCAL,
    ],
)
def laravel__service__install_local(
    context: ExecutionContext,
    service: AppService,
) -> None:
    php_packages = service.app_workdir.get_runtime_config().search(
        "local_packages.php"
    )
    if php_packages.is_none():
        context.io.log("No local_packages.php configured, nothing to wire.")
        return

    vendors = " ".join(sorted(php_packages.to_dict().keys()))

    # Composer keeps the (possibly stale) registry version of a package even
    # when a newer local source exists, so the deterministic wiring is a
    # forced symlink over vendor/ — every local package of each declared
    # vendor, installed or not.
    script = f"""
set -e
cd {_APP_DIR}
{_COMPOSER} install --no-scripts
for vendor in {vendors}; do
  [ -d "{_VENDOR_DEV_DIR}/$vendor" ] || continue
  mkdir -p "vendor/$vendor"
  for src in {_VENDOR_DEV_DIR}/$vendor/*/; do
    pkg=$(basename "$src")
    [ -f "$src/composer.json" ] || continue
    rm -rf "vendor/$vendor/$pkg"
    ln -s "${{src%/}}" "vendor/$vendor/$pkg"
    echo "  symlinked $vendor/$pkg"
  done
done
rm -f bootstrap/cache/packages.php bootstrap/cache/services.php
{_COMPOSER} dump-autoload
php artisan optimize:clear
"""

    context.io.log(f"Wiring local composer packages ({vendors}) into vendor/…")
    output = service.addon_manager.docker_exec(
        service.name, ["/bin/sh", "-c", script]
    )
    context.io.log(output)
