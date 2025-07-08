# ansible.builtin.generator inventory sample

```shell
ansible-inventory -i inventory.yml --list
{
    "_meta": {
        "hostvars": {}
    },
    "all": {
        "children": [
            "ungrouped"
        ]
    },
    "ungrouped": {
        "hosts": [
            "demo_host"
        ]
    }
}
```