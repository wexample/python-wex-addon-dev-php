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
APP_DIR = "/var/www/html"
VENDOR_DEV_DIR = "/var/www/vendor-dev"

# The wexample php images ship a /usr/bin/composer wrapper pinned to an older
# PHP binary; invoking the phar through PATH php guarantees the runtime version.
COMPOSER_BIN = "php /usr/bin/composer.phar"


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
def composer__service__install_local(
    context: ExecutionContext,
    service: AppService,
) -> None:
    """Generic composer wiring, reusable by any PHP runtime service.

    Delegating services (laravel, symfony…) call this with their own
    ``service`` so the work runs inside their container, then append their
    framework-specific steps (cache clears…).
    """
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
cd {APP_DIR}
{COMPOSER_BIN} install --no-scripts
for vendor in {vendors}; do
  [ -d "{VENDOR_DEV_DIR}/$vendor" ] || continue
  mkdir -p "vendor/$vendor"
  for src in {VENDOR_DEV_DIR}/$vendor/*/; do
    pkg=$(basename "$src")
    [ -f "$src/composer.json" ] || continue
    rm -rf "vendor/$vendor/$pkg"
    ln -s "${{src%/}}" "vendor/$vendor/$pkg"
    echo "  symlinked $vendor/$pkg"
  done
done
{COMPOSER_BIN} dump-autoload
"""

    context.io.log(f"Wiring local composer packages ({vendors}) into vendor/…")
    output = service.addon_manager.docker_exec(
        service.name, ["/bin/sh", "-c", script]
    )
    context.io.log(output)
