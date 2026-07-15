from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command
from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE
from wexample_wex_addon_dev_javascript.services.node.commands.service.install_local import (
    node__service__install_local,
)

from wexample_wex_addon_dev_php.const.tags import DomainTag
from wexample_wex_addon_dev_php.services.composer.commands.service.install_local import (
    APP_DIR,
    composer__service__install_local,
)

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext
    from wexample_wex_addon_app.service.app_service import AppService

# Symfony images ship a sane composer on PATH (no php-pinned phar wrapper).
COMPOSER_BIN = "composer"


@command(
    type=COMMAND_TYPE_SERVICE,
    description="Wire locally-developed composer and npm packages into the app (local env only)",
    tags=[
        DomainTag.LANGUAGE_PHP,
        DomainTag.FRAMEWORK,
        EffectTag.WRITE,
        AudienceTag.AGENT_SAFE,
        ScopeTag.APP,
        ScopeTag.CONTAINER,
        ScopeTag.LOCAL,
    ],
)
def symfony__service__install_local(
    context: ExecutionContext,
    service: AppService,
) -> None:
    # Generic composer and node wiring, executed in this service's container.
    composer__service__install_local.function(
        context=context, service=service, composer_bin=COMPOSER_BIN
    )
    node__service__install_local.function(context=context, service=service)

    output = service.addon_manager.docker_exec(
        service.name,
        ["/bin/sh", "-c", f"cd {APP_DIR} && bin/console cache:clear"],
    )
    context.io.log(output)
