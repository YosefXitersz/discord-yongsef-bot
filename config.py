import os

WHITELIST_ROLES = ["Admin", "Moderator", "Mod", "Administrator"]
WHITELIST_CHANNELS = []

EKSTENSI_BERBAHAYA = [
    ".exe", ".bat", ".cmd", ".com", ".msi", ".vbs", ".vbe",
    ".js", ".jse", ".wsf", ".wsh", ".scr", ".pif", ".jar",
    ".ps1", ".ps2", ".psm1", ".reg", ".dll", ".sys", ".lnk",
    ".hta", ".cpl", ".inf", ".sh", ".bash", ".zsh", ".py",
    ".rb", ".php", ".pl", ".msp", ".mst", ".gadget"
]

EKSTENSI_GAMBAR = [
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp",
    ".tiff", ".tif", ".svg", ".ico", ".heic", ".avif"
]
