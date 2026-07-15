from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE

from wexample_wex_addon_dev_php.const.tags import DomainTag
from wexample_wex_addon_dev_php.services.composer.commands.service.install_local import (
    APP_DIR,
    COMPOSER_BIN,
)

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext
    from wexample_wex_addon_app.service.app_service import AppService


@option(
    name="composer_packages",
    type=str,
    required=True,
    description="Space-separated composer package names whose constraint changed in composer.json",
)
@command(
    type=COMMAND_TYPE_SERVICE,
    description="Refresh composer.lock after a composer.json dependency change",
    tags=[
        DomainTag.LANGUAGE_PHP,
        EffectTag.WRITE,
        AudienceTag.AGENT_SAFE,
        ScopeTag.APP,
        ScopeTag.CONTAINER,
        ScopeTag.LOCAL,
    ],
)
def composer__service__refresh_lock(
    context: ExecutionContext,
    service: AppService,
    composer_packages: str,
    composer_bin: str = COMPOSER_BIN,
) -> None:
    """Generic composer lock refresh, reusable by any PHP runtime service.

    Delegating services (laravel, symfony…) call this with their own
    ``service`` so the work runs inside their container.
    """
    # --no-install rewrites composer.lock only: vendor/ may hold local
    # development symlinks that a real install would overwrite.
    # --with-all-dependencies lets the updated packages' own (locked)
    # dependencies move too, or sibling library bumps would dead-lock the
    # partial update.
    output = service.addon_manager.docker_exec(
        service.name,
        [
            "/bin/sh",
            "-c",
            f"cd {APP_DIR} && {composer_bin} update --no-install"
            f" --with-all-dependencies {composer_packages}",
        ],
    )
    context.io.log(output)
