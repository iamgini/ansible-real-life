# Slack Notification with Block

```shell
$ export SLACK_BOT_TOKEN=<bot token>

$ ansible-playbook reporting.yaml  -e "send_slack=true"
```



- https://api.slack.com/


## Appendix

Slack block divider

```json
    {% if not loop.last %}
    {
      "type": "divider"
    },
    {% endif %}
```