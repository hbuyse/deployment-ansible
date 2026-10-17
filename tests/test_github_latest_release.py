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
def lookup(monkeypatch, tmp_path):
    """Return install(answer): the lookup, and the list of the requests it sent to GitHub."""
    lookup_loader.add_directory(str(PLUGINS_DIR), with_subdir=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_LATEST_RELEASE_CACHE_TTL", raising=False)
    monkeypatch.setenv("GITHUB_LATEST_RELEASE_CACHE_DIR", str(tmp_path / "cache"))
    requests = []

    def install(answer):
        """`answer` is the release, an exception, or a list of them returned one after the other."""
        answers = list(answer) if isinstance(answer, list) else None

        def fake_urlopen(request, timeout):
            requests.append((request, timeout))
            current = answers.pop(0) if answers is not None else answer
            if isinstance(current, Exception):
                raise current
            return io.BytesIO(json.dumps(current).encode())

        module = lookup_loader.get("github_latest_release")
        monkeypatch.setattr(sys.modules[type(module).__module__], "urlopen", fake_urlopen)
        return module, requests

    return install


@pytest.fixture
def clock(monkeypatch, lookup):
    """Control the time seen by the plugin."""
    lookup_loader.add_directory(str(PLUGINS_DIR), with_subdir=False)
    module = sys.modules[type(lookup_loader.get("github_latest_release")).__module__]
    now = {"value": 1_000_000.0}
    monkeypatch.setattr(module, "_now", lambda: now["value"])
    return now


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


def test_answer_is_cached(lookup):
    module, requests = lookup({"tag_name": "v1"})
    assert module.run(["owner/repo"]) == ["v1"]
    assert module.run(["owner/repo"]) == ["v1"]
    assert len(requests) == 1


def test_cache_is_shared_between_instances(lookup):
    module, requests = lookup({"tag_name": "v1"})
    module.run(["owner/repo"])
    other = lookup_loader.get("github_latest_release")
    assert other.run(["owner/repo"]) == ["v1"]
    assert len(requests) == 1


def test_each_repository_has_its_own_entry(lookup):
    module, requests = lookup([{"tag_name": "v1"}, {"tag_name": "v2"}])
    assert module.run(["owner/one", "owner/two"]) == ["v1", "v2"]
    assert module.run(["owner/two", "owner/one"]) == ["v2", "v1"]
    assert len(requests) == 2


def test_stale_answer_is_asked_again(lookup, clock):
    module, requests = lookup([{"tag_name": "v1"}, {"tag_name": "v2"}])
    assert module.run(["owner/repo"]) == ["v1"]
    clock["value"] += 899
    assert module.run(["owner/repo"]) == ["v1"]
    clock["value"] += 2
    assert module.run(["owner/repo"]) == ["v2"]
    assert len(requests) == 2


def test_ttl_is_configurable(lookup, clock, monkeypatch):
    monkeypatch.setenv("GITHUB_LATEST_RELEASE_CACHE_TTL", "10")
    module, requests = lookup([{"tag_name": "v1"}, {"tag_name": "v2"}])
    module.run(["owner/repo"])
    clock["value"] += 11
    assert module.run(["owner/repo"]) == ["v2"]


def test_ttl_zero_turns_the_cache_off(lookup, monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_LATEST_RELEASE_CACHE_TTL", "0")
    module, requests = lookup({"tag_name": "v1"})
    module.run(["owner/repo"])
    module.run(["owner/repo"])
    assert len(requests) == 2
    assert not (tmp_path / "cache").exists()


@pytest.mark.parametrize("status", [403, 429, 503])
def test_stale_answer_is_used_when_github_refuses(lookup, clock, status):
    error = HTTPError("https://api.github.com", status, "rate limit exceeded", {}, None)
    module, requests = lookup([{"tag_name": "v1"}, error])
    module.run(["owner/repo"])
    clock["value"] += 100_000
    assert module.run(["owner/repo"]) == ["v1"]
    assert len(requests) == 2


def test_stale_answer_is_used_when_the_network_is_down(lookup, clock):
    module, _ = lookup([{"tag_name": "v1"}, URLError("no route to host")])
    module.run(["owner/repo"])
    clock["value"] += 100_000
    assert module.run(["owner/repo"]) == ["v1"]


def test_missing_repository_is_not_hidden_by_the_cache(lookup, clock):
    error = HTTPError("https://api.github.com", 404, "Not Found", {}, None)
    module, _ = lookup([{"tag_name": "v1"}, error])
    module.run(["owner/repo"])
    clock["value"] += 100_000
    with pytest.raises(AnsibleLookupError, match="404 Not Found"):
        module.run(["owner/repo"])


def test_failure_is_not_cached(lookup):
    error = HTTPError("https://api.github.com", 403, "rate limit exceeded", {}, None)
    module, requests = lookup([error, {"tag_name": "v1"}])
    with pytest.raises(AnsibleLookupError):
        module.run(["owner/repo"])
    assert module.run(["owner/repo"]) == ["v1"]
    assert len(requests) == 2


@pytest.mark.parametrize("content", ["not json", "[]", '{"owner/repo": "v1"}', '{"owner/repo": {"tag": 1}}'])
def test_corrupted_cache_is_ignored(lookup, tmp_path, content):
    cache = tmp_path / "cache"
    cache.mkdir()
    (cache / "github_latest_release.json").write_text(content)
    module, requests = lookup({"tag_name": "v1"})
    assert module.run(["owner/repo"]) == ["v1"]
    assert json.loads((cache / "github_latest_release.json").read_text())["owner/repo"]["tag"] == "v1"
    assert len(requests) == 1


def test_default_cache_directory_follows_xdg_cache_home(lookup, monkeypatch, tmp_path):
    monkeypatch.delenv("GITHUB_LATEST_RELEASE_CACHE_DIR")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))
    module, _ = lookup({"tag_name": "v1"})
    module.run(["owner/repo"])
    assert (tmp_path / "xdg" / "deployment-ansible" / "github_latest_release.json").is_file()


def test_unwritable_cache_does_not_fail_the_lookup(lookup, monkeypatch, tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("a file where the cache directory should be")
    monkeypatch.setenv("GITHUB_LATEST_RELEASE_CACHE_DIR", str(blocker / "cache"))
    module, _ = lookup({"tag_name": "v1"})
    assert module.run(["owner/repo"]) == ["v1"]
