Issue scenario:

Playbook

```shell
---
- name: Floating Point Operation
  hosts: localhost
  gather_facts: false
  vars:
    tagname: 1.1
    increment: 0.3
  tasks:
    - name: Print tagname
      debug:
        msg: "{{ tagname }}"

    - name: Increment tagname value
      set_fact:
        #tagname: "{{ tagname | float }}" #" + 0.1  }}"
        tagname: "{{ tagname | float  + increment | float }}"

    - name: Print the String
      debug:
        msg: "{{ tagname }}"
```

Output:

```shell
$  ansible-playbook site.yml 

PLAY [Floating Point Operation] ***********************************************************************************

TASK [Print tagname] **********************************************************************************************
ok: [localhost] => {
    "msg": 1.1
}

TASK [Increment tagname value] ************************************************************************************
ok: [localhost]

TASK [Print the String] *******************************************************************************************
ok: [localhost] => {
    "msg": "1.4000000000000001"
}

PLAY RECAP ********************************************************************************************************
localhost                  : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

Ansible version:

```shell
$ ansible --version
ansible [core 2.11.12] 
  config file = /home/iamgini/ansible/ansible-real-life/ansible-floating-point-operation/ansible.cfg
  configured module search path = ['/home/iamgini/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /home/iamgini/pyvirt/ansible-plain/lib64/python3.10/site-packages/ansible
  ansible collection location = /home/iamgini/.ansible/collections:/usr/share/ansible/collections
  executable location = /home/iamgini/pyvirt/ansible-plain/bin/ansible
  python version = 3.10.8 (main, Oct 12 2022, 00:00:00) [GCC 12.2.1 20220819 (Red Hat 12.2.1-2)]
  jinja version = 3.1.2
  libyaml = True
```

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