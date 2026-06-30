import discord
from discord.ext import commands
from discord import app_commands
import os
from config import WHITELIST_ROLES

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Keluarkan member dari server")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Tidak ada alasan"):
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"✅ {member.mention} berhasil di-kick. Alasan: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Saya tidak memiliki izin untuk meng-kick member ini.", ephemeral=True)

    @app_commands.command(name="ban", description="Ban member dari server")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "Tidak ada alasan"):
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"✅ {member.mention} berhasil di-ban. Alasan: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Saya tidak memiliki izin untuk mem-ban member ini.", ephemeral=True)

    @app_commands.command(name="clear", description="Hapus sejumlah pesan di channel ini")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            return await interaction.response.send_message("❌ Jumlah pesan harus antara 1 dan 100.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Berhasil menghapus {len(deleted)} pesan.")

    @app_commands.command(name="status", description="Tampilkan status perlindungan bot")
    @app_commands.default_permissions(manage_messages=True)
    async def status(self, interaction: discord.Interaction):
        log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))
        
        embed = discord.Embed(
            title="🛡️ Status Perlindungan Bot",
            color=discord.Color.green()
        )
        embed.add_field(name="🔗 Anti-Link", value="✅ Aktif", inline=True)
        embed.add_field(name="🖼️ Anti-Gambar", value="✅ Aktif", inline=True)
        embed.add_field(name="☣️ Anti-File Berbahaya", value="✅ Aktif", inline=True)
        embed.add_field(
            name="📋 Log Channel",
            value=f"<#{log_channel_id}>" if log_channel_id != 0 else "Nonaktif",
            inline=True
        )
        embed.add_field(
            name="👑 Role Dikecualikan",
            value=", ".join(f"`{r}`" for r in WHITELIST_ROLES),
            inline=False
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
