import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite

class ConfigCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    config_group = app_commands.Group(name="setup", description="Pengaturan dasar bot untuk server ini")
    whitelist_group = app_commands.Group(name="whitelist", description="Pengaturan whitelist role dan channel")
    badword_group = app_commands.Group(name="badword", description="Pengaturan filter kata kasar")

    @config_group.command(name="log_channel", description="Set channel untuk log pelanggaran")
    @app_commands.describe(channel="Pilih channel teks")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("INSERT INTO guild_config (guild_id, log_channel_id) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET log_channel_id = excluded.log_channel_id", (interaction.guild_id, channel.id))
            await db.commit()
        await interaction.response.send_message(f"✅ Log channel telah diatur ke {channel.mention}", ephemeral=True)

    @config_group.command(name="welcome_channel", description="Set channel untuk ucapan selamat datang")
    @app_commands.describe(channel="Pilih channel teks")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("INSERT INTO guild_config (guild_id, welcome_channel_id) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET welcome_channel_id = excluded.welcome_channel_id", (interaction.guild_id, channel.id))
            await db.commit()
        await interaction.response.send_message(f"✅ Welcome channel telah diatur ke {channel.mention}", ephemeral=True)

    @config_group.command(name="autorole", description="Set role otomatis untuk member baru")
    @app_commands.describe(role="Pilih role")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_autorole(self, interaction: discord.Interaction, role: discord.Role):
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("INSERT INTO guild_config (guild_id, autorole_id) VALUES (?, ?) ON CONFLICT(guild_id) DO UPDATE SET autorole_id = excluded.autorole_id", (interaction.guild_id, role.id))
            await db.commit()
        await interaction.response.send_message(f"✅ Auto-role telah diatur ke {role.mention}", ephemeral=True)

    @whitelist_group.command(name="add_role", description="Tambahkan role ke whitelist (kebal filter)")
    @app_commands.describe(role="Pilih role")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_wl_role(self, interaction: discord.Interaction, role: discord.Role):
        async with aiosqlite.connect("bot_database.db") as db:
            try:
                await db.execute("INSERT INTO whitelist_roles (guild_id, role_id) VALUES (?, ?)", (interaction.guild_id, role.id))
                await db.commit()
                await interaction.response.send_message(f"✅ Role {role.mention} ditambahkan ke whitelist.", ephemeral=True)
            except aiosqlite.IntegrityError:
                await interaction.response.send_message(f"⚠️ Role {role.mention} sudah ada di whitelist.", ephemeral=True)

    @whitelist_group.command(name="remove_role", description="Hapus role dari whitelist")
    @app_commands.describe(role="Pilih role")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_wl_role(self, interaction: discord.Interaction, role: discord.Role):
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("DELETE FROM whitelist_roles WHERE guild_id = ? AND role_id = ?", (interaction.guild_id, role.id))
            await db.commit()
        await interaction.response.send_message(f"✅ Role {role.mention} dihapus dari whitelist.", ephemeral=True)

    @whitelist_group.command(name="add_channel", description="Tambahkan channel ke whitelist (bebas filter)")
    @app_commands.describe(channel="Pilih channel teks")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_wl_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        async with aiosqlite.connect("bot_database.db") as db:
            try:
                await db.execute("INSERT INTO whitelist_channels (guild_id, channel_id) VALUES (?, ?)", (interaction.guild_id, channel.id))
                await db.commit()
                await interaction.response.send_message(f"✅ Channel {channel.mention} ditambahkan ke whitelist.", ephemeral=True)
            except aiosqlite.IntegrityError:
                await interaction.response.send_message(f"⚠️ Channel {channel.mention} sudah ada di whitelist.", ephemeral=True)

    @whitelist_group.command(name="remove_channel", description="Hapus channel dari whitelist")
    @app_commands.describe(channel="Pilih channel teks")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_wl_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("DELETE FROM whitelist_channels WHERE guild_id = ? AND channel_id = ?", (interaction.guild_id, channel.id))
            await db.commit()
        await interaction.response.send_message(f"✅ Channel {channel.mention} dihapus dari whitelist.", ephemeral=True)

    @badword_group.command(name="add", description="Tambahkan kata ke filter badword")
    @app_commands.describe(word="Kata kasar (tanpa spasi)")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_badword(self, interaction: discord.Interaction, word: str):
        word = word.lower()
        async with aiosqlite.connect("bot_database.db") as db:
            try:
                await db.execute("INSERT INTO badwords (guild_id, word) VALUES (?, ?)", (interaction.guild_id, word))
                await db.commit()
                await interaction.response.send_message(f"✅ Kata `{word}` ditambahkan ke filter.", ephemeral=True)
            except aiosqlite.IntegrityError:
                await interaction.response.send_message(f"⚠️ Kata `{word}` sudah ada di filter.", ephemeral=True)

    @badword_group.command(name="remove", description="Hapus kata dari filter badword")
    @app_commands.describe(word="Kata kasar (tanpa spasi)")
    @app_commands.checks.has_permissions(administrator=True)
    async def remove_badword(self, interaction: discord.Interaction, word: str):
        word = word.lower()
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("DELETE FROM badwords WHERE guild_id = ? AND word = ?", (interaction.guild_id, word))
            await db.commit()
        await interaction.response.send_message(f"✅ Kata `{word}` dihapus dari filter.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ConfigCmd(bot))
