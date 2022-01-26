import discord
from discord.ext import commands
import asyncio

from utls.useful_functions import try_do_smt_with_higher_than_you, create_muted_role, bot_embed, create_signature


class DurationConverter(commands.Converter):

    async def convert(self, ctx: commands.Command, argument):
        """convert valid duration and reason to valid values

        :param ctx: commands.Context
        :param argument: str
        :return: tuple(int, str, str)

        Example
        -------
        10m reason-> (10*60, 10d, reason)
        """
        if not argument:
            return 0, '', ''

        duration = argument.split()[0]
        amount = duration[:-1]
        unit = duration[-1]

        time_units = {"s": 1, "m": 60, "h": 60 * 60, "d": 60 * 60 * 24, "w": 60 * 60 * 24 * 7}

        if amount.isdigit() and unit in time_units:
            return int(amount)*time_units[unit], duration, ""
        else:
            return 0, '', argument

    @staticmethod
    def convert_dur(argument):
        """do same as class convert method
        """
        if not argument:
            return 0, "", ""
        """do same as convert"""
        duration = argument.split()[0]
        amount = duration[:-1]
        unit = duration[-1]

        time_units = {"s": 1, "m": 60, "h": 60 * 60, "d": 60 * 60 * 24, "w": 60 * 60 * 24 * 7}

        if amount.isdigit() and unit in time_units:
            return int(amount)*time_units[unit], duration, ""
        else:
            return 0, "", argument


class ChatModerationCog(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="mute", help='Mute selected user in text channels.')
    @commands.has_permissions(manage_messages=True, manage_roles=True)
    @try_do_smt_with_higher_than_you
    async def mute(self, ctx: commands.Context, member: discord.Member, duration:DurationConverter = "", *reason):
        """ mute user, IDK why if when I try to pass no duration through decorator
         with check DurationConverter it raises errors with invalid number of arguments
         works fine, but looks ugly.

         :param ctx: commands.Context
         :param member: discord.Member
         :param duration: DurationConverter
         :param reason: Optional[str]
         """
        duration = DurationConverter.convert_dur(duration)
        try:
            time_to_wait, unit_s, reason_0 = duration
        except ValueError:
            time_to_wait, unit_s, reason_0 = 0, '', ''

        comma = ' ' if reason_0 else ''  # this comma needed to separate reasons, if they exists
        reason = reason_0 + comma + " ".join(reason)
        """ this lines will be removed, after i find solution """

        muted = discord.utils.get(ctx.guild.roles, name="Muted")

        """ if no "Muted" role on server, create it for default role"""
        if not muted:
            muted = await create_muted_role(ctx)

        await member.add_roles(muted)

        description = f"User {member.mention} has been muted!"
        emb = bot_embed(self.client, description=description, colour=discord.Colour.red())

        emb = create_signature(emb=emb, ctx=ctx, member=member, invoker='Moderator',
                               reason=reason, time=unit_s)

        await ctx.reply(embed=emb)

        if time_to_wait:
            await asyncio.sleep(time_to_wait)
            await member.remove_roles(muted)

    @commands.command(name="unmute", help="Unmute selected user in text channels.")
    @commands.has_permissions(manage_messages=True, manage_roles=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        """unmute user, if he was muted

        :param ctx: commands.Context
        :param member: discord.Member
        :return:
        """
        if "Muted" not in [role.name for role in member.roles]:
            description = f"{member.mention} hasn't been muted!"
            colour = discord.Colour.orange()
        else:
            muted = discord.utils.get(ctx.guild.roles, name="Muted")
            await member.remove_roles(muted)

            description = f"{member.mention} hasn't been muted!"
            colour = discord.Colour.green()

        emb = bot_embed(self.client, description=description, colour=colour)

        if colour == discord.Colour.green():
            emb = create_signature(emb=emb, ctx=ctx, member=member, invoker='Moderator')

        await ctx.reply(embed=emb)

    @commands.command(name="ban", help="Ban selected user from server.")
    @commands.has_permissions(ban_members=True)
    @try_do_smt_with_higher_than_you
    async def ban(self, ctx: commands.Context, member: discord.Member, duration: DurationConverter = '', *reason):
        """ban user from server duration and reason are optional
        (works without them, but with same crutches, as mute)

        :param ctx: commands.Context
        :param member: discord.Member
        :param duration: DurationConverter
        :param reason: Optional[str]
        """
        duration = DurationConverter.convert_dur(duration)
        try:
            time_to_wait, unit_s, reason_0 = duration
        except ValueError:
            time_to_wait, unit_s, reason_0 = 0, '', ''

        comma = ' ' if reason_0 else ''  # this comma needed to separate reasons, if they exists
        reason = reason_0 + comma + " ".join(reason)
        """ this lines will be removed, after i find solution """

        await ctx.guild.ban(member, reason=reason)

        description = f"User {member.mention} was banned!"
        colour = discord.Colour.red()

        emb = bot_embed(self.client, description=description, colour=colour)
        emb = create_signature(emb=emb, ctx=ctx, member=member, invoker='Moderator',
                               reason=reason, time=unit_s)

        await ctx.reply(embed=emb)
        if time_to_wait:
            await asyncio.sleep(time_to_wait)
            await ctx.guild.unban(member)

    @commands.command(name="unban", help="Unban user.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, *, member):
        """unban user, sensitive to input

        Example
        -------
        unban User#1234

        :param ctx: commands.Context
        :param member: str
        """
        that_user = None
        try:
            member_name, member_discriminator = member.split('#')
        except ValueError:
            description = f"User name must looks like User#1337."
            colour = discord.Colour.red()
        else:
            banned_users = await ctx.guild.bans()

            description = f"This user hasn't been banned!"
            colour = discord.Colour.orange()

            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    description = f"{user.mention} has been unbanned!"
                    colour = discord.Colour.green()
                    that_user = user
                    break

        emb = bot_embed(self.client, description=description, colour=colour)

        if that_user:
            emb = create_signature(emb=emb, ctx=ctx, member=that_user, invoker='Moderator')

        await ctx.reply(embed=emb)

    @commands.command(name="kick", help="Kick user from server.")
    @commands.has_permissions(kick_members=True)
    @try_do_smt_with_higher_than_you
    async def kick(self, ctx, member: discord.Member, *reason):
        """kick user from server

        :param ctx: commands.Context
        :param member: discord,member
        :param reason: Optional[str]
        """
        reason = " ".join(reason)
        description = f"User {member.mention} has been kicked!"
        colour = discord.Colour.red()
        emb = bot_embed(self.client, description=description, colour=colour)

        emb = create_signature(emb=emb, ctx=ctx, member=member, invoker='Moderator')

        await ctx.reply(embed=emb)
        await ctx.guild.kick(member, reason=reason)


def setup(client):
    client.add_cog(ChatModerationCog(client))
