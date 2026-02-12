import re
import os
from os import environ, getenv
from Script import script

# --- Helper Functions ---
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "on"]:
        return True
    elif value.lower() in ["false", "no", "0", "off"]:
        return False
    return default

# =========================================================
# 🤖 BOT INFO & CREDENTIALS
# =========================================================
SESSION = environ.get('SESSION', 'Webavbot')
API_ID = int(environ.get('API_ID', '12000656'))
API_HASH = environ.get('API_HASH', 'd927c13beaaf5110f2c071273')
BOT_TOKEN = environ.get('BOT_TOKEN', '70917168:AAF8TzmnNYW721xIUUuseLU41xa5bRA')

# Admin Settings
ADMINS = [int(x) for x in environ.get('ADMINS', '5977931010').split()]
OWNER_USERNAME = environ.get("OWNER_USERNAME", 'BOT_OWNER26')

# =========================================================
# 🗄️ DATABASE CONNECTION
# =========================================================
DB_URL = environ.get('DATABASE_URI', "mongodb+srv://teshsjsg1:axxxxtz@testing.kwuyhwka.mongodb.net/?appName=testing")
DB_NAME = environ.get('DATABASE_NAME', "testing")

# =========================================================
# 📢 CHANNELS & LOGS
# =========================================================
# Mandatory Channels
BIN_CHANNEL = int(environ.get("BIN_CHANNEL", '-1002114619001'))
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", '-1002114619001'))

# Feature Specific Logs
PREMIUM_LOGS = int(environ.get("PREMIUM_LOGS", '-1002114619001'))
VERIFIED_LOG = int(environ.get('VERIFIED_LOG', '-1002114619001'))
SUPPORT_GROUP = int(environ.get("SUPPORT_GROUP", "-1002114619001"))

# Auth Channels (Safe Parsing)
auth_channel_str = environ.get("AUTH_CHANNEL", "-1002114619001")
AUTH_CHANNEL = [int(x) for x in auth_channel_str.split()] if auth_channel_str else []

# =========================================================
# 🔗 LINKS & URLS
# =========================================================
CHANNEL = environ.get('CHANNEL', 'https://t.me/AV_BOTz_UPDATE')
SUPPORT = environ.get('SUPPORT', 'https://t.me/AV_SUPPORT_GROUP')

# =========================================================
# ⚙️ SETTINGS & LIMITS
# =========================================================
FSUB = is_enabled(environ.get("FSUB", "True"), True)
ENABLE_LIMIT = is_enabled(environ.get("ENABLE_LIMIT", "True"), True)
MAINTENANCE_MODE = is_enabled(environ.get("MAINTENANCE_MODE", "False"), False)

# Time & Rate Limits
TIMEZONE = environ.get("TIMEZONE", "Asia/Kolkata")
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
SLEEP_THRESHOLD = int(getenv('SLEEP_THRESHOLD', '60'))
RATE_LIMIT_TIMEOUT = int(environ.get("RATE_LIMIT_TIMEOUT", "600"))

# File Limits
MAX_FILES = int(environ.get("MAX_FILES", "5"))
BATCH_LIMIT = int(environ.get('BATCH_LIMIT', 60))

# =========================================================
# 🖼️ MEDIA & CAPTIONS
# =========================================================
QR_CODE = environ.get('QR_CODE', 'https://graph.org/file/6afb4093d5ec5c4176979.jpg')
AUTH_PICS = environ.get('AUTH_PICS', 'https://envs.sh/AwV.jpg')
PICS = environ.get('PICS', 'https://ibb.co/VpTJNNCN')
FILE_PIC = environ.get('FILE_PIC', 'https://i.ibb.co/bj4My0bW/photo-2025-07-21-02-15-21-7529360175656861700.jpg')

FILE_CAPTION = environ.get('FILE_CAPTION', script.CAPTION)
CHANNEL_FILE_CAPTION = environ.get('CHANNEL_FILE_CAPTION', '<b>Channel:</b> <code>{}</code>\n<b>File:</b> <code>{}</code>')

# =========================================================
# 🎬 MINI APP CONFIG (Telegram WebApp for Video Streaming)
# =========================================================
ENABLE_MINI_APP = is_enabled(environ.get("ENABLE_MINI_APP", "True"), True)

# =========================================================
# 🌐 SERVER & APP CONFIG
# =========================================================
WORKERS = int(getenv('WORKERS', '4'))
MULTI_CLIENT = False
name = str(environ.get('name', 'avbotz'))

# Heroku & Port Config
if 'DYNO' in environ:
    ON_HEROKU = True
    APP_NAME = str(getenv('APP_NAME'))
else:
    ON_HEROKU = False
    APP_NAME = None

PORT = int(getenv('PORT', '2626'))
NO_PORT = is_enabled(getenv("NO_PORT", "False"), False)
HAS_SSL = is_enabled(getenv("HAS_SSL", "False"), False)
BIND_ADDRESS = getenv("WEB_SERVER_BIND_ADDRESS", "127.0.0.1")

# URL Generation
# Use provided URL from env, or generate based on FQDN/IP
custom_url = environ.get("URL")
if custom_url:
    URL = custom_url
else:
    FQDN = getenv("FQDN", BIND_ADDRESS)
    PROTOCOL = "https" if HAS_SSL else "http"
    PORT_SEGMENT = "" if NO_PORT else f":{PORT}"
    URL = f"{PROTOCOL}://{FQDN}{PORT_SEGMENT}/"

# Default fallback if nothing works (Matches your provided koyeb link)
if not URL or URL == "/":
    URL = "https://forward-jolyn-vnnmbs-62200c9e.koyeb.app/"
    
