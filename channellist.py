import asyncio
import os
import re
from urllib.parse import urlparse

import pandas as pd
from colorama import Fore, Style
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import UsernameNotOccupiedError

load_dotenv()

# API details
phone = os.getenv("PH_NUMBER")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")


async def scrape_forwards(channel_name):
    channel_list = []
    source_urls = []
    count = 0

    async with TelegramClient(phone, api_id, api_hash) as client:
        async for message in client.iter_messages(channel_name):
            if message.forward is not None:
                try:
                    id = message.forward.original_fwd.from_id
                    if id is not None:
                        try:
                            ent = await client.get_entity(id)
                            target_channel_entity = await client.get_entity(
                                message.to_id.channel_id
                            )
                            target_channel_title = target_channel_entity.title
                            channel_list.append(
                                [
                                    ent.title,
                                    target_channel_title
                                ]
                            )
                            source_url = f"https://t.me/{ent.username}"
                            source_urls.append(source_url)
                            count += 1
                            print(
                                f"From {Fore.CYAN} + {ent.title} + {Style.RESET_ALL} to"  # noqa: E501
                                f"{Fore.YELLOW} + {target_channel_title} + {Style.RESET_ALL}"  # noqa: E501
                            )
                        except ValueError as e:
                            print("Skipping forward:", e)
                        except UsernameNotOccupiedError:
                            print(
                                "Skipping forward:"
                                f"Username not occupied for entity ID {id}"
                            )
                except PermissionError as e:
                    print(
                        f"{Fore.RED}Skipping forward:"
                        f"Private/Inaccessible: {e}{Style.RESET_ALL}"
                    )

    df = pd.DataFrame(channel_list, columns=["From", "To"])
    source_df = pd.DataFrame(source_urls, columns=["SourceURL"])

    os.makedirs("Adjacency List", exist_ok=True)
    os.makedirs("Source URLs", exist_ok=True)

    sanitized_channel_name = re.sub(r'[\/:*?"<>|]', "_", channel_name)
    channel_name_without_prefix = sanitized_channel_name.split("/")[-1]
    if channel_name_without_prefix.startswith("https___t.me_"):
        channel_name_without_prefix = channel_name_without_prefix.replace(
            "https___t.me_", ""
        )

    df.to_csv(
        os.path.join("Adjacency List", f"{channel_name_without_prefix}.csv"),
        header=False,
        index=False,
    )
    source_df.to_csv(
        os.path.join(
            "Source URLs",
            f"{channel_name_without_prefix}SourceURLs.csv"
        ),
        header=False,
        index=False,
    )


async def main():
    channels_file = input(
        "Enter the name of the file containing"
        "the list of channels (csv or txt): "
    )

    with open(channels_file) as file:
        channels = [line.strip() for line in file if line.strip()]
    channels = list(set(channels))

    for channel in channels:
        parsed_url = urlparse(channel)
        if parsed_url.netloc != "t.me":
            print(f"Skipping invalid Telegram URL: {channel}")
            continue

        print(f"Scraping forwards from {channel}...")
        await scrape_forwards(channel)
        print("CSV files created for", channel)
        print()


if __name__ == "__main__":
    asyncio.run(main())

print("Forwards scraped successfully.")
