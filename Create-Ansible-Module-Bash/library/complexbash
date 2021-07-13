#!/bin/bash

function create_file
    {
    if [ -f "$dest" ]; then
        changed="false"
        msg="file already exists"
    else
        echo 'Hello, "world!"' >> $dest
        changed="true"
        msg="file created"
    fi   
    contents=$(cat "$dest" 2>&1 | python -c 'import json,sys; print json.dumps(sys.stdin.read())')
    }

function delete_file
    {
    if [ -f "$dest" ]; then
        changed="true"
        msg="file deleted"
        contents=$(cat "$dest" 2>&1 | python -c 'import json,sys; print json.dumps(sys.stdin.read())')
        output=$(rm -f $dest 2>&1 | python -c 'import json,sys; print json.dumps(sys.stdin.read())')
        if [ $? -ne 0 ]; then
            printf '{"failed": true, "msg": "error deleting file", "output": %s}' "$output"
            exit 1
        fi
    else
        changed="false"
        msg="file not present"
        contents='""'
    fi   
    }

function convert_to_upper
    {
    if [ ! -f "$dest" ]; then
        create_file
        msg="$msg, "
    fi
    current=$(cat $dest)
    new=$(echo "$current" | tr '[:lower:]' '[:upper:]')
    if [ "$current" = "$new" ]; then
        changed="false"
        msg="${msg}file not changed"
        contents=$(printf "$current" | python -c 'import json,sys; print json.dumps(sys.stdin.read())')
    else
        echo "$new" > $dest
        changed="true"
        msg="${msg}file converted to upper case"
        contents=$(printf "$new" | python -c 'import json,sys; print json.dumps(sys.stdin.read())')
    fi
    }

function convert_to_lower
    {
    if [ ! -f "$dest" ]; then
        create_file
        msg="$msg, "
    fi
    contents=$(ls -l "$dest" 2>&1 | python -c 'import json,sys; print json.dumps(sys.stdin.read())')
    current=$(cat $dest)
    new=$(echo "$current" | tr '[:upper:]' '[:lower:]')
    if [ "$current" = "$new" ]; then
        changed="false"
        msg="${msg}file not changed"
        contents=$(printf "$current" | python -c 'import json,sys; print json.dumps(sys.stdin.read())')
    else
        echo "$new" > $dest
        changed="true"
        msg="${msg}file converted to lower case"
        contents=$(printf "$new" | python -c 'import json,sys; print json.dumps(sys.stdin.read())')
    fi
    }

source $1

if [ -z "$dest" ]; then
    printf '{"failed": true, "msg": "missing required arguments: dest"}'
    exit 1
fi
if [ -z "$state" ]; then
    printf '{"failed": true, "msg": "missing required arguments: state"}'
    exit 1
fi

changed="false"
msg=""
contents=""

case $state in
    present)
        create_file
        ;;
    absent)
        delete_file
        ;;
    upper)
        convert_to_upper
        ;;
    lower)
        convert_to_lower
        ;;
    *)
        printf '{"failed": true, "msg": "invalid state: %s"}' "$state"
        exit 1
        ;;
esac

printf '{"changed": %s, "msg": "%s", "contents": %s}' "$changed" "$msg" "$contents"

exit 0
