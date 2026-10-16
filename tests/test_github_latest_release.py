import io
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest
from ansible.errors import AnsibleLookupError
from ansible.plugins.loader import lookup_loader

PLUGINS_DIR = Path(__file__).resolve().parents[1] / "lookup_plugins"


@pytest.fixture
def lookup(monkeypatch):
    lookup_loader.add_directory(str(PLUGINS_DIR), with_subdir=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    requests = []

    def install(answer):
        def fake_urlopen(request, timeout):
            requests.append((request, timeout))
            if isinstance(answer, Exception):
                raise answer
            return io.BytesIO(json.dumps(answer).encode())

        module = lookup_loader.get("github_latest_release")
        monkeypatch.setattr(sys.modules[type(module).__module__], "urlopen", fake_urlopen)
        return module, requests

    return install


def test_returns_the_tag_of_each_repository(lookup):
    module, requests = lookup({"tag_name": "v4.44.1"})
    assert module.run(["mikefarah/yq", "direnv/direnv"]) == ["v4.44.1", "v4.44.1"]
    assert [request.full_url for request, _ in requests] == [
        "https://api.github.com/repos/mikefarah/yq/releases/latest",
        "https://api.github.com/repos/direnv/direnv/releases/latest",
    ]


def test_sends_no_authorization_without_token(lookup):
    module, requests = lookup({"tag_name": "v1"})
    module.run(["owner/repo"])
    assert not requests[0][0].has_header("Authorization")


def test_sends_the_token_from_the_environment(lookup, monkeypatch):
    module, requests = lookup({"tag_name": "v1"})
    monkeypatch.setenv("GITHUB_TOKEN", "secret")
    module.run(["owner/repo"])
    assert requests[0][0].get_header("Authorization") == "Bearer secret"


def test_http_error_names_the_repository(lookup):
    error = HTTPError("https://api.github.com", 403, "rate limit exceeded", {}, None)
    module, _ = lookup(error)
    with pytest.raises(AnsibleLookupError, match=r"403 rate limit exceeded.*owner/repo"):
        module.run(["owner/repo"])


def test_network_error_names_the_repository(lookup):
    module, _ = lookup(URLError("no route to host"))
    with pytest.raises(AnsibleLookupError, match=r"owner/repo.*no route to host"):
        module.run(["owner/repo"])


def test_release_without_tag(lookup):
    module, _ = lookup({"name": "nightly"})
    with pytest.raises(AnsibleLookupError, match="no tag_name"):
        module.run(["owner/repo"])
