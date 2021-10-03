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
from discord import Embed, Game, Message, User, Intents
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from json import load
from typing import Union
from time import mktime

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
client: commands.Bot = commands.Bot(
    command_prefix="\\", Intents=Intents.default()
)  # Arbitrary unused prefix
client.remove_command("help")
slash: SlashCommand = SlashCommand(client, sync_commands=True)

# Globals
NEW_LINE_CHAR: str = "\n"

###############
### Classes ###
###############
class MessageDatabases:
    """
    Little databases for different types of message history
    Every channel will have one message saved
    """

    deleted_messages: dict = {}
    edited_messages: dict = {}
    removed_reactions: dict = {}


#################
### Functions ###
#################
pass


##############
### Events ###
##############
@client.event
async def on_ready() -> None:
    """The bot is online"""

    Logger.log(f"Bot is online and is logged in as {client.user}")
    await client.change_presence(activity=Game("/snipe"))


@client.event
async def on_message_delete(message: Message) -> None:
    """A message was deleted, so save it to the deleted message database"""

    # TODO - check that message isn't an embed

    # Check if author is a User (not a str)
    message_author: Union[str, User] = message.author
    if type(message_author) is type(User):
        message_author = f"{message.author.name}#{message.author.discriminator}"
        Logger.warn(f"{message_author} is type User, have they left the guild?")

    # Get created timestamp (datetime.datetime object) to Unix timestamp
    creation_timestamp: int = int(mktime(message.created_at.timetuple()))

    # Get all attachements
    attachements: list = message.attachments
    if len(attachements) != 0:
        attachements = [
            f"{attachement.filename}: {attachement.url}" for attachement in attachements
        ]  # url will be saved for up to a couple minutes after deletion

    message_content: str = message.content if len(message.content) != 0 else "<empty>"

    # Update deleted_messages
    MessageDatabases.deleted_messages[message.channel.id]: dict = {
        "author": message_author,
        "message": message_content,
        "attachements": attachements,
        "creation_timestamp": creation_timestamp,
    }

    Logger.log(
        f"A message being deleted has been intercepted! Here's some info:{NEW_LINE_CHAR}"
        + f"Author: {message_author}{NEW_LINE_CHAR}Message: {message_content}{NEW_LINE_CHAR}"
        + f"Creation timestamp: {creation_timestamp}{NEW_LINE_CHAR}"
        + f"Attachements: {[attachement for attachement in attachements]}"
    )


################
### Commands ###
################
@slash.slash(name="snipe", description="Snipe a deleted message")
async def _snipe_command(ctx: SlashContext) -> None:
    Logger.log(f"Snipe slash command called in channel ID: {ctx.channel.id}")
    # There's a deleted message available
    if ctx.channel.id in MessageDatabases.deleted_messages:
        deleted_message: dict = MessageDatabases.deleted_messages[ctx.channel.id]
        await ctx.send(
            f"Snipe snipe! <t:{deleted_message['creation_timestamp']}>{NEW_LINE_CHAR}"
            + f"Author: {deleted_message['author']}{NEW_LINE_CHAR}"
            + f"Message: {deleted_message['message']}{NEW_LINE_CHAR}"
            # Show attachements if there are any
            + (
                "Attachements:"
                + NEW_LINE_CHAR.join(
                    [attachement for attachement in deleted_message["attachements"]]
                )
                if len(deleted_message["attachements"]) != 0
                else ""
            )
        )
        return

    # No deleted message is available
    await ctx.send(
        "I hate to say this but, sadly, there is no deleted "
        + "message to snipe from this channel. Sorry!"
    )


###########
### Run ###
###########
if __name__ == "__main__":
    Logger.log("Running bot!")
    try:
        client.run(CONFIG["token"])
    except Exception as error:
        Logger.log_error(error)
        exit(1)

    Logger.warn("Discord bot stopped")

else:
    Logger.warn("Discord bot isn't running by itself!")
