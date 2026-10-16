SSH_DIR = "/root/.ssh"
EMAIL = "molecule@example.com"


def test_ssh_directory(host):
    """~/.ssh exists and is only accessible by its owner."""
    ssh_dir = host.file(SSH_DIR)
    assert ssh_dir.is_directory
    assert oct(ssh_dir.mode) == "0o700"


def test_private_key_is_deployed(host):
    """The private key is deployed."""
    assert host.file(f"{SSH_DIR}/id_rsa").is_file


def test_private_key_is_not_readable_by_others(host):
    """OpenSSH ignores a private key that is readable by group or others."""
    private_key = host.file(f"{SSH_DIR}/id_rsa")
    assert oct(private_key.mode) == "0o600", f"id_rsa has mode {oct(private_key.mode)}, expected 0o600"


def test_public_key(host):
    """The public key is templated with the email and is world readable."""
    public_key = host.file(f"{SSH_DIR}/id_rsa.pub")
    assert public_key.is_file
    assert oct(public_key.mode) == "0o644"
    content = public_key.content_string.strip()
    assert content.startswith("ssh-rsa ")
    assert content.endswith(f" {EMAIL}")
    assert "{{" not in content


def test_config_files(host):
    """The ssh client configuration and its drop-in directory are deployed."""
    config = host.file(f"{SSH_DIR}/config")
    assert config.is_file
    assert "Include ~/.ssh/config.d/*.conf" in config.content_string

    drop_in = host.file(f"{SSH_DIR}/config.d/01_forward-agent-x11.conf")
    assert drop_in.is_file
    assert "ForwardAgent yes" in drop_in.content_string


def test_ssh_client_parses_the_configuration(host):
    """`ssh -G` resolves the configuration, including the drop-in file."""
    cmd = host.run(f"ssh -G -F {SSH_DIR}/config localhost")
    assert cmd.rc == 0, cmd.stderr
    options = {line.split(" ", 1)[0]: line.split(" ", 1)[1] for line in cmd.stdout.splitlines() if " " in line}
    assert options["forwardagent"] == "yes"
    assert options["forwardx11"] == "yes"
