import bot
import os


def main():
    token = os.environ.get("TOKEN")
    dict_bot = bot.Bot(token)
    dict_bot.run()


if __name__ == "__main__":
    main()
