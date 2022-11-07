
```shell
$  ansible-playbook site.yml 

PLAY [Floating Point Operation] ************************************************

TASK [Print tagname] ***********************************************************
ok: [localhost] => {
    "msg": "0.0"
}

TASK [Increment tagname value] *************************************************
ok: [localhost]

TASK [Print the String] ********************************************************
ok: [localhost] => {
    "msg": "0.1"
}

PLAY RECAP *********************************************************************
localhost                  : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

```
$  ansible-playbook site.yml -e 'tagname="0.3"'

PLAY [Floating Point Operation] ************************************************

TASK [Print tagname] ***********************************************************
ok: [localhost] => {
    "msg": "0.3"
}

TASK [Increment tagname value] *************************************************
ok: [localhost]

TASK [Print the String] ********************************************************
ok: [localhost] => {
    "msg": "0.3"
}

PLAY RECAP *********************************************************************
localhost                  : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

```
$  ansible-playbook site.yml -e 'tagname="0.2"'

PLAY [Floating Point Operation] ************************************************

TASK [Print tagname] ***********************************************************
ok: [localhost] => {
    "msg": "0.2"
}

TASK [Increment tagname value] *************************************************
ok: [localhost]

TASK [Print the String] ********************************************************
ok: [localhost] => {
    "msg": "0.2"
}

PLAY RECAP *********************************************************************
localhost                  : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```