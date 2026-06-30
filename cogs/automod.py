import discord
from discord.ext import commands
import re
from config import EKSTENSI_BERBAHAYA, EKSTENSI_GAMBAR
from datetime import datetime, timedelta
import aiosqlite
import os

URL_PATTERN = re.compile(
    r"(https?://[^\s]+|www\.[^\s]+|\b[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}(/[^\s]*)?)",
    re.IGNORECASE
)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.spam_cache = {}  # {user_id: [timestamps]}

    async def tambah_warn(self, user_id: int, guild_id: int, reason: str):
        async with aiosqlite.connect("bot_database.db") as db:
            await db.execute(
                "CREATE TABLE IF NOT EXISTS warns (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, guild_id INTEGER, reason TEXT, timestamp TEXT)"
            )
            await db.execute(
                "INSERT INTO warns (user_id, guild_id, reason, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, guild_id, reason, datetime.now().isoformat())
            )
            await db.commit()
            
            # Hitung jumlah warn
            async with db.execute("SELECT COUNT(*) FROM warns WHERE user_id = ? AND guild_id = ?", (user_id, guild_id)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def log_pelanggaran(self, guild: discord.Guild, embed: discord.Embed):
        async with aiosqlite.connect("bot_database.db") as db:
            async with db.execute("SELECT log_channel_id FROM guild_config WHERE guild_id = ?", (guild.id,)) as cursor:
                row = await cursor.fetchone()
                if not row or not row[0]:
                    return
                channel_id = row[0]
                
        channel = guild.get_channel(channel_id)
        if channel:
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        is_admin = isinstance(message.author, discord.Member) and message.author.guild_permissions.administrator
        
        async with aiosqlite.connect("bot_database.db") as db:
            # Cek Whitelist Channel
            async with db.execute("SELECT 1 FROM whitelist_channels WHERE guild_id = ? AND channel_id = ?", (message.guild.id, message.channel.id)) as cursor:
                if await cursor.fetchone():
                    return
                    
            # Cek Whitelist Role
            if not is_admin and isinstance(message.author, discord.Member):
                role_ids = [r.id for r in message.author.roles]
                placeholders = ",".join("?" for _ in role_ids)
                if role_ids:
                    query = f"SELECT 1 FROM whitelist_roles WHERE guild_id = ? AND role_id IN ({placeholders})"
                    params = [message.guild.id] + role_ids
                    async with db.execute(query, params) as cursor:
                        if await cursor.fetchone():
                            return
            elif is_admin:
                return # Admin kebal
                
            # Ambil daftar badword
            badwords = []
            async with db.execute("SELECT word FROM badwords WHERE guild_id = ?", (message.guild.id,)) as cursor:
                async for row in cursor:
                    badwords.append(row[0])

        # Anti-Spam Sederhana (5 pesan dalam 5 detik)
        user_id = message.author.id
        now = datetime.now()
        if user_id not in self.spam_cache:
            self.spam_cache[user_id] = []
            
        self.spam_cache[user_id].append(now)
        # Hapus yang lebih lama dari 5 detik
        self.spam_cache[user_id] = [t for t in self.spam_cache[user_id] if (now - t).total_seconds() <= 5]
        
        if len(self.spam_cache[user_id]) >= 5:
            self.spam_cache[user_id] = [] # Reset
            try:
                await message.author.timeout(timedelta(minutes=5), reason="Spamming")
                await message.channel.send(f"🚫 {message.author.mention} telah di-timeout selama 5 menit karena spam.")
            except discord.Forbidden:
                pass
            return

        # Cek Anti-Mention Spam
        if len(message.mentions) > 5:
            try:
                await message.delete()
                await message.author.timeout(timedelta(minutes=10), reason="Mention Spam")
                await message.channel.send(f"🚨 {message.author.mention} telah di-timeout karena spam mention.")
            except discord.Forbidden:
                pass
            return

        # Cek Attachment
        hapus_pesan = False
        alasan = ""
        tipe_pelanggaran = ""

        if message.attachments:
            for attachment in message.attachments:
                nama_file = attachment.filename.lower()
                ekstensi = "." + nama_file.rsplit(".", 1)[-1] if "." in nama_file else ""

                if ekstensi in EKSTENSI_BERBAHAYA:
                    hapus_pesan = True
                    alasan = f"Mengirim file berbahaya: `{attachment.filename}`"
                    tipe_pelanggaran = "File Berbahaya"
                    break
                
                if ekstensi in EKSTENSI_GAMBAR or (attachment.content_type and attachment.content_type.startswith("image/")):
                    hapus_pesan = True
                    alasan = f"Mengirim gambar: `{attachment.filename}`"
                    tipe_pelanggaran = "Gambar"
                    break

        # Cek Link
        if not hapus_pesan and message.content and URL_PATTERN.search(message.content):
            hapus_pesan = True
            alasan = "Mengirim Link / URL"
            tipe_pelanggaran = "Link"
            
        # Cek Badword
        if not hapus_pesan and message.content:
            msg_lower = message.content.lower()
            for word in badwords:
                if word in msg_lower:
                    hapus_pesan = True
                    alasan = f"Mengirim kata terlarang: ||{word}||"
                    tipe_pelanggaran = "Badword"
                    break

        if hapus_pesan:
            try:
                await message.delete()
            except discord.Forbidden:
                pass

            total_warns = await self.tambah_warn(message.author.id, message.guild.id, tipe_pelanggaran)
            
            peringatan = f"⚠️ {message.author.mention} Pesan kamu dihapus karena **{tipe_pelanggaran}**. (Peringatan ke-{total_warns})"
            
            try:
                await message.channel.send(peringatan, delete_after=8)
            except discord.Forbidden:
                pass

            # Timeout otomatis jika warn mencapai 3
            if total_warns >= 3:
                try:
                    await message.author.timeout(timedelta(hours=1), reason="Mencapai 3 peringatan (AutoMod)")
                    await message.channel.send(f"🚨 {message.author.mention} di-timeout selama 1 jam karena mencapai 3 peringatan.")
                except discord.Forbidden:
                    pass

            embed = discord.Embed(
                title=f"🚨 {tipe_pelanggaran} Terdeteksi",
                description=f"Alasan: {alasan}\nTotal Peringatan: {total_warns}",
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="👤 Pengguna", value=f"{message.author.mention} (`{message.author}`)", inline=True)
            embed.add_field(name="📌 Channel", value=message.channel.mention, inline=True)
            await self.log_pelanggaran(message.guild, embed)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
