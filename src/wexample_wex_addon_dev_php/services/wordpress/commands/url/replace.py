from __future__ import annotations

from typing import TYPE_CHECKING

from wexample_cli.const.tags import AudienceTag, EffectTag, ScopeTag
from wexample_cli.decorator.command import command
from wexample_cli.decorator.option import option
from wexample_wex_core.const.globals import COMMAND_TYPE_SERVICE

from wexample_wex_addon_dev_php.const.tags import DomainTag

if TYPE_CHECKING:
    from wexample_app.response.abstract_response import AbstractResponse
    from wexample_cli.context.execution_context import ExecutionContext
    from wexample_wex_addon_app.service.app_service import AppService


@option(
    name="new_url",
    short_name="n",
    type=str,
    required=False,
    description="New site URL",
)
@option(
    name="old_url",
    short_name="o",
    type=str,
    required=False,
    description="Old site URL (auto-detected if omitted)",
)
@option(
    name="yes",
    short_name="y",
    type=bool,
    is_flag=True,
    required=False,
    description="Do not ask for confirmation",
)
@command(
    type=COMMAND_TYPE_SERVICE,
    description="Replace the WordPress site URL using wp-cli",
    tags=[
        DomainTag.CONFIG,
        DomainTag.FRAMEWORK,
        DomainTag.LANGUAGE_PHP,
        EffectTag.NETWORK_CALL,
        EffectTag.SUBPROCESS_SPAWN,
        EffectTag.WRITE,
        AudienceTag.AGENT_SAFE,
        ScopeTag.APP,
        ScopeTag.LOCAL,
    ],
)
def wordpress__url__replace(
    context: ExecutionContext,
    service: AppService,
    new_url: str | None = None,
    old_url: str | None = None,
    yes: bool = False,
) -> AbstractResponse:
    import subprocess

    import click
    from wexample_app.response.shell_command_response import ShellCommandResponse

    runtime = service.app_workdir.get_runtime_config()
    app_project_name = runtime.search("app.project_name").get_str()
    cli_container = f"{app_project_name}_wordpress_cli"

    target_url = _normalize_url(new_url or _guess_new_url(service))

    if old_url is None:
        detect = subprocess.run(
            ["docker", "exec", cli_container, "wp", "option", "get", "siteurl"],
            capture_output=True,
            text=True,
        )
        if detect.returncode != 0:
            raise RuntimeError(
                f"Unable to detect current WordPress URL:\n{detect.stderr}"
            )
        source_url = _normalize_url(detect.stdout.strip())
    else:
        source_url = _normalize_url(old_url)

    if source_url == target_url:
        context.io.log("WordPress URL already matches target URL")
        return ShellCommandResponse(kernel=context.kernel, content=["true"])

    if not yes and not click.confirm(
        f"Replace WordPress URL from '{source_url}' to '{target_url}'?",
        default=True,
    ):
        raise RuntimeError("WordPress URL replacement aborted by user")

    return ShellCommandResponse(
        kernel=context.kernel,
        content=[
            "docker",
            "exec",
            cli_container,
            "wp",
            "search-replace",
            source_url,
            target_url,
            "--skip-columns=guid",
        ],
    )


def _guess_new_url(service: AppService) -> str:
    runtime = service.app_workdir.get_runtime_config()
    domains = runtime.search("app.domains").get_list_or_default([])
    if domains:
        first = domains[0].get_str()
        return _normalize_url(f"https://{first}")

    domain = runtime.search("app.domain").get_str_or_none()
    if domain:
        return _normalize_url(f"https://{domain}")

    raise RuntimeError("Unable to guess the new WordPress URL from runtime app domains")


def _normalize_url(url: str) -> str:
    return url.rstrip("/")
