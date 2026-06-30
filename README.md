# 🛡️ Bot Discord — Anti-Link, Anti-Gambar, Anti-File Berbahaya

Bot sederhana berbasis **discord.py** untuk menjaga keamanan server kamu.

---

## ✅ Fitur

| Fitur | Keterangan |
|---|---|
| 🔗 Anti-Link | Hapus otomatis pesan yang mengandung URL |
| 🖼️ Anti-Gambar | Hapus otomatis attachment gambar (png, jpg, gif, dll) |
| ☣️ Anti-File Berbahaya | Blokir file mencurigakan (.exe, .bat, .cmd, dll) |
| 👑 Whitelist Role | Admin & Moderator bebas kirim apa saja |
| 📋 Log Pelanggaran | Kirim log ke channel khusus (opsional) |

---

## 🚀 Cara Setup

### 1. Install Python
Download Python 3.10+ dari https://python.org

### 2. Install Library
```bash
pip install -r requirements.txt
```

### 3. Buat Bot Discord
1. Buka https://discord.com/developers/applications
2. Klik **"New Application"**, beri nama botmu
3. Masuk ke tab **"Bot"** → klik **"Add Bot"**
4. Aktifkan semua **Privileged Gateway Intents**:
   - ✅ PRESENCE INTENT
   - ✅ SERVER MEMBERS INTENT
   - ✅ MESSAGE CONTENT INTENT
5. Klik **"Reset Token"** → salin tokennya

### 4. Edit File `bot.py`
Buka `bot.py` dan sesuaikan bagian konfigurasi:

```python
TOKEN = "TOKEN_BOT_KAMU_DISINI"   # ← Token dari Discord Developer Portal

LOG_CHANNEL_ID = 0                 # ← Isi ID channel log (0 = nonaktif)

WHITELIST_ROLES = ["Admin", "Moderator"]  # ← Role yang dikecualikan

WHITELIST_CHANNELS = []            # ← ID channel yang dikecualikan dari filter
```

**Cara ambil ID channel:**
Aktifkan Developer Mode di Discord (Settings → Advanced → Developer Mode),
lalu klik kanan channel → "Copy Channel ID"

### 5. Invite Bot ke Server
1. Di Developer Portal, masuk ke tab **"OAuth2" → "URL Generator"**
2. Centang scope: `bot`
3. Centang permissions:
   - ✅ Read Messages / View Channels
   - ✅ Send Messages
   - ✅ Manage Messages ← **wajib untuk hapus pesan**
   - ✅ Embed Links
4. Salin URL yang dihasilkan → buka di browser → pilih server

### 6. Jalankan Bot
```bash
python bot.py
```

---

## 💬 Perintah Bot

| Perintah | Keterangan | Izin |
|---|---|---|
| `!status` | Tampilkan status perlindungan aktif | Manage Messages |

---

## ⚙️ Kustomisasi

### Tambah/kurangi ekstensi file berbahaya
Edit list `EKSTENSI_BERBAHAYA` di `bot.py`:
```python
EKSTENSI_BERBAHAYA = [".exe", ".bat", ...]
```

### Tambah channel khusus yang bebas filter
```python
WHITELIST_CHANNELS = [123456789012345678]  # ID channel
```

### Tambah role yang dikecualikan
```python
WHITELIST_ROLES = ["Admin", "Moderator", "Trusted"]
```

---

## 🔒 Tips Keamanan
- Jangan pernah bagikan TOKEN botmu kepada siapapun
- Simpan token di environment variable jika deploy ke server
- Pastikan bot punya permission **"Manage Messages"** agar bisa hapus pesan
