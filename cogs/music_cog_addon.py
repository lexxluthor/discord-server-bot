"""
this module is responsible for all music-related stuff
playing, skipping, pausing, etc.
"""
from datetime import timedelta

import discord
from discord.ext import commands
from youtube_dl import YoutubeDL


from utls.useful_functions import bot_embed, right_channel_checker, special_permission_checker, double_call_if_fail


class MusicCog(commands.Cog):

    def __init__(self, client):
        self.client = client

        # 2d array containing [song, channel], if future for song will be separated class
        self.music_queue = []

        # options for music downloading/playing.
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.YDL_OPTIONS_COOKIES = {'format': 'bestaudio', 'noplaylist': 'True', 'cookiefile': 'coookies.txt'}
        self.YDL_OPTIONS_PLAYLIST = {'format': 'bestaudio', 'noplaylist': 'False'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.channel_name = "bot-commands"
        self.OPTIONS_COUNT = 4
        self.MAX_DISPLAYED_TRACKS = 10

    # searching the item on YouTube
    @double_call_if_fail
    def search_yt(self, item) -> dict:
        """
        this function go to YouTube and download only (?) one song
        it gets first track from search.

        :param item: str
        """
        flag = True
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                if item.startswith("https"):
                    info = ydl.extract_info(item, download=False)
                else:
                    info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception as e:
                print(e)
                flag = False

        if not flag:
            with YoutubeDL(self.YDL_OPTIONS_COOKIES) as ydl:
                try:
                    if item.startswith("https"):
                        info = ydl.extract_info(item, download=False)
                    else:
                        info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
                except Exception as e:
                    print(e)
                    return False

        return {'source': info['formats'][0]['url'], 'title': info['title'], 'duration': info['duration'],
                'channel': info['channel'], 'thumbnail': info['thumbnail'], 'channel_url': info['channel_url']}

    """     function which select song from list of songs. 
        will be implemented later, after I read youtube_dl documentation    """
    # async def select_song(self, ctx: commands.Context, songs):
    #     components = []
    #     for i in range(self.options_count):
    #         print(songs[i])
    #         # button = discord_components.Button(label=songs[i]['title'], style=3, custom_id="button"+str(i))
    #         # components.append(button)
    #     # await ctx.send('123')
    #     return songs[0]

    def play_next(self, ctx: commands.Context):
        """get new song from queue if it exists after skip, or looping through all queue
        until it ends

        :param ctx: commands.Context
        """
        if len(self.music_queue) > 0:
            # get the first url
            m_url = self.music_queue[0][0]['source']
            # remove the first element as you are currently playing it
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
            try:
                voice.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
            except discord.ClientException:
                """ if I try to skip track, it is raise ClientException, idk why. mb it is problem with vc.stop"""
                print('Trying to skip tracks')
            except AttributeError:
                """ if bot leaves, he raise AttributeError"""
                print("Trying to leave voice channel")
            self.music_queue.pop(0)

    async def play_song(self, ctx: commands.Context, song):
        """this function calls from play command, after any try to set song
        responsible for good-looking answer with Embed

        :param ctx: commands.Context,
        :param song
        """
        # song = await self.select_song(ctx, songs)
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if not song:
            await ctx.reply(
                "Could not download the song. Incorrect format try another keyword. "
                "This could be due to playlist or a livestream format.")
        else:
            duration = "{:0>8}".format(str(timedelta(seconds=song['duration'])))

            emb = discord.Embed(title=song['title'],
                                description='Song added to queue!', colour=discord.Colour.blurple())
            emb.set_thumbnail(url=song['thumbnail'])
            emb.set_author(name=song['channel'], url=song['channel_url'])
            emb.add_field(name="Duration", value=f"{duration}")

            await ctx.reply(embed=emb)

            self.music_queue.append([song, voice.channel])

            if not voice.is_playing():
                self.play_next(ctx)

    @commands.command(name="play", help="Plays a selected song from youtube")
    @commands.check(right_channel_checker)
    async def play(self, ctx: commands.Context, *args):
        """play song with this name, if it is link - get it directly by url

        :param ctx: commands.Context
        :param args: str
        """
        name = " ".join(args)

        if ctx.author.voice:
            voice_channel = ctx.author.voice.channel
        else:
            emb = bot_embed(self.client, title='You are not in voice channel')
            await ctx.reply(embed=emb)
            return

        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if ctx.voice_client and voice_channel != ctx.voice_client.channel:
            emb = bot_embed(self.client, title="Bot playing in different voice channel")
            await ctx.reply(embed=emb)
        else:
            if not voice:
                await voice_channel.connect()
            try:
                song = self.search_yt(name)
            except Exception as e:
                print(e)
                song = self.search_yt(name)

            await self.play_song(ctx, song)

    @commands.command(name="queue", help="Displays the current songs in queue")
    @commands.check(right_channel_checker)
    async def queue(self, ctx: commands.Context):
        """shows the first songs in queue, no more than hardcoded MAX_DISPLAYED_TRACKS
        also create nice representing for queue

        :param ctx: commands.Context
        """
        emb = bot_embed(self.client, title="Queue", colour=discord.Colour.dark_gold(),
                        description=f"First {min(self.MAX_DISPLAYED_TRACKS, len(self.music_queue))} track of queue")

        if not self.music_queue:
            emb = bot_embed(self.client, title="Queue",
                            description=f"No tracks in queue", colour=discord.Colour.dark_gold())
        else:
            cnt = 0
            for song, channel in self.music_queue:
                cnt += 1
                minutes = song['duration'] // 60
                seconds = song['duration'] - minutes * 60

                emb.add_field(name=song['title'], value=f"{song['channel']}  {minutes}:{seconds}", inline=False)
                if cnt == self.MAX_DISPLAYED_TRACKS:
                    break
        await ctx.reply(embed=emb)

    @commands.command(name="skip", help="Skips the current song being played")
    @commands.check(special_permission_checker)
    @commands.check(right_channel_checker)
    async def skip(self, ctx: commands.Context):
        """skips the playing song, but for some unexpected reason skip 2 songs, instead of 1

        :param ctx: commands.Context
        """
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if not voice or not voice.is_playing():
            return

        """ when try to skip, from queue deletes two first tracks, not only 1"""
        if self.music_queue:
            self.music_queue.insert(0, self.music_queue[0])

        voice.stop()
        # try to play next in the queue if it exists
        self.play_next(ctx)

    @commands.command(name="leave", help="Disconnecting bot from VC")
    @commands.check(special_permission_checker)
    @commands.check(right_channel_checker)
    async def leave(self, ctx: commands.Context):
        """
        force bot to leave channel. by himself he leaves if not playing music
        approximately 2 minutes

        :param ctx: commands.Context
        """
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if voice:
            await voice.disconnect()
            title = "Leaving voice channel. Bye bye."
        else:
            title = "Bot not in voice channel"

        emb = bot_embed(self.client, title=title)
        await ctx.reply(embed=emb)

    @commands.command(name="pause", help="Pause current song", pass_context=True)
    @commands.check(right_channel_checker)
    @commands.check(special_permission_checker)
    async def pause(self, ctx: commands.Context):
        """:param ctx: commands.Context
        """
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        if not voice:
            title = "Bot not in voice channel. Nothing to pause."
        elif voice.is_playing():
            voice.pause()
            title = "Paused"
        else:
            title = "No audio to pause"

        emb = bot_embed(self.client, title=title)
        await ctx.reply(embed=emb)

    @commands.command(name="resume", help="Resume song if it is paused")
    @commands.check(special_permission_checker)
    @commands.check(right_channel_checker)
    async def resume(self, ctx: commands.Context):
        """:param ctx: commands.Context
        """
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
        else:
            title = "Audio is already playing/No audio"
            emb = bot_embed(self.client, title=title)
            await ctx.reply(embed=emb)

    @commands.command(name="clear", help="Clear queue")
    @commands.check(special_permission_checker)
    @commands.check(right_channel_checker)
    async def clear(self, ctx: commands.Context):
        """clear queue simply by setting it equal to empty list

        :param ctx: commands.Context
        """
        self.music_queue = []

        title = "Queue is cleared!"
        emb = bot_embed(self.client, title=title)
        await ctx.reply(embed=emb)

    @commands.command(name="error", help="About errors")
    @commands.check(right_channel_checker)
    async def error(self, ctx: commands.Context):
        """if you find some errors, or know, how fix existing - try to contact me :)
        if you want to tell me your opinion about how broken it is - it is not worth it

        :param ctx: commands.Context
        """
        description = """
            This is still beta version(like Dota 2)
            common errors - random queue clearing, skip of tracks,
            usually it depends on track size.
            also a lot of sound errors that lies on api problems:
            noise, distortion, accelerations.
            it will be fixed asap.
            (only after i pass my at the university)
            """
        emb = bot_embed(self.client, title="Errors", description=description)
        await ctx.reply(embed=emb)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """
        catch errors and print them in console

        :param ctx: commands.Context
        :param error: commands.CommandError
        """
        if ctx.command:
            print(ctx.command.cog_name, ctx.command.name, end=" ")
        print(error)


def setup(client):
    client.add_cog(MusicCog(client))
