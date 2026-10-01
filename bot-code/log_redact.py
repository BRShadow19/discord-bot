"""Redact sensitive values from log output so logs are safe to paste into chats and issues.

Two kinds of data in this bot's logs are sensitive:
  * googlevideo stream URLs. Their query string carries the host's public IP and signed tokens,
    and discord.player logs the whole ffmpeg command (URL included) at DEBUG.
  * secrets such as the Discord token and API keys, which can leak through tracebacks (for
    example a requests error that echoes a URL containing ?appid=<key>).
Voice IP discovery also logs the host's public IP at DEBUG ("detected ip: ...").

install() wraps the formatter of every handler on the root logger, so the final text (message and
traceback) is redacted no matter which logger produced it.

Not covered: output that bypasses Python logging, such as ffmpeg's own stderr, and IPv6 addresses
outside of a URL query string.
"""
import logging
import os
import re

# Environment variables that hold secrets (the names used by token.env / the Dockerfile).
SECRET_ENV_VARS = ('TOKEN', 'KEY', 'WEA', 'WEATHER', 'SPOTIFY_ID', 'SPOTIFY_SECRET', 'OSU', 'OSU_ID')
MIN_SECRET_LENGTH = 6   # shorter values would match unrelated text

# scheme://host/path?query  ->  scheme://host/path?<redacted>
_URL_QUERY = re.compile(r'((?:https?|wss?)://[^\s\'"?#]+)\?[^\s\'"]*')
# Four-part dotted numbers. Longer dotted strings (version numbers) are left alone.
_IPV4 = re.compile(r'(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?!\.?\d)')

_secret_re = None
_secret_names = {}


def _load_secrets():
    """(Re)read the secret values from the environment. Call after load_dotenv()."""
    global _secret_re, _secret_names
    names = {}
    for var in SECRET_ENV_VARS:
        value = os.environ.get(var, '')
        if len(value) >= MIN_SECRET_LENGTH:
            names[value] = var
    _secret_names = names
    if names:
        # Longest first so a secret that contains another one is replaced as a whole.
        _secret_re = re.compile('|'.join(re.escape(v) for v in sorted(names, key=len, reverse=True)))
    else:
        _secret_re = None


def redact(text):
    """Return text with secrets, URL query strings and IPv4 addresses replaced."""
    if _secret_re is not None:
        text = _secret_re.sub(lambda m: '<%s>' % _secret_names[m.group(0)], text)
    text = _URL_QUERY.sub(r'\1?<redacted>', text)
    return _IPV4.sub('<ip>', text)


class RedactingFormatter(logging.Formatter):
    """Wraps another formatter and redacts its output, including any traceback."""

    def __init__(self, inner):
        super().__init__()
        self._inner = inner

    def format(self, record):
        return redact(self._inner.format(record))


def install(logger=None):
    """Redact everything printed by the handlers on `logger` (default: the root logger).

    Safe to call more than once. Call it after load_dotenv() so the secrets are in the environment.
    """
    _load_secrets()
    for handler in (logger or logging.getLogger()).handlers:
        if not isinstance(handler.formatter, RedactingFormatter):
            handler.setFormatter(RedactingFormatter(handler.formatter or logging.Formatter()))
