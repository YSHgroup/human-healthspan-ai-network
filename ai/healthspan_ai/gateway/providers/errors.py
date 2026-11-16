"""Shared errors raised by AI provider adapters."""


class ProviderConfigurationError(Exception):
    """The selected provider is missing required configuration."""


class ProviderRequestError(Exception):
    """The provider rejected or failed to complete a request."""