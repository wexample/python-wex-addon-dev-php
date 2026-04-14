from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE
from wexample_wex_core.decorator.command import command

if TYPE_CHECKING:
    from wexample_wex_addon_app.service.app_service import AppService
    from wexample_wex_core.context.execution_context import ExecutionContext


@command(
    type=COMMAND_TYPE_SERVICE,
    description="Configure wordpress service in app config",
)
def wordpress__service__install(
    context: ExecutionContext,
    service: AppService,
) -> None:
    config_file = service.app_workdir.get_config_file()
    config = config_file.read_config()

    config.set_by_path(f"service.{service.name}.db_prefix", "wp_")

    config_file.write_config(config)
    service.app_workdir.get_runtime_config(rebuild=True)

    context.io.log("Configured wordpress service defaults")
