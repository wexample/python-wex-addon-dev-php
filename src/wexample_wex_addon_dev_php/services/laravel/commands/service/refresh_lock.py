from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE

from wexample_wex_addon_dev_php.const.tags import DomainTag
from wexample_wex_addon_dev_php.services.composer.commands.service.refresh_lock import (
    composer__service__refresh_lock,
)

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext
    from wexample_wex_addon_app.service.app_service import AppService


@option(
    name="packages",
    type=str,
    required=True,
    description="Space-separated composer package names whose constraint changed in composer.json",
)
@command(
    type=COMMAND_TYPE_SERVICE,
    description="Refresh composer.lock after a composer.json dependency change",
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
def laravel__service__refresh_lock(
    context: ExecutionContext,
    service: AppService,
    packages: str,
) -> None:
    # Generic composer lock refresh, executed in this service's container.
    return composer__service__refresh_lock.function(
        context=context, service=service, packages=packages
    )
