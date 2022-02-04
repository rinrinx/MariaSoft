import re
from os import environ

id_pattern = re.compile(r'^.\d+$')

def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
SESSION = environ.get('SESSION', 'Media_search')
API_ID = int(environ['API_ID'])
API_HASH = environ['API_HASH']
BOT_TOKEN = environ['BOT_TOKEN']

# Bot settings
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = bool(environ.get('USE_CAPTION_FILTER', True))
PICS = (environ.get('PICS', 'https://telegra.ph/file/7e56d907542396289fee4.jpg https://telegra.ph/file/9aa8dd372f4739fe02d85.jpg https://telegra.ph/file/adffc5ce502f5578e2806.jpg)).split()

# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '0').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in environ.get('AUTH_USERS', '').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []
auth_channel = environ.get('AUTH_CHANNEL')
auth_grp = environ.get('AUTH_GROUP')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "")
DATABASE_NAME = environ.get('DATABASE_NAME', "dzflm")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'Telegram_files')

# Others
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', 0))
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'TeamEvamaria')
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", None)
BROADCAST_AS_COPY = bool(environ.get("BROADCAST_AS_COPY", True))

# Heroku
HEROKU_APP_NAME = environ.get('HEROKU_APP_NAME', None)
HEROKU_API_KEY = environ.get('HEROKU_API_KEY', None)

LOG_STR = "Mevcut Özelleştirilmiş Konfigürasyonlar:-\n"
LOG_STR += (f"CUSTOM_FILE_CAPTION etkinleştirildi {CUSTOM_FILE_CAPTION}, Dosyalarınız bu özelleştirilmiş başlıkla birlikte gönderilecek.\n" if CUSTOM_FILE_CAPTION else "CUSTOM_FILE_CAPTION bulunamadı, dosyanın varsayılan altyazıları kullanılacak.\n")
LOG_STR += (f"BROADCAST_AS_COPY etkinleştirildi {BROADCAST_AS_COPY}, Bot yayınları etiketsiz olarak yayınlanacak.\n" if BROADCAST_AS_COPY else "BROADCAST_AS_COPY bulunamadı. Yayınlarınız etiketli olarak gönderilecek.\n")
