import math

import requests
import heroku3

from pyrogram import Client, filters
from info import ADMINS, HEROKU_APP_NAME, HEROKU_API_KEY

@Client.on_message(filters.command('usage') & filters.user(ADMINS))
async def dyno_usage(bot, message):
    heroku_api = "https://api.heroku.com"
    if HEROKU_API_KEY is not None and HEROKU_APP_NAME is not None:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        app = Heroku.app(HEROKU_APP_NAME)
    else:
        await message.reply_text(
            "Please insert your HEROKU_APP_NAME and HEROKU_API_KEY in Vars"
        )
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/81.0.4044.117 Mobile Safari/537.36"
    )
    user_id = Heroku.account().id
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + user_id + "/actions/get-quota"
    session = requests.Session()
    with session as ses:
        with ses.get(heroku_api + path, headers=headers) as r:
            result = r.json()
            """Account Quota."""
            quota = result["account_quota"]
            quota_used = result["quota_used"]
            quota_remain = quota - quota_used
            quota_percent = math.floor(quota_remain / quota * 100)
            minutes_remain = quota_remain / 60
            hours = math.floor(minutes_remain / 60)
            minutes = math.floor(minutes_remain % 60)
            day = math.floor(hours / 24)

            """App Quota."""
            Apps = result["apps"]
            for apps in Apps:
                if apps.get("app_uuid") == app.id:
                    AppQuotaUsed = apps.get("quota_used") / 60
                    AppPercent = math.floor(apps.get("quota_used") * 100 / quota)
                    break
            else:
                AppQuotaUsed = 0
                AppPercent = 0

            AppHours = math.floor(AppQuotaUsed / 60)
            AppMinutes = math.floor(AppQuotaUsed % 60)

            await message.reply_text(
                f"<b>ℹ️ Dyno Usage ℹ️</b>\n\n<code>🟢 {app.name}</code>:\n"
                f"• <code>{AppHours}</code> <b>Hours and</b> <code>{AppMinutes}</code> <b>Minutes\n💯: {AppPercent}%</b>\n\n"
                "<b>⚠️ Dyno Remaining ⚠️</b>\n"
                f"• <code>{hours}</code> <b>Hours and</b> <code>{minutes}</code> <b>Minutes\n💯: {quota_percent}%</b>\n\n"
                "<b>❌ Estimated Expired ❌</b>\n"
                f"• <code>{day}</code> <b>Days</b>"
            )
