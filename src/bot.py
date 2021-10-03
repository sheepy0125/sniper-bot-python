"""
Sniper Bot - Python edition
Created by sheepy0125, inspired by DankMemer
02/10/2021
"""

#############
### Setup ###
#############
# Import
from tools import Logger
from discord import Embed, Game
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from json import load

# Parse configuration
try:
    with open("config.json") as config_file:
        try:
            CONFIG: dict = load(config_file)

            # Assertions (config is good)
            assert (
                "token" in CONFIG and "application_id" in CONFIG
            ), 'Configuration must have "token" and "application_id" keys'

            assert (token_type := type(CONFIG["token"])) is type(
                str()
            ), f'Config file: "token" must be a string (not "{token_type}")'

            assert (application_id_type := type(CONFIG["application_id"])) is type(
                str()
            ), f'Config file: "application_id" must be a string (not "{application_id_type.__name__}")'

        except Exception as error:
            Logger.log_error(error)
            exit(1)

except Exception as error:
    Logger.log_error(error)
    Logger.fatal("Is the configuration file present?")
    Logger.fatal(
        "Are you running this bot in the root directory?"
    )  # TODO - make this a module to avoid CWD shenanigans
    exit(1)

# Create bot
pass

#################
### Functions ###
#################
pass

################
### Commands ###
################
pass

###########
### Run ###
###########
if __name__ == "__main__":
    Logger.log("Running bot!")
