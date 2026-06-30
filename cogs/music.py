import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

# Setup yt-dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {} # {guild_id: [YTDLSource]}

    def check_queue(self, guild_id, voice_client):
        if self.queues.get(guild_id):
            source = self.queues[guild_id].pop(0)
            voice_client.play(source, after=lambda e: self.check_queue(guild_id, voice_client))

    @app_commands.command(name="play", description="Putar lagu dari YouTube/Spotify")
    @app_commands.describe(url="Link lagu atau judul pencarian")
    async def play(self, interaction: discord.Interaction, url: str):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Kamu harus berada di Voice Channel terlebih dahulu!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if not voice_client:
            await voice_channel.connect()
            voice_client = interaction.guild.voice_client

        await interaction.response.send_message(f"🔍 Sedang mencari dan menyiapkan lagu: `{url}`...")

        try:
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            
            if interaction.guild.id not in self.queues:
                self.queues[interaction.guild.id] = []

            if voice_client.is_playing():
                self.queues[interaction.guild.id].append(player)
                await interaction.followup.send(f"🎵 Lagu dimasukkan ke antrean: **{player.title}**")
            else:
                voice_client.play(player, after=lambda e: self.check_queue(interaction.guild.id, voice_client))
                await interaction.followup.send(f"▶️ Sedang memutar: **{player.title}**")
                
        except Exception as e:
            await interaction.followup.send(f"❌ Terjadi kesalahan: {e}")

    @app_commands.command(name="stop", description="Hentikan lagu dan keluar dari Voice Channel")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client:
            self.queues[interaction.guild.id] = []
            await voice_client.disconnect()
            await interaction.response.send_message("⏹️ Musik dihentikan dan bot keluar dari Voice Channel.")
        else:
            await interaction.response.send_message("❌ Bot tidak sedang berada di Voice Channel.", ephemeral=True)

    @app_commands.command(name="skip", description="Lewati lagu saat ini")
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop() # Ini akan mentrigger 'after' di play dan memutar lagu berikutnya
            await interaction.response.send_message("⏭️ Lagu dilewati.")
        else:
            await interaction.response.send_message("❌ Tidak ada lagu yang sedang diputar.", ephemeral=True)
            
    @app_commands.command(name="queue", description="Lihat daftar antrean lagu")
    async def queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in self.queues and self.queues[guild_id]:
            q_list = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(self.queues[guild_id])])
            embed = discord.Embed(title="🎵 Antrean Lagu", description=q_list, color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("📂 Antrean kosong.")

async def setup(bot):
    await bot.add_cog(Music(bot))
