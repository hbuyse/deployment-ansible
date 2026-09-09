# AGENTS.md

Guidance for AI coding agents working in this repository.

## What this repo is

An Ansible-based personal system configuration ("dotfiles as roles") for Arch/EndeavourOS/Manjaro/CachyOS,
Ubuntu/Debian, Fedora and FreeBSD. Everything runs against `hosts: localhost`; there is no remote inventory.

Top-level playbooks (each installs a themed set of roles):

- [development.yml](development.yml) — dev tooling, language servers, editors, VCS
- [sway.yml](sway.yml) — Sway window manager and Wayland desktop tools
- [term.yml](term.yml) — terminal/shell tooling
- [tools.yml](tools.yml) — GUI applications and desktop clients

Every playbook includes [pre_tasks/main.yml](pre_tasks/main.yml) and [post_tasks/main.yml](post_tasks/main.yml),
which dispatch to an OS-family-specific file (`archlinux.yml`, `debian.yml`, `redhat.yml`) when present.

[install.sh](install.sh) is the bootstrap entry point for a fresh machine: installs `git`/`ansible`, clones this
repo, and seeds `host_vars/localhost.yml`.

## Repo layout

- `roles/<name>/` — one role per tool/app, standard Ansible role layout (`tasks/`, `defaults/`, `vars/`,
  `templates/`, `files/`, `handlers/`, `meta/`). OS-specific variants are usually split as
  `vars/archlinux.yml`, `vars/debian.yml`, `vars/redhat.yml` and/or `tasks/<os_family>.yml`, selected via
  `ansible_facts.os_family` / `ansible_facts.distribution`.
- `roles/<name>/molecule/default/` — Molecule test scenario, present only for roles that have one (currently
  `nvim`, `opencode`). Not every role is expected to have tests.
- `host_vars/localhost.yml` — machine-local secrets/config (e.g. `ssh_pubkey_email`), gitignored, must be
  created before running any playbook.
- `collections/` — vendored Ansible collections declared in [requirements.yml](requirements.yml)
  (`ansible.posix`, `community.general`, `kewlfft.aur`).
- `callback_plugins/prettify.py` — third-party stdout callback, vendored (do not hand-edit; re-fetched by
  `install.sh` from its upstream repo).
- `scripts/` — helper scripts invoked by pre-commit hooks (see below).

## Making changes

- Match the existing task style: `name:` strings use the `"<Section> | <Step>"` convention (see any file
  under `pre_tasks/`, `post_tasks/`, or `roles/*/tasks/`).
- When a task/variable differs by OS, follow the existing pattern in that role (`vars/<os_family>.yml` include,
  or `when: ansible_facts.os_family == "..."`) rather than inventing a new mechanism.
- Keep `ansible-lint` (`profile: production`, see [.ansible-lint.yml](.ansible-lint.yml)) and `yamlfmt`
  (see [.yamlfmt.yaml](.yamlfmt.yaml)) happy — both run in pre-commit and CI-equivalent checks.
- Indentation: 2 spaces for YAML, 4 spaces otherwise, LF line endings, 120 max line length — see
  [.editorconfig](.editorconfig).
- If a role needs a Molecule scenario, copy the layout from `roles/nvim/molecule/default/` or
  `roles/opencode/molecule/default/` (`molecule.yml`, `prepare.yml`, `converge.yml`, `tests/test_default.py`).

## Validating changes

```sh
# Lint Ansible content (same config pre-commit uses)
ansible-lint -p -q

# Format-check YAML
yamlfmt -lint

# Run a role's Molecule test (only for roles that have a molecule/ directory)
cd roles/<role> && molecule test

# Syntax-check a playbook without applying it
ansible-playbook <playbook>.yml --syntax-check
```

Pre-commit ([.pre-commit-config.yaml](.pre-commit-config.yaml)) runs: trailing-whitespace / end-of-file-fixer /
large-file checks, `yamlfmt`, `codespell`, `luacheck` (Lua files, via
[scripts/run-luacheck.sh](scripts/run-luacheck.sh)), `ansible-lint`, and Molecule tests for changed roles that
have a `molecule/` directory (via [scripts/run-molecule-tests.sh](scripts/run-molecule-tests.sh) — silently
skipped if `molecule` isn't installed). Run `pre-commit run --all-files` before committing if it's set up
locally.

Never run a full playbook (`ansible-playbook development.yml`, etc.) against the agent's own environment — these
playbooks install system packages, change desktop/session config, and touch dotfiles on the *real* target
machine (`hosts: localhost` is literal). Prefer `--syntax-check`, `ansible-lint`, and Molecule tests, which run
in isolated Docker/Podman containers.

## Conventions worth knowing

- Roles are added to a playbook's `roles:` list, optionally gated with `when:` (e.g.
  `when: ansible_facts.hostname == "hbuyse-promax14"` for machine-specific roles, or
  `when: ansible_facts.os_family not in ["Debian"]` for OS-specific alternatives like `fuzzel`/`wofi`).
- `host_vars/localhost.yml` is required but not committed; don't assume its contents beyond what
  [README.md](README.md) documents (`ssh_pubkey_email`).
- `roles/*/README.md` is the stock `ansible-galaxy init` template in most roles and is not kept up to date —
  don't treat it as documentation of that role's actual behavior; read `tasks/main.yml` instead.
