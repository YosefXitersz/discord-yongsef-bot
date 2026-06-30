import discord
from discord.ext import commands
from datetime import datetime
import aiosqlite

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild: discord.Guild):
        async with aiosqlite.connect("bot_database.db") as db:
            async with db.execute("SELECT log_channel_id FROM guild_config WHERE guild_id = ?", (guild.id,)) as cursor:
                row = await cursor.fetchone()
                if row and row[0]:
                    return guild.get_channel(row[0])
        return None

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
            
        log_channel = await self.get_log_channel(message.guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="🗑️ Pesan Dihapus",
            description=f"**Pesan dari {message.author.mention} dihapus di {message.channel.mention}**\n\n{message.content}",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=f"{message.author}", icon_url=message.author.display_avatar.url)
        embed.set_footer(text=f"ID Pengguna: {message.author.id} | ID Pesan: {message.id}")
        
        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild or before.content == after.content:
            return
            
        log_channel = await self.get_log_channel(before.guild)
        if not log_channel:
            return

        embed = discord.Embed(
            title="✏️ Pesan Diedit",
            description=f"**Pesan dari {before.author.mention} diedit di {before.channel.mention}**",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Sebelum", value=before.content or "*(kosong)*", inline=False)
        embed.add_field(name="Sesudah", value=after.content or "*(kosong)*", inline=False)
        embed.set_author(name=f"{before.author}", icon_url=before.author.display_avatar.url)
        embed.set_footer(text=f"ID Pengguna: {before.author.id} | ID Pesan: {before.id}")
        
        try:
            await log_channel.send(embed=embed)
        except discord.Forbidden:
            pass

async def setup(bot):
    await bot.add_cog(Logger(bot))
