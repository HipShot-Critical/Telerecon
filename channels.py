import asyncio
import os

import pandas as pd
from colorama import Fore, Style
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

# API details
phone = os.getenv("PH_NUMBER")
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")


async def main():
    client = TelegramClient(phone, api_id, api_hash)
    await client.start()

    print(
        '\nThis tool will scrape a Telegram channel for'
        'all forwarded messages and their original source.\n'
    )

    while True:
        try:
            channel_name = input("Please enter a Telegram channel name:\n")
            print(f'You entered "{channel_name}"')
            answer = input('Is this correct? (y/n)')
            if answer == 'y':
                print('Scraping forwards from', channel_name, '...')
                break
        except Exception:
            continue

    channel_list = []
    source_urls = []
    count = 0

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
                        channel_list.append([ent.title, target_channel_title])
                        source_url = f"https://t.me/{ent.username}"
                        source_urls.append(source_url)
                        count += 1
                        print(
                            f"From ({Fore.CYAN} + {ent.title} + {Style.RESET_ALL}) to"  # noqa: E501
                            f"({Fore.YELLOW} + {target_channel_title} + {Style.RESET_ALL})"  # noqa: E501
                        )
                    except ValueError as e:
                        print("Skipping forward:", e)

            except PermissionError as e:
                print(
                    f"{Fore.RED}Skipping forward: Private/Inaccessible:"
                    f"{e}{Style.RESET_ALL}"
                )

    # Create the folders if they don't exist
    adjacency_folder = 'Adjacency List'
    urls_folder = 'Source URLs'
    os.makedirs(adjacency_folder, exist_ok=True)
    os.makedirs(urls_folder, exist_ok=True)

    df = pd.DataFrame(channel_list, columns=['From', 'To'])
    df.to_csv(
        os.path.join(
            adjacency_folder, f'{channel_name}.csv'
        ), header=False, index=False
    )

    source_df = pd.DataFrame(source_urls, columns=['SourceURL'])
    source_df.to_csv(
        os.path.join(
            urls_folder, f'{channel_name}SourceURLs.csv'
        ), header=False, index=False
    )

    await client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())

print('Forwards scraped successfully.')

again = input('Do you want to scrape more channels? (y/n)')
if again == 'y':
    print('Restarting...')
    exec(open("channels.py").read())
else:
    pass

launcher = input('Do you want to return to the launcher? (y/n)')
if launcher == 'y':
    print('Restarting...')
    exec(open("launcher.py").read())
