"""
Automatically generate the config.json file
Created by sheepy0125
03/10/2021
P.S. I am aware that this code sucks, but it 
just needs to do the job its supposed to do :)
"""

#############
### Setup ###
#############
# Import
from os import getcwd
from os.path import exists
from json import dump

# Config
config: dict = {}

############
### Main ###
############

# Basic checks / confirmations
input(
    f"Your CWD is {getcwd()}. Exit now if you don't want that "
    + "(press return to continue)"
)

if exists("config.json"):
    input(
        "A config.json already exists, this will overwrite it "
        + "(press return to continue)"
    )

# Generator questions

# Token
config["token"]: str = input("What is your bot's token (bot -> token -> copy)? > ")

# Guild IDs
def ask_guild_id_questions() -> list:
    guild_ids: list = []
    print(
        "You can find guild IDs by enabling developer mode in Discord "
        + "settings, right clicking the server you want this bot to be in, "
        + 'and clicking "Copy ID".'
    )
    print("You may exit this anytime by pressing return without any text.")
    while True:
        guild_id_input: str = input("Guild ID > ")

        # Exiting, no more guild IDs to input
        if len(guild_id_input) == 0:
            break

        # Attempt to add guild ID
        try:
            guild_ids.append(int(guild_id_input))
        except ValueError:
            print("The guild ID must be an integer.")

    print("Here is the list of guild IDs:")
    print(guild_ids)

    return guild_ids


while True:
    if (
        ask_guild_id_questions_input := input(
            "Would you like to have some specific servers that you'll have the bot "
            + "run in (this will have the bot work immediately in these servers)? > "
        ).lower()
    ) in ["yes", "y", "", "sure", "yeah"]:
        config["guild_ids"]: list = ask_guild_id_questions()
        break

    elif ask_guild_id_questions_input in ["no", "n", "nah", "nope"]:
        config["guild_ids"]: list = []
        break

    else:
        print('You must enter "yes" or "no".')

# Embed color
while True:
    embed_color_input: str = input(
        "Enter a hexadecimal number for the " + "color that the snipe embed will be."
    )

    try:
        embed_color_int: int = int(embed_color_input, base=16)
    except ValueError:
        print("Your embed color must be valid hexadecimal.")
        continue

    if embed_color_int > 0xFFFFFF:
        print("Your embed color must be less than or equal to 0xffffff.")
        continue

    break

config["embed_color"]: str = embed_color_input

# Save config
print("Done collecting configuration information! Saving config")
with open("config.json", "w") as config_file:
    config_file.truncate(0)
    dump(config, config_file, indent=4)

print("Saved!")
