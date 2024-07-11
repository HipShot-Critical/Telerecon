import os
import re
import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageEntityTextUrl
from colorama import Fore, Style
import details as ds

# Login details
api_id = ds.apiID
api_hash = ds.apiHash
phone = ds.number

async def main():
    client = TelegramClient(phone, api_id, api_hash)

    await client.start()

    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        await client.sign_in(phone, input('Enter the code: '))

    print(
        f'{Fore.CYAN}Please enter a target Telegram channel (e.g. https://t.me/{Fore.LIGHTYELLOW_EX}your_channel{Fore.CYAN}):{Style.RESET_ALL}\n')
    print()

    while True:
        try:
            channel_name = input("Please enter a Telegram channel name: ")
            print(f'You entered "{channel_name}"')
            answer = input('Is this correct? (y/n) ')
            if answer == 'y':
                print(f'Scraping URLs from {channel_name}...')
                break
        except Exception:
            continue

    urls = set()  # Use a set to deduplicate URLs

    total_urls_scraped = 0  # Variable to store total scraped URLs count

    async for message in client.iter_messages(channel_name, limit=None):
        if message.entities is not None:
            for entity in message.entities:
                if isinstance(entity, MessageEntityTextUrl):
                    url = entity.url
                    if 'https://t.me/' in url:
                        if match := re.match(
                            r'https?://t\.me/([^/\s]+)/?', url
                        ):
                            channel_link = f'https://t.me/{match[1]}'
                            urls.add(channel_link)
                            total_urls_scraped += 1  # Increment total count
                            print(f"URL - {Fore.CYAN}https://t.me/{match[1]}{Style.RESET_ALL}")
        if message.text and isinstance(message.text, str):
            matches = re.findall(r'https?://t\.me/([^/\s]+)/?', message.text)
            for match in matches:
                channel_link = f'https://t.me/{match}'
                urls.add(channel_link)
                total_urls_scraped += 1  # Increment total count
                print(f"URL - {Fore.CYAN}https://t.me/{match}{Style.RESET_ALL}")

    urls_folder = 'URLs'
    os.makedirs(urls_folder, exist_ok=True)
    output_filename = os.path.join(urls_folder, f'{channel_name}.csv')

    # Read existing URLs if the file exists
    existing_urls = set()
    if os.path.exists(output_filename):
        with open(output_filename, 'r', encoding='utf-8') as file:
            existing_urls = set(file.read().splitlines())

    # Combine new URLs with existing URLs
    all_urls = urls.union(existing_urls)
    new_urls_count = len(all_urls) - len(existing_urls)

    # Write the combined and deduplicated URLs back to the file
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write('\n'.join(sorted(all_urls)))

    print(f'URLs scraped successfully. Saved to: {output_filename}')
    print(f'URLs scraped: {total_urls_scraped} | New URLs added to {channel_name}.csv: {new_urls_count} | {channel_name} URL count: {len(all_urls)}')

   # Update the total_urls file
    total_urls_filename = 'total_urls.csv'
    total_urls = set()
    if os.path.exists(total_urls_filename):
        with open(total_urls_filename, 'r', encoding='utf-8') as file:
            total_urls = set(file.read().splitlines())

    # Combine all URLs and deduplicate
    total_urls_before = len(total_urls)
    total_urls = total_urls.union(all_urls)
    new_total_urls_count = len(total_urls) - total_urls_before
    # Write the combined and deduplicated total URLs back to the file
    with open(total_urls_filename, 'w', encoding='utf-8') as file:
        file.write('\n'.join(sorted(total_urls)))

    print(f'Total URLs updated successfully. Saved to: {total_urls_filename} | New URLs added: {new_total_urls_count} | Total: {len(total_urls)}')

if __name__ == '__main__':
    asyncio.run(main())
