#!/usr/bin/env python3
"""Where text is allowed to live. Research vs logs vs secrets."""
from __future__ import annotations

RESEARCH_DB = "/home/jesse/wisdom-scaffold/data/optiplex_index.db"
LOGS_DB = "/home/jesse/wisdom-scaffold/data/logs_index.db"
SECRETS_DB = "/home/jesse/wisdom-scaffold/data/secrets.db"

# Noise that drowned G99 hits. These leave research and go to logs_index.db
JUNK_SUBSTR = (
    "/logs/git-fleet/",
    "/git-fleet/",
    "/vendor_archive/",
    "/logs/",
    "/stamps/",
    "/__pycache__/",
    "/.git/",
    "/.venv/",
    "/node_modules/",
    "/.aider.tags.cache",
    "/sync-conflict-",
    "/dump/chunks.github/",
    "/clone_temp_",
    "/github_clone_temp_",
)

# Never store file bodies in any search index
SECRET_SUBSTR = (
    "/.ssh/",
    "/.gnupg/",
    "id_ed25519",
    "id_rsa",
    ".env",
    "credentials",
    "api_key",
    "apikey",
    "secret_key",
    "OPENROUTER_API_KEY",
    "bearer",
    "wallet.dat",
    "auth.json",
    "token.json",
)


def is_junk(path: str) -> bool:
    p = path.replace("\\", "/")
    return any(s in p for s in JUNK_SUBSTR)


def is_secret(path: str) -> bool:
    p = path.replace("\\", "/").lower()
    return any(s.lower() in p for s in SECRET_SUBSTR)


def bucket(path: str) -> str:
    if is_secret(path):
        return "secrets"
    if is_junk(path):
        return "logs"
    return "research"
