from typing import Optional
from discord.ext import commands
import discord


def right_channel_checker(ctx: commands.Context) -> bool:
    """by default all not-moderators command allowed only in special channel

    :param ctx: commands.Context
    :return: bool
    """
    return ctx.channel.name == "bot-commands"


def special_permission_checker(ctx: commands.Context) -> bool:
    """allow default not DJ user use all music bot commands, if no DJ in voice channel

    :param ctx: commands.Context
    :return: bool
    """
    if not ctx.author.voice:
        return False

    voice_channel = ctx.author.voice.channel
    members = voice_channel.members

    dj_not_in_channel = all(["DJ" not in [role.name for role in member.roles] for member in members])

    return ("DJ" in [role.name for role in ctx.author.roles]) or dj_not_in_channel or ctx.bot.owner_id == ctx.author.id


def double_call_if_fail(func):
    """call function second time, if in first it fails

    :param func: function
    """
    def wrapper(*args, **kwargs):
        try:
            r = func(*args, **kwargs)
        except Exception as e:
            print(e)
            return func(*args, **kwargs)
        else:
            return r

    return wrapper


def bot_embed(client: discord.Client, title: Optional[str] = '', description: Optional[str] = '',
              colour: Optional[discord.Colour] = None) -> discord.Embed:
    """create good-looking answer when replying to user

    :param client: discord.Client
    :param title: Optional[str]
    :param description: Optional[str]
    :param colour: discord.Colour
    :return: discord.Embed
    """
    if not colour:
        colour = discord.Colour.random()
    emb = discord.Embed(title=title, description=description, colour=colour)
    emb.set_author(name=client.user.name, icon_url=client.user.avatar_url)
    return emb


def create_signature(emb: discord.Embed, ctx: commands.Context, member: discord.Member,
                     invoker: str, reason: Optional[str] = '', time: Optional[str] = '') -> discord.Embed:

    """add signature to embed, which responsible for signature of moderator, who banned/muted/etc. user.

    :param emb: discord.Embed
    :param ctx: commands.Context
    :param member: discord.Member
    :param invoker:
    :param reason:
    :param time:
    :return:
    """
    url = member.avatar_url
    name = invoker
    invoker_mention = ctx.author.mention

    if reason:
        emb.add_field(name='Reason', value=reason)

    if time:
        emb.add_field(name='Time', value=time)

    emb.set_thumbnail(url=url)
    emb.add_field(name=name, value=invoker_mention)

    return emb


def try_do_smt_with_higher_than_you(func):
    """ decorator
    checker that triggers if you try ban/mute/kick smb with higher or equal role

    :param func:
    """

    async def wrapper(self, ctx: commands.Context, member: Optional[discord.Member] = None, *args) -> bool:
        command_name = ctx.command.name

        if not member:
            return False

        if member.bot:
            description = f"You can't {command_name} bot. Beep boop bop."
            colour = discord.Colour.orange()
        elif ('administrator', True) in member.guild_permissions:
            description = f"You can't {command_name} yourself or other moderator."
            colour = discord.Colour.orange()
        else:
            return await func(self, ctx, member, *args)

        emb = bot_embed(self.client, description=description, colour=colour)
        await ctx.reply(embed=emb)
        return False

    return wrapper


async def create_muted_role(ctx: commands.Context) -> discord.Role:
    """standard role for muted person. create it, if it not exist

    :param ctx: commands.Context
    :return: discord.Role
    """
    await ctx.guild.create_role(name="Muted")
    muted = discord.utils.get(ctx.guild.roles, name="Muted")

    for channel in ctx.guild.channels:
        await channel.set_permissions(muted, speak=True,
                                      send_messages=False, read_messages=True, read_message_history=True)
    return muted
