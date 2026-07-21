import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

CHANNELS = [
    int(os.getenv("CHANNEL_1")),
    int(os.getenv("CHANNEL_2")),
    int(os.getenv("CHANNEL_3")),
    int(os.getenv("CHANNEL_4")),
]
