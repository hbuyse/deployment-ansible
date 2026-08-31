import json
import stat


def test_binary_installed(host):
    """Test that the opencode binary was installed."""
    binary = host.file("/root/.local/bin/opencode")
    assert binary.exists
    assert binary.is_file
    assert stat.S_IXUSR & binary.mode or stat.S_IXGRP & binary.mode or stat.S_IXOTH & binary.mode


def test_config_directory_created(host):
    """Test that the opencode config directory was created."""
    config_dir = host.file("/root/.config/opencode")
    assert config_dir.exists
    assert config_dir.is_directory


def test_agents_directory_created(host):
    """Test that the agents subdirectory was created."""
    agents_dir = host.file("/root/.config/opencode/agents")
    assert agents_dir.exists
    assert agents_dir.is_directory


def test_tui_config(host):
    """Test that tui.jsonc was copied with correct content."""
    tui = host.file("/root/.config/opencode/tui.jsonc")
    assert tui.exists
    assert tui.is_file
    content = json.loads(tui.content_string)
    assert content["theme"] == "catppuccin"


def test_opencode_config_providers(host):
    """Test that opencode.jsonc contains the configured providers."""
    config = host.file("/root/.config/opencode/opencode.jsonc")
    assert config.exists
    assert config.is_file
    content = json.loads(config.content_string)
    assert "enabled_providers" in content
    assert "openai" in content["enabled_providers"]
    assert "provider" in content
    assert content["provider"]["openai"]["api_key"] == "sk-test-key-12345"


def test_opencode_config_default_agent(host):
    """Test that default_agent is set correctly."""
    config = host.file("/root/.config/opencode/opencode.jsonc")
    content = json.loads(config.content_string)
    assert content["default_agent"] == "plan"


def test_opencode_config_mcp(host):
    """Test that MCP configuration is present (even if empty)."""
    config = host.file("/root/.config/opencode/opencode.jsonc")
    content = json.loads(config.content_string)
    assert "mcp" in content


def test_review_agent(host):
    """Test that review.md agent was created with correct model."""
    review = host.file("/root/.config/opencode/agents/review.md")
    assert review.exists
    assert review.is_file
    content = review.content_string
    assert "model: gpt-4" in content
    assert "mode: subagent" in content
    assert "Reviews code for quality and best practices" in content


def test_config_file_permissions(host):
    """Test that config files have correct permissions (0644)."""
    for path in [
        "/root/.config/opencode/opencode.jsonc",
        "/root/.config/opencode/tui.jsonc",
        "/root/.config/opencode/agents/review.md",
    ]:
        f = host.file(path)
        assert f.exists
        mode = f.mode & 0o777
        assert mode == 0o644, f"{path} has mode {oct(mode)}, expected 0o644"


def test_config_directory_permissions(host):
    """Test that config directories have correct permissions (0755)."""
    for path in [
        "/root/.config/opencode",
        "/root/.config/opencode/agents",
    ]:
        d = host.file(path)
        assert d.exists
        mode = d.mode & 0o777
        assert mode == 0o755, f"{path} has mode {oct(mode)}, expected 0o755"
