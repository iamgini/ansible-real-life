
## Prepare the Library Directory and add modules

```shell
$ mkdir library
touch library/customhello.sh
# add content
```

## Variables

```yaml
    - name: Application Name and Version
      customapp:
        application_name: python
        application_version: 3.8
```

We have variables `application_name` and `application_version`. We can get the name of this file from the `$1` variable (make sure bash syntax is correct). Source the variable content to convert these arguments to bash variables.

```shell
source $1
```

This will create the variables `$application_name` and `$application_version`.

## Output

The output from your module must be in JSON format. If you return any other output, Ansible will treat it as a failure. 

- `changed`: Return this if your module was successful. Set it to true if it made any changes or false if everything was already in the correct state.

- `failed`: set this to true if your modules failed. You can set it to false if you module worked, or you can leave it out and Ansible will assume it worked.

- `msg`: Return an error message if your module failed. You can also set this to an information message on success.

## Reference
- [Writing Ansible Modules in Bash](https://github.com/pmarkham/writing-ansible-modules-in-bash/blob/master/ansible_bash_modules.md)