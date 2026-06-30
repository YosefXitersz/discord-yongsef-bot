import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiosqlite

# Load environment variables dari .env file
load_dotenv()

TOKEN = os.getenv("TOKEN")

if not TOKEN or TOKEN == "TOKEN_BOT_KAMU_DISINI":
    print("❌ ERROR: Token bot belum diisi!")
    print("Silakan buka file .env dan masukkan token bot kamu.")
    exit()

class VibeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True
        intents.members = True # Dibutuhkan untuk events member join/remove

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None # Opsional: nonaktifkan default help
        )

    async def setup_hook(self):
        # Load semua cogs di dalam folder cogs
        print("Mulai memuat cogs...")
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Cog dimuat: {filename}")
        
        # Inisialisasi Database
        print("Menyiapkan database...")
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute("CREATE TABLE IF NOT EXISTS warns (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, guild_id INTEGER, reason TEXT, timestamp TEXT)")
            await db.execute("CREATE TABLE IF NOT EXISTS guild_config (guild_id INTEGER PRIMARY KEY, log_channel_id INTEGER, welcome_channel_id INTEGER, autorole_id INTEGER)")
            await db.execute("CREATE TABLE IF NOT EXISTS whitelist_roles (guild_id INTEGER, role_id INTEGER, PRIMARY KEY (guild_id, role_id))")
            await db.execute("CREATE TABLE IF NOT EXISTS whitelist_channels (guild_id INTEGER, channel_id INTEGER, PRIMARY KEY (guild_id, channel_id))")
            await db.execute("CREATE TABLE IF NOT EXISTS badwords (guild_id INTEGER, word TEXT, PRIMARY KEY (guild_id, word))")
            await db.commit()
        print("✅ Database siap.")
        
        # Sync slash commands ke Discord
        print("Menyinkronkan slash commands...")
        await self.tree.sync()
        print("✅ Slash commands disinkronkan.")

    async def on_ready(self):
        print("=" * 45)
        print(f"  ✅ Bot aktif sebagai: {self.user}")
        print("=" * 45)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="🛡️ Melindungi server"
            )
        )

bot = VibeBot()

if __name__ == "__main__":
    bot.run(TOKEN)
