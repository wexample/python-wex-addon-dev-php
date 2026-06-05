"""Domain tags exposed by this addon — one entry per `domain:*` value its commands use."""
from __future__ import annotations


class DomainTag:
    """Functional domain this addon's commands touch."""

    APP_LIFECYCLE = "domain:app-lifecycle"
    CONFIG = "domain:config"
    DB = "domain:db"
    FRAMEWORK = "domain:framework"
    LANGUAGE_PHP = "domain:language-php"
