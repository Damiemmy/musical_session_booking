import requests


def trigger_email(trigger, email, username):

    requests.post(
        "http://localhost:3000/dev/send-email",

        json={
            "trigger": trigger,
            "email": email,
            "username": username,
        }
    )