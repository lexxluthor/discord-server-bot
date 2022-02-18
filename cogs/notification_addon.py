import requests
import json
import time
from typing import List

import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup


time_for_update = 30

class TikTokUser():
    def __init__(self, username: str):
        self.headers = {
            'user-agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 '
                'Safari/537.36',
        }
        self.cookies = {
            's_v_web_id': 'verify_kzphj93w_JIM2XXxx_AxOz_4c1x_808L_XZirKkAjLI4B',
            'ttwid': '1%7CS_TMJhc-tFIuKXQzu0J3BUj3w8G5ks4NKeLtRCItunc%7C1645012712%7Cdadb8e161f2647377f0d8690c5065cee9cdabfd9029e4f67989890b8f5a9634b',
        }
        self.username = username

        self.last_video_id = None

    def get_creation_time_from_url(self, url: str):
        """
        https://www.tiktok.com/node/share/video/@daxak4/7064567001926143234
        """
        video_id = url.split('/')[-1]
        req_url = 'https://www.tiktok.com/node/share/video/@' + self.username + '/' + video_id

        r = requests.get(req_url, headers=self.headers, cookies=self.cookies)

        dictionary = json.loads(r.text)
        time_of_creation_in_seconds = dictionary.get('itemInfo').get('itemStruct').get('createTime')

        return time_of_creation_in_seconds

    def check_for_updates(self):
        r = requests.get('https://www.tiktok.com/@' + self.username, headers=self.headers, cookies=self.cookies)

        soup = BeautifulSoup(r.text, 'lxml')
        video_ids = []

        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if link_to_video(link=href, username=self.username):
                video_id = int(href.split('/')[-1])
                video_ids.append(video_id)

        if not self.last_video_id:
            self.last_video_id = video_ids[0]

        if video_ids:
            last_video = max(video_ids)
            if self.last_video_id < last_video:
                self.last_video_id = last_video

    def last_video_creation_time(self):
        url = get_url_from_id(self.username, self.last_video_id)
        return self.get_creation_time_from_url(url)

    def last_video_url(self):
        return get_url_from_id(self.username, self.last_video_id)

    def download_video_by_url(self, url: str):
        """
        https://www.tiktok.com/node/share/video/@daxak4/7064567001926143234
        """
        video_id = url.split('/')[-1]
        req_url = 'https://www.tiktok.com/node/share/video/@' + self.username + '/' + video_id

        r = requests.get(req_url, headers=self.headers, cookies=self.cookies)
        dictionary = json.loads(r.text)
        addr = dictionary.get('itemInfo').get('itemStruct').get('video').get('downloadAddr')

        r = requests.get(addr)

        with open('tiktok.mp4', 'wb') as f:
            print(123)
            f.write(r.content)

        return addr


def link_to_video(link: str, username: str) -> bool:
    if 'tiktok.com/@' + username + '/video/' in link:
        return True
    return False


def get_url_from_id(username: str, id: int):
    return f'https://www.tiktok.com/@{username}/video/{id}'


class NotificationCog(commands.Cog):

    def __init__(self, client: discord.Client):
        self.client = client
        self.TikTokUsers: List[TikTokUser] = []

        self.TikTokUsers.append(TikTokUser('daxak4'))

    def cog_unload(self):
        self.tiktok_check.cancel()

    @tasks.loop(seconds=time_for_update)
    async def tiktok_check(self, guild: discord.Guild):
        notification_channel = None
        for channel in guild.channels:
            if channel.name == 'notification':
                notification_channel = channel
        if not notification_channel:
            notification_channel = guild.system_channel

        current_time = time.time()

        for user in self.TikTokUsers:
            user.check_for_updates()
            if (current_time - user.last_video_creation_time()) < time_for_update*2:
                await notification_channel.send(f"@everyone @{user.username} has new TikTok. Check it not!\n"
                         f"{user.last_video_url()}")

    @commands.is_owner()
    @commands.command(name='add', help='add new TikTok user to notification list')
    async def add(self, ctx: commands.Context, name: str):
        """ will be implemented later """
        pass

    @commands.is_owner()
    @commands.command()
    async def set_tiktok_check(self, ctx: commands.Context):
        if not self.tiktok_check.is_running():
            self.tiktok_check.start(ctx.guild)

        await ctx.send("Start checking TikTok.")

    @commands.is_owner()
    @commands.command()
    async def unset_tiktok_check(self, ctx: commands.Context):
        if self.tiktok_check.is_running():
            self.tiktok_check.canel()

        await ctx.send("End checking TikTok.")

    @commands.command(name='tiktok', aliases=['tt', 'тикток'])
    async def tiktok(self, ctx: commands.Context):
        for user in self.TikTokUsers:
            await ctx.send(f"@{user.username} last TikTok:\n {user.last_video_url()}")

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            if guild.name == 'Daxak':
                if not self.tiktok_check.is_running():
                    self.tiktok_check.start(guild)


def setup(client):
    client.add_cog(NotificationCog(client))
