import discord
from discord.ext import commands
import aiosqlite

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        async with aiosqlite.connect("bot_database.db") as db:
            async with db.execute("SELECT welcome_channel_id, autorole_id FROM guild_config WHERE guild_id = ?", (member.guild.id,)) as cursor:
                row = await cursor.fetchone()
                
        if row:
            channel_id = row[0]
            autorole_id = row[1]
            
            # Auto-Role
            if autorole_id:
                role = member.guild.get_role(autorole_id)
                if role:
                    try:
                        await member.add_roles(role)
                    except discord.Forbidden:
                        pass
            
            # Welcome Message
            if channel_id:
                channel = member.guild.get_channel(channel_id)
                if channel:
                    embed = discord.Embed(
                        title="👋 Selamat Datang!",
                        description=f"Halo {member.mention}, selamat datang di **{member.guild.name}**! Jangan lupa baca peraturan server ya.",
                        color=discord.Color.green()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    try:
                        await channel.send(embed=embed)
                    except discord.Forbidden:
                        pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        async with aiosqlite.connect("bot_database.db") as db:
            async with db.execute("SELECT welcome_channel_id FROM guild_config WHERE guild_id = ?", (member.guild.id,)) as cursor:
                row = await cursor.fetchone()
                
        if row and row[0]:
            channel = member.guild.get_channel(row[0])
            if channel:
                embed = discord.Embed(
                    title="😢 Selamat Tinggal!",
                    description=f"**{member.name}** telah keluar dari server. Sampai jumpa lagi!",
                    color=discord.Color.red()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    pass

async def setup(bot):
    await bot.add_cog(Events(bot))
