"""
Sniper Bot - Python edition
Created by sheepy0125, inspired by DankMemer
02/10/2021
"""

#############
### Setup ###
#############
# Import
from utils.tools import Logger
from discord import Embed, Game, Message, User, Intents, Embed
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from json import load
from typing import Union
from datetime import datetime

# Parse configuration
try:
    with open("config.json") as config_file:
        try:
            CONFIG: dict = load(config_file)

            # Assertions (config is good)
            assert (token_type := type(CONFIG["token"])) is type(
                str()
            ), f'Config file: "token" must be a string (not "{token_type}")'

            assert (guild_ids_type := type(CONFIG["guild_ids"])) is type(
                list()
            ), f'Config file: "guild_ids" must be a list of integers (not "{guild_ids_type.__name__}")'

            CONFIG["embed_color"]: int = int(CONFIG["embed_color"], base=16)
            assert (
                CONFIG["embed_color"] <= 0xFFFFFF
            ), "Embed color must be less than or equal to 0xffffff"

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
WHITESPACE_CHAR: str = "\u200b"
IMAGE_TYPES: list = ["png", "jpg", "jpeg", "gif"]

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
def is_image(filename: str) -> bool:
    """Returns if the file is an image"""

    return filename.rsplit(".")[-1].lower() not in IMAGE_TYPES


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

    # Note for this commit removing the datetime.datetime -> Unix timestamp:
    # discord.Embed.timestamp takes a datetime.datetime object, not Unix timestamp
    creation_timestamp: datetime = message.created_at

    # Get attachment (if there is one)
    attachment: Union[str, None] = (
        message.attachments[0].url if len(message.attachments) != 0 else None
    )

    message_content: str = (
        message.content if len(message.content) != 0 else "<empty message>"
    )

    # Update deleted_messages
    MessageDatabases.deleted_messages[message.channel.id]: dict = {
        "author": message_author,
        "message": message_content,
        "attachment": attachment,
        "creation_timestamp": creation_timestamp,
    }

    Logger.log(
        f"A message being deleted has been intercepted!{NEW_LINE_CHAR}"
        + f"Author: {message_author}{NEW_LINE_CHAR}"
        + f"Message: {message_content}{NEW_LINE_CHAR}"
        + f"Attachment: {attachment}{NEW_LINE_CHAR}"
        + f"Creation timestamp: {creation_timestamp}"
    )


################
### Commands ###
################
@slash.slash(
    name="snipe", description="Snipe a deleted message", guild_ids=CONFIG["guild_ids"]
)
async def _snipe_deleted_message_command(ctx: SlashContext) -> None:
    """Snipe a deleted message"""

    Logger.log(f"Snipe slash command called in channel ID {ctx.channel.id}")
    # There's a deleted message available
    if ctx.channel.id in MessageDatabases.deleted_messages:
        deleted_message: dict = MessageDatabases.deleted_messages[ctx.channel.id]
        sniped_embed: Embed = Embed(
            description=deleted_message["message"],
            timestamp=deleted_message["creation_timestamp"],
            color=CONFIG["embed_color"],
        )
        sniped_embed.set_author(name=deleted_message["author"])
        sniped_embed.set_footer(text=f"posted in #{ctx.channel.name}")
        if attachment_url := deleted_message["attachment"]:
            # Use markdown for a link if the attachment isn't an image (isn't supported in embed)
            if is_image(attachment_url):
                sniped_embed.description += (
                    f"{NEW_LINE_CHAR}[Attachment]({attachment_url})"
                )

            else:
                sniped_embed.set_image(url=attachment_url)

        await ctx.send(embed=sniped_embed)

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
