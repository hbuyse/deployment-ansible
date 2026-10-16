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

- clang
- claude_code
- docker
- nodejs
- nvim
- opencode
- rustup
- ssh
- zsh

To run the tests, change your directory to the role you want to test and run the following:

```sh
molecule test
```

The `github_latest_release` lookup plugin has unit tests:

```sh
python3 -m pytest tests
```

## Troubleshooting

```sh
ANSIBLE_STDOUT_CALLBACK=default ansible-playbook -K --vault-password-file=~/.ansible-pass.txt <playbook>.yml -vv
```
