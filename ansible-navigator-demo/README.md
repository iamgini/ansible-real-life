# Ansible Navigator Demo

## Installing `ansible-navigator`

```shell
## Using Python
$ python3 -m pip install ansible-navigator --user

## Using package manager on RHEL
## ------ A subscription is required ------
$ dnf install \
  --enablerepo=ansible-automation-platform-2.4-for-rhel-8-x86_64-rpms \
  ansible-navigator
```

## `ansible-navigator` settings

```yaml
---
ansible-navigator:
  editor:
    command: code-server {filename}
    console: false
  execution-environment:
    container-engine: podman
    enabled: true
    image: registry.redhat.io/ansible-automation-platform-24/ee-supported-rhel8:1.0.0-395
    pull:
      policy: missing
    volume-mounts:
      - dest: /tempreports/
        options: Z
        src: /tmp/reports
  logging:
    append: false
  mode: stdout
  playbook-artifact:
    enable: true
    replay: artifacts/{playbook_name}-artifact-{time_stamp}.json
    save-as: artifacts/{playbook_name}-artifact-{time_stamp}.json

```

### Sample settings

```yaml
$  ansible-navigator settings --sample
---
ansible-navigator:
#   ansible:
#     config:
#       # Help options for ansible-config command in stdout mode
#       help: False
#       # Specify the path to the ansible configuration file
#       path: ./ansible.cfg
#     # Extra parameters passed to the corresponding command
#     cmdline: "--forks 15"
...<omitted for brevity>...
#   settings:
#     # Show the effective settings. Defaults, CLI parameters, environment
#     # variables, and the settings file will be combined
#     effective: False
#     # Generate a sample settings file
#     sample: False
#     # Generate a schema for the settings file ('json'= draft-07 JSON Schema)
#     schema: json
#     # Show the source of each current settings entry
#     sources: False
#   # Specify the IANA time zone to use or 'local' to use the system time
#   # zone
#   time-zone: UTC


```

## How to use `ansible-navigator`

```shell
$ ansible-navigator run site.yaml -m stdout

$ ansible-navigator exec -m stdout -- ansible  localhost -m ping
localhost | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/libexec/platform-python"
    },
    "changed": false,
    "ping": "pong"
}
```

```shell
$  ansible-navigator exec -m stdout -- ansible --version
ansible [core 2.13.7]
  config file = /home/iamgini/ansible-bau/infrastructure-automation/ansible.cfg
  configured module search path = ['/home/runner/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/lib/python3.9/site-packages/ansible
  ansible collection location = /home/iamgini/ansible-bau/infrastructure-automation/collections
  executable location = /usr/bin/ansible
  python version = 3.9.13 (main, Nov  9 2022, 13:16:24) [GCC 8.5.0 20210514 (Red Hat 8.5.0-15)]
  jinja version = 3.0.3
  libyaml = True

```

## Replay

Configuration:

```yaml
---
ansible-navigator:
  playbook-artifact:
  enable: true
    replay: artifacts/{playbook_name}-artifact-{time_stamp}.json
    save-as: artifacts/{playbook_name}-artifact-{time_stamp}.json
```

```shell
$ ansible-navigator replay artifacts/site-artifact-2023-09-24T08:31:39.472901+00:00.json
```

```shell
$ ansible-navigator run openshift-node-restart.yaml \
  --penv OPENSHIFT_LOGIN_USERNAME \
  --penv OPENSHIFT_LOGIN_PASSWORD \
  --penv EMAIL_TO \
  --penv EMAIL_SMTP_SERVER \
  --penv EMAIL_SMTP_PORT \
  --penv EMAIL_SMTP_USERNAME \
  --penv EMAIL_SMTP_PASSWORD \
  -e "ocp_cluster=RH_DEV node_name=computer103"

```

## References

- [Ansible Navigator Cheat Sheet](https://www.techbeatly.com/ansible-navigator-cheat-sheet/)