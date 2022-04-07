# Ansible for AWS Systems Manager

## Requirements
The below requirements are needed on the local controller node that executes this connection.

The remote EC2 instance must be running the AWS Systems Manager Agent (SSM Agent).

The control machine must have the aws session manager plugin installed.

The remote EC2 linux instance must have the curl installed.



## Create an Admin IAM user for AWS
https://docs.aws.amazon.com/systems-manager/latest/userguide/setup-create-admin-user.html


## Check SSM managed instances


```shell
$ aws ssm describe-instance-information
```

Goto SSM console -> Run Command
(Change regions as needed)
https://ap-southeast-1.console.aws.amazon.com/systems-manager/run-command?region=ap-southeast-1#


## Install Session Manager plugin on Linux

https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-linux

## Creating Associations

```shell
$ aws ssm create-association --name "AWS-ApplyAnsiblePlaybooks" \
--targets "Key=tag:Name,Values=demo-ec2" \
--parameters '{"SourceType":["GitHub"],"SourceInfo":["{\"owner\":\"ansibleDocumentTest\", \"repository\": \"Ansible\", \"getOptions\": \"branch:master\"}"],"InstallDependencies":["True"],"PlaybookFile":["hello-world-playbook.yml"],"ExtraVariables":["SSM=True"],"Check":["False"],"Verbose":["-v"]}' \
--association-name "AnsibleAssociation" --schedule-expression "cron(0 2 ? * SUN *)"
```

## Verify EC2 instance access from AWS CLI

```shell
[gmadappa@gmadappa Ansible-AWS-systems-manager]$ ^[[200~aws ssm start-session --target ~^C
[gmadappa@gmadappa Ansible-AWS-systems-manager]$ aws ssm start-session --target i-0bc9fc987639f549b

Starting session with SessionId: devops-0b1808ceee8dd5646
sh-4.2$ 
sh-4.2$ whoami
ssm-user
```

## References

- [Running Ansible Playbooks using EC2 Systems Manager Run Command and State Manager](https://aws.amazon.com/blogs/mt/running-ansible-playbooks-using-ec2-systems-manager-run-command-and-state-manager/)
- 