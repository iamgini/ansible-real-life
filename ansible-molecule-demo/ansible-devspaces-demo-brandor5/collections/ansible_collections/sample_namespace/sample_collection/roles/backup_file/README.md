backup_file
=========

Sample role to demonstrate running molecule inside of OpenShift Dev Spaces. Molecule is configured to leverage the downstream API to create containers in the user's devspace namespace. This role does not require elevated permissions or modifications to OpenShift.

Requirements
------------

- The Kubernetes python module is required. This is installed to the DevSpace as part of the molecule prepare stage.
- The 'oc' binary is required. This is installed as part of the molecule prepare stage and added to ~/.bashrc. If you need to run oc commands you can source your bashrc file after running the prepare. `source ~/.bashrc`
- kubernetes.core collection
- community.okd or redhat.openshift collection
- Required collections are included in the requirements.yml file that can be installed with `ansible-galaxy install -r requirements.yml` command


Manually installing dependencies (rather than using `molecule prepare`)
-------------

Download the 'oc' binary from the downloads route local to the cluster and add to path

```
mkdir $HOME/bin
curl -o $HOME/bin/oc http://downloads.openshift-console.svc.cluster.local/amd64/linux/oc
chmod u+x $HOME/bin/oc
export PATH=$PATH:$HOME/bin
```

OpenShift Token is automatically injected. You can verify this by running the following commands:

```
oc whoami
oc get pods
```

Install the required collections:

```
ansible-galaxy collection install -r demo/backup_file/requirements.yml
```

Role Variables
--------------

| Name | Required | Default | Type | Description |
| ------- | -------- | -------- | ---------- | ------------------------|
| backup_file_source | yes | '/etc/hosts' | string | The file to be backed up |
| backup_file_dest_folder | yes | '/tmp/backups' | string | The folder where backups are stored |
| backup_file_dest_suffix | no | '.bak' | string | The suffix to be appended to backup files |
| backup_file_dest_dir_owner | no | current user id | string | The owner permission for back up folder |
| backup_file_dest_dir_group | no | current group id | string | The group permission for the back up folder |
| backup_file_dest_dir_mode | no | '0750' | string | The mode permission for the backup folder |
| backup_file_dest_owner | no | current user id | string | The owner permission for the backed up file |
| backup_file_dest_group | no | current group id | string | The group permission for the backed up file |
| backup_file_dest_mode | no | '0640' | string | The mode permission for the backed up file |
| backup_file_remote_source | no | true | bool | If the source file exists on the remote system |

Dependencies
------------

No dependencies other than the collections included in the requirements.yml

- kubernetes.core collection
- community.okd or redhat.openshift collection
- Required collections are included in the requirements.yml file that can be installed with `ansible-galaxy install -r requirements.yml` command

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

  - name: Simple test case
    hosts: all
    connection: community.okd.oc
    vars:
      backup_file_source: '/etc/resolv.conf'
      backup_file_dest_folder: '/tmp/backups'
    roles:
      - backup_file

License
-------

GNU General Public License v3.0 or later
