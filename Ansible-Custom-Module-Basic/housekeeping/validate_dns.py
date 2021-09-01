#!/usr/bin/python3

# Deprecated due to the introduction of collection; still keeping here
ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: validate_dns
short_description: DNS Validation Module
version_added: "2.10"
description:
    - "DNS Validation Module"
options:
    dns_server_ip:
        description:
            - The DNS Server to validate the DNS entries.
        required: true
    dns_address:
        description:
            - The DNS Address to be validated.
        required: true
        type: list
    target_ip_address:
        description:
            - The Target IP Address to be matched.
        required: true
      
author:
    - Gineesh Madapparambath (@ginigangadharan)
'''

EXAMPLES = '''
# Validate single URL
- name: validate_dns
  validate_dns:
    target_ip_address: 10.1.10.10
    dns_server_ip: 1.1.1.1
    dns_address:
      - example.com
    
# Validate Multiple URLs
- name: validate_dns
  validate_dns:
    target_ip_address: 10.1.10.10
    dns_server_ip: 1.1.1.1
    dns_address:
      - example.com
      - abc.com
      - xyz.com
'''

RETURN = '''
'''

from ansible.module_utils.basic import AnsibleModule


#import os
#import socket
#import subprocess, shlex
#
#class bcolors:
#    HEADER = '\033[95m'
#    OKBLUE = '\033[94m'
#    OKGREEN = '\033[92m'
#    WARNING = '\033[93m'
#    FAIL = '\033[91m'
#    ENDC = '\033[0m' #no color
#    BOLD = '\033[1m'
#    UNDERLINE = '\033[4m'
#    INFO='\033[0;36m'
#myfilename = 'ping.txt'
#
#def pinghost(hostname):
#    command_line = "/bin/ping -c1 " + hostname
#    args = shlex.split(command_line)
#    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#    pingStatus = 'ok';	
#    for line in p.stdout:
#        output = line.rstrip().decode('UTF-8')
#        if (output.endswith('unreachable.')) :
#            #No route from the local system. Packets sent were never put on the wire.
#            pingStatus = 'unreacheable'
#            break
#        elif (output.startswith('Ping request could not find host')) :
#            pingStatus = 'host_not_found'
#            break
#        elif ('unknown' in output ) :
#            pingStatus = 'host_not_found'
#            break
#        elif (output.startswith('1 packets transmitted, 0 received')) :
#            pingStatus = 'no'
#            break
#        if (output.startswith('Request timed out.')) :
#            #No Echo Reply messages were received within the default time of 1 second.
#            pingStatus = 'timed_out'
#            break
#        #end if
#    #endFor
#    return pingStatus
##endDef    
#
#print (bcolors.INFO + 'DNS Test - ver 2.2.0.\n' + bcolors.ENDC)
#timestart = "$(date)"
#counter = 0
#pingcount = 0
#dnscount = 0
#nodnscount = 0
#print (bcolors.OKBLUE + bcolors.UNDERLINE +'%-4s |%-18s |%-6s |%s' % ('No.',"Hostname","Ping","STATUS") + bcolors.ENDC)
#with open(myfilename,mode='r') as varfile:
#  for line in varfile:
#    counter = counter + 1
#    line = line.replace('\n','')
#    try:
#      startcolor = bcolors.OKGREEN
#      statusText2 = ''
#      addr = socket.gethostbyname(line)
#      pingresp = pinghost(addr)
#      if addr:
#        fqdn = socket.getfqdn(line) 
#        dnscount = dnscount + 1
#        if pingresp == 'ok':
#          pingcount = pingcount + 1
#        else:
#          startcolor = bcolors.WARNING
#          statusText2 = bcolors.FAIL + '[host not reachable]'
#      pingResponse = pingresp
#      statusText = fqdn + ',' + addr + statusText2
#    except IOError:
#      nodnscount = nodnscount + 1
#      statusText = 'NO DNS Entry Found'
#      pingResponse = 'na'
#      startcolor = bcolors.FAIL
#    #else:
#      #print 'Done'
#    finally:
#      print (startcolor + '%-4s |%-18s |%-6s |%s' % ( counter ,line,pingResponse,statusText) + bcolors.ENDC)
#
#varfile.close() #close the file
#
#timeend = "$(date)"
#print (bcolors.OKBLUE + "\n======================== Summary ======================================" + bcolors.ENDC)
#print (bcolors.OKGREEN , dnscount , "with DNS |" + bcolors.WARNING , nodnscount , "without DNS |" + bcolors.OKGREEN , pingcount , " reachable" + bcolors.ENDC)
#