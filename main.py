import os


def main():
    create_directory()
    try:
        with open("launcher.py", 'r') as file:
            code = file.read()
        exec(code)
    except KeyboardInterrupt:
        print("\nExiting...\n\n")
        exit()


def create_directory():
    # Secondary method...
    # Create a directory for saving CSV files and media if it doesn't exist
    if not os.path.exists("Collection"):
        os.makedirs("Collection")


if __name__ == "__main__":
    main()
