# Ansible execution using AWS Systems Manager connection

## Requirements

The below requirements are needed on the local controller node that executes this connection.

- The remote EC2 instance must be running the AWS Systems Manager Agent (SSM Agent).
- The control machine must have the aws session manager plugin installed.
- The remote EC2 linux instance must have the curl installed.

- [Ansible execution using AWS Systems Manager connection](#ansible-execution-using-aws-systems-manager-connection)
  - [Requirements](#requirements)
  - [Steps involved](#steps-involved)
    - [Install SSM Agent on EC2 instance](#install-ssm-agent-on-ec2-instance)
    - [Create an IAM instance profile for Systems Manager](#create-an-iam-instance-profile-for-systems-manager)
    - [Attach an IAM instance profile to an Amazon EC2 instance](#attach-an-iam-instance-profile-to-an-amazon-ec2-instance)
    - [Verify the instances under AWS System Manager -> Fleet Manager](#verify-the-instances-under-aws-system-manager---fleet-manager)
    - [Create an S3 bucket](#create-an-s3-bucket)
    - [Install Session Manager plugin on controlnode](#install-session-manager-plugin-on-controlnode)
    - [Verify EC2 instance access from AWS CLI](#verify-ec2-instance-access-from-aws-cli)
  - [Ansible Inventory](#ansible-inventory)
  - [Ansible Playbook](#ansible-playbook)
  - [Troubleshooting](#troubleshooting)
    - [`aws_ssm.py` Bug](#aws_ssmpy-bug)
    - [Creating Associations (Not required)](#creating-associations-not-required)
  - [References](#references)

## Steps involved

After creating the EC2 instances (manual or auto), follow the steps below.

### Install SSM Agent on EC2 instance

[Manually install SSM Agent on EC2 instances for Linux](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-manual-agent-install.html)

In most cases SSM agent will be installed on AMI's (eg: below)

```shell
ubuntu@ip-172-31-23-232:~$ sudo snap install amazon-ssm-agent --classic
snap "amazon-ssm-agent" is already installed, see 'snap help refresh'
```

### Create an IAM instance profile for Systems Manager 

[Documentation](https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-instance-profile.html)

### Attach an IAM instance profile to an Amazon EC2 instance

[Attach the Systems Manager instance profile to an existing instance (console)](https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-launch-managed-instance.html#setup-launch-managed-instance-existing)

### Verify the instances under AWS System Manager -> Fleet Manager

Check [Fleet Manager](https://ap-southeast-1.console.aws.amazon.com/systems-manager/managed-instances?region=ap-southeast-1) and verify instances are manageble using SSM.

### Create an S3 bucket

This bucket need to pass to the playbook for filetransfer

### Install Session Manager plugin on controlnode

[Install Session Manager plugin on Linux](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-linux)

Check SSM managed instances from controlnode

```shell
$ aws ssm describe-instance-information
```

### Verify EC2 instance access from AWS CLI

```shell
[iamgini@iamgini Ansible-AWS-systems-manager]$ ^[[200~aws ssm start-session --target ~^C
[iamgini@iamgini Ansible-AWS-systems-manager]$ aws ssm start-session --target i-0bc9fc987639f549b

Starting session with SessionId: devops-0b1808ceee8dd5646
sh-4.2$ 
sh-4.2$ whoami
ssm-user
```

## Ansible Inventory

```ini
[me]
localhost ansible_connection=local

[nodes]
i-0339dcfa7070e9c5e
```

## Ansible Playbook

Remember to pass the [`aws_ssm`](https://docs.ansible.com/ansible/latest/collections/community/aws/aws_ssm_connection.html) connection plugin variables.

```yaml
---
- name: Install httpd
  hosts: nodes
  become: true
  #gather_facts: false
  vars:
    #ansible_python_interpreter: /usr/bin/python3
    ansible_user: ssm-user
    ansible_aws_ssm_profile: devops
    ansible_connection: community.aws.aws_ssm
    ansible_aws_ssm_bucket_name: "ansible-demo-bucket-2022apr07"
    ansible_aws_ssm_region: ap-southeast-1
```

```shell
(ansible210) [iamgini@iamgini Ansible-AWS-systems-manager]$ ansible-playbook deploy-web.yaml 
PLAY [Install httpd] *************************************************************************

TASK [Gathering Facts] ***********************************************************************
ok: [i-0339dcfa7070e9c5e]

TASK [Install vim] ***************************************************************************
ok: [i-0339dcfa7070e9c5e]

TASK [Node info] 
ok: [i-0339dcfa7070e9c5e] => {
    "msg": [
        "172.31.25.63"
    ]
}

TASK [OS info] *******************************************************************************
ok: [i-0339dcfa7070e9c5e] => {
    "msg": "Ubuntu"
}

PLAY RECAP ***********************************************************************************
i-0339dcfa7070e9c5e        : ok=4    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

## Troubleshooting

### `aws_ssm.py` Bug

There is a bug in the `aws_ssm.py` and the workaround can be found [here](https://github.com/ansible-collections/community.aws/issues/113#issuecomment-686617173)

File: 

`YOUR_PATH/collections/ansible_collections/community/aws/plugins/connection/aws_ssm.py`

```python
--- a/plugins/connection/aws_ssm.py	2020-09-03 18:43:43.818000000 +0200
+++ b/plugins/connection/aws_ssm.py	2020-09-03 18:43:19.805000000 +0200
@@ -288,11 +288,17 @@
 
         profile_name = ''
         region_name = self.get_option('region')
-        ssm_parameters = dict()
 
         client = boto3.client('ssm', region_name=region_name)
         self._client = client
-        response = client.start_session(Target=self.instance_id, Parameters=ssm_parameters)
+
+        if self.is_windows:
+            ssm_parameters = dict()
+            response = client.start_session(Target=self.instance_id, Parameters=ssm_parameters)
+        else:
+            ssm_parameters = {"command": ["bash -l"]}
+            response = client.start_session(Target=self.instance_id, DocumentName="AWS-StartInteractiveCommand", Parameters=ssm_parameters)
+
         self._session_id = response['SessionId']
 
         cmd = [
```

### Creating Associations (Not required)

```shell
$ aws ssm create-association --name "AWS-ApplyAnsiblePlaybooks" \
--targets "Key=tag:Name,Values=demo-ec2" \
--parameters '{"SourceType":["GitHub"],"SourceInfo":["{\"owner\":\"ansibleDocumentTest\", \"repository\": \"Ansible\", \"getOptions\": \"branch:master\"}"],"InstallDependencies":["True"],"PlaybookFile":["hello-world-playbook.yml"],"ExtraVariables":["SSM=True"],"Check":["False"],"Verbose":["-v"]}' \
--association-name "AnsibleAssociation" --schedule-expression "cron(0 2 ? * SUN *)"
```

## References

- [Running Ansible Playbooks using EC2 Systems Manager Run Command and State Manager](https://aws.amazon.com/blogs/mt/running-ansible-playbooks-using-ec2-systems-manager-run-command-and-state-manager/)
- [How To Add An EC2 Instance To AWS System Manager (SSM)](https://cloudaffaire.com/how-to-add-an-ec2-instance-to-aws-system-manager-ssm/)
- [Create an Admin IAM user for AWS](https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-create-admin-user.html)