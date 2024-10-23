# Slack Notification with Block

```shell
export SLACK_BOT_TOKEN=<bot token>
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