#!/usr/bin/python

DOCUMENTATION = '''
---
module: hello_message
short_description: A Hello Message Module
version_added: "2.10"
description:
    - "A Hello Message Module"
options:
    message:
        description:
            - The message to be printed.
        required: true
        type: string
    name:
        description:
            - The name of the person.
        required: false
        type: string
      
author:
    - Gineesh Madapparambath (@ginigangadharan)
'''

EXAMPLES = '''
# Simple Custom Hello App
- name: Calling hello_message module
  hello_message:
    message: "Hello"
    name: "John"
'''

RETURN = '''
greeting:
    description: Hello Response
    returned: success
    type: str
    sample: Hello World
os_version:
    description: Operating System Information
    returned: success
    type: str
    sample: Linux 4.18.0-305.el8.x86_64 #1 SMP Thu Apr 29 08:54:30 EDT 2021
'''

from ansible.module_utils.basic import *

def main():
    module_args = dict(
        message=dict(type='str', required=True),
        name=dict(type='str', required=False),
    )
    result = dict(
        changed=False,
        greeting='Sample Message',
        os_version=''
    )
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if check mode
    if module.check_mode:
        module.exit_json(**result)

    # default name
    source_name = "World"

    # if message is fail, then fail
    if module.params['message'] == 'fail':
        module.fail_json(msg='Failing this module', **result)
    
    if module.params['name']:
        source_name = module.params['name']

    result['greeting'] = module.params['message'] + " " + source_name
    result['os_version'] = platform.system()+ " " + platform.release() + " " + platform.version()
    module.exit_json(**result)

if __name__ == "__main__":
    main()