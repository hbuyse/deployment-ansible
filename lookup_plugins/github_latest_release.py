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
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ansible.errors import AnsibleLookupError
from ansible.plugins.lookup import LookupBase

API_URL = "https://api.github.com/repos/{repository}/releases/latest"


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "deployment-ansible"}
        token = self.get_option("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        tags = []
        for repository in terms:
            request = Request(API_URL.format(repository=repository), headers=headers)
            try:
                with urlopen(request, timeout=self.get_option("timeout")) as response:
                    release = json.load(response)
            except HTTPError as error:
                raise AnsibleLookupError(
                    f"GitHub answered {error.code} {error.reason} for the latest release of {repository}"
                ) from error
            except (URLError, TimeoutError, json.JSONDecodeError) as error:
                raise AnsibleLookupError(f"Cannot get the latest release of {repository}: {error}") from error

            try:
                tags.append(release["tag_name"])
            except (KeyError, TypeError) as error:
                raise AnsibleLookupError(f"The latest release of {repository} has no tag_name") from error
        return tags
