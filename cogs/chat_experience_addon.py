import os
import json

import discord
from discord.ext import commands

from utls.useful_functions import right_channel_checker


class ChatExperienceCog(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.exp_per_message = 4
        self.pow = 1/4
        self.users_file = 'users.json'

        if not os.path.isfile(self.users_file):
            with open(self.users_file, "w+") as f:
                f.write('{}')

    @staticmethod
    async def update_data(users, user):
        """create a user, if he not exists in users aray

        :param users: list[users]
        :param user: dict
        """
        if str(user.id) not in users:
            users[str(user.id)] = {}
            users[str(user.id)]['exp'] = 0
            users[str(user.id)]['level'] = 1

    async def add_experience(self, users, user):
        """add hardcoded exp_per_message to experience to user

        :param users: list[user]
        :param user: dict
        """
        users[str(user.id)]['exp'] += self.exp_per_message

    async def level_up(self, users, user, channel):
        """level up user, if his experience*pow > level int value

        :param users: list[user]
        :param user: dict
        :param channel: discord.Channel
        :return:
        """
        updated_lvl = int(users[str(user.id)]["exp"] ** self.pow)

        if users[str(user.id)]['level'] < updated_lvl:
            users[str(user.id)]['level'] = updated_lvl
            await channel.send(f"{user.mention} reached up level {updated_lvl}.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """update all user information, after he sends message
        if he sends messages too quick - can congratulate with lvl up twice

        :param message: discord.Message
        """
        with open("users.json", "r", encoding='utf8') as f:
            users = json.load(f)

        await self.update_data(users, message.author)
        await self.add_experience(users, message.author)

        with open("users.json", "w", encoding='utf8') as f:
            json.dump(users, f, indent=2, sort_keys=True)

        await self.level_up(users, message.author, message.channel)

        with open("users.json", "w", encoding='utf8') as f:
            json.dump(users, f, indent=2, sort_keys=True)

    # region with user commands

    @commands.command(name='level', help='Display user current level')
    @commands.check(right_channel_checker)
    async def level(self, ctx: commands.Context, member: discord.Member = None):
        """show user his level information

        :param ctx: commands.Context
        :return:
        """
        with open("users.json", "r", encoding='utf8') as f:
            users = json.load(f)
        if member:
            msg = f"User {member.name} has"
            user = users[str(member.id)]
        else:
            msg = "You have"
            user = users[str(ctx.author.id)]

        await ctx.reply(f"{msg} {user['level']} level and {user['exp']} experience.")


def setup(client):
    client.add_cog(ChatExperienceCog(client))
