# Slack Notification with Block

```shell
$ export SLACK_BOT_TOKEN=<bot token>

$ ansible-playbook notify-slack.yaml
```


## Appendix

Slack block divider

```json
    {% if not loop.last %}
    {
      "type": "divider"
    },
    {% endif %}
```