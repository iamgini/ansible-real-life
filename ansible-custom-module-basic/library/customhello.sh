#!/bin/bash

display="This is a simple bash module"
OS="$(uname)"
HOSTNAME="$(uname -n)"
echo -e "{\"changed\": false, \"operating_system\": \"$OS\", \"hostname\": \"$HOSTNAME\", \"Message\":\"Hello, "$display"\"}"