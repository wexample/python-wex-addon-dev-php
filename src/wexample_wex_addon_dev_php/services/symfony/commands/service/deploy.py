from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command
from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE

from wexample_wex_addon_dev_php.const.tags import DomainTag
from wexample_wex_addon_dev_php.services.composer.commands.service.install_local import (
    APP_DIR,
)

if TYPE_CHECKING:
    from wexample_cli.context.execution_context import ExecutionContext
    from wexample_wex_addon_app.service.app_service import AppService


@command(
    type=COMMAND_TYPE_SERVICE,
    description="Post-deployment tasks for a symfony app (doctrine migrations)",
    tags=[
        DomainTag.LANGUAGE_PHP,
        DomainTag.FRAMEWORK,
        EffectTag.WRITE,
        AudienceTag.AGENT_SAFE,
        ScopeTag.APP,
        ScopeTag.CONTAINER,
    ],
)
def symfony__service__deploy(
    context: ExecutionContext,
    service: AppService,
) -> None:
    """Run once by `.release/deploy` after the app restarted on new images.

    Idempotent: applies pending doctrine migrations only. --no-interaction is
    vital — the deploy webhook has no TTY, doctrine's data-loss prompt would
    silently abort the migration (which is how unapplied migrations reached
    prod). Apps without a migrations/ directory are skipped.
    """
    script = f"""
set -e
cd {APP_DIR}
if [ -d migrations ]; then
  bin/console doctrine:migrations:migrate --no-interaction --allow-no-migration
else
  echo "No migrations/ directory, skipping."
fi
"""
    output = service.addon_manager.docker_exec(
        service.name, ["/bin/sh", "-c", script]
    )
    context.io.log(output)
