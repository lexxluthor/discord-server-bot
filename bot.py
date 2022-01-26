from discord.ext import commands
import os
from dotenv import load_dotenv


load_dotenv()

PREFIX = os.getenv('PREFIX', '!')
TOKEN = os.getenv('TOKEN')
Bot = commands.Bot(command_prefix=PREFIX)


@Bot.command()
@commands.is_owner()
async def load(ctx: commands.Context, extension):
    """load cog extension to bot

    :param ctx: commands.Context
    :param extension: str
    """
    print(f"load {extension}")

    Bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} extension successfully loaded.")


@Bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    """unload cog extension from bot

        :param ctx: commands.Context
        :param extension: str
    """
    print(f"unload {extension}")

    Bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} extension successfully loaded.")


@Bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    """reload bot cog extension

        :param ctx: commands.Context
        :param extension: str
    """
    print(f"reload {extension}")

    Bot.unload_extension(f"cogs.{extension}")
    Bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} extension successfully loaded.")


@Bot.event
async def on_ready():
    print("Bot is ready")


def load_cogs():
    """ load all cogs
    """
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            Bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"cogs.{filename[:-3]}")


load_cogs()


Bot.run(TOKEN)

#
# @client.event
# async def on_messages(message):
#     if message.author == client.user:
#         return
