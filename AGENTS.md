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
- `group_vars/all.yml` — variables shared by every playbook and by the Molecule scenarios (`alt_arch`, `deb_arch`,
  `os_vars_files`). Facts are not injected as variables (`inject_facts_as_vars = False` in
  [ansible.cfg](ansible.cfg)): use `ansible_facts.os_family`, never `ansible_os_family`.
- `molecule/shared/` — preparation and converge playbooks shared by the Molecule scenarios of the roles.
- `renovate.json` — [Renovate](https://docs.renovatebot.com/) configuration (pinned versions).
  Packages installed with `community.general.cargo`, `community.general.npm`, `community.general.pipx`,
  `ansible.builtin.pip` or `community.general.cpanm` are pinned (`state: present` + version, never `state: latest`) and
  followed by one custom regex manager, so Renovate opens one pull request per package. Put the comment
  `# renovate: datasource=<crate|npm|pypi|cpan> depName=<package>` right above the version line: `version: "1.2.3"`,
  `<role>_version: "1.2.3"`, or `name: "package==1.2.3"` for pip and pipx.
- `host_vars/localhost.yml` — machine-local secrets/config (e.g. `ssh_pubkey_email`), gitignored, must be
  created before running any playbook.
- `collections/` — vendored Ansible collections declared in [requirements.yml](requirements.yml)
  (`ansible.posix`, `community.general`, `kewlfft.aur`).
- `callback_plugins/prettify.py` — stdout callback, originally from
  [roots/ansible-output-prettify](https://github.com/roots/ansible-output-prettify) and now maintained in this repo
  (`install.sh` no longer fetches it, so don't overwrite it with the upstream version). Besides the per-role
  `┌─ <role>` header, it prints dedicated `pre-tasks`, `post-tasks` and `<role> › handlers` sections, handlers
  having their own colors. Test changes with a throwaway playbook using `debug` tasks, not the real playbooks.
- `lookup_plugins/github_latest_release.py` — lookup returning the tag of the latest release of a GitHub repository
  (`lookup('github_latest_release', 'owner/repo')`, uses `GITHUB_TOKEN` when set). Answers are cached for 15 minutes in
  `~/.cache/deployment-ansible/github_latest_release.json` (`GITHUB_LATEST_RELEASE_CACHE_TTL` and
  `GITHUB_LATEST_RELEASE_CACHE_DIR` change it), and a stale answer is used when GitHub is unreachable or rate limited.
  Its unit tests are in `tests/` (`python3 -m pytest tests`). Roles installing a tool from its GitHub releases use it
  instead of calling the API.
- `scripts/` — helper scripts invoked by pre-commit hooks (see below).

## Making changes

- Match the existing task style: `name:` strings are short and capitalized, without a section prefix such as
  `"Pre-tasks | ..."` (see any file under `pre_tasks/`, `post_tasks/`, or `roles/*/tasks/`). The callback already
  prints the role / `pre-tasks` / `post-tasks` / `handlers` header above them.
- When a task/variable differs by OS, follow the existing pattern in that role (`vars/<os_family>.yml` include,
  or `when: ansible_facts.os_family == "..."`) rather than inventing a new mechanism.
  OS variables are loaded with `include_vars: "{{ item }}"` looping over
  `query('ansible.builtin.first_found', ansible_facts.os_family | lower ~ '.yml', skip=true)` (no `skip` when the file
  must exist), copy that task from a role.
  When a role differs between distributions of the same family (Ubuntu and Debian), use `ubuntu.yml` next to
  `debian.yml` and loop over `query('ansible.builtin.first_found', os_vars_files, paths=[role_path ~ '/vars'])` (and
  `/tasks` for the task files): `os_vars_files` (in [group_vars/all.yml](group_vars/all.yml)) lists the distribution
  file, then the family one. Packages that exist only in the AUR go in `<role>_aur_packages`, installed by `kewlfft.aur.aur`
  and turned off by `<role>_aur: false`.
- Tags: the tags shared by all the tasks of a role are declared once on its entry in the playbooks
  (`- role: "yq"` then `tags: yq`), not on each task, because role tags are also inherited by the tasks it includes.
  Only put `tags:` on a task for a subset of the role (e.g. `clangd`). A role with `meta` dependencies, or used as a
  dependency (`rustup`, `golang`, `direnv`…), keeps its tags on its tasks: Ansible runs a dependency only once, so
  with `--tags` the first inclusion, under the parent's tags, would skip the later explicit entry.
  A dependency that is never listed in a playbook (`sway_session`) is not concerned: it runs with the tags of the role
  that needs it, so the roles that only depend on such a role keep their tags in the playbooks.
- Keep `ansible-lint` (`profile: production`, see [.ansible-lint.yml](.ansible-lint.yml)) and `yamlfmt`
  (see [.yamlfmt.yaml](.yamlfmt.yaml)) happy — both run in pre-commit and CI-equivalent checks.
- Indentation: 2 spaces for YAML, 4 spaces otherwise, LF line endings, 120 max line length — see
  [.editorconfig](.editorconfig).
- If a role needs a Molecule scenario, copy the `molecule.yml` and `tests/test_default.py` of a similar role (for
  instance `roles/jq/molecule/default/`). The scenarios use the playbooks of [molecule/shared/](molecule/shared/) and
  select what to prepare with `molecule_*` variables (documented at the top of `prepare.yml` and `converge.yml`); extra
  preparation goes in `tasks/prepare.yml` next to `molecule.yml`. Install the tools with
  `pip install -r requirements-molecule.txt`.

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
