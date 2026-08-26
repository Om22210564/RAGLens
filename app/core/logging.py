import logging

SENSITIVE_KEYS = frozenset({"authorization", "password", "secret", "token", "api_key"})


def redact_mapping(values: dict[str, object]) -> dict[str, object]:
    return {
        key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else value
        for key, value in values.items()
    }


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        force=True,  # Replace the existing logging configuration with this configuration.
    )


# `level.upper()` produces standard logging levels such as `DEBUG` and `INFO`.
# The logging module expects those level names in uppercase.
