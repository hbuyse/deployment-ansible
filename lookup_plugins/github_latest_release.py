# Copyright (c) Henri Buyse
# SPDX-License-Identifier: GPL-3.0-or-later
"""Lookup returning the tag of the latest release of a GitHub repository."""

from __future__ import annotations

DOCUMENTATION = r"""
name: github_latest_release
short_description: Tag name of the latest release of a GitHub repository
description:
  - Ask the GitHub API for the latest release of each repository and return its tag name.
  - The lookup runs on the controller.
  - The answers are kept in a cache file shared by all the runs, because unauthenticated requests are limited to 60 per
    hour and each host of a play would otherwise ask again. A stale answer is still used, with a warning, when GitHub
    cannot be reached or refuses the request (rate limit).
  - A request that fails with an answer that may be transient (not found, rate limit, server error, network error) is
    sent again after a delay that doubles each time, because GitHub sometimes answers 404 for a repository that exists.
options:
  _terms:
    description: Repositories, written as C(owner/name).
    required: true
  token:
    description:
      - GitHub token used to authenticate the request.
      - Unauthenticated requests are limited to 60 per hour and per IP address.
    type: str
    env:
      - name: GITHUB_TOKEN
  timeout:
    description: Timeout of the request, in seconds.
    type: int
    default: 30
  retries:
    description: Number of times a request that failed with a transient looking answer is sent again.
    type: int
    default: 2
    env:
      - name: GITHUB_LATEST_RELEASE_RETRIES
  retry_delay:
    description: Seconds to wait before the first new try, the delay doubles each time.
    type: float
    default: 1.0
    env:
      - name: GITHUB_LATEST_RELEASE_RETRY_DELAY
  cache_ttl:
    description:
      - Number of seconds during which an answer is reused without asking GitHub again, C(0) turns the cache off.
    type: int
    default: 900
    env:
      - name: GITHUB_LATEST_RELEASE_CACHE_TTL
  cache_dir:
    description:
      - Directory of the cache file.
      - Defaults to C(deployment-ansible) in C($XDG_CACHE_HOME), or in C(~/.cache).
    type: str
    env:
      - name: GITHUB_LATEST_RELEASE_CACHE_DIR
"""

EXAMPLES = r"""
- name: Get the version of yq
  ansible.builtin.set_fact:
    yq_latest_version: "{{ lookup('github_latest_release', 'mikefarah/yq') }}"

- name: Get the version of direnv, without the leading v
  ansible.builtin.set_fact:
    direnv_latest_version: "{{ lookup('github_latest_release', 'direnv/direnv')[1:] }}"
"""

RETURN = r"""
_raw:
  description: Tag name of the latest release of each repository, for instance C(v4.44.1).
  type: list
  elements: str
"""

import json
import os
import tempfile
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

API_URL = "https://api.github.com/repos/{repository}/releases/latest"
CACHE_FILE = "github_latest_release.json"
# Answers after which a stale cached tag is better than a failure
RETRY_LATER = (403, 429, 500, 502, 503, 504)
# Answers worth a new try: GitHub sometimes answers 404 for a repository that exists
TRANSIENT = (*RETRY_LATER, 404)

display = Display()


def _now():
    return time.time()


def _sleep(seconds):
    time.sleep(seconds)


def _valid(entry):
    if not isinstance(entry, dict):
        return False
    return isinstance(entry.get("tag"), str) and isinstance(entry.get("fetched"), (int, float))


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "deployment-ansible"}
        token = self.get_option("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        ttl = self.get_option("cache_ttl")
        cache_path = self._cache_path() if ttl > 0 else None

        tags = []
        for repository in terms:
            cached = self._read_cache(cache_path).get(repository) if cache_path else None
            if cached and _now() - cached["fetched"] < ttl:
                tags.append(cached["tag"])
                continue

            try:
                tag = self._fetch_with_retries(repository, headers)
            except AnsibleLookupError as error:
                if cached and getattr(error, "retry_later", False):
                    display.warning(f"{error}: using the cached release {cached['tag']} of {repository}")
                    tags.append(cached["tag"])
                    continue
                raise
            if cache_path:
                self._store(cache_path, repository, tag)
            tags.append(tag)
        return tags

    def _fetch_with_retries(self, repository, headers):
        retries = self.get_option("retries")
        delay = self.get_option("retry_delay")
        for attempt in range(retries + 1):
            try:
                return self._fetch(repository, headers)
            except AnsibleLookupError as error:
                if attempt == retries or not getattr(error, "transient", False):
                    raise
                display.vv(f"{error}: new try in {delay * 2**attempt} s")
                _sleep(delay * 2**attempt)
        raise AssertionError("unreachable")  # pragma: no cover

    def _fetch(self, repository, headers):
        request = Request(API_URL.format(repository=repository), headers=headers)
        try:
            with urlopen(request, timeout=self.get_option("timeout")) as response:
                release = json.load(response)
        except HTTPError as error:
            failure = AnsibleLookupError(
                f"GitHub answered {error.code} {error.reason} for the latest release of {repository}"
            )
            failure.retry_later = error.code in RETRY_LATER
            failure.transient = error.code in TRANSIENT
            raise failure from error
        except (URLError, TimeoutError) as error:
            failure = AnsibleLookupError(f"Cannot get the latest release of {repository}: {error}")
            failure.retry_later = True
            failure.transient = True
            raise failure from error
        except json.JSONDecodeError as error:
            raise AnsibleLookupError(f"Cannot get the latest release of {repository}: {error}") from error

        try:
            return release["tag_name"]
        except (KeyError, TypeError) as error:
            raise AnsibleLookupError(f"The latest release of {repository} has no tag_name") from error

    def _cache_path(self):
        directory = self.get_option("cache_dir")
        if not directory:
            base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
            directory = Path(base) / "deployment-ansible"
        return Path(directory).expanduser() / CACHE_FILE

    @staticmethod
    def _read_cache(path):
        try:
            content = json.loads(path.read_text())
        except (OSError, ValueError):
            return {}
        if not isinstance(content, dict):
            return {}
        return {repository: entry for repository, entry in content.items() if _valid(entry)}

    def _store(self, path, repository, tag):
        """Add the answer to the cache file, which other runs may be updating: write it in one atomic step."""
        content = self._read_cache(path)
        content[repository] = {"tag": tag, "fetched": _now()}
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as temporary:
                json.dump(content, temporary)
            os.replace(temporary.name, path)
        except OSError as error:
            display.vvv(f"Cannot write the cache of github_latest_release in {path}: {error}")
