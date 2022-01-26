import discord
from discord.ext import commands

from utls.useful_functions import right_channel_checker


class UserAppearance(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(name="avatar", help="Display mentioned user avatar")
    @commands.check(right_channel_checker)
    async def avatar(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        emb = discord.Embed(description=f"User {member.mention}",
                            colour=discord.Colour.blue())
        emb.set_image(url=member.avatar_url)

        await ctx.reply(embed=emb)


def setup(client):
    client.add_cog(UserAppearance(client))
