"""Safe YAML loading for repository configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .model import ConfigurationError, RepositoryConfig, config_from_mapping


class _UniqueSafeLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: _UniqueSafeLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ConfigurationError(f"config.{key}: duplicate field")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def load_config(path: str | Path) -> RepositoryConfig:
    """Load and validate YAML without resolving environment variables or running commands."""
    source = Path(path)
    try:
        text = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError(f"config: cannot read {source}: {exc.strerror or exc}") from exc
    return parse_config(text)


def parse_config(text: str) -> RepositoryConfig:
    try:
        raw = yaml.load(text, Loader=_UniqueSafeLoader)
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"config: invalid YAML: {exc}") from exc
    if raw is None:
        raise ConfigurationError("config: document must not be empty")
    return config_from_mapping(raw)
