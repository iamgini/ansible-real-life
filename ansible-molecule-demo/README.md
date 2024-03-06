# Ansible Molecule

Important:

- Molecule supports only the latest two major versions of Ansible (N/N-1), meaning that if the latest version is 2.9.x, we will also test our code with 2.8.x.

## Installation

```shell
$ python3 -m pip install molecule

$ molecule --version
molecule 6.0.3 using python 3.12
    ansible:2.16.2
    default:6.0.3 from molecule
```

## Configure `COLLECTIONS_PATHS`

Add the custom collection path in `~/.ansible.cfg`

```ini
[defaults]
COLLECTIONS_PATHS = ./collections:~/.ansible/collections/ansible_collections:/usr/share/ansible/collections/ansible_collections:/home/iamgini/ansible/ansible-real-life/ansible-molecule-demo/

```

## Using Molecule

```shell
$ cd collections/ansible_collections/

$ ansible-galaxy collection init iamgini.moleculedemo
- Collection iamgini.moleculedemo was created successfully
```

Create a demo role

```shell
$ cd roles/

$ ansible-galaxy role init demo_role
- Role demo_role was created successfully
```

Update the `demo_role/tasks/main.yml`

```yaml
---
# tasks file for demo_role
- name: A test task from Molecule demo role
  ansible.builtin.debug:
    msg: "A test task from Molecule demo role."
```

Create a playbook in collection directory (`playbooks/install_web.yaml`)

```yaml
---
- name: Demo Molecule playbook
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Role Testing
      ansible.builtin.include_role:
        name: iamgini.moleculedemo.demo_role
        tasks_from: main.yml
```

Create a new directory in your collection called `extensions` and init molecule scenarios.

```shell
$ mkdir extensions
$ cd extensions/
$ molecule init scenario
INFO     Initializing new scenario default...

PLAY [Create a new molecule scenario] ******************************************

TASK [Check if destination folder exists] **************************************
changed: [localhost]

TASK [Check if destination folder is empty] ************************************
ok: [localhost]

TASK [Fail if destination folder is not empty] *********************************
skipping: [localhost]

TASK [Expand templates] ********************************************************
changed: [localhost] => (item=molecule/default/destroy.yml)
changed: [localhost] => (item=molecule/default/molecule.yml)
changed: [localhost] => (item=molecule/default/create.yml)
changed: [localhost] => (item=molecule/default/converge.yml)

PLAY RECAP *********************************************************************
localhost                  : ok=3    changed=2    unreachable=0    failed=0    skipped=1    rescued=0    ignored=0

INFO     Initialized scenario in /home/iamgini/ansible/ansible-real-life/ansible-molecule-demo/iamgini/moleculedemo/extensions/molecule/default successfully.
```

```shell
$  tree molecule/
molecule/
└── default
    ├── converge.yml
    ├── create.yml
    ├── destroy.yml
    └── molecule.yml

2 directories, 4 files
```



## References

- [Ansible Molecule Documentation](https://ansible.readthedocs.io/projects/molecule/)
- [devspaces-samples/ansible-devspaces-demo](https://github.com/devspaces-samples/ansible-devspaces-demo)
- [Developing and Testing Ansible Roles with Molecule and Podman - Part 1](https://www.ansible.com/blog/developing-and-testing-ansible-roles-with-molecule-and-podman-part-1)
- [Developing and Testing Ansible Roles with Molecule and Podman - Part 2](https://www.ansible.com/blog/developing-and-testing-ansible-roles-with-molecule-and-podman-part-2)
- [Testing Ansible Automation with Molecule Pt. 2](https://medium.com/contino-engineering/testing-ansible-automation-with-molecule-pt-2-7e2ff5a70bcc)