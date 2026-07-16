from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_wex_addon_dev_javascript.services.node.commands.service.refresh_lock import (
    node__service__refresh_lock,
)
from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE

from wexample_wex_addon_dev_php.const.tags import DomainTag
from wexample_wex_addon_dev_php.services.composer.commands.service.refresh_lock import (
    composer__service__refresh_lock,
)

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext
    from wexample_wex_addon_app.service.app_service import AppService


@option(
    name="composer_packages",
    type=str,
    required=False,
    default="",
    description="Space-separated composer package names whose constraint changed in composer.json",
)
@option(
    name="npm_packages",
    type=str,
    required=False,
    default="",
    description="Space-separated npm package names whose constraint changed in package.json",
)
@command(
    type=COMMAND_TYPE_SERVICE,
    description="Refresh composer and javascript lock files after a dependency change",
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
    composer_packages: str = "",
    npm_packages: str = "",
) -> None:
    # Generic lock refreshes, executed in this service's container.
    if composer_packages:
        composer__service__refresh_lock.function(
            context=context, service=service, composer_packages=composer_packages
        )
    if npm_packages:
        node__service__refresh_lock.function(
            context=context, service=service, npm_packages=npm_packages
        )
