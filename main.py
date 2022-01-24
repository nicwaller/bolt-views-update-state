import json
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ["SLACK_BOT_TOKEN"])

VIEW_ID = 'view_1'
ACTION_SELECT_NONE = 'action-select-none'
ACTION_SELECT_ALL = 'action-select-all'


def generate_view(num_checkboxes: int = 3, selected: bool = False, state_summary: str = ''):
    def generate_checkboxes(count: int):
        for i in range(0, count):
            yield {
                "value": str(i),
                "text": {
                    "type": "mrkdwn",
                    "text": str(i)
                }
            }

    checkbox_group = {
        "type": "checkboxes",
        "action_id": "checkbox_group",
        "options": list(generate_checkboxes(num_checkboxes)),
    }

    if selected:
        checkbox_group['initial_options'] = list(generate_checkboxes(num_checkboxes))

    final_view = {
            "type": "modal",
            "callback_id": VIEW_ID,
            "title": {"type": "plain_text", "text": "Checkbox View State"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "First, press *Select All* and *Select None* and observe that the checkboxes change state as expected."
                    }
                },
                {
                    "type": "divider",
                },
                {
                    "type": "actions",
                    "block_id": "buttons",
                    "elements": [
                        {
                            "type": "button",
                            "action_id": ACTION_SELECT_ALL,
                            "text": {
                                "type": "plain_text",
                                "text": "Select All",
                                "emoji": False,
                            }
                        },
                        {
                            "type": "button",
                            "action_id": ACTION_SELECT_NONE,
                            "text": {
                                "type": "plain_text",
                                "text": "Select None",
                                "emoji": False,
                            }
                        }
                    ]
                },
                {
                    "type": "actions",
                    "block_id": "checkblox",
                    "elements": [checkbox_group],
                },
            ],
            # Invalid additional property: state
            # "state": {
            #     "values": {
            #         "checkblox": {
            #             "checkbox_group": {
            #                 "type": "checkboxes",
            #                 "selected_options": []
            #             }
            #         }
            #     }
            # }
        }
    final_view['blocks'] += [
        {
            "type": "divider",
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Next, toggle one of the checkboxes directly. "
                        "Then Try pressing the *Select All* and *Select None* buttons again"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "Observe that none of the checkboxes change their state now. "
                        "The select all/none buttons rely on changing initial_options "
                        "to change the checkbox selection values. But that is a fake change "
                        "which is superseded by real state created by toggling any checkbox."
            }
        },
        {
            "type": "divider",
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Selected:* {state_summary}",
            }
        },
    ]
    return final_view


@app.command("/modal-test")
def open_modal(ack, client, body):
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view=generate_view(num_checkboxes=3, selected=False)
    )


# noinspection DuplicatedCode
@app.action(ACTION_SELECT_NONE)
def select_none(ack, body, client):
    ack()
    client.views_update(
        view_id=body['view']['id'],
        hash=body['view']['hash'],
        view=generate_view(
            num_checkboxes=3,
            selected=False,
            state_summary=json.dumps(body['view']['state']['values']['checkblox']['checkbox_group']['selected_options']),
        ),
    )


@app.action(ACTION_SELECT_ALL)
def select_all(ack, body, client):
    ack()
    client.views_update(
        view_id=body['view']['id'],
        hash=body['view']['hash'],
        view=generate_view(
            num_checkboxes=3,
            selected=True,
            state_summary=json.dumps(body['view']['state']['values']['checkblox']['checkbox_group']['selected_options']),
        ),
    )


# noinspection DuplicatedCode
@app.action("checkbox_group")
def handle_some_action(ack, body, client):
    ack()
    client.views_update(
        view_id=body['view']['id'],
        hash=body['view']['hash'],
        view=generate_view(
            num_checkboxes=3,
            selected=False,
            state_summary=json.dumps(body['view']['state']['values']['checkblox']['checkbox_group']['selected_options']),
        ),
    )


@app.view(VIEW_ID)
def handle_view_events(ack):
    ack()


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
