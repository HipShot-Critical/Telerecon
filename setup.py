import os

from colorama import Fore, Style, init


# Function to update details.py file
def update_env_details(api_id, api_hash, phone_number):
    with open(".env", "w") as file:
        file.write(f'API_ID = "{api_id}"\n')
        file.write(f'API_HASH = "{api_hash}"\n')
        file.write(f'PH_NUMBER = "{phone_number}"\n')


# Primary method...
# Create a directory for saving CSV files and media if it doesn't exist
if not os.path.exists("Collection"):
    os.makedirs("Collection")

# ask user for telegram details and guide them through it
init(autoreset=True)

print(Fore.CYAN + r' __________________________________________________________________')  # noqa: E501
print(Fore.CYAN + r'   _______ ______ _      ______ _____  ______ _____ ____  _   _    ')  # noqa: E501
print(Fore.CYAN + r'  |__   __|  ____| |    |  ____|  __ \|  ____/ ____/ __ \| \ | |   ')  # noqa: E501
print(Fore.CYAN + r'     | |  | |__  | |    | |__  | |__) | |__ | |   | |  | |  \| |   ')  # noqa: E501
print(Fore.CYAN + r'     | |  |  __| | |    |  __| |  _  /|  __|| |   | |  | | . ` |   ')  # noqa: E501
print(Fore.CYAN + r'     | |  | |____| |____| |____| | \ \| |___| |___| |__| | |\  |   ')  # noqa: E501
print(Fore.CYAN + r'     |_|  |______|______|______|_|  \_\______\_____\____/|_| \_| v2')  # noqa: E501
print(Fore.CYAN + r'___________________________________________________________________')  # noqa: E501
print(Style.RESET_ALL)

print('Welcome to the Telegram Scraper setup wizard.')
print('This file will insert your login information to the Telegram Scraper scripts.')  # noqa: E501
print('Follow the README instructions to get your credentials.')

while True:
    try:
        api_id = input("Please enter your API ID:\n")
        print(f'You entered "{api_id}"')
        confirmation = input('Is this correct? (y/n)')
        if confirmation.lower() == 'y':
            print('Updating...')
            break
    except ValueError:
        continue

while True:
    try:
        api_hash = input("Please enter your API Hash:\n")
        print(f'You entered "{api_hash}"')
        confirmation = input('Is this correct? (y/n)')
        if confirmation.lower() == 'y':
            print('Updating...')
            break
    except ValueError:
        continue

while True:
    try:
        phone_number = input("Please enter your phone number:\n")
        print(f'You entered "{phone_number}"')
        confirmation = input('Is this correct? (y/n)')
        if confirmation.lower() == 'y':
            print('Updating...')
            break
    except ValueError:
        continue

update_env_details(api_id, api_hash, phone_number)

print('Setup is complete.')

launcher = input('Do you want to open the launcher? (y/n)')

if launcher.lower() == 'y':
    print('Starting...')
    exec(open("launcher.py").read())
else:
    print(
        'The launcher is now ready and can be started with'
        'the launcher.py file. You may now close the terminal.'
    )
