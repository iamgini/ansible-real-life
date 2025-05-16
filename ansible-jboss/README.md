# Changes made to redhat.eap collection

Note: Due to the timeline constraints, we 'forked' the `redhat.eap` as `jboss.eap` (to avoid any naming clashes). There might be original collection way to do this but we couldn't spend much time to explore the exact usage as per the customer requirement.

This is a tracker for the changes we made to the collection; hopefully we can prepare a PR later to the original collection once we have time.

Also check [`collection-diff-auto`](collection-diff-auto.log)


(diff -r ~/ansible-bau/ansible-jboss-automation/collections/ansible_collections/jboss/eap8/roles/ ~/ansible-bau/jboss/redhat-eap-1.5.7/roles/ > collection-diff-auto.log)

- [Changes made to redhat.eap collection](#changes-made-to-redhateap-collection)
  - [eap\_install/tasks/systemd-v2.yml](#eap_installtaskssystemd-v2yml)
  - [eap\_systemd/vars/main.yml](#eap_systemdvarsmainyml)
  - [eap\_systemd/templates/wfly.conf.j2](#eap_systemdtemplateswflyconfj2)
  - [ap\_systemd/templates/wfly.service.j2](#ap_systemdtemplateswflyservicej2)
  - [eap\_systemd/tasks/main.yml](#eap_systemdtasksmainyml)
  - [eap\_uninstall/handlers/systemd.yml](#eap_uninstallhandlerssystemdyml)
  - [eap\_uninstall/handlers/main.yml](#eap_uninstallhandlersmainyml)
  - [eap\_uninstall/defaults/main.yml](#eap_uninstalldefaultsmainyml)
  - [eap\_utils/tasks/jboss\_cli.yml](#eap_utilstasksjboss_cliyml)

## eap_install/tasks/systemd-v2.yml

Tto fix the SElinux if non-standard base directory path - eg: `/apps/jboss`

```yaml
    - name: Update SELinux type of standalone.sh to bin_t
      ansible.builtin.command: "chcon -t bin_t {{ eap_install_workdir }}/jboss-eap-8.0/bin/standalone.sh"
      register: selinux_output_1
      changed_when: selinux_output_1.stdout_lines | length > 0
      become: true
```

Also commented out several steps as we are cloning the entire standalone directory instead of individual files and config.

## eap_systemd/vars/main.yml

```yaml
eap_systemd:
  instance_name: "{{ eap_app_name }}{{ eap_instance_item }}"
  .
  .
  selinux:
    pid_path: "/run/{{ eap_app_name }}{{ eap_instance_item }}"
  log_dir: "{{ eap_home }}/log"
```

## eap_systemd/templates/wfly.conf.j2

- `-Djboss.node.name={{ eap_instance_name }}`

> `-Djboss.node.name={{ eap_systemd.instance_name }}`

- `JBOSS_PIDFILE={{ eap_systemd.selinux.pid_path }}/{{ eap_instance_name }}.pid`

> `JBOSS_PIDFILE={{ eap_systemd.selinux.pid_path }}/{{ eap_systemd.instance_name }}.pid`

- `EAP_SERVER_CONFIG={{ eap_config_base }}.xml`

> `EAP_SERVER_CONFIG={{ eap_config_base }}`

## ap_systemd/templates/wfly.service.j2

- `RuntimeDirectory={{ eap_instance_name }}`

> `RuntimeDirectory={{ eap_systemd.instance_name }}`

- Added

## eap_systemd/tasks/main.yml

```yaml
- name: Clone standalone dir to {{ eap_systemd.instance_name }}
  become: true
  ansible.builtin.copy:
    src: "{{ eap_home }}/standalone/"
    dest: "{{ eap_home }}/{{ eap_systemd.instance_name }}/"
    group: "{{ eap_systemd.group }}"
    owner: "{{ eap_systemd.user }}"
    mode: '0755'
    remote_src: true
```

## eap_uninstall/handlers/systemd.yml

renamed the file to `eap_uninstall/handlers/main.yml`

## eap_uninstall/handlers/main.yml

- `eap_uninstall_systemd_service_file: "/usr/lib/systemd/system/{{ eap_uninstall_service_name }}.service"`

> `eap_uninstall_systemd_service_file: "/etc/systemd/system/{{ eap_uninstall_service_name }}.service"`

## eap_uninstall/defaults/main.yml

Amended to match with the `eap_install` variables

```yaml
eap_uninstall_config_file_location: '/etc/sysconfig'
eap_uninstall_conf_file_suffix: '.conf'
eap_uninstall_service_config_location: '/etc/systemd/system'
eap_uninstall_service_config_file_suffix: '.service'
eap_uninstall_systemd_service_file: "{{ eap_uninstall_service_config_location }}/{{ eap_uninstall_service_name }}.{{ eap_uninstall_service_config_file_suffix }}"
eap_uninstall_systemd_service_conf_file: "{{ eap_uninstall_config_file_location }}/{{ eap_uninstall_service_name }}{{ eap_uninstall_conf_file_suffix }}"
```

(2025-05-16 onwards)

## eap_utils/tasks/jboss_cli.yml

Setting `jboss_cli_controller_port` variable will increase the value unnecessarily when we call the `jboss_cli.yml` multiple times.
And if any error, the `Reset CLI port to default` task will be skipped! Hence, moved the execution inside a block and `Reset CLI port to default` to  the `always` section.
