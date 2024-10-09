# deployment-ansible

System configuration based on Ansible

```sh
pip install ansible ansible-core watchdog
if grep -q "ID_LIKE=debian" /etc/os-release; then
    pip install python-debian
fi
```
