# deployment-ansible

System configuration based on Ansible

```bash
git clone https://github.com/hbuyse/deployment-ansible
cd deployment-ansible
bash ./install.sh
```

> [!WARNING] Do not forget to specify some variables in the host_vars/localhost.yml file

## Testing

Some roles have tests. Here is the list:

- ansiblelint
- ansiblels
- bashls
- bitwarden
- black
- brightnessctl
- btop
- cava
- clang
- claude_code
- claude_desktop
- codespell
- composels
- cssls
- direnv
- docker
- fastfetch
- fd
- foot
- fuzzel
- gdm
- ghostty
- golang
- greetd
- htmlls
- isort
- jq
- jsonls
- kanshi
- libreoffice
- luals
- markdownls
- mimeapps
- minicom
- nerdfonts
- netrc
- nextcloud
- nodejs
- npmrc
- nvim
- oh_my_posh
- opencode
- owncloud_client
- perlnavigator
- perltidy
- pipx
- podman
- pre_commit
- prettier
- python
- qemu_kvm
- ruff
- rustup
- shellcheck
- shfmt
- spotify
- ssh
- sway
- swayidle
- swaylock
- swaync
- tailwindcss_lsp
- texlab
- themes
- thunderbird
- tmux
- tombi
- tuigreet
- tuned
- user
- vscode
- vscodium
- wallpapers
- waybar
- web_browsers
- webapplications
- wireplumber
- wireshark
- wlprop
- wlsunset
- wofi
- xdg_desktop_portal
- xfce4
- yamlfmt
- yamlls
- yq
- zoom
- zsh

To run the tests, install the tools (`pip install -r requirements-molecule.txt`), change your directory to the role you
want to test and run the following:

```sh
molecule test
```

The scenarios share their preparation and converge playbooks, in [molecule/shared/](molecule/shared/): a scenario is a
`molecule.yml` (platforms, and the `molecule_*` variables that tell the shared playbooks what to prepare) and a
`tests/test_default.py`. Copy the `molecule.yml` of a similar role to add one.

The `github_latest_release` lookup plugin has unit tests:

```sh
python3 -m pytest tests
```

## Troubleshooting

```sh
ANSIBLE_STDOUT_CALLBACK=default ansible-playbook -K --vault-password-file=~/.ansible-pass.txt <playbook>.yml -vv
```
