from base64 import b64decode
from dotenv import load_dotenv
from os import getenv
from requests import post, HTTPError

load_dotenv()

def post_to_discord(content: str, name: str):
    webhook_url = f"https://discord.com/api/webhooks/{getenv('DISCORD_WEBHOOK_ID')}"
    content = f"{getenv('DISCORD_USER')}\n{content}"

    data = {"content": content, "username": name}
    response = post(webhook_url, json=data)
    if response.status_code != 204:
        raise HTTPError(f"Failed to send message to Discord: {response.text}")