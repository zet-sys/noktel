import asyncio
import re
import time
import os
import sys
import logging
import json
import random
import math
import string
import zipfile
import shutil
import sqlite3
import struct
import base64
import socket
import traceback
import html  # <--- WAJIB ADA BUAT FITUR BACA ERROR LENGKAP
from io import BytesIO
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Union
from telethon.tl.functions.account import GetPasswordRequest
from telethon.tl.functions.account import GetAuthorizationsRequest
from telethon.tl.functions.auth import ResetAuthorizationsRequest

WIB = timezone(timedelta(hours=7))
START_TIME = datetime.now(WIB)

try:
    from pyrogram import Client, filters
    from pyrogram.types import (
        InlineKeyboardButton, 
        InlineKeyboardMarkup, 
        CallbackQuery, 
        Message,
        ForceReply,
        InputMediaPhoto
    )
    from pyrogram.enums import ParseMode
    from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
    from pyrogram.errors import FloodWait, RPCError, PeerIdInvalid, MessageNotModified
    
    from telethon import TelegramClient, errors
    from telethon.sessions import StringSession
    from bson.objectid import ObjectId 
    
    from config import Config
    import database
    from payment import PaymentGateway 
    from logch import Logger
except ImportError as e:
    print(f"❌ ᴄʀɪᴛɪᴄᴀʟ ᴇʀʀᴏʀ ɪᴍᴘᴏʀᴛ (MODULE MISSING): {e}")
    print("👉 TIPS: Silakan jalankan command berikut di terminal VPS Anda:")
    print("   pip install pyrogram tgcrypto telethon motor motor-asyncio aiohttp")
    sys.exit(1)

# ============================================================
# DICTIONARY AUTO-REGION MEGA ULTRA PRO MAX (SELURUH DUNIA)
# ============================================================
# ============================================================
# DICTIONARY AUTO-REGION MEGA ULTRA PRO MAX (DATABASE NORMAL)
# ============================================================
COUNTRY_CODES = {
    # KODE +1 (AMERIKA UTARA & KARIBIA)
    "1242": ("🇧🇸 Bahama", "BS"), "1246": ("🇧🇧 Barbados", "BB"), "1264": ("🇦🇮 Anguilla", "AI"), 
    "1268": ("🇦🇬 Antigua dan Barbuda", "AG"), "1284": ("🇻🇬 Kepulauan Virgin Inggris", "VG"), 
    "1340": ("🇻🇮 Kepulauan Virgin AS", "VI"), "1345": ("🇰🇾 Kepulauan Cayman", "KY"), 
    "1441": ("🇧🇲 Bermuda", "BM"), "1473": ("🇬🇩 Grenada", "GD"), "1649": ("🇹🇨 Turks dan Caicos", "TC"), 
    "1658": ("🇯🇲 Jamaika", "JM"), "1664": ("🇲🇸 Montserrat", "MS"), "1670": ("🇲🇵 Kepulauan Mariana Utara", "MP"), 
    "1671": ("🇬🇺 Guam", "GU"), "1684": ("🇦🇸 Samoa Amerika", "AS"), "1721": ("🇸🇽 Sint Maarten", "SX"), 
    "1758": ("🇱🇨 Saint Lucia", "LC"), "1767": ("🇩🇲 Dominika", "DM"), "1784": ("🇻🇨 Saint Vincent", "VC"), 
    "1787": ("🇵🇷 Puerto Riko", "PR"), "1809": ("🇩🇴 Republik Dominika", "DO"), "1829": ("🇩🇴 Republik Dominika", "DO"), 
    "1849": ("🇩🇴 Republik Dominika", "DO"), "1868": ("🇹🇹 Trinidad dan Tobago", "TT"), "1869": ("🇰🇳 Saint Kitts dan Nevis", "KN"), 
    "1876": ("🇯🇲 Jamaika", "JM"), "1939": ("🇵🇷 Puerto Riko", "PR"), 
    "1": ("🇺🇸 Amerika / Kanada", "US"),
    
    # KODE +7 (RUSIA & KAZAKHSTAN)
    "7": ("🇷🇺 Rusia / Kazakhstan", "RU"), 
    
    # AFRIKA
    "20": ("🇪🇬 Mesir", "EG"), "211": ("🇸🇸 Sudan Selatan", "SS"), "212": ("🇲🇦 Maroko", "MA"), 
    "213": ("🇩🇿 Aljazair", "DZ"), "216": ("🇹🇳 Tunisia", "TN"), "218": ("🇱🇾 Libya", "LY"), 
    "220": ("🇬🇲 Gambia", "GM"), "221": ("🇸🇳 Senegal", "SN"), "222": ("🇲🇷 Mauritania", "MR"), 
    "223": ("🇲🇱 Mali", "ML"), "224": ("🇬🇳 Guinea", "GN"), "225": ("🇨🇮 Pantai Gading", "CI"), 
    "226": ("🇧🇫 Burkina Faso", "BF"), "227": ("🇳🇪 Niger", "NE"), "228": ("🇹🇬 Togo", "TG"), 
    "229": ("🇧🇯 Benin", "BJ"), "230": ("🇲🇺 Mauritius", "MU"), "231": ("🇱🇷 Liberia", "LR"), 
    "232": ("🇸🇱 Sierra Leone", "SL"), "233": ("🇬🇭 Ghana", "GH"), "234": ("🇳🇬 Nigeria", "NG"), 
    "235": ("🇹🇩 Chad", "TD"), "236": ("🇨🇫 Afrika Tengah", "CF"), "237": ("🇨🇲 Kamerun", "CM"), 
    "238": ("🇨🇻 Tanjung Verde", "CV"), "239": ("🇸🇹 Sao Tome & Principe", "ST"), "240": ("🇬🇶 Guinea Khatulistiwa", "GQ"), 
    "241": ("🇬🇦 Gabon", "GA"), "242": ("🇨🇬 Rep. Kongo", "CG"), "243": ("🇨🇩 RD Kongo", "CD"), 
    "244": ("🇦🇴 Angola", "AO"), "245": ("🇬🇼 Guinea Bissau", "GW"), "246": ("🇮🇴 Diego Garcia", "IO"), 
    "248": ("🇸🇨 Seychelles", "SC"), "249": ("🇸🇩 Sudan", "SD"), "250": ("🇷🇼 Rwanda", "RW"), 
    "251": ("🇪🇹 Etiopia", "ET"), "252": ("🇸🇴 Somalia", "SO"), "253": ("🇩🇯 Djibouti", "DJ"), 
    "254": ("🇰🇪 Kenya", "KE"), "255": ("🇹🇿 Tanzania", "TZ"), "256": ("🇺🇬 Uganda", "UG"), 
    "257": ("🇧🇮 Burundi", "BI"), "258": ("🇲🇿 Mozambik", "MZ"), "260": ("🇿🇲 Zambia", "ZM"), 
    "261": ("🇲🇬 Madagaskar", "MG"), "262": ("🇷🇪 Reunion", "RE"), "263": ("🇿🇼 Zimbabwe", "ZW"), 
    "264": ("🇳🇦 Namibia", "NA"), "265": ("🇲🇼 Malawi", "MW"), "266": ("🇱🇸 Lesotho", "LS"), 
    "267": ("🇧🇼 Botswana", "BW"), "268": ("🇸🇿 Eswatini", "SZ"), "269": ("🇰🇲 Komoro", "KM"), 
    "27": ("🇿🇦 Afrika Selatan", "ZA"), "290": ("🇸🇭 Saint Helena", "SH"), "291": ("🇪🇷 Eritrea", "ER"), 
    "297": ("🇦🇼 Aruba", "AW"), "298": ("🇫🇴 Kepulauan Faroe", "FO"), "299": ("🇬🇱 Greenland", "GL"),
    
    # EROPA
    "30": ("🇬🇷 Yunani", "GR"), "31": ("🇳🇱 Belanda", "NL"), "32": ("🇧🇪 Belgia", "BE"), 
    "33": ("🇫🇷 Prancis", "FR"), "34": ("🇪🇸 Spanyol", "ES"), "350": ("🇬🇮 Gibraltar", "GI"), 
    "351": ("🇵🇹 Portugal", "PT"), "352": ("🇱🇺 Luksemburg", "LU"), "353": ("🇮🇪 Irlandia", "IE"), 
    "354": ("🇮🇸 Islandia", "IS"), "355": ("🇦🇱 Albania", "AL"), "356": ("🇲🇹 Malta", "MT"), 
    "357": ("🇨🇾 Siprus", "CY"), "358": ("🇫🇮 Finlandia", "FI"), "359": ("🇧🇬 Bulgaria", "BG"), 
    "36": ("🇭🇺 Hungaria", "HU"), "370": ("🇱🇹 Lithuania", "LT"), "371": ("🇱🇻 Latvia", "LV"), 
    "372": ("🇪🇪 Estonia", "EE"), "373": ("🇲🇩 Moldova", "MD"), "374": ("🇦🇲 Armenia", "AM"), 
    "375": ("🇧🇾 Belarus", "BY"), "376": ("🇦🇩 Andorra", "AD"), "377": ("🇲🇨 Monako", "MC"), 
    "378": ("🇸🇲 San Marino", "SM"), "379": ("🇻🇦 Vatikan", "VA"), "380": ("🇺🇦 Ukraina", "UA"), 
    "381": ("🇷🇸 Serbia", "RS"), "382": ("🇲🇪 Montenegro", "ME"), "383": ("🇽🇰 Kosovo", "XK"), 
    "385": ("🇭🇷 Kroasia", "HR"), "386": ("🇸🇮 Slovenia", "SI"), "387": ("🇧🇦 Bosnia & Herzegovina", "BA"), 
    "389": ("🇲🇰 Makedonia Utara", "MK"), "39": ("🇮🇹 Italia", "IT"), "40": ("🇷🇴 Romania", "RO"), 
    "41": ("🇨🇭 Swiss", "CH"), "420": ("🇨🇿 Ceko", "CZ"), "421": ("🇸🇰 Slovakia", "SK"), 
    "423": ("🇱🇮 Liechtenstein", "LI"), "43": ("🇦🇹 Austria", "AT"), "44": ("🇬🇧 Inggris", "GB"), 
    "45": ("🇩🇰 Denmark", "DK"), "46": ("🇸🇪 Swedia", "SE"), "47": ("🇳🇴 Norwegia", "NO"), 
    "48": ("🇵🇱 Polandia", "PL"), "49": ("🇩🇪 Jerman", "DE"),
    
    # AMERIKA TENGAH & SELATAN
    "500": ("🇫🇰 Kep. Falkland", "FK"), "501": ("🇧🇿 Belize", "BZ"), "502": ("🇬🇹 Guatemala", "GT"), 
    "503": ("🇸🇻 El Salvador", "SV"), "504": ("🇭🇳 Honduras", "HN"), "505": ("🇳🇮 Nikaragua", "NI"), 
    "506": ("🇨🇷 Kosta Rika", "CR"), "507": ("🇵🇦 Panama", "PA"), "508": ("🇵🇲 Saint Pierre & Miquelon", "PM"), 
    "509": ("🇭🇹 Haiti", "HT"), "51": ("🇵🇪 Peru", "PE"), "52": ("🇲🇽 Meksiko", "MX"), 
    "53": ("🇨🇺 Kuba", "CU"), "54": ("🇦🇷 Argentina", "AR"), "55": ("🇧🇷 Brazil", "BR"), 
    "56": ("🇨🇱 Chile", "CL"), "57": ("🇨🇴 Kolombia", "CO"), "58": ("🇻🇪 Venezuela", "VE"), 
    "590": ("🇬🇵 Guadeloupe", "GP"), "591": ("🇧🇴 Bolivia", "BO"), "592": ("🇬🇾 Guyana", "GY"), 
    "593": ("🇪🇨 Ekuador", "EC"), "594": ("🇬🇫 Guyana Prancis", "GF"), "595": ("🇵🇾 Paraguay", "PY"), 
    "596": ("🇲🇶 Martinique", "MQ"), "597": ("🇸🇷 Suriname", "SR"), "598": ("🇺🇾 Uruguay", "UY"), 
    "599": ("🇨🇼 Curacao", "CW"),
    
    # ASIA TENGGARA & OSEANIA
    "60": ("🇲🇾 Malaysia", "MY"), "61": ("🇦🇺 Australia", "AU"), "62": ("🇮🇩 Indonesia", "ID"), 
    "63": ("🇵🇭 Filipina", "PH"), "64": ("🇳🇿 Selandia Baru", "NZ"), "65": ("🇸🇬 Singapura", "SG"), 
    "66": ("🇹🇭 Thailand", "TH"), "670": ("🇹🇱 Timor Leste", "TL"), "672": ("🇳🇫 Pulau Norfolk", "NF"), 
    "673": ("🇧🇳 Brunei Darussalam", "BN"), "674": ("🇳🇷 Nauru", "NR"), "675": ("🇵🇬 Papua Nugini", "PG"), 
    "676": ("🇹🇴 Tonga", "TO"), "677": ("🇸🇧 Kep. Solomon", "SB"), "678": ("🇻🇺 Vanuatu", "VU"), 
    "679": ("🇫🇯 Fiji", "FJ"), "680": ("🇵🇼 Palau", "PW"), "681": ("🇼🇫 Wallis & Futuna", "WF"), 
    "682": ("🇨🇰 Kep. Cook", "CK"), "683": ("🇳🇺 Niue", "NU"), "685": ("🇼🇸 Samoa", "WS"), 
    "686": ("🇰🇮 Kiribati", "KI"), "687": ("🇳🇨 Kaledonia Baru", "NC"), "688": ("🇹🇻 Tuvalu", "TV"), 
    "689": ("🇵🇫 Polinesia Prancis", "PF"), "690": ("🇹🇰 Tokelau", "TK"), "691": ("🇫🇲 Mikronesia", "FM"), 
    "692": ("🇲🇭 Kep. Marshall", "MH"),
    
    # ASIA TIMUR
    "81": ("🇯🇵 Jepang", "JP"), "82": ("🇰🇷 Korea Selatan", "KR"), "84": ("🇻🇳 Vietnam", "VN"), 
    "850": ("🇰🇵 Korea Utara", "KP"), "852": ("🇭🇰 Hong Kong", "HK"), "853": ("🇲🇴 Makau", "MO"), 
    "855": ("🇰🇭 Kamboja", "KH"), "856": ("🇱🇦 Laos", "LA"), "86": ("🇨🇳 Tiongkok", "CN"), 
    "880": ("🇧🇩 Bangladesh", "BD"), "886": ("🇹🇼 Taiwan", "TW"),
    
    # TIMUR TENGAH & ASIA TENGAH/SELATAN
    "90": ("🇹🇷 Turki", "TR"), "91": ("🇮🇳 India", "IN"), "92": ("🇵🇰 Pakistan", "PK"), 
    "93": ("🇦🇫 Afghanistan", "AF"), "94": ("🇱🇰 Sri Lanka", "LK"), "95": ("🇲🇲 Myanmar", "MM"), 
    "960": ("🇲🇻 Maladewa", "MV"), "961": ("🇱🇧 Lebanon", "LB"), "962": ("🇯🇴 Yordania", "JO"), 
    "963": ("🇸🇾 Suriah", "SY"), "964": ("🇮🇶 Irak", "IQ"), "965": ("🇰🇼 Kuwait", "KW"), 
    "966": ("🇸🇦 Arab Saudi", "SA"), "967": ("🇾🇪 Yaman", "YE"), "968": ("🇴🇲 Oman", "OM"), 
    "970": ("🇵🇸 Palestina", "PS"), "971": ("🇦🇪 Uni Emirat Arab", "AE"), "972": ("🇮🇱 Israel", "IL"), 
    "973": ("🇧🇭 Bahrain", "BH"), "974": ("🇶🇦 Qatar", "QA"), "975": ("🇧🇹 Bhutan", "BT"), 
    "976": ("🇲🇳 Mongolia", "MN"), "977": ("🇳🇵 Nepal", "NP"), "98": ("🇮🇷 Iran", "IR"), 
    "992": ("🇹🇯 Tajikistan", "TJ"), "993": ("🇹🇲 Turkmenistan", "TM"), "994": ("🇦🇿 Azerbaijan", "AZ"), 
    "995": ("🇬🇪 Georgia", "GE"), "996": ("🇰🇬 Kirgistan", "KG"), "998": ("🇺🇿 Uzbekistan", "UZ")
}

def get_auto_region(phone_number: str):
    """
    Deteksi region otomatis, output NORMAL CASE untuk masuk ke Database.
    Ini biar command '/ubahharga Myanmar 5000' bisa jalan tanpa perlu font aneh.
    """
    clean_num = str(phone_number).replace("+", "").replace(" ", "").replace("-", "").strip()
    
    for code in sorted(COUNTRY_CODES.keys(), key=len, reverse=True):
        if clean_num.startswith(code):
            country_name, country_id = COUNTRY_CODES[code]
            return country_name, country_id # Bersih, normal, gak di-translate
            
    return "🏳️ Global", "DEFAULT"

def to_smallcaps(text: str) -> str:
    """
    Alat tempur khusus UI/Etalase! 
    Panggil fungsi ini SAAT NAMPILIN MENU ke buyer biar estetik!
    Contoh: to_smallcaps(stok['region'])
    """
    smallcaps_trans = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", 
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    return str(text).translate(smallcaps_trans)

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ɪǫʙᴀʟsʜᴏᴘ_ᴍᴀɪɴ")
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)

PHOTO_URL = "https://files.catbox.moe/kxtcyz.jpg"

cekdv_queue = {}
user_states: Dict[int, Dict[str, Any]] = {} 
LoginState: Dict[int, Dict[str, Any]] = {}
waiting_manual_proof: Dict[int, Dict[str, Any]] = {}
bulk_queue_state: Dict[int, List[str]] = {}
restock_summary: Dict[int, Dict[str, Any]] = {}

bot = Client(
    "ɪǫʙᴀʟᴜʙᴏᴛsᴇʀᴠɪᴄᴇ",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    parse_mode=ParseMode.HTML,
    workers=100
)

def get_greeting() -> str:
    current_hour = datetime.now(WIB).hour
    if 4 <= current_hour < 11:
        return f"{Config.pagi} Sᴇʟᴀᴍᴀᴛ Pᴀɢɪ"
    elif 11 <= current_hour < 15:
        return f"{Config.siang} Sᴇʟᴀᴍᴀᴛ Sɪᴀɴɢ"
    elif 15 <= current_hour < 18:
        return f"{Config.sore} Sᴇʟᴀᴍᴀᴛ Sᴏʀᴇ"
    else:
        return f"{Config.malam} Sᴇʟᴀᴍᴀᴛ Mᴀʟᴀᴍ"

def format_rupiah(amount: int) -> str:
    try:
        return f"Rp {int(amount):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"

def get_region_flag(region_name: str) -> str:
    if not region_name or region_name == "-": 
        return "-"
    r = str(region_name).strip().lower()
    flags = {
        "indo": "🇮🇩", "malay": "🇲🇾", "thai": "🇹🇭", "filip": "🇵🇭", "phil": "🇵🇭", 
        "mesir": "🇪🇬", "sing": "🇸🇬", "El Salvador": "🇸🇻", "amerika": "🇺🇸", "uk": "🇬🇧", 
        "viet": "🇻🇳", "rusia": "🇷🇺", "china": "🇨🇳"
    }
    for key, flag in flags.items():
        if key in r: 
            return f"{region_name.title()} {flag}"
    return region_name.title()

def extract_flag_only(region_formatted: str) -> str:
    try:
        flag = "".join(c for c in region_formatted if c not in string.ascii_letters and c not in string.whitespace and c != "-")
        return flag.strip() if flag.strip() else Config.globe
    except Exception as e:
        logger.debug(f"Error extract flag: {e}")
        return Config.globe

async def perform_bot_logout(session_string: str, user_id: int) -> None:
    if not session_string or session_string == "None": 
        logger.warning(f"⚠️ Sesi kosong untuk user {user_id}, membatalkan proses logout.")
        return
        
    t_client = TelegramClient(StringSession(session_string), Config.API_ID, Config.API_HASH)
    try:
        logger.info(f"🔄 Memulai proses logout aman untuk perangkat user {user_id}...")
        await t_client.connect()
        
        if not await t_client.is_user_authorized(): 
            logger.warning(f"⚠️ Sesi sudah tidak valid sebelum bot logout (User {user_id}).")
            return
            
        await t_client.log_out()
        logger.info(f"✅ BOT LOGOUT SUCCESS FOR USER {user_id}.")
    except Exception as e:
        logger.error(f"❌ ERROR LOGOUT USER {user_id}: {e}")
    finally:
        if t_client.is_connected(): 
            await t_client.disconnect()
            logger.info(f"🔌 Socket Telethon diputuskan dengan aman (User {user_id}).")

def get_uptime() -> str:
    delta = datetime.now(WIB) - START_TIME
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    mins, secs = divmod(rem, 60)
    return f"{days}ᴅ {hours}ʜ {mins}ᴍ {secs}s"

async def auto_cancel_order(lock_id, user_id, client):
    await asyncio.sleep(600)
    
    stock_sample = await database.stocks_col.find_one({"status": f"pending_{lock_id}"})
    
    if stock_sample:
        await database.stocks_col.update_many(
            {"status": f"pending_{lock_id}"}, 
            {"$set": {"status": "ready"}}
        )
        
        waiting_manual_proof.pop(user_id, None)
        try:
            await client.send_message(
                user_id, 
                f"<blockquote><b>{Config.peringatan} ɪɴᴠᴏɪᴄᴇ ᴇxᴘɪʀᴇᴅ!</b>\nWᴀᴋᴛᴜ 10 ᴍᴇɴɪᴛ ʜᴀʙɪs, ᴘᴇsᴀɴᴀɴ ᴅɪʙᴀᴛᴀʟᴋᴀɴ ᴏᴛᴏᴍᴀᴛɪs ᴋᴀʀᴇɴᴀ ᴛɪᴅᴀᴋ ᴀᴅᴀ ʙᴜᴋᴛɪ ᴛʀᴀɴsғᴇʀ.</blockquote>"
            )
        except: pass
        logger.info(f"Order {lock_id} Expired.")
    else:
        logger.info(f"Timer {lock_id} stop. Status sudah aman.")

# =====================================================================
# 🛠️ SISTEM UTAMA: BULK QUEUE ENGINE (NEW SUPER LOGIC)
# =====================================================================
async def trigger_next_bulk_stok(client: Client, message: Message, u_id: int):
    queue = bulk_queue_state.get(u_id, [])
    if not queue:
        summary = restock_summary.get(u_id, {"count": 0, "items": {}})
        await client.send_message(
            chat_id=u_id,
            text=f"<blockquote><b>{Config.centanghijau} ᴘʀᴏsᴇs ʀᴇsᴛᴏᴄᴋ sᴇʟᴇsᴀɪ!</b>\nᴛᴏᴛᴀʟ ᴀᴋᴜɴ ʙᴇʀʜᴀsɪʟ ᴅɪʟᴏɢɪɴ: <b>{summary.get('count', 0)} ᴀᴄᴄ</b></blockquote>"
        )

        # --- EKSEKUSI LOG KE CHANNEL VVIP ---
        items = summary.get("items", {})
        owner_name = f"@{message.from_user.username}" if message.from_user and message.from_user.username else "ᴀᴅᴍɪɴ"
        
        for key, grp in items.items():
            is_limper = (grp["limit"] == "ON")
            item_label = "ʟɪᴍᴘᴇʀ" if is_limper else "ɴᴏ ᴍɪɴᴜs"
            
            # Validasi harga (kalo admin set 0, ambil default dr config)
            final_logged_price = grp["price"]
            if final_logged_price <= 0:
                final_logged_price = Config.get_price(grp["prefix"], grp["dc"], grp["region"], is_limper)
                
            try:
                await Logger.log_restock_summary(
                    client=client, 
                    count=grp["count"], 
                    item_name=item_label, 
                    prefix_id=grp["prefix"], 
                    price=final_logged_price, 
                    owner_username=owner_name,
                    region=grp["region"]
                )
                await asyncio.sleep(0.5) # Jeda aman anti-flood telegram
            except Exception as e:
                logger.error(f"Gagal nge-blast log addstok: {e}")

        # Bersihin memori biar ga tumpang tindih
        user_states.pop(u_id, None)
        restock_summary.pop(u_id, None)
        return

    # current_line = ID|DC|NOMER|LIMIT|BENEFIT|PASSWORD|HARGA
    current_line = queue[0]
    p = current_line.split("|")
    phone = p[2].strip()
    
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        
        t_client = TelegramClient(StringSession(), Config.API_ID, Config.API_HASH)
        await t_client.connect()
        phone_code = await t_client.send_code_request(phone)
        
        LoginState[u_id] = {
            "client": t_client, "phone": phone, "hash": phone_code.phone_code_hash,
            "data": p
        }
        user_states[u_id] = {"action": "wait_stok_otp"}
        
        await client.send_message(
            u_id,
            f"<blockquote><b>{Config.loading} Mᴇᴍᴘʀᴏsᴇs: <code>{phone}</code></b>\nRᴇᴘʟʏ ᴘᴇsᴀɴ ɪɴɪ ᴅᴇɴɢᴀɴ ᴏᴛᴘ ᴀɴᴅᴀ!</blockquote>",
            reply_markup=ForceReply(selective=True)
        )
    except Exception as e:
        await client.send_message(u_id, f"{Config.silang} Error {phone}: `{e}`. Mengalihkan ke akun selanjutnya...")
        queue.pop(0)
        bulk_queue_state[u_id] = queue
        await trigger_next_bulk_stok(client, message, u_id)



# Fungsi pembantu untuk mengambil ID angka dari teks <emoji id=12345>
def extract_id(config_val: str) -> str:
    match = re.search(r'id=(\d+)', str(config_val))
    return match.group(1) if match else None

async def send_main_menu(client: Client, chat_id: int, user_id: int) -> None:
    try:
        # Ambil data dari database
        user_data, _ = await database.get_user(user_id)
        saldo = user_data.get("balance", 0) if user_data else 0
        
        # Hitung total pembelian sukses untuk profil (biar keren & dinamis)
        try:
            total_buy = await database.stocks_col.count_documents({"buyer_id": user_id, "status": "sold"})
        except:
            total_buy = 0
        
        # Coba ambil username/nama Telegram
        try:
            user_info = await client.get_users(user_id)
            username = f"@{user_info.username}" if user_info.username else user_info.first_name
        except:
            username = "Pengguna"

        # Teks Menu dengan Pseudo-Bold VVIP & Config Custom Emoji
        text = (
            f"<blockquote>"
            f"{Config.malam} <b>𝗪 𝗘 𝗟 𝗖 𝗢 𝗠 𝗘   𝗧 𝗢   𝗦 𝗧 𝗢 𝗥 𝗘</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.statistik} <b>𝗦 𝗧 𝗔 𝗧 𝗜 𝗦 𝗧 𝗜 𝗞   𝗣 𝗥 𝗢 𝗙 𝗜 𝗟</b>\n"
            f" {Config.user} ᴜsᴇʀɴᴀᴍᴇ : {username}\n"
            f" {Config.kanan} ɪᴅ ᴛᴇʟᴇ : <code>{user_id}</code>\n"
            f" {Config.kanan} sᴀʟᴅᴏ : <b>{format_rupiah(saldo)}</b>\n"
            f" {Config.kanan} ᴛᴏᴛᴀʟ ᴏʀᴅᴇʀ : <b>{total_buy} ᴀᴋᴜɴ</b>\n\n"
            f"{Config.robot} <b>𝗜 𝗡 𝗙 𝗢 𝗥 𝗠 𝗔 𝗦 𝗜   𝗕 𝗢 𝗧</b>\n"
            f" {Config.kanan} sᴛᴀᴛᴜs : ᴏɴʟɪɴᴇ 𝟸𝟺/𝟽 {Config.orangtanpaplus}\n"
            f" {Config.kanan} ᴜᴘᴛɪᴍᴇ : {get_uptime()}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.roketputih} <i>sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ᴍᴇɴᴜ ᴛʀᴀɴsᴀᴋsɪ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ, sɪsᴛᴇᴍ ᴍᴇᴍᴘʀᴏsᴇs ᴏᴛᴏᴍᴀᴛɪs ᴅᴀɴ ᴄᴇᴘᴀᴛ!</i>"
            f"</blockquote>"
        )

        # Formasi Tombol Baru: 1 - 2 - 2 - 2 - 2 (Super Rapi & Padat)
        btns = InlineKeyboardMarkup([
            # 1. DEPOSIT (Paling Atas, Full Width biar user fokus top-up)
            [
                InlineKeyboardButton("ᴅᴇᴘᴏsɪᴛ sᴀʟᴅᴏ", callback_data="deposit_menu", icon_custom_emoji_id=extract_id(Config.kredit))
            ],
            # 2. TRANSAKSI UTAMA (Etalase disandingkan dengan Order Saya)
            [
                InlineKeyboardButton("ᴇᴛᴀʟᴀsᴇ ᴛᴏᴋᴏ", callback_data="pilih_stok", icon_custom_emoji_id=extract_id(Config.keranjang)),
                InlineKeyboardButton("ᴏʀᴅᴇʀ sᴀʏᴀ", callback_data="my_orders", icon_custom_emoji_id=extract_id(Config.box))
            ],
            # 3. PANTAUAN STOK & RIWAYAT
            [
                InlineKeyboardButton("ᴄᴇᴋ sᴛᴏᴋ ʀᴇᴀᴅʏ", callback_data="check_all_stock", icon_custom_emoji_id=extract_id(Config.struk)),
                InlineKeyboardButton("ʀɪᴡᴀʏᴀᴛ ʙᴇʟɪ", callback_data="history_menu", icon_custom_emoji_id=extract_id(Config.pesansurat))
            ],
            # 4. INFO AKUN & SISTEM
            [
                InlineKeyboardButton("ᴘʀᴏғɪʟ sᴀʏᴀ", callback_data="profile_menu", icon_custom_emoji_id=extract_id(Config.orang)),
                InlineKeyboardButton("sᴛᴀᴛɪsᴛɪᴋ ʙᴏᴛ", callback_data="open_stats", icon_custom_emoji_id=extract_id(Config.statistik))
            ],
            # 5. EKSTRA & SUPPORT
            [
                InlineKeyboardButton("ʙᴇʟɪ sᴄʀɪᴘᴛ ɪɴɪ", callback_data="open_script_menu", icon_custom_emoji_id=extract_id(Config.script)),
                InlineKeyboardButton("ʜᴜʙᴜɴɢɪ ᴏᴡɴᴇʀ", url="https://t.me/Zyexe", icon_custom_emoji_id=extract_id(Config.titiktitik))
            ]
        ])

        try: 
            await client.send_photo(chat_id=chat_id, photo=PHOTO_URL, caption=text, reply_markup=btns)
        except Exception as photo_e:
            logger.debug(f"Gagal send photo menu utama, fallback ke text: {photo_e}")
            await client.send_message(chat_id=chat_id, text=text, reply_markup=btns)
            
    except Exception as e:
        logger.error(f"FATAL ERROR send_main_menu: {e}")

async def send_panel_menu(client: Client, message: Message, user_id: int, is_edit: bool = False):
    try:
        stats = await database.get_global_stats()
        
        text = (
            f"<blockquote><b>{Config.mahkota} 𝗣 𝗔 𝗡 𝗘 𝗟   𝗔 𝗗 𝗠 Ｉ 𝗡   𝗩 𝗩 Ｉ Ｐ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.statistik} <b>sᴛᴀᴛɪsᴛɪᴋ ᴅᴀᴛᴀʙᴀsᴇ ʀᴇᴀʟᴛɪᴍᴇ:</b>\n"
            f" ➥ ᴛᴏᴛᴀʟ ᴜsᴇʀ ʙᴏᴛ : <b>{stats.get('users', 0)} ᴏʀᴀɴɢ</b>\n"
            f" ➥ sᴛᴏᴋ ᴀᴋᴜɴ ʀᴇᴀᴅʏ : <b>{stats.get('ready', 0)} ᴀᴋᴜɴ</b>\n"
            f" ➥ ᴛᴏᴛᴀʟ ᴀᴋᴜɴ sᴏʟᴅ : <b>{stats.get('sold', 0)} ᴀᴋᴜɴ</b>\n"
            f" ➥ ᴛᴏᴛᴀʟ sᴄʀɪᴘᴛ sᴏʟᴅ : <b>{stats.get('scripts_sold', 0)} ᴋᴀʟɪ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.rodaputarputih} <b>ᴘᴀɴᴅᴜᴀɴ ᴄᴏᴍᴍᴀɴᴅ ᴍᴀɴᴜᴀʟ ᴏᴡɴᴇʀ:</b>\n"
            f"{Config.pin} <code>/clearsaldo [ID]</code> - ʀᴇsᴇᴛ sᴀʟᴅᴏ ᴜsᴇʀ ᴊᴀᴅɪ 0 ᴛᴏᴛᴀʟ\n"
            f"{Config.pin} <code>/clear [UID/Prefix]</code> - ʜᴀᴘᴜs sᴛᴏᴋ sᴘᴇsɪғɪᴋ (ᴇx: /clear 62)\n"
            f"{Config.pin} <code>/clearall</code> - ʜᴀᴘᴜs ᴅᴀɴ ʟᴏɢᴏᴜᴛ sᴇᴍᴜᴀ sᴛᴏᴋ ʀᴇᴀᴅʏ\n"
            f"{Config.pin} <code>/addstok</code> - ᴛᴀᴍʙᴀʜ ᴅᴀᴛᴀ ᴀᴋᴜɴ ɴᴏᴋᴛᴇʟ ʙᴀʀᴜ\n"
            f"{Config.pin} <code>/bc</code> - ʙʀᴏᴀᴅᴄᴀsᴛ (ʀᴇᴘʟʏ ᴘᴇsᴀɴ ᴀᴘᴀᴘᴜɴ ᴜɴᴛᴜᴋ ᴅɪᴋɪʀɪᴍ ᴋᴇ sᴇᴍᴜᴀ ᴜsᴇʀ)\n"
            f"{Config.pin} <code>/ubahharga [ID],[Harga],[Negara]</code> - ᴜʙᴀʜ ʜᴀʀɢᴀ & ʙʀᴏᴀᴅᴄᴀsᴛ\n"
            f"{Config.pin} <code>/ping</code> - ᴄᴇᴋ ᴜᴘᴛɪᴍᴇ, ᴘɪɴɢ, ᴅᴀɴ sᴛᴀᴛᴜs ᴋᴇsᴇʜᴀᴛᴀɴ sᴇʀᴠᴇʀ\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.rodaputarputih} <b>ᴀᴛᴀᴜ ɢᴜɴᴀᴋᴀɴ ᴛᴏᴍʙᴏʟ ᴘɪɴᴛᴀsᴀɴ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ:</b></blockquote>"
        )
        
        btns = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("ᴄᴇᴋ ᴏᴍsᴇᴛ ᴛᴏᴛᴀʟ", callback_data="admin_cek_omset", icon_custom_emoji_id=extract_id(Config.harga)),
                InlineKeyboardButton("ᴛᴀᴍʙᴀʜ sᴛᴏᴋ ʙᴀʀᴜ", callback_data="admin_addstok", icon_custom_emoji_id=extract_id(Config.masukin))
            ],
            [
                InlineKeyboardButton("ʙʀᴏᴀᴅᴄᴀsᴛ ᴘᴇsᴀɴ", callback_data="admin_bc", icon_custom_emoji_id=extract_id(Config.toa)),
                InlineKeyboardButton("ᴜʙᴀʜ ʜᴀʀɢᴀ", callback_data="admin_req_ubahharga", icon_custom_emoji_id=extract_id(Config.ubahharga))
            ],
            [
                InlineKeyboardButton("ʀᴇsᴇᴛ sᴀʟᴅᴏ", callback_data="admin_req_clearsaldo", icon_custom_emoji_id=extract_id(Config.clear)), 
                InlineKeyboardButton("ʜᴀᴘᴜs ᴜɪᴅ/sᴛᴏᴋ", callback_data="admin_req_clearuid", icon_custom_emoji_id=extract_id(Config.cekdevice))
            ],
            [
                InlineKeyboardButton("ʙᴀᴄᴋᴜᴘ ᴅᴀᴛᴀʙᴀsᴇ", callback_data="admin_backup", icon_custom_emoji_id=extract_id(Config.backup)), 
                InlineKeyboardButton("ʜᴀᴘᴜs sᴇᴍᴜᴀ ʀᴇᴀᴅʏ", callback_data="confirm_clear_all_stok", icon_custom_emoji_id=extract_id(Config.clearall))
            ],
            [
                InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ ᴜᴛᴀᴍᴀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))
            ]
        ])
        
        if is_edit:
            await message.edit_text(text, reply_markup=btns)
        else:
            await message.reply(text, reply_markup=btns)
            
    except Exception as e:
        logger.error(f"Error render panel menu: {e}")


@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    try:
        user = message.from_user
        
        user_data, is_new = await database.get_user(user.id)
        if is_new:
            logger.info(f"🎉 MENYAMBUT USER BARU: {user.id} ({user.first_name})")
            await Logger.log_new_user(client, user.id, user.first_name, user.username)
        
        user_states.pop(user.id, None)
        LoginState.pop(user.id, None)
        waiting_manual_proof.pop(user.id, None)
        
        # 1. Cek Channel Wajib
        channels = ["Zyeco", "noktelzye"]
        is_joined = True
        
        for ch in channels:
            try: 
                await client.get_chat_member(ch, user.id)
            except UserNotParticipant:
                is_joined = False
                logger.info(f"🚫 User {user.id} belum join channel {ch}.")
                break # Berhenti loop jika satu saja belum join
            except Exception as e:
                logger.warning(f"Error saat cek channel {ch}: {e}")
                continue

        # 2. Jika belum join, kirim pesan penolakan dan STOP
        if not is_joined:
            text_join = (
                f"<blockquote><b>{Config.peringatan} 𝗔 𝗞 𝗦 𝗘 𝗦   𝗗 𝗜 𝗧 𝗢 𝗟 𝗔 𝗞 !</b>\n\n"
                f"ʜᴀʟᴏ ʙᴏsᴋᴜ, ᴜɴᴛᴜᴋ ᴅᴀᴘᴀᴛ ᴍᴇɴɢɢᴜɴᴀᴋᴀɴ ʟᴀʏᴀɴᴀɴ ʙᴏᴛ ɪɴɪ,\n"
                f"ᴀɴᴅᴀ ᴅɪᴡᴀᴊɪʙᴋᴀɴ ᴜɴᴛᴜᴋ ʙᴇʀɢᴀʙᴜɴɢ ᴅɪ ᴄʜᴀɴɴᴇʟ ʀᴇsᴍɪ ᴋᴀᴍɪ\n"
                f"ᴛᴇʀʟᴇʙɪʜ ᴅᴀʜᴜʟᴜ ᴀɢᴀʀ ᴛɪᴅᴀᴋ ᴋᴇᴛɪɴɢɢᴀʟᴀɴ ɪɴғᴏ ᴛᴇʀᴜᴘᴅᴀᴛᴇ,\n"
                f"sᴛᴏᴋ ʙᴀʀᴜ, ᴅᴀɴ ᴘʀᴏᴍᴏ ᴍᴇɴᴀʀɪᴋ ʟᴀɪɴɴʏᴀ.</blockquote>"
            )
            btns_join = InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 1 (ᴡᴀᴊɪʙ)", url="https://t.me/Zyeco", icon_custom_emoji_id=extract_id(Config.toa))],
                [InlineKeyboardButton("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 2 (ᴡᴀᴊɪʙ)", url="https://t.me/noktelzye", icon_custom_emoji_id=extract_id(Config.toa))],
                [InlineKeyboardButton("sᴀʏᴀ sᴜᴅᴀʜ ᴊᴏɪɴ (ᴄᴇᴋ ᴜʟᴀɴɢ)", callback_data="start", icon_custom_emoji_id=extract_id(Config.putar))]
            ])
            return await message.reply_text(text_join, reply_markup=btns_join)

        # 3. Jika sudah join, lanjut alur normal
        if len(message.command) > 1 and message.command[1] == "open_store":
            text = (
                f"<blockquote><b>{Config.market} 𝗦 Ｉ 𝗟 𝗔 𝗛 𝗞 𝗔 𝗡   𝗣 Ｉ 𝗟 𝗜 𝗛</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ sᴀʟᴀʜ sᴀᴛᴜ ᴋᴀᴛᴇɢᴏʀɪ\n"
                "ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ ᴜɴᴛᴜᴋ ᴍᴇʟɪʜᴀᴛ sᴛᴏᴋ ʀᴇᴀᴅʏ ʏᴀɴɢ ᴛᴇʀsᴇᴅɪᴀ.</blockquote>"
            )
            btns = InlineKeyboardMarkup([
                [InlineKeyboardButton("ᴀᴄᴄ ʟɪᴍᴘᴇʀ (ʟɪᴍɪᴛ ᴏɴ)", callback_data="kat_limper", icon_custom_emoji_id=extract_id(Config.api))],
                [InlineKeyboardButton("ᴀᴄᴄ ɴᴏ ᴍɪɴᴜs (ʟɪᴍɪᴛ ᴏғғ)", callback_data="kat_nominus", icon_custom_emoji_id=extract_id(Config.berlian1))],
                [InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ ᴜᴛᴀᴍᴀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]
            ])
            return await message.reply(text, reply_markup=btns)
            
        # Animasi Loading
        msg = await message.reply_text(f"<blockquote><b>{Config.loading} ᴍᴇᴍᴜᴀᴛ sɪsᴛᴇᴍ: 𝟶%</b>\nᴍᴇɴʏɪᴀᴘᴋᴀɴ ᴅᴀᴛᴀʙᴀsᴇ...</blockquote>")
        for p in [15, 35, 60, 85, 100]:
            await asyncio.sleep(0.3)
            try: await msg.edit_text(f"<blockquote><b>{Config.loading} ᴍᴇᴍᴜᴀᴛ sɪsᴛᴇᴍ: {p}%</b>\nᴍᴇɴɢᴀᴍʙɪʟ ᴅᴀᴛᴀ ᴘʀᴏғɪʟ...</blockquote>")
            except: pass
        
        await msg.delete()
        await send_main_menu(client, message.chat.id, user.id)

    except Exception as e:
        logger.error(f"Critical error di start_handler: {e}")


@bot.on_message(filters.command("panel") & filters.private)
async def panel_admin_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id != Config.OWNER_ID:
        return await message.reply(f"<blockquote><b>{Config.silang} ᴀᴋsᴇs ɪʟᴇɢᴀʟ ᴅɪᴛᴏʟᴀᴋ:</b>\nᴍᴀᴀғ, ᴘᴇʀɪɴᴛᴀʜ ɪɴɪ ʜᴀɴʏᴀ ᴅɪᴘᴇʀᴜɴᴛᴜᴋᴋᴀɴ ʙᴀɢɪ ᴀᴅᴍɪɴ ᴜᴛᴀᴍᴀ / ᴏᴡɴᴇʀ ʙᴏᴛ!</blockquote>")
    
    await send_panel_menu(client, message, user_id, is_edit=False)

FEATURE_CACHE = {}

async def is_feature_on(fitur_name: str) -> bool:
    global FEATURE_CACHE
    
    if fitur_name in FEATURE_CACHE:
        return FEATURE_CACHE[fitur_name]
        
    try:
        setting = await database.db.settings_col.find_one({"fitur": fitur_name})
        if setting:
            status = setting.get("is_active", True)
            FEATURE_CACHE[fitur_name] = status
            return status
        return True
    except:
        return True

@bot.on_message(filters.command("migrasidb") & filters.user(Config.OWNER_ID))
async def cmd_migrasidb(client: Client, message: Message):
    # Cek apakah owner memasukkan angka harga setelah command
    if len(message.command) < 2:
        return await message.reply(
            f"<blockquote><b>{Config.silang} 𝗙𝗢𝗥𝗠𝗔𝗧 𝗦𝗔𝗟𝗔𝗛!</b>\n"
            f"Sɪʟᴀʜᴋᴀɴ ᴍᴀsᴜᴋᴋᴀɴ ʜᴀʀɢᴀ ᴜɴᴛᴜᴋ sᴛᴏᴋ ʟᴀᴍᴀ.\n"
            f"<i>Cᴏɴᴛᴏʜ:</i> <code>/migrasidb 3000</code></blockquote>"
        )
    
    # Validasi apakah yang diketik benar-benar angka
    try:
        harga_migrasi = int(message.command[1])
    except ValueError:
        return await message.reply(
            f"<blockquote><b>{Config.peringatan} 𝗛𝗔𝗥𝗚𝗔 𝗛𝗔𝗥𝗨𝗦 𝗔𝗡𝗚𝗞𝗔!</b>\n"
            f"Jᴀɴɢᴀɴ ɢᴜɴᴀᴋᴀɴ ᴛɪᴛɪᴋ ᴀᴛᴀᴜ ʜᴜʀᴜғ.\n"
            f"<i>Cᴏɴᴛᴏʜ:</i> <code>/migrasidb 3000</code></blockquote>"
        )

    msg = await message.reply(
        f"<blockquote><b>{Config.loading} ᴍᴇᴍᴜʟᴀɪ ᴍɪɢʀᴀsɪ ᴅᴀᴛᴀʙᴀsᴇ...</b>\n"
        f"ᴍᴇɴʏᴇsᴜᴀɪᴋᴀɴ sᴛᴏᴋ ʟᴀᴍᴀ ᴅᴇɴɢᴀɴ ʜᴀʀɢᴀ <b>{format_rupiah(harga_migrasi)}</b></blockquote>"
    )
    
    # Cari semua stok yang ready di database
    stocks = await database.stocks_col.find({"status": "ready"}).to_list(length=None)
    count = 0
    
    for s in stocks:
        updates = {}
        
        # 1. Update Tipe Tag (Etalase)
        if "tipe_tag" not in s:
            benefit = str(s.get("benefit", "")).lower()
            if "fake" in benefit:
                updates["tipe_tag"] = "fake"
            elif "scam" in benefit:
                updates["tipe_tag"] = "scam"
            else:
                updates["tipe_tag"] = "polos"
                
        # 2. Update Status Email
        if "email" not in s:
            updates["email"] = "OFF (Stok Lama)"
            
        # 3. Update Harga Menggunakan Input dari Owner
        if "custom_price" not in s or not s["custom_price"]:
            updates["custom_price"] = harga_migrasi
            
        # Jika ada yang perlu diupdate, eksekusi ke MongoDB
        if updates:
            await database.stocks_col.update_one({"_id": s["_id"]}, {"$set": updates})
            count += 1
            
    await msg.edit_text(
        f"<blockquote><b>{Config.centanghijau} 𝗠𝗜𝗚𝗥𝗔𝗦𝗜 𝗦𝗘𝗟𝗘𝗦𝗔𝗜!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{Config.box} Bᴇʀʜᴀsɪʟ ᴍᴇɴɢᴜᴘᴅᴀᴛᴇ <b>{count} ᴀᴋᴜɴ ʟᴀᴍᴀ</b>.\n"
        f"{Config.harga} Hᴀʀɢᴀ sᴛᴏᴋ ʟᴀᴍᴀ ᴅɪsᴇᴛ : <b>{format_rupiah(harga_migrasi)}</b>\n"
        f"{Config.belifast} Sɪʟᴀʜᴋᴀɴ ᴄᴇᴋ ᴍᴇɴᴜ <b>Eᴛᴀʟᴀsᴇ Tᴏᴋᴏ</b> sᴇᴋᴀʀᴀɴɢ!</blockquote>"
    )
    
@bot.on_message(filters.command("addzip"), group=-1) 
async def handle_addzip(client, message):
    print("\n[DEBUG-ADDZIP] Command /addzip terpanggil oleh user!")
    
    # 1. VALIDASI USER
    u_id = message.from_user.id if message.from_user else (message.sender_chat.id if message.sender_chat else None)
    if not u_id:
        return await message.reply(f"<blockquote><b>{Config.peringatan} 𝗘𝗥𝗥𝗢𝗥 𝗦𝗜𝗦𝗧𝗘𝗠:</b>\nɢᴀɢᴀʟ ᴍᴇɴᴅᴇᴛᴇᴋsɪ ɪᴅ ᴀɴᴅᴀ. ᴍᴀᴛɪᴋᴀɴ ᴍᴏᴅᴇ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.</blockquote>")

    # 2. VALIDASI OWNER
    is_owner = False
    owner_config = Config.OWNER_ID
    valid_owners = [str(x) for x in owner_config] if isinstance(owner_config, list) else [str(owner_config)]
    if str(u_id) in valid_owners:
        is_owner = True

    if not is_owner:
        return await message.reply(f"<blockquote><b>{Config.silang} 𝗔𝗞𝗦𝗘𝗦 𝗗𝗜𝗧𝗢𝗟𝗔𝗞!</b>\nɪᴅ ᴀɴᴅᴀ ᴛɪᴅᴀᴋ ᴛᴇʀᴅᴀғᴛᴀʀ sᴇʙᴀɢᴀɪ ᴏᴡɴᴇʀ.</blockquote>")

    # 3. TANGKAP HARGA 
    raw_text = message.text or message.caption or ""
    args = raw_text.strip().split()
    custom_price_arg = 0
    if len(args) > 1:
        try:
            price_str = ''.join(filter(str.isdigit, args[1]))
            if price_str: custom_price_arg = int(price_str)
        except Exception:
            return await message.reply(f"<blockquote><b>{Config.silang} 𝗙𝗢𝗥𝗠𝗔𝗧 𝗛𝗔𝗥𝗚𝗔 𝗦𝗔𝗟𝗔𝗛!</b>\nᴄᴏɴᴛᴏʜ: <code>/addzip 2500</code></blockquote>")

    # 4. CARI TARGET FILE
    target_msg = message.reply_to_message if message.reply_to_message else message
    if not target_msg.document:
        return await message.reply(
            f"<blockquote><b>{Config.silang} 𝗖𝗔𝗥𝗔 𝗣𝗘𝗡𝗚𝗚𝗨𝗡𝗔𝗔𝗡 𝗦𝗔𝗟𝗔𝗛!</b>\n"
            f"ᴋɪʀɪᴍ/ʀᴇᴘʟʏ ғɪʟᴇ <b>.zip</b> ᴅᴇɴɢᴀɴ ғᴏʀᴍᴀᴛ <code>/addzip 2500</code></blockquote>"
        )
        
    doc = target_msg.document
    if not doc.file_name.endswith(('.zip', '.ZIP', '.Zip')):
        return await message.reply(f"<blockquote><b>{Config.silang} 𝗜𝗧𝗨 𝗕𝗨𝗞𝗔𝗡 𝗙𝗜𝗟𝗘 .zip!</b></blockquote>")

    # 5. AWAL PROSES - INFO KE ADMIN
    msg = await message.reply(f"<blockquote><b>{Config.loading} 𝗠𝗘𝗠𝗣𝗥𝗢𝗦𝗘𝗦 𝗙𝗜𝗟𝗘 𝗭𝗜𝗣...</b>\n━━━━━━━━━━━━━━━━━━━━━\n{Config.fileplus} ғɪʟᴇ: <b>{doc.file_name}</b>\n{Config.harga} ʜᴀʀɢᴀ sᴇᴛ: <b>ʀᴘ {custom_price_arg:,}</b>\n\n<i>ᴍᴇɴᴅᴏᴡɴʟᴏᴀᴅ ᴅᴀɴ ᴍᴇɴɢᴇᴋsᴛʀᴀᴋ ᴅᴀᴛᴀ...</i></blockquote>")
    
    try:
        import zipfile, os, shutil, json, sqlite3, struct, base64, socket, asyncio, math, time
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        from telethon.tl.functions.account import GetPasswordRequest # Tambahan import untuk Cek Email
        
        # DOWNLOAD FILE
        file_path = await target_msg.download()
        extract_dir = f"downloads/zip_import_{u_id}_{int(time.time())}"
        os.makedirs(extract_dir, exist_ok=True)
        
        # EKSTRAK ZIP
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        dc_ips = {
            1: "149.154.175.53", 2: "149.154.167.51", 
            3: "149.154.175.100", 4: "149.154.167.91", 5: "91.108.56.130"
        }
        
        # KUMPULKAN FILE UNTUK DI CEK
        files_to_process = []
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(".json"):
                    json_path = os.path.join(root, file)
                    base_name = file.replace(".json", "")
                    session_path = os.path.join(root, f"{base_name}.session")
                    if os.path.exists(session_path):
                        files_to_process.append((json_path, session_path, base_name))

        total_files = len(files_to_process)
        if total_files == 0:
            shutil.rmtree(extract_dir, ignore_errors=True)
            if os.path.exists(file_path): os.remove(file_path)
            return await msg.edit_text(f"<blockquote><b>{Config.silang} 𝗘𝗥𝗥𝗢𝗥 𝗙𝗜𝗟𝗘:</b>\nғɪʟᴇ ᴢɪᴘ ᴋᴏsᴏɴɢ ᴀᴛᴀᴜ ғᴏʀᴍᴀᴛ ᴛɪᴅᴀᴋ ᴠᴀʟɪᴅ (ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴘᴀsᴀɴɢᴀɴ ғɪʟᴇ .json & .session).</blockquote>")

        success_count = 0
        fail_count = 0
        summary_log_data = {}
        last_edit_time = 0
        
        # PROSES DENGAN PROGRESS BAR DAN LIVE CHECK
        for idx, (json_path, session_path, base_name) in enumerate(files_to_process, 1):
            
            # --- UPDATE PROGRESS BAR (Setiap 3 Detik biar ga FloodWait) ---
            if time.time() - last_edit_time > 3 or idx == 1 or idx == total_files:
                persen = math.floor((idx / total_files) * 100)
                blok_isi = math.floor((idx / total_files) * 10)
                blok_kosong = 10 - blok_isi
                bar_baterai = "▰" * blok_isi + "▱" * blok_kosong
                
                try:
                    await msg.edit_text(
                        f"<blockquote><b>{Config.loading} 𝗠𝗘𝗠𝗣𝗥𝗢𝗦𝗘𝗦 𝗙𝗜𝗟𝗘 𝗭𝗜𝗣...</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🔄 ᴘʀᴏɢʀᴇss : [ {bar_baterai} ] <b>{persen}%</b>\n"
                        f"{Config.centanghijau} sᴜᴋsᴇs: <b>{success_count}</b> | {Config.silang} ɢᴀɢᴀʟ: <b>{fail_count}</b>\n\n"
                        f"<i>{Config.cekdevice} ᴍᴇɴɢᴇᴄᴇᴋ sᴛᴀᴛᴜs ᴇᴍᴀɪʟ & sᴘᴀᴍʙᴏᴛ sᴇᴄᴀʀᴀ ʟɪᴠᴇ: {idx}/{total_files}...</i></blockquote>"
                    )
                    last_edit_time = time.time()
                except Exception: pass
            
            try:
                # 1. BACA JSON
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                user_id = int(data.get("user_id", 0))
                two_fa = data.get("twoFA", "")
                phone = str(data.get("phone", ""))
                if not phone.startswith("+"): phone = "+" + phone
                
                region_name, region_code = get_auto_region(phone) # FIX BENDERA
                
                # 2. BACA SQLITE SESSION
                conn = sqlite3.connect(session_path)
                c = conn.cursor()
                try:
                    c.execute("SELECT dc_id, server_address, port, auth_key FROM sessions")
                    row = c.fetchone()
                    dc_id, server_address, port, auth_key = row
                except:
                    c.execute("SELECT dc_id, auth_key FROM sessions")
                    row = c.fetchone()
                    dc_id, auth_key = row
                    server_address = dc_ips.get(int(dc_id), "149.154.167.51")
                    port = 443
                conn.close()
                
                if not row or not auth_key: raise ValueError("Auth_key kosong")
                if len(auth_key) != 256: auth_key = auth_key.ljust(256, b'\0')[:256]

                # 3. CONVERT KE TELETHON STRING
                try: ip_bytes = socket.inet_aton(server_address)
                except: ip_bytes = socket.inet_aton(dc_ips.get(int(dc_id), "149.154.167.51"))
                packed_telethon = struct.pack('>B4sH256s', int(dc_id), ip_bytes, int(port), auth_key)
                telethon_string = '1' + base64.urlsafe_b64encode(packed_telethon).decode('utf-8')
                
                # ==========================================
                # 🤖 LIVE CHECK EMAIL & SPAMBOT VVIP
                # ==========================================
                limit_status = "OFF" # Asumsi awal
                email_status = "OFF (Kosong)" # Asumsi awal
                
                t_client = TelegramClient(StringSession(telethon_string), Config.API_ID, Config.API_HASH)
                
                try:
                    await t_client.connect()
                    if await t_client.is_user_authorized():
                        
                        # --- CEK EMAIL (BARU) ---
                        try:
                            pwd_info = await t_client(GetPasswordRequest())
                            email_status = "ON (Aktif)" if pwd_info.has_recovery else "OFF (Kosong)"
                        except Exception as e_email:
                            print(f"[DEBUG-EMAIL] Gagal cek email UID {user_id}: {e_email}")
                            email_status = "OFF (Kosong)"
                        
                        # --- CEK SPAMBOT ---
                        await t_client.send_message("SpamBot", "/start")
                        await asyncio.sleep(1.5) # Jeda nunggu SpamBot balas
                        
                        spambot_msgs = await t_client.get_messages("SpamBot", limit=2)
                        if spambot_msgs:
                            reply_text = spambot_msgs[0].message.lower()
                            if any(k in reply_text for k in ["good news", "kabar baik", "no limits", "bebas"]):
                                limit_status = "OFF"
                            else:
                                limit_status = "ON"
                    else:
                        raise Exception("Sesi Mati / Terout")
                except Exception as e:
                    print(f"[DEBUG-LIVECHECK] Gagal ngecek akun {user_id}, Fallback ke JSON. Error: {e}")
                    limit_status = "ON" if str(data.get("spambot", "")).lower() in ["limit", "true", "on"] else "OFF"
                    email_status = "OFF (Kosong)"
                finally:
                    if t_client.is_connected():
                        await t_client.disconnect()
                # ==========================================
                
                uid_str = str(user_id)
                prefix_val = uid_str[0] if uid_str else "0"
                label_val = Config.LABELS.get(prefix_val, f"Id {prefix_val}xxx")
                
                group_key = f"{region_code}_{limit_status}_{prefix_val}_{dc_id}"
                
                stok_item = {
                    "uid": uid_str,
                    "dc": str(dc_id),
                    "phone": phone,
                    "region": region_name,
                    "region_code": region_code,
                    "limit": limit_status,
                    "email": email_status,     # <--- SEKARANG UDAH DINAMIS BUKAN "-" LAGI         
                    "benefit": "-",            
                    "password": two_fa,
                    "label": label_val,
                    "session": telethon_string, 
                    "status": "ready",
                    "is_sold": False,
                    "custom_price": custom_price_arg,
                    "tipe_tag": "polos" 
                }
                
                # JIKA SEMUA VARIABEL AMAN, INSERT DB
                await database.stocks_col.insert_one(stok_item)
                
                # 5. REKAP UNTUK LOG 
                if group_key not in summary_log_data:
                    summary_log_data[group_key] = {
                        "count": 0, "region": region_name, "limit": limit_status, 
                        "prefix": prefix_val, "dc": str(dc_id)
                    }
                summary_log_data[group_key]["count"] += 1
                success_count += 1
                
            except Exception as e:
                import traceback
                print(f"[DEBUG-ADDZIP] Error parsing file {base_name}: {e}")
                traceback.print_exc() 
                fail_count += 1
                
        # 6. BERSIH-BERSIH FILE SEMENTARA
        try:
            shutil.rmtree(extract_dir, ignore_errors=True)
            if os.path.exists(file_path): os.remove(file_path)
        except Exception: pass
            
        # 7. EKSEKUSI LOG KE CHANNEL
        try:
            owner_name = f"@{message.from_user.username}" if message.from_user and message.from_user.username else "𝗔𝗗𝗠𝗜𝗡"
            for key, grp in summary_log_data.items():
                is_limper = (grp["limit"] == "ON")
                item_label = "𝗟𝗶𝗺𝗽𝗲𝗿" if is_limper else "𝗡𝗼 𝗠𝗶𝗻𝘂𝘀"
                
                final_logged_price = custom_price_arg if custom_price_arg > 0 else Config.get_price(grp["prefix"], grp["dc"], grp["region"], is_limper)
                
                await Logger.log_restock_summary(
                    client=client, 
                    count=grp["count"], 
                    item_name=item_label, 
                    prefix_id=grp["prefix"], 
                    price=final_logged_price, 
                    owner_username=owner_name,
                    region=grp["region"]
                )
                await asyncio.sleep(0.5) 
        except Exception as e:
            print(f"[DEBUG-ADDZIP] ⚠️ Gagal Blast Log Channel: {e}")
                
        # 8. NOTIFIKASI AKHIR KE BOT
        price_notif_text = f"<b>ʀᴘ {custom_price_arg:,}</b>" if custom_price_arg > 0 else "<b>ʜᴀʀɢᴀ ᴅᴇғᴀᴜʟᴛ (ᴄᴏɴғɪɢ)</b>"
        await msg.edit_text(
            f"<blockquote><b>{Config.centanghijau} 𝗕𝗘𝗥𝗛𝗔𝗦𝗜𝗟 𝗔𝗗𝗗 𝗦𝗧𝗢𝗞 𝗩𝗜𝗔 𝗭𝗜𝗣!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.box} <b>ᴛᴏᴛᴀʟ sᴜᴋsᴇs :</b> {success_count} ᴀᴋᴜɴ\n"
            f"{Config.silang} <b>ᴛᴏ𝘁ᴀʟ ɢᴀɢᴀ𝗹  :</b> {fail_count} ᴀᴋᴜɴ\n"
            f"{Config.harga} <b>sᴇᴛ ʜᴀʀɢᴀ    :</b> {price_notif_text}\n\n"
            f"<i>sᴛᴏᴋ ʙᴇʀʜᴀsɪʟ ᴍᴀsᴜᴋ, ᴅᴀɴ sᴛᴀᴛᴜs ᴇᴍᴀɪʟ sᴇʀᴛᴀ sᴘᴀᴍʙᴏᴛ ᴛᴇʟᴀʜ ᴅɪᴄᴇᴋ sᴇᴄᴀʀᴀ ʟɪᴠᴇ. ʟᴀᴘᴏʀᴀɴ ᴛᴇʟᴀʜ ᴅɪ-ʙʟᴀsᴛ ᴋᴇ ᴄʜᴀɴɴᴇʟ!</i></blockquote>"
        )
        
    except Exception as e:
        import traceback
        err_detail = traceback.format_exc()
        print(f"[DEBUG-ADDZIP] FATAL ERROR:\n{err_detail}")
        await msg.edit_text(f"<blockquote><b>{Config.silang} 𝗧𝗘𝗥𝗝𝗔𝗗𝗜 𝗞𝗘𝗦𝗔𝗟𝗔𝗛𝗔𝗡 𝗙𝗔𝗧𝗔𝗟:</b>\n<code>{e}</code>\n\nᴄᴇᴋ ʟᴏɢ ᴄᴏɴsᴏʟᴇ ᴠᴘs/ᴛᴇʀᴍᴜx ʟᴜ ʙᴜᴀᴛ ᴅᴇᴛᴀɪʟɴʏᴀ ʙᴏs!</blockquote>")

@bot.on_message(filters.command("fixspam"), group=-1)
async def handle_fixspam(client, message):
    u_id = message.from_user.id if message.from_user else (message.sender_chat.id if message.sender_chat else None)
    
    # Validasi Owner
    owner_config = Config.OWNER_ID
    valid_owners = [str(x) for x in owner_config] if isinstance(owner_config, list) else [str(owner_config)]
    if str(u_id) not in valid_owners:
        return await message.reply("Akses ditolak!")

    msg = await message.reply(f"<blockquote><b>{Config.loading} 𝗠𝗘𝗠𝗨𝗟𝗔𝗜 𝗔𝗨𝗧𝗢-𝗙𝗜𝗫 𝗦𝗣𝗔𝗠𝗕𝗢𝗧...</b>\nMengekstrak data dari database...</blockquote>")
    
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        import asyncio
        
        # Ambil semua stok yang masih ready
        stocks = await database.stocks_col.find({"status": "ready"}).to_list(length=None)
        total = len(stocks)
        
        if total == 0:
            return await msg.edit_text("Database kosong bosku, gak ada yang perlu di-fix!")

        sukses_ubah = 0
        
        for idx, s in enumerate(stocks, 1):
            await msg.edit_text(f"<blockquote><b>{Config.loading} 𝗠𝗘𝗠𝗣𝗘𝗥𝗕𝗔𝗜𝗞𝗜 𝗗𝗔𝗧𝗔...</b>\n🔄 Cek akun {idx}/{total}\nUID: <code>{s.get('uid')}</code></blockquote>")
            
            telethon_string = s.get("session")
            if not telethon_string:
                continue
                
            t_client = TelegramClient(StringSession(telethon_string), Config.API_ID, Config.API_HASH)
            limit_status = s.get("limit", "ON") # Default ke ON kalau gagal
            
            try:
                await t_client.connect()
                if await t_client.is_user_authorized():
                    await t_client.send_message("SpamBot", "/start")
                    await asyncio.sleep(1.5)
                    
                    spambot_msgs = await t_client.get_messages("SpamBot", limit=2)
                    if spambot_msgs:
                        reply_text = spambot_msgs[0].message.lower()
                        if any(k in reply_text for k in ["good news", "kabar baik", "no limits", "bebas"]):
                            limit_status = "OFF"
                        else:
                            limit_status = "ON"
                else:
                    print(f"Sesi mati untuk UID: {s.get('uid')}")
            except Exception as e:
                print(f"Error fixspam UID {s.get('uid')}: {e}")
            finally:
                if t_client.is_connected():
                    await t_client.disconnect()
            
            # Update langsung ke Database!
            if s.get("limit") != limit_status:
                await database.stocks_col.update_one(
                    {"_id": s["_id"]}, 
                    {"$set": {"limit": limit_status}}
                )
                sukses_ubah += 1
                
        await msg.edit_text(f"<blockquote><b>{Config.centanghijau} 𝗔𝗨𝗧𝗢-𝗙𝗜𝗫 𝗦𝗘𝗟𝗘𝗦𝗔𝗜!</b>\n━━━━━━━━━━━━━━━━━━━━━\nTotal akun dicek: {total}\nBerhasil diperbaiki statusnya: {sukses_ubah} akun.</blockquote>")
        
    except Exception as e:
        await msg.edit_text(f"Error: {e}")
        

@bot.on_message(filters.command(["on", "off"]) & filters.user(Config.OWNER_ID))
async def cmd_toggle_features(client: Client, message: Message):
    cmd = message.command[0].lower()
    
    if len(message.command) < 2:
        text_help = (
            f"<blockquote><b>{Config.rodaputarputih} 𝗦𝗜𝗦𝗧𝗘𝗠 𝗞𝗢𝗡𝗧𝗥𝗢𝗟 𝗙𝗜𝗧𝗨𝗥 {Config.rodaputarputih}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"ꜰᴏʀᴍᴀᴛ ᴘᴇʀɪɴᴛᴀʜ ʏᴀɴɢ ᴀɴᴅᴀ ᴍᴀsᴜᴋᴋᴀɴ sᴀʟᴀʜ!\n\n"
            f"{Config.pin} <b>ɢᴜɴᴀᴋᴀɴ:</b> <code>/{cmd} [nama_fitur]</code>\n\n"
            f"{Config.catatan} <b>ᴅᴀꜰᴛᴀʀ ꜰɪᴛᴜʀ ᴠᴀʟɪᴅ:</b>\n"
            f" ➥ <code>deposit</code> (ᴍᴇɴᴜ ᴛᴏᴘ-ᴜᴘ sᴀʟᴅᴏ)\n"
            f" ➥ <code>etalase</code> (ᴍᴇɴᴜ ʙᴇʟɪ ᴀᴋᴜɴ)\n"
            f" ➥ <code>script</code> (ᴍᴇɴᴜ ᴘᴇᴍʙᴇʟɪᴀɴ sᴄʀɪᴘᴛ)\n\n"
            f"{Config.bintang} <i>ᴄᴏɴᴛᴏʜ: <code>/off etalase</code></i></blockquote>"
        )
        return await message.reply(text_help)
        
    fitur_target = message.command[1].lower()
    valid_features = ["deposit", "etalase", "script"]
    
    if fitur_target not in valid_features:
        return await message.reply(f"<blockquote><b>{Config.silang} 𝗙𝗜𝗧𝗨𝗥 𝗧𝗜𝗗𝗔𝗞 𝗩𝗔𝗟𝗜𝗗</b>\nᴘɪʟɪʜ sᴀʟᴀʜ sᴀᴛᴜ ᴅᴀʀɪ: {', '.join(valid_features)}</blockquote>")
        
    is_active = (cmd == "on")
    
    global FEATURE_CACHE
    FEATURE_CACHE[fitur_target] = is_active
    
    await database.db.settings_col.update_one(
        {"fitur": fitur_target},
        {"$set": {"is_active": is_active}},
        upsert=True
    )
    
    status_text = f"{Config.centanghijau} 𝗔𝗞𝗧𝗜𝗙" if is_active else f"{Config.silang} 𝗗𝗜𝗠𝗔𝗧𝗜𝗞𝗔𝗡"
    admin_name = message.from_user.first_name
    admin_id = message.from_user.id
    
    admin_reply = (
        f"<blockquote><b>{Config.rodaputarputih} 𝗦𝗧𝗔𝗧𝗨𝗦 𝗙𝗜𝗧𝗨𝗥 𝗨𝗣𝗗𝗔𝗧𝗘𝗗 {Config.rodaputarputih}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"ᴜᴘᴅᴀᴛᴇ ʙᴇʀʜᴀsɪʟ ᴅɪᴊᴀʟᴀɴᴋᴀɴ!\n\n"
        f"{Config.rodaputarputih} ꜰɪᴛᴜʀ ᴛᴀʀɢᴇᴛ : <b>{fitur_target.upper()}</b>\n"
        f"{Config.statistik} sᴛᴀᴛᴜs ʙᴀʀᴜ : <b>{status_text}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>sɪsᴛᴇᴍ ʙᴏᴛ ᴛᴇʟᴀʜ ᴅɪᴘᴇʀʙᴀʀᴜɪ ʀᴇᴀʟᴛɪᴍᴇ!</i></blockquote>"
    )
    await message.reply(admin_reply)

    from logch import Logger
    await Logger.log_system_action(client, admin_name, admin_id, fitur_target, status_text)

@bot.on_message(filters.command("resetstok") & filters.user(Config.OWNER_ID))
async def force_reset_stock(client, message):
    # Menggunakan regex untuk mencari semua stok yang statusnya diawali "pending_"
    # Ini bakal menyapu bersih semua stok yang nyangkut di sistem pembayaran
    result = await database.stocks_col.update_many(
        {"status": {"$regex": "^pending_"}},
        {"$set": {"status": "ready", "is_sold": False}}
    )
    
    await message.reply(f"✅ **Dibereskan!**\n\nSebanyak {result.modified_count} stok yang nyangkut telah dikembalikan ke status **READY**.")
    

@bot.on_message(filters.command("ceksesion") & filters.private)
async def ceksesion_handler(client: Client, message: Message):
    u_id = message.from_user.id
    if u_id != Config.OWNER_ID: 
        return
        
    loading_msg = await message.reply_text(f"<blockquote>{Config.loading} ᴍᴇɴɢᴇᴋsᴛʀᴀᴋ sᴇᴍᴜᴀ sᴇsɪ ʀᴇᴀᴅʏ ᴋᴇ .ᴢɪᴘ...</blockquote>")
    
    # Inisialisasi nama folder dan file zip sementara
    timestamp = int(time.time())
    tmp_dir = f"backup_sesi_{timestamp}"
    sessions_dir = os.path.join(tmp_dir, "sessions")
    zip_base_name = f"Backup_Ready_{timestamp}"
    zip_file_path = f"{zip_base_name}.zip"
    
    try:
        # Ambil stok status ready
        stocks = await database.stocks_col.find({"status": "ready"}).to_list(length=None)
        
        if not stocks:
            return await loading_msg.edit_text(f"<blockquote>{Config.silang} ɢᴀɢᴀʟ: ᴛɪᴅᴀᴋ ᴀᴅᴀ sᴛᴏᴋ sᴇsɪ ʏᴀɴɢ ʙᴇʀsᴛᴀᴛᴜs 'ready' sᴀᴀᴛ ɪɴɪ.</blockquote>")
            
        # Buat folder penampung sementara
        os.makedirs(sessions_dir, exist_ok=True)
        
        json_backup_data = []
        
        # Proses extract massal sesi ke file fisik
        for s in stocks:
            # 1. Normalisasi untuk backup data JSON utama
            s_copy = s.copy()
            if "_id" in s_copy: 
                s_copy["_id"] = str(s_copy["_id"])
            if "created_at" in s_copy and isinstance(s_copy["created_at"], datetime):
                s_copy["created_at"] = s_copy["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            json_backup_data.append(s_copy)
                
            # 2. Ambil identitas nomor / ID untuk penamaan file .session
            phone = s.get("phone") or s.get("phone_number") or str(s.get("_id"))
            # Bersihkan karakter aneh pada nama file agar aman di Linux/Windows
            safe_phone = "".join(c for c in str(phone) if c.isalnum() or c in "+_-")
            
            # 3. Ambil data sesi (sesuaikan dengan key DB kamu)
            session_data = s.get("session") or s.get("session_string") or s.get("session_str") or s.get("session_data")
            
            if session_data:
                file_session_path = os.path.join(sessions_dir, f"{safe_phone}.session")
                try:
                    # Jika berupa teks biasa (Pyrogram String Session)
                    if isinstance(session_data, str):
                        with open(file_session_path, "w", encoding="utf-8") as sf:
                            sf.write(session_data)
                    # Jika berupa bytes / biner (Telethon SQLite session data)
                    else:
                        with open(file_session_path, "wb") as sf:
                            sf.write(bytes(session_data))
                except Exception as file_err:
                    logger.error(f"Gagal menulis file sesi untuk {safe_phone}: {file_err}")

        # 4. Simpan rekap file JSON utama ke dalam folder zip juga
        with open(os.path.join(tmp_dir, "database_backup.json"), "w", encoding="utf-8") as f:
            json.dump(json_backup_data, f, indent=4, ensure_ascii=False)
            
        # 5. Kompres folder menjadi file .zip murni
        shutil.make_archive(base_name=zip_base_name, format="zip", root_dir=tmp_dir)
        
        # Hapus loading message lama
        await loading_msg.delete()
        
        # Kirim file zip hasil kompresi gila ke owner
        caption_text = (
            f"<blockquote><b>{Config.centanghijau} 𝗕𝗔𝗖𝗞𝗨𝗣 𝗦𝗘𝗦𝗜 𝗥𝗘𝗔𝗗𝗬 (𝗭𝗜𝗣 𝗠𝗔𝗡𝗨𝗔𝗟)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.statistik} ᴛᴏᴛᴀʟ sᴛᴏᴋ sᴇsɪ : <b>{len(stocks)} ᴀᴋᴜɴ</b>\n"
            f"{Config.box} ғᴏʀᴍᴀᴛ ʙᴀᴄᴋᴜᴘ  : <b>.ᴢɪᴘ (sᴇssɪᴏɴ + ᴊsᴏɴ)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.catatan} ᴇxᴛʀᴀᴄᴛ ғɪʟᴇ ᴢɪᴘ ɪɴɪ ᴜɴᴛᴜᴋ ᴍᴇɴɢᴀᴍʙɪʟ sᴇᴍᴜᴀ ғɪʟᴇ <code>.sᴇssɪᴏɴ</code> individual ᴍᴀᴜᴘᴜɴ ᴍᴇᴛᴀᴅᴀᴛᴀ database-ɴʏᴀ. ᴀᴍᴀɴ, ᴘʀᴀᴋᴛɪs, & sɪᴀᴘ ɪɴᴘᴜᴛ ᴜʟᴀɴɢ ᴛᴀɴᴘᴀ OTP!</blockquote>"
        )
        
        # Tombol interaktif pembersih chat
        btns = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="🗑️ ʜᴀᴘᴜs ᴘᴇsᴀɴ", callback_data="delete_message")
        ]])
        
        await client.send_document(
            chat_id=u_id,
            document=zip_file_path,
            caption=caption_text,
            reply_markup=btns
        )
        
    except Exception as e:
        logger.error(f"Error manual backup ZIP: {e}")
        await loading_msg.edit_text(f"<blockquote>{Config.silang} ᴇʀʀᴏ r: {str(e)}</blockquote>")
        
    finally:
        # PEMBERSIHAN TOTAL: Hapus folder temporary & file zip di server agar tidak menumpuk sampah storage
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)

@bot.on_message(filters.private & filters.reply)
async def handle_search_history_reply(client: Client, message: Message):
    u_id = message.from_user.id
    
    # Ambil state dari user
    state = user_states.get(u_id, {}).get("action")
    
    if state == "wait_search_history":
        keyword = message.text.strip()
        user_states.pop(u_id, None) # Hapus state biar ga nyangkut
        
        # Mencari data di database berdasarkan ID, label, atau nomor hp yang match
        query_db = {
            "buyer_id": u_id,
            "status": "sold",
            "$or": [
                {"label": {"$regex": keyword, "$options": "i"}},
                {"uid": {"$regex": keyword, "$options": "i"}},
                {"phone": {"$regex": keyword, "$options": "i"}}
            ]
        }
        
        # Tarik maksimal 30 hasil biar nggak menuhin layar bot
        results = await database.stocks_col.find(query_db).to_list(length=30)
        
        if not results:
            text = (
                f"<blockquote><b>{Config.silang} 𝗛𝗔𝗦𝗜𝗟 𝗣𝗘𝗡𝗖𝗔𝗥𝗜𝗔𝗡 𝗞𝗢𝗦𝗢𝗡𝗚</b>\n\n"
                f"ᴍᴀᴀғ, ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ʀɪᴡᴀʏᴀᴛ ᴀᴋᴜɴ ʏᴀɴɢ ᴄᴏᴄᴏᴋ ᴅᴇɴɢᴀɴ ᴋᴀᴛᴀ ᴋᴜɴᴄɪ <code>{keyword}</code>.</blockquote>"
            )
            btns = InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ʀɪᴡᴀʏᴀᴛ", callback_data="history_menu", icon_custom_emoji_id=extract_id(Config.kembali))]])
            return await message.reply(text, reply_markup=btns)
            
        text = (
            f"<blockquote><b>{Config.cekdevice} 𝗛𝗔𝗦𝗜𝗟 𝗣𝗘𝗡𝗖𝗔𝗥𝗜𝗔𝗡: <code>{keyword}</code></b>\n\n"
            f"ᴅɪᴛᴇᴍᴜᴋᴀɴ <b>{len(results)} ᴀᴋᴜɴ</b>.\nᴘɪʟɪʜ ᴀᴋᴜɴ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ ᴜɴᴛᴜᴋ ᴍᴇʟɪʜᴀᴛ ᴅᴇᴛᴀɪʟ sᴛᴏᴋ (ᴏᴛᴘ/ᴘᴡ):</blockquote>"
        )
        
        btns = []
        for o in results:
            label = o.get('label', 'Unknown')
            phone = o.get('phone', 'NoPhone')
            # Akan melempar user langsung ke detail stok (ord_det) persis seperti di Order Saya
            btns.append([InlineKeyboardButton(
                text=f"{label} {phone}", 
                callback_data=f"ord_det_{o['_id']}", 
                icon_custom_emoji_id=extract_id(Config.bulattitik)
            )])
        
        btns.append([InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data="history_menu", icon_custom_emoji_id=extract_id(Config.kembali))])
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(btns))
             
@bot.on_message(filters.command("cekdv") & filters.user(Config.OWNER_ID))
async def cmd_cekdv(client, message):
    msg = await message.reply(f"<blockquote><b>{Config.loading} ᴍᴇᴍᴜᴀᴛ ᴅᴀᴛᴀ ᴇᴛᴀʟᴀsᴇ... ᴍᴏʜᴏɴ ᴛᴜɴɢɢᴜ.</b></blockquote>")
    
    ready_stocks = await database.stocks_col.find({"status": "ready", "is_sold": False}).to_list(length=None)
    
    if not ready_stocks:
        return await msg.edit_text(f"<blockquote><b>{Config.silang} ᴛɪᴅᴀᴋ ᴀᴅᴀ sᴛᴏᴋ ʀᴇᴀᴅʏ ᴜɴᴛᴜᴋ ᴅɪᴄᴇᴋ!</b></blockquote>")
        
    u_id = message.from_user.id
    
    cekdv_queue[u_id] = {
        "uids": [stok["uid"] for stok in ready_stocks],
        "index": 0
    }
    
    await msg.edit_text(
        f"<blockquote><b>{Config.centanghijau} ᴅɪᴛᴇᴍᴜᴋᴀɴ {len(ready_stocks)} sᴛᴏᴋ ʀᴇᴀᴅʏ!</b>\n"
        f"ᴍᴇᴍᴜʟᴀɪ ᴘᴇɴɢᴇᴄᴇᴋᴀɴ ᴠᴠɪᴘ ᴍᴇɢᴀ ᴘʀᴏ ᴍᴀx... {Config.cekdevice}</blockquote>"
    )
    await asyncio.sleep(1)
    await process_next_cekdv(client, msg, u_id)

async def process_next_cekdv(client, message_to_edit, u_id):
    queue_data = cekdv_queue.get(u_id)
    
    if not queue_data or not queue_data["uids"]:
        return await message_to_edit.edit_text(f"<blockquote><b>{Config.centanghijau} sᴇᴍᴜᴀ ᴀɴᴛʀᴇᴀɴ ᴛᴇʟᴀʜ sᴇʟᴇsᴀɪ!</b></blockquote>")
        
    idx = queue_data["index"]
    total_stok = len(queue_data["uids"])
    
    if idx >= total_stok:
        return await message_to_edit.edit_text(f"<blockquote><b>{Config.centanghijau} sᴇᴍᴜᴀ sᴛᴏᴋ ʀᴇᴀᴅʏ ᴛᴇʟᴀʜ sᴇʟᴇsᴀɪ ᴅɪᴄᴇᴋ!</b></blockquote>")
        
    current_uid = queue_data["uids"][idx]
    akun_ke = idx + 1
    
    persen = math.floor((akun_ke / total_stok) * 100)
    blok_isi = math.floor((akun_ke / total_stok) * 10)
    blok_kosong = 10 - blok_isi
    bar_baterai = "▰" * blok_isi + "▱" * blok_kosong
    
    stok_data = await database.stocks_col.find_one({"uid": current_uid})
    
    def get_nav_buttons(has_tendang=False):
        btns = []
        nav_row = []
        if has_tendang: 
            btns.append([InlineKeyboardButton("ᴛᴇɴᴅᴀɴɢ ᴅᴇᴠɪᴄᴇ ʟᴀɪɴ", callback_data=f"cekdv_term_{current_uid}", icon_custom_emoji_id=extract_id(Config.tongsampah))])
        if idx > 0: 
            nav_row.append(InlineKeyboardButton("ᴘʀᴇᴠ", callback_data="cekdv_prev", icon_custom_emoji_id=extract_id(Config.kembali)))
        if idx < total_stok - 1: 
            nav_row.append(InlineKeyboardButton("ɴᴇxᴛ", callback_data="cekdv_next", icon_custom_emoji_id=extract_id(Config.masukin)))
        elif idx == total_stok - 1: 
            nav_row.append(InlineKeyboardButton("sᴇʟᴇsᴀɪ", callback_data="cekdv_next", icon_custom_emoji_id=extract_id(Config.centanghijau)))
        if nav_row: 
            btns.append(nav_row)
        btns.append([InlineKeyboardButton("ʙᴇʀʜᴇɴᴛɪ", callback_data="cekdv_stop", icon_custom_emoji_id=extract_id(Config.berhenti))])
        return InlineKeyboardMarkup(btns)


    if not stok_data:
        return await message_to_edit.edit_text(f"<blockquote><b>{Config.silang} ᴀᴋᴜɴ ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ!</b></blockquote>", reply_markup=get_nav_buttons())

    region = stok_data.get("region", "UNKNOWN").upper()
    phone = stok_data.get("phone", "Unknown")
    session_string = stok_data.get("session", "")
    
    text_result = (
        f"<blockquote><b>{Config.nomer} ᴄᴇᴋ ᴅᴇᴠɪᴄᴇ ᴀᴋᴜɴ [{akun_ke}/{total_stok}]</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{Config.loading} <b>ᴘʀᴏɢʀᴇss :</b> [ {bar_baterai} ] <b>{persen}%</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"{Config.id} <b>ɪᴅ ᴀᴋᴜɴ :</b> <code>{current_uid}</code>\n"
        f"{Config.globe} <b>ɴᴇɢᴀʀᴀ  :</b> {region}\n"
        f"{Config.telepon} <b>ɴᴏᴍᴏʀ   :</b> <code>{phone}</code>\n\n"
    )
    
    t_client = None
    try:
        t_client = TelegramClient(StringSession(session_string), Config.API_ID, Config.API_HASH)
        
        await asyncio.wait_for(t_client.connect(), timeout=15.0)
        
        if not await t_client.is_user_authorized():
            text_result += f"{Config.silang} <b>sᴛᴀᴛᴜs:</b> sᴇsɪ ᴍᴀᴛɪ / ᴛᴇʀᴏᴜᴛ\n<i>(Aman: Database tidak diubah)</i>"
            await message_to_edit.edit_text(text_result + "</blockquote>", reply_markup=get_nav_buttons())
            return

        auths = await t_client(GetAuthorizationsRequest())
        devices = auths.authorizations
        
        text_result += f"{Config.cekdevice} <b>ᴛᴏᴛᴀʟ ᴅᴇᴠɪᴄᴇ: {len(devices)}</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
        for i, d in enumerate(devices, 1):
            is_current = f" <b>({Config.robot} ʙᴏᴛ ɪɴɪ)</b>" if getattr(d, 'current', False) else ""
            device_name = str(getattr(d, 'device_model', 'UNKNOWN')).upper()
            platform_name = str(getattr(d, 'platform', 'UNKNOWN')).upper()
            app_ver = str(getattr(d, 'app_version', 'UNKNOWN'))
            ip_addr = str(getattr(d, 'ip', 'UNKNOWN'))
            country = str(getattr(d, 'country', 'UNKNOWN'))
            
            text_result += (
                f"<b>{i}. {device_name}</b>{is_current}\n"
                f" ├ ᴘʟᴀᴛғᴏʀᴍ: {platform_name} | ᴠ{app_ver}\n"
                f" └ ɪᴘ ᴀʟᴀᴍᴀᴛ: <code>{ip_addr}</code> ({country})\n\n"
            )
            
        has_tendang = len(devices) > 1
        await message_to_edit.edit_text(text_result + "</blockquote>", reply_markup=get_nav_buttons(has_tendang))
        
    except asyncio.TimeoutError:
        text_result += f"{Config.peringatan} <b>sᴛᴀᴛᴜs:</b> Kᴏɴᴇᴋsɪ Tɪᴍᴇᴏᴜᴛ (Tᴇʟᴇɢʀᴀᴍ Lᴇᴍᴏᴛ)\n<i>(Aman: Silakan Next Akun)</i>"
        await message_to_edit.edit_text(text_result + "</blockquote>", reply_markup=get_nav_buttons())
        
    except Exception as e:
        text_result += f"{Config.peringatan} <b>ᴇʀʀᴏʀ ᴀsʟɪ:</b> <code>{str(e)[:50]}...</code>\n<i>(Aman: Silakan Next Akun)</i>"
        await message_to_edit.edit_text(text_result + "</blockquote>", reply_markup=get_nav_buttons())
        
    finally:
        if t_client and t_client.is_connected():
            await t_client.disconnect()

@bot.on_callback_query(filters.regex(r"^cekdv_next$") & filters.user(Config.OWNER_ID))
async def cb_cekdv_next(client, query):
    u_id = query.from_user.id
    queue_data = cekdv_queue.get(u_id)
    if queue_data: queue_data["index"] += 1
    await process_next_cekdv(client, query.message, u_id)
    
@bot.on_callback_query(filters.regex(r"^cekdv_prev$") & filters.user(Config.OWNER_ID))
async def cb_cekdv_prev(client, query):
    u_id = query.from_user.id
    queue_data = cekdv_queue.get(u_id)
    if queue_data and queue_data["index"] > 0: queue_data["index"] -= 1
    await process_next_cekdv(client, query.message, u_id)

@bot.on_callback_query(filters.regex(r"^cekdv_stop$") & filters.user(Config.OWNER_ID))
async def cb_cekdv_stop(client, query):
    cekdv_queue.pop(query.from_user.id, None)
    await query.message.edit_text(f"<blockquote><b>{Config.berhenti} ᴘᴇɴɢᴇᴄᴇᴋᴀɴ ᴅᴇᴠɪᴄᴇ ᴛᴇʟᴀʜ ᴅɪʜᴇɴᴛɪᴋᴀɴ.</b></blockquote>")

@bot.on_callback_query(filters.regex(r"^cekdv_term_") & filters.user(Config.OWNER_ID))
async def cb_cekdv_term(client, query):
    u_id = query.from_user.id
    target_uid = query.data.split("_")[2]
    
    await query.answer(f"{Config.loading} ᴍᴇɴᴇɴᴅᴀɴɢ ᴅᴇᴠɪᴄᴇ ʟᴀɪɴ... ᴍᴏʜᴏɴ ᴛᴜɴɢɢᴜ!", show_alert=False)
    
    stok_data = await database.stocks_col.find_one({"uid": target_uid})
    if not stok_data:
        return await query.answer(f"{Config.silang} sᴛᴏᴋ ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ!", show_alert=True)
        
    session_string = stok_data.get("session", "")
    t_client = None
    
    try:
        t_client = TelegramClient(StringSession(session_string), Config.API_ID, Config.API_HASH)
        await asyncio.wait_for(t_client.connect(), timeout=15.0)
        
        if not await t_client.is_user_authorized():
            return await query.answer(f"{Config.silang} ɢᴀɢᴀʟ: sᴇsɪ sᴜᴅᴀʜ ᴍᴀᴛɪ!", show_alert=True)
            
        await t_client(ResetAuthorizationsRequest())
        await query.answer(f"{Config.centanghijau} ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴇɴᴅᴀɴɢ!", show_alert=True)
        await process_next_cekdv(client, query.message, u_id)
        
    except asyncio.TimeoutError:
        await query.answer(f"{Config.peringatan} ɢᴀɢᴀʟ: Tᴇʟᴇɢʀᴀᴍ Lᴇᴍᴏᴛ / Tɪᴍᴇᴏᴜᴛ", show_alert=True)
    except Exception as e:
        err_msg = str(e).lower()
        if "fresh" in err_msg:
            await query.answer(f"{Config.silang} ɢᴀɢᴀʟ: sᴇsɪ ᴍᴀsɪʜ ʙᴀʀᴜ ʟᴏɢɪɴ. ᴛᴜɴɢɢᴜ 𝟸𝟺 ᴊᴀᴍ.", show_alert=True)
        else:
            await query.answer(f"{Config.peringatan} ɢᴀɢᴀʟ: {str(e)[:30]}", show_alert=True)
    finally:
        if t_client and t_client.is_connected():
            await t_client.disconnect()



# 🆘 TOMBOL DARURAT BALIKIN STOK (CUMA BISA DIPAKE OWNER)



@bot.on_message(filters.command("fixstok") & filters.user(Config.OWNER_ID))
async def cmd_fixstok(client, message):
    msg = await message.reply(f"\n\n{Config.loading} ᴍᴇᴍᴘʀᴏsᴇs ᴘᴇᴍᴜʟɪʜᴀɴ sᴛᴏᴋ...\nᴍᴇɴᴀʀɪᴋ ᴋᴇᴍʙᴀʟɪ ᴀᴋᴜɴ ʏᴀɴɢ ʙᴇʀsᴛᴀᴛᴜs 'ᴛᴇʀᴏᴜᴛ' ᴋᴇ ᴇᴛᴀʟᴀsᴇ.\n\n")
    try:
        # Menarik paksa akun yang 'terout' balik jadi 'ready'
        result = await database.stocks_col.update_many(
            {"status": "terout"},
            {"$set": {"status": "ready", "is_sold": False}}
        )
        await msg.edit_text(
            f"<blockquote><b>{Config.centanghijau} 𝗣𝗘𝗠𝗨𝗟𝗜𝗛𝗔𝗡 𝗕𝗘𝗥𝗛𝗔𝗦𝗜𝗟!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.putar} ᴛᴏᴛᴀʟ ᴅɪᴘᴜʟɪʜᴋᴀɴ : <b>{result.modified_count} ᴀᴋᴜɴ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"sᴇᴍᴜᴀ ᴀᴋᴜɴ ᴛᴇʀsᴇʙᴜᴛ sᴇᴋᴀʀᴀɴɢ sᴜᴅᴀʜ ᴋᴇᴍʙᴀʟɪ ᴋᴇ sᴛᴀᴛᴜs <b>𝗥𝗘𝗔𝗗𝗬</b> ᴅᴀɴ ᴍᴜɴᴄᴜʟ ʟᴀɢɪ ᴅɪ ᴇᴛᴀʟᴀsᴇ!</blockquote>"
        )
    except Exception as e:
        await msg.edit_text(f"<blockquote><b>{Config.silang} ɢᴀɢᴀʟ ᴍᴇᴍᴜʟɪʜᴋᴀɴ sᴛᴏᴋ:</b>\n<code>{str(e)}</code></blockquote>") 




# 🚀 FITUR VVIP: EMERGENCY PUSH (AUTO-INJECT VIA ID AKUN / UID)



@bot.on_message(filters.command("push") & filters.user(Config.OWNER_ID))
async def cmd_push_account(client, message):
    """Mendorong akun langsung ke dalam menu 'Order Saya' milik buyer"""

    # 1. Validasi Format Command (MURNI PAKAI ID AKUN)
    if len(message.command) < 3:
        return await message.reply(
            f"<blockquote><b>{Config.silang} ꜰᴏʀᴍᴀᴛ sᴀʟᴀʜ!</b>\n"
            f"ᴄᴏɴᴛᴏʜ ᴘᴇɴɢɢᴜɴᴀᴀɴ: <code>/push [ID_BUYER] [ID_AKUN]</code>\n"
            f"ᴍɪsᴀʟ: <code>/push 123456789 8637171623</code></blockquote>"
        )

    target_user_id = message.command[1].strip()
    target_uid = message.command[2].strip()

    msg_wait = await message.reply(f"<blockquote><b>{Config.loading} ᴍᴇᴍᴘʀᴏsᴇs ᴘᴜsʜ ᴀᴋᴜɴ ᴋᴇ ʙᴜʏᴇʀ...</b></blockquote>")

    try:
        # 2. Cek apakah stok akun dengan UID (ID Akun) tersebut ada di database
        stok_data = await database.stocks_col.find_one({"uid": target_uid})
        if not stok_data:
            return await msg_wait.edit_text(f"<blockquote><b>{Config.silang} ᴇʀʀᴏʀ:</b> ᴀᴋᴜɴ ᴅᴇɴɢᴀɴ ɪᴅ <code>{target_uid}</code> ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ sᴛᴏᴋ!</blockquote>")
        
        if stok_data.get("is_sold"):
            return await msg_wait.edit_text(f"<blockquote><b>{Config.peringatan} ᴘᴇʀɪɴɢᴀᴛᴀɴ:</b> ᴀᴋᴜɴ <code>{target_uid}</code> sᴜᴅᴀʜ ʙᴇʀsᴛᴀᴛᴜs <b>sᴏʟᴅ/ᴛᴇʀᴊᴜᴀʟ</b>. ɢᴜɴᴀᴋᴀɴ <code>/ready {target_uid}</code> ᴛᴇʀʟᴇʙɪʜ ᴅᴀʜᴜʟᴜ ᴊɪᴋᴀ ɪɴɢɪɴ ᴍᴇᴍᴘᴜsʜ ᴜʟᴀɴɢ!</blockquote>")

        # 3. Generate OID Khusus Push Admin
        import random, string
        from datetime import datetime
        random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        new_oid = f"PUSH-{random_str}"

        # 4. Inject ke Database Orders (Otomatis Lunas / PAID)
        new_order = {
            "oid": new_oid,
            "user_id": int(target_user_id),
            "stok_uid": target_uid,
            "status": "PAID",
            "price": 0, # Manual push admin
            "date": datetime.now(WIB)
        }
        await database.orders_col.insert_one(new_order)

        # 5. Update status Stok menjadi SOLD
        await database.stocks_col.update_one(
            {"uid": target_uid},
            {"$set": {"status": "sold", "is_sold": True}}
        )

        # 6. Kirim Notif ke Buyer lengkap dengan Tombol Interaktif!
        text_to_buyer = (
            f"<blockquote><b>{Config.hadiah} ᴘᴇsᴀɴᴀɴ ᴀɴᴅᴀ ᴛᴇʟᴀʜ ᴅɪᴋɪʀɪᴍ (ᴘᴜsʜ ᴀᴅᴍɪɴ)</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"ᴀᴅᴍɪɴ ᴛᴇʟᴀʜ ᴍᴇᴍᴀsᴜᴋᴋᴀɴ ᴀᴋᴜɴ ᴋᴇ ᴅᴀʟᴀᴍ ᴅᴀғᴛᴀʀ ᴏʀᴅᴇʀ ᴀɴᴅᴀ.\n\n"
            f"{Config.box} <b>ɪᴅ ᴀᴋᴜɴ :</b> <code>{target_uid}</code>\n"
            f"{Config.struk} <b>ɴᴏ ɪɴᴠᴏɪᴄᴇ:</b> <code>{new_oid}</code>\n\n"
            f"<i>{Config.catatan} sɪʟᴀʜᴋᴀɴ ᴋʟɪᴋ ᴛᴏᴍʙᴏʟ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴜᴋᴀ ᴅᴇᴛᴀɪʟ ᴀᴋᴜɴ ᴅᴀɴ ᴍᴇᴍɪɴᴛᴀ ᴋᴏᴅᴇ ᴏᴛᴘ!</i></blockquote>"
        )
        
        # Gunakan callback_data standar bot lu untuk buka order
        btn_buyer = InlineKeyboardMarkup([
            [InlineKeyboardButton("ʙᴜᴋᴀ ᴏʀᴅᴇʀ sᴀʏᴀ", callback_data="my_orders", icon_custom_emoji_id=extract_id(Config.box))]
])

        try:
            await client.send_message(int(target_user_id), text_to_buyer, reply_markup=btn_buyer)
            await msg_wait.edit_text(
                f"<blockquote><b>{Config.centanghijau} ᴘᴜsʜ ʙᴇʀʜᴀsɪʟ 𝟷𝟶𝟶% !</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"ᴀᴋᴜɴ ɪᴅ <code>{target_uid}</code> sᴜᴅᴀʜ ʀᴇsᴍɪ ᴍᴀsᴜᴋ ᴋᴇ ᴍᴇɴᴜ <b>ᴏʀᴅᴇʀ sᴀʏᴀ</b> ᴍɪʟɪᴋ ʙᴜʏᴇʀ <code>{target_user_id}</code>.\n\n"
                f"sᴇᴋᴀʀᴀɴɢ ʙᴜʏᴇʀ ʙɪsᴀ ᴍᴇɴɢᴋʟɪᴋ ᴛᴏᴍʙᴏʟ ᴍɪɴᴛᴀ ᴏᴛᴘ sᴇᴘᴇʀᴛɪ ʙɪᴀsᴀ!</blockquote>"
            )
        except Exception as send_err:
            await msg_wait.edit_text(f"<blockquote><b>{Config.peringatan} ɢᴀɢᴀʟ ᴍᴇɴɢɪʀɪᴍ ᴋᴇ ʙᴜʏᴇʀ:</b>\nʙᴜʏᴇʀ ᴍᴜɴɢᴋɪɴ ᴛᴇʟᴀʜ ᴍᴇᴍʙʟᴏᴋɪʀ ʙᴏᴛ.\n\n<i>ᴛᴀᴘɪ ᴊᴀɴɢᴀɴ ᴋʜᴀᴡᴀᴛɪʀ, ᴀᴋᴜɴ sᴜᴅᴀʜ ᴍᴀsᴜᴋ ᴋᴇ ᴍᴇɴᴜ ᴏʀᴅᴇʀ ᴍᴇʀᴇᴋᴀ.</i></blockquote>")
            
    except Exception as e:
        await msg_wait.edit_text(f"<blockquote><b>{Config.silang} ᴄʀɪᴛɪᴄᴀʟ ᴇʀʀᴏʀ:</b>\n<code>{str(e)}</code></blockquote>") 




# 📊 FITUR VVIP: INSPEKSI MASSAL STOK DENGAN PANEL INTERAKTIF HAPUS (/cekall)



# Variabel penampung sementara di RAM untuk menyimpan list UID mati sebelum dihapus
ram_dead_sessions = {}

@bot.on_message(filters.command("cekall") & filters.user(Config.OWNER_ID))
async def cmd_cek_all_sessions(client, message):
    """Mengecek seluruh sesi akun ready secara massal tanpa langsung menghapusnya"""
    msg_wait = await message.reply(
        f"\n\n{Config.putar} ᴍᴇᴍᴜʟᴀɪ ᴀᴜᴅɪᴛ ᴍᴀssᴀʟ sᴛᴏᴋ...\n"
        f"sᴇᴅᴀɴɢ ᴍᴇɴᴀʀɪᴋ sᴇʟᴜʀᴜʜ ᴅᴀᴛᴀ sᴛᴏᴋ ʀᴇᴀᴅʏ ᴅᴀɴ ᴍᴇɴɢɪɴsᴘᴇᴋsɪ ᴋᴇ sᴇʀᴠᴇʀ ᴛᴇʟᴇɢʀᴀᴍ.\n"
        f"ᴘʀᴏsᴇs ɪɴɪ ʙᴇʀᴊᴀʟᴀɴ sᴇᴄᴀʀᴀ sᴀғᴇ-ᴍᴏᴅᴇ (ᴛɪᴅᴀᴋ ʟᴀɴɢsᴜɴɢ ʜᴀᴘᴜs)...\n\n"
    )
    
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        
        all_ready_stocks = await database.stocks_col.find({
            "status": "ready",
            "is_sold": False
        }).to_list(length=None)

        total_stok_awal = len(all_ready_stocks)
        if total_stok_awal == 0:
            return await msg_wait.edit_text(f"<blockquote><b>{Config.box} sᴛᴀᴛᴜs ᴀᴜᴅɪᴛ sᴛᴏᴋ</b>\n━━━━━━━━━━━━━━━━━━━━━\n{Config.silang} ᴛɪᴅᴀᴋ ᴀᴅᴀ sᴛᴏᴋ ᴅᴇɴɢᴀɴ sᴛᴀᴛᴜs <b>READY</b> ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ sᴇᴋᴀʀᴀɴɢ!</blockquote>")
            
        count_alive = 0
        count_dead = 0
        list_terout_uid = []
        
        for stok in all_ready_stocks:
            uid_akun = stok.get("uid", "UNKNOWN")
            session_string = stok.get("session") or stok.get("session_string") or stok.get("string")
            
            if not session_string and "data" in stok and isinstance(stok["data"], list) and len(stok["data"]) > 1:
                session_string = stok["data"][1]
                
            if not session_string:
                count_dead += 1
                list_terout_uid.append(uid_akun)
                continue
                
            try:
                t_client = TelegramClient(StringSession(session_string), Config.API_ID, Config.API_HASH)
                await t_client.connect()
                
                if await t_client.is_user_authorized():
                    count_alive += 1
                else:
                    count_dead += 1
                    list_terout_uid.append(uid_akun)
                await t_client.disconnect()
            except:
                count_dead += 1
                list_terout_uid.append(uid_akun)
                
            await asyncio.sleep(0.2)
            
        # Simpan list UID mati ke RAM temporary agar bisa dieksekusi tombol konfirmasi nanti
        ram_dead_sessions[message.from_user.id] = list_terout_uid
        
        detail_terout = ", ".join([f"<code>{x}</code>" for x in list_terout_uid]) if list_terout_uid else "ᴛɪᴅᴀᴋ ᴀᴅᴀ"
        
        # Simpan list UID mati ke RAM temporary agar bisa dieksekusi tombol konfirmasi nanti
        ram_dead_sessions[message.from_user.id] = list_terout_uid
        
        detail_terout = ", ".join([f"<code>{x}</code>" for x in list_terout_uid]) if list_terout_uid else "ᴛɪᴅᴀᴋ ᴀᴅᴀ"
        
        report_text = (
            f"<blockquote><b>{Config.statistik} 𝗟𝗔𝗣𝗢𝗥𝗔𝗡 𝗔𝗨𝗗𝗜𝗧 𝗦𝗧𝗢𝗞 𝗩𝗩𝗜𝗣</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
            f"{Config.tanggal} 𝗪𝗮𝗸𝘁𝘂 : <code>{datetime.now(WIB).strftime('%d %B %Y | %H:%M WIB')}</code>\n\n"
            f"{Config.box} 𝗧𝗼𝘁𝗮𝗹 𝗦𝘁𝗼𝗸 𝗗𝗶𝗰𝗲𝗸 : <b>{total_stok_awal} ᴀᴋᴜɴ</b>\n"
            f"{Config.centanghijau} 𝗦𝘁𝗼𝗸 𝗔𝗹𝗶𝘃𝗲 (𝗔𝗺𝗮𝗻) : <b>{count_alive} ᴀᴋᴜɴ</b>\n"
            f"{Config.silang} 𝗦𝘁𝗼𝗸 𝗠𝗮𝘁𝗶 (𝗧𝗲𝗿𝗼𝘂𝘁) : <b>{count_dead} ᴀᴋᴜɴ</b>\n\n"
            f"{Config.berhenti} 𝗗𝗲𝘁𝗮𝗶𝗹 𝗨𝗜𝗗 𝗦𝗲𝘀𝗶 𝗠𝗮𝘁𝗶 :\n"
            f"{detail_terout}</blockquote>"
        )
        
        # Jika ada yang mati, tampilin tombol interaktif buat eksekusi pembersihan
        if count_dead > 0:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("𝗛𝗮𝗽𝘂𝘀 𝗦𝗲𝘀𝗶 𝗠𝗮𝘁𝗶", callback_data="ask_purge_dead", icon_custom_emoji_id=extract_id(Config.hapus))]
            ])
            await msg_wait.edit_text(report_text, reply_markup=keyboard)
        else:
            await msg_wait.edit_text(report_text)
            
    except Exception as main_err:
        await msg_wait.edit_text(f"<blockquote><b>{Config.peringatan} ᴄʀɪᴛɪᴄᴀʟ ᴇʀʀᴏʀ ᴀᴜᴅɪᴛ:</b>\n<code>{str(main_err)}</code></blockquote>")



# 🔍 FITUR VVIP: CEK SESI (AUTHORIZATIONS) AKUN NOKTEL [VERSI TELETHON]



@bot.on_message(filters.command("cek") & filters.user(Config.OWNER_ID))
async def cmd_cek_session(client, message):
    """Mengecek perangkat yang terhubung ke sebuah akun"""
    if len(message.command) < 2:
        return await message.reply(f"\n\n{Config.silang} Format Salah!\nContoh: /cek 628123456789\n\n")

    uid_target = message.command[1].strip()
    msg_wait = await message.reply(f"<blockquote><b>{Config.loading} Menyambungkan ke Server Pusat...</b>\nMengecek status sesi dan perangkat.</blockquote>")

    # 1. Cari data di Database
    stok = await database.stocks_col.find_one({"uid": uid_target})
    if not stok:
        return await msg_wait.edit_text(f"<blockquote><b>{Config.silang} ERROR:</b>\nData akun tidak ditemukan di database!</blockquote>")

    # 2. Ambil Session String
    session_string = stok.get("session") or stok.get("session_string") or stok.get("string")
    if not session_string and "data" in stok and isinstance(stok["data"], list) and len(stok["data"]) > 1:
        session_string = stok["data"][1]
        
    if not session_string:
        return await msg_wait.edit_text(f"<blockquote><b>{Config.silang} ERROR:</b>\nSession String (Data Login) tidak ditemukan untuk akun ini!</blockquote>")

    # 3. Proses Cek Perangkat Live pake TELETHON
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        from telethon.tl.functions.account import GetAuthorizationsRequest

        # Bikin tangan robot Telethon sementara buat ngecek
        t_client = TelegramClient(
            StringSession(session_string), 
            Config.API_ID, 
            Config.API_HASH
        )
        await t_client.connect()

        # Cek apakah sesinya masih hidup
        if not await t_client.is_user_authorized():
            await t_client.disconnect()
            return await msg_wait.edit_text(f"<blockquote><b>{Config.silang} 𝗦𝗘𝗦𝗜 𝗠𝗔𝗧𝗜 / 𝗧𝗘𝗥𝗣𝗨𝗧𝗨𝗦!</b>\nAkun <code>{uid_target}</code> sudah log out atau terbanned dari Telegram.</blockquote>")

        # Tembak API Telegram buat minta daftar perangkat
        result = await t_client(GetAuthorizationsRequest())
        perangkat_list = result.authorizations
        
        # 4. Format Tampilan Hasil VVIP
        text = (
            f"<blockquote><b>{Config.nomer} 𝗦𝗧𝗔𝗧𝗨𝗦 𝗦𝗘𝗦𝗜 𝗔𝗞𝗨𝗡</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.uid} <b>𝗜𝗗 :</b> <code>{uid_target}</code>\n"
            f"{Config.antena} <b>𝗣𝗘𝗥𝗔𝗡𝗚𝗞𝗔𝗧 :</b> Ada {len(perangkat_list)}\n\n"
        )
        
        for i, auth in enumerate(perangkat_list, start=1):
            device = auth.device_model or "Unknown Device"
            app_name = auth.app_name or "Unknown App"
            ip = auth.ip or "Unknown IP"
            country = auth.country or "Unknown"
            
            # Di Telethon, sesi saat ini memiliki nilai hash = 0
            is_current = " <b>(Sesi Ini)</b>" if getattr(auth, 'hash', 1) == 0 else ""
            
            text += f"<b>{i}. {device}{is_current}</b>\n"
            text += f"├ 𝗔𝗽𝗹𝗶𝗸𝗮𝘀𝗶: {app_name}\n"
            text += f"├ 𝗜𝗣: <code>{ip}</code>\n"
            text += f"╰ 𝗟𝗼𝗸𝗮𝘀𝗶: {country}\n\n"
            
        text += "</blockquote>"
        
        await t_client.disconnect()
        await msg_wait.edit_text(text)
        
    except Exception as e:
        err_msg = str(e).upper()
        if "BASE64" in err_msg or "INVALID" in err_msg:
            await msg_wait.edit_text(f"<blockquote><b>{Config.silang} 𝗦𝗘𝗦𝗜 𝗧𝗜𝗗𝗔𝗞 𝗩𝗔𝗟𝗜𝗗!</b>\nFormat string rusak atau tidak lengkap.</blockquote>")
        else:
            await msg_wait.edit_text(f"<blockquote><b>{Config.peringatan} 𝗘𝗥𝗥𝗢𝗥 𝗖𝗘𝗞 𝗦𝗘𝗦𝗜:</b>\n<code>{str(e)}</code></blockquote>") 


@bot.on_message(filters.command("ready") & filters.user(Config.OWNER_ID))
async def cmd_ready(client, message):
    """
    ᴘᴇʀɪɴᴛᴀʜ ᴅᴀʀᴜʀᴀᴛ: /ʀᴇᴀᴅʏ [ᴜɪᴅ]
    ꜰᴜɴɢsɪ: ᴍᴇɴɢᴜʙᴀʜ sᴛᴀᴛᴜs ᴀᴋᴜɴ ᴅᴀʀɪ sᴏʟᴅ/ᴠᴇʀɪꜰʏɪɴɢ ʙᴀʟɪᴋ ᴋᴇ ʀᴇᴀᴅʏ
    """
    if len(message.command) < 2:
        return await message.reply(
            f"<blockquote>{Config.silang} <b>ꜰᴏʀᴍᴀᴛ sᴀʟᴀʜ!</b>\n"
            f"ᴄᴏɴᴛᴏʜ: <code>/ready 8414541103</code></blockquote>"
        )

    uid_target = message.command[1].strip()
    
    # Update Database ke READY
    result = await database.stocks_col.update_one(
        {"uid": uid_target},
        {"$set": {"status": "ready", "is_sold": False}}
    )
    
    if result.modified_count > 0:
        await message.reply(
            f"<blockquote>{Config.centanghijau} <b>ʙᴇʀʜᴀsɪʟ!</b>\n\n"
            f"ᴀᴋᴜɴ <code>{uid_target}</code> sᴇᴋᴀʀᴀɴɢ sᴛᴀᴛᴜsɴʏᴀ <b>ʀᴇᴀᴅʏ</b> "
            f"ᴅᴀɴ ʙɪsᴀ ᴅɪᴊᴜᴀʟ ᴋᴇᴍʙᴀʟɪ. {Config.roketputih}</blockquote>"
        )
    else:
        await message.reply(
            f"<blockquote>{Config.silang} <b>ɢᴀɢᴀʟ!</b>\n\n"
            f"ᴀᴋᴜɴ <code>{uid_target}</code> ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ᴀᴛᴀᴜ sᴛᴀᴛᴜsɴʏᴀ "
            f"ᴍᴇᴍᴀɴɢ sᴜᴅᴀʜ <b>ʀᴇᴀᴅʏ</b>.</blockquote>"
        )

 


@bot.on_message(filters.command("addsaldo") & filters.private)
async def cmd_add_saldo(client: Client, message: Message):
    # Proteksi: Hanya OWNER yang bisa pakai command ini
    if message.from_user.id != Config.OWNER_ID:
        return

    # Pecah pesan /addsaldo [ID_USER] [JUMLAH]
    args = message.text.split()
    
    if len(args) != 3:
        await message.reply(
            f"<blockquote><b>{Config.silang} ғᴏʀᴍᴀᴛ ᴘᴇʀɪɴᴛᴀʜ sᴀʟᴀʜ!</b>\n"
            f"ᴄᴀʀᴀ ᴘᴀᴋᴀɪ: <code>/addsaldo ɪᴅ_ᴜsᴇʀ ᴊᴜᴍʟᴀʜ</code>\n"
            f"ᴄᴏɴᴛᴏʜ: <code>/addsaldo 123456789 10000</code></blockquote>"
        )
        return

    try:
        target_id = int(args[1])
        amount = int(args[2])
    except ValueError:
        await message.reply(
            f"<blockquote><b>{Config.silang} ɪᴅ ᴅᴀɴ ᴊᴜᴍʟᴀʜ ʜᴀʀᴜs ᴀɴɢᴋᴀ!</b>\n"
            f"ᴘᴀsᴛɪᴋᴀɴ ᴛɪᴅᴀᴋ ᴀᴅᴀ ʜᴜʀᴜғ ᴀᴛᴀᴜ sɪᴍʙᴏʟ ʏᴀɴɢ ᴍᴇɴʏᴇʟɪᴘ.</blockquote>"
        )
        return

    if amount <= 0:
        await message.reply(
            f"<blockquote><b>{Config.silang} ᴊᴜᴍʟᴀʜ sᴀʟᴅᴏ ᴛɪᴅᴀᴋ ᴠᴀʟɪᴅ!</b>\n"
            f"ᴍᴀsᴜᴋᴋᴀɴ ᴀɴɢᴋᴀ ʟᴇʙɪʜ ᴅᴀʀɪ 0 ᴜɴᴛᴜᴋ ᴍᴇɴᴀᴍʙᴀʜ sᴀʟᴅᴏ.</blockquote>"
        )
        return

    # Eksekusi penambahan saldo ke database
    success = await database.add_user_balance(target_id, amount)
    
    if success:
        # Notif ke Admin
        await message.reply(
            f"<blockquote><b>{Config.centanghijau} sᴀʟᴅᴏ ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.user} ɪᴅ ᴜsᴇʀ : <code>{target_id}</code>\n"
            f"{Config.harga} ᴊᴜᴍʟᴀʜ : <b>ʀᴘ {amount:,}</b>\n\n"
            f"sᴀʟᴅᴏ ᴜsᴇʀ ᴛᴇʟᴀʜ sᴜᴋsᴇs ᴅɪᴘᴇʀʙᴀʀᴜɪ ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ sɪsᴛᴇᴍ.</blockquote>".replace(',', '.')
        )
        
        # Kirim Notif ke User (Penerima Saldo)
        try:
            await client.send_message(
                target_id,
                f"<blockquote><b>{Config.hadiah} ᴛᴏᴘ ᴜᴘ sᴀʟᴅᴏ ʙᴇʀʜᴀsɪʟ!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"sᴇʟᴀᴍᴀᴛ! sᴀʟᴅᴏ ᴀᴋᴜɴ ᴀɴᴅᴀ ᴛᴇʟᴀʜ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ sᴇʙᴇsᴀʀ <b>ʀᴘ {amount:,}</b> ᴏʟᴇʜ ᴀᴅᴍɪɴ.\n\n"
                f"{Config.catatan} sɪʟᴀʜᴋᴀɴ ᴄᴇᴋ ᴘʀᴏғɪʟ ᴀɴᴅᴀ ᴜɴᴛᴜᴋ ᴍᴇʟɪʜᴀᴛ ᴘᴇʀᴜʙᴀʜᴀɴ sᴀʟᴅᴏ. ᴛᴇʀɪᴍᴀ ᴋᴀsɪʜ!</blockquote>".replace(',', '.')
            )
        except Exception:
            # Mengabaikan error jika user nge-blokir bot / belum pernah start bot
            pass
    else:
        # Gagal (Biasanya karena ID tidak ditemukan di DB)
        await message.reply(
            f"<blockquote><b>{Config.silang} ɢᴀɢᴀʟ ᴍᴇɴᴀᴍʙᴀʜ sᴀʟᴅᴏ!</b>\n"
            f"ᴘᴀsᴛɪᴋᴀɴ ɪᴅ ᴜsᴇʀ ᴛᴇʀsᴇʙᴜᴛ ʙᴇɴᴀʀ ᴅᴀɴ sᴜᴅᴀʜ ᴛᴇʀᴅᴀғᴛᴀʀ ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ ʙᴏᴛ ɪɴɪ.</blockquote>"
        ) 




# 📸 [ 7. HANDLER FOTO BUKTI TRANSFER (MANUAL PAYMENT CHECKER) ]



@bot.on_message(filters.photo & filters.private)
async def handle_manual_proof_transfer(client: Client, message: Message):
    """
    Fungsi Penjaga Gerbang Pembayaran Manual VVIP.
    Update status ke 'verifying' agar kebal dari auto-cancel 10 menit
    dan mengirim notifikasi lengkap dengan info produk ke Admin.
    """
    user_id = message.from_user.id

    if user_id in waiting_manual_proof:
        data = waiting_manual_proof[user_id]
        sid_pass = data.get('sid')
        product_name = data.get('product', 'ᴘʀᴏᴅᴜᴋ ᴛɪᴅᴀᴋ ᴅɪᴋᴇᴛᴀʜᴜɪ') # <-- AMBIL NAMA PRODUK

        # 🛡️ PROTEKSI ANTI-EXPIRED: Ubah status dari 'pending' ke 'verifying'
        # Timer auto_cancel_order tidak akan memproses pembatalan jika status sudah verifying
        if sid_pass:
            await database.stocks_col.update_many(
                {"status": f"pending_{sid_pass}"},
                {"$set": {"status": f"verifying_{sid_pass}"}}
            )

        username_buyer = message.from_user.username
        buyer_name = f"@{username_buyer}" if username_buyer else message.from_user.first_name

        # Feedback ke Buyer
        await message.reply_text(
            f"<blockquote><b>{Config.centanghijau} ʙᴜᴋᴛɪ ᴛʀᴀɴsғᴇʀ ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴇʀɪᴍᴀ!</b>\n"
            f"ᴍᴏʜᴏɴ ʙᴇʀsᴀʙᴀʀ, ᴛʀᴀɴsᴀᴋsɪ ᴀɴᴅᴀ sᴇᴅᴀɴɢ ᴅᴀʟᴀᴍ ᴀɴᴛʀɪᴀɴ ᴅᴀɴ "
            f"ᴀᴋᴀɴ ᴅɪᴠᴇʀɪғɪᴋᴀsɪ ᴏʟᴇʜ ᴀᴅᴍɪɴ ᴋᴀᴍɪ ᴅᴀʟᴀᴍ ᴡᴀᴋᴛᴜ 1-3 ᴍᴇɴɪᴛ ᴋᴇ ᴅᴇᴘᴀɴ.</blockquote>"
        )
        
        # ==========================================
        # ROUTING CERDAS: Memisahkan Payload Callback & Tipe Header
        # ==========================================
        if sid_pass.startswith("DEP-"):
            cb_acc = f"accD_{user_id}_{sid_pass}"
            cb_dec = f"decD_{user_id}_{sid_pass}"
            tipe_order = "𝗗 𝗘 𝗣 𝗢 𝗦 𝗜 𝗧 𝗦 𝗔 𝗟 𝗗 𝗢"
        elif sid_pass.startswith("SC-"):
            cb_acc = f"accSC_{user_id}_{sid_pass}"
            cb_dec = f"decSC_{user_id}_{sid_pass}"
            tipe_order = "𝗦 𝗖 𝗥 𝗜 𝗣 𝗧 𝗕 𝗢 𝗧 𝗩 𝗩 𝗜 𝗣"
        else:
            cb_acc = f"accM_{user_id}_{sid_pass}"
            cb_dec = f"decM_{user_id}_{sid_pass}"
            tipe_order = "𝗣 𝗘 𝗦 𝗔 𝗡 𝗔 𝗡 𝗔 𝗞 𝗨 𝗡 𝗡 𝗢 𝗞 𝗧 𝗘 𝗟"

        btns_admin = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ᴛᴇʀɪᴍᴀ & ᴋᴏɴғɪʀᴍᴀsɪ ᴘᴇᴍʙᴀʏᴀʀᴀɴ", callback_data=cb_acc, icon_custom_emoji_id=extract_id(Config.centanghijau))],
            [InlineKeyboardButton(text="ᴛᴏʟᴀᴋ ᴘᴇᴍʙᴀʏᴀʀᴀɴ (ᴛɪᴅᴀᴋ ᴠᴀʟɪᴅ)", callback_data=cb_dec, icon_custom_emoji_id=extract_id(Config.silang))],
            [InlineKeyboardButton(text="ᴄʜᴀᴛ ʙᴜʏᴇʀ", url=f"tg://user?id={user_id}", icon_custom_emoji_id=extract_id(Config.titiktitik))]
        ])

        
        formatted_price = format_rupiah(data['price'])

        # Penambahan baris Produk di Caption Admin
        caption_admin = (
            f"<blockquote><b>{Config.pesansurat} {tipe_order} ( 𝗠 𝗔 𝗡 𝗨 𝗔 𝗟 )</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.user} ɴᴀᴍᴀ ʙᴜʏᴇʀ: <b>{buyer_name}</b> (<code>{user_id}</code>)\n"
            f"{Config.box} ᴘʀᴏᴅᴜᴋ : <b>{product_name}</b>\n" # <-- INFO BARU BIAR LU GAK BINGUNG
            f"{Config.uid} ɪᴅ ᴘʀᴏᴅᴜᴋ : <code>{sid_pass}</code>\n"
            f"{Config.harga} ᴛᴏᴛᴀʟ ᴛғ : <b>{formatted_price}</b>\n"
            f"⏰ ᴡᴀᴋᴛᴜ ᴛғ : <b>{datetime.now(WIB).strftime('%Y-%m-%d %H:%M:%S')}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.peringatan} <b>ᴘᴇʀʜᴀᴛɪᴀɴ ᴜɴᴛᴜᴋ ᴀᴅᴍɪɴ:</b>\n"
            f"ᴘᴀsᴛɪᴋᴀɴ ᴅᴀɴᴀ sᴜᴅᴀʜ ᴍᴀsᴜᴋ sᴇʙᴇʟᴜᴍ ᴍᴇɴᴇᴋᴀɴ ᴛᴏᴍʙᴏʟ ᴛᴇʀɪᴍᴀ.</blockquote>"
        )
        
        try:
            # Mengirimkan resi ke Owner
            await message.copy(chat_id=Config.OWNER_ID, caption=caption_admin, reply_markup=btns_admin)
            
            # Hapus antrian setelah sukses kirim ke admin
            waiting_manual_proof.pop(user_id, None)
            logger.info(f"Resi manual dari {user_id} sukses diteruskan ke Owner.")
        except Exception as e:
            logger.error(f"Gagal mengirim bukti manual ke admin: {e}")
            await message.reply_text(f"{Config.silang} Terjadi kesalahan internal saat mengirim bukti ke admin.") 

@bot.on_callback_query()
async def on_callback(client: Client, query: CallbackQuery):
    global WIB  
    import time, asyncio, random, io, zipfile, json
    from datetime import datetime
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from bson.objectid import ObjectId

    data = query.data
    u_id = query.from_user.id
    u_name = query.from_user.first_name
    chat_id = query.message.chat.id

    # Anti-Spin Loader untuk Telegram App
    try: await query.answer()
    except: pass

    # ============================================================
    # 🛑 1. PROTEKSI FITUR (CEGATAN TOTAL ON/OFF)
    # ============================================================
    async def block_feature(feature_name):
        text_block = (
            f"<blockquote><b>{Config.peringatan} 𝗙𝗜𝗧𝗨𝗥 𝗗𝗜𝗠𝗔𝗧𝗜𝗞𝗔𝗡 {Config.peringatan}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"ᴍᴀᴀꜰ ʙᴏsᴋᴜ, ꜰɪᴛᴜʀ <b>{feature_name.upper()}</b> sᴀᴀᴛ ɪɴɪ\n"
            f"sᴇᴅᴀɴɢ ᴅɪᴍᴀᴛɪᴋᴀɴ ᴏʟᴇʜ ᴀᴅᴍɪɴ ᴜɴᴛᴜᴋ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ.\n\n"
            f"<i>sɪʟᴀʜᴋᴀɴ ᴄᴏʙᴀ ʙᴇʙᴇʀᴀᴘᴀ sᴀᴀᴛ ʟᴀɢɪ!</i></blockquote>"
        )
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ʜᴏᴍᴇ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]])

        try:
            await query.answer(f"{Config.peringatan} Fitur {feature_name.upper()} sedang maintenance!", show_alert=True)
        except:
            pass
        
        try:
            if query.message.photo:
                await query.edit_message_caption(caption=text_block, reply_markup=btns)
            else:
                await query.edit_message_text(text=text_block, reply_markup=btns)
        except:
            pass

    # CEGATAN DEPOSIT
    if data in ["deposit_menu", "depo_manual"] or data.startswith(("depo_", "pAut_D_", "pMan_D_")):
        if not await is_feature_on("deposit"):
            return await block_feature("deposit")

    # CEGATAN ETALASE
    elif data in ["pilih_stok", "open_store", "kat_limper", "kat_nominus", "check_all_stock", "open_bulk"] or data.startswith(("lst_", "buy_", "bulk_T_", "bch_", "abq_")):
        if not await is_feature_on("etalase"):
            return await block_feature("etalase")

    # CEGATAN SCRIPT
    elif data == "open_script_menu" or data.startswith(("buySC_", "payAutoSC_", "payManSC_")):
        if not await is_feature_on("script"):
            return await block_feature("script")


    # ============================================================
    # 🚀 2. ROUTING MENU UTAMA (Tombol-tombol Lu)
    # ============================================================
    if data == "back_home":
        try: 
            await query.message.delete()
        except: 
            pass
        await send_main_menu(client, chat_id, u_id)
        return

    elif data == "back_panel":
        if u_id != Config.OWNER_ID: 
            return
        await send_panel_menu(client, query.message, u_id, is_edit=True)
        return

    elif data == "profile_menu":
        user_data, _ = await database.get_user(u_id)
        saldo = user_data.get("balance", 0) if user_data else 0
        
        # Hitung total akun yang pernah dibeli user ini dari DB
        total_buy = await database.stocks_col.count_documents({"buyer_id": u_id, "status": "sold"})
        
        text_profil = (
            f"<blockquote><b>{Config.orang} 𝗣 𝗥 𝗢 𝗙 𝗜 𝗟   𝗦 𝗔 𝗬 𝗔</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.id} <b>𝗜𝗗 𝗔𝗸𝘂𝗻   :</b> <code>{u_id}</code>\n"
            f"{Config.orang} <b>𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲 :</b> {u_name}\n"
            f"{Config.kredit} <b>𝗦𝗮𝗹𝗱𝗼    :</b> {format_rupiah(saldo)}\n"
            f"{Config.keranjang} <b>𝗧𝗼𝘁𝗮𝗹 𝗕𝘂𝘆 :</b> {total_buy} ᴀᴋᴜɴ\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>ᴛᴇʀɪᴍᴀ ᴋᴀsɪʜ ᴛᴇʟᴀʜ ᴍᴇɴᴊᴀᴅɪ ᴘᴇʟᴀɴɢɢᴀɴ sᴇᴛɪᴀ ᴋᴀᴍɪ!</i></blockquote>"
        )
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]])
        
        try:
            if query.message.photo: await query.message.edit_caption(caption=text_profil, reply_markup=btns)
            else: await query.message.edit_text(text=text_profil, reply_markup=btns)
        except Exception: pass

    elif data == "history_menu":
        # Ambil 5 riwayat terakhir sebagai preview
        recent_orders = await database.stocks_col.find({
            "buyer_id": u_id, "status": "sold"
        }).sort("_id", -1).limit(5).to_list(length=None)
        
        if not recent_orders:
            text_riwayat = (
                f"<blockquote><b>{Config.box} 𝗥𝗜𝗪𝗔𝗬𝗔𝗧 𝗣𝗘𝗠𝗕𝗘𝗟𝗜𝗔𝗡</b>\n\n"
                f"{Config.silang} ᴀɴᴅᴀ ʙᴇʟᴜᴍ ᴍᴇᴍɪʟɪᴋɪ ʀɪᴡᴀʏᴀᴛ ᴘᴇᴍʙᴇʟɪᴀɴ ᴀᴘᴀᴘᴜɴ.</blockquote>"
            )
        else:
            text_riwayat = f"<blockquote><b>{Config.box} 𝗥𝗜𝗪𝗔𝗬𝗔𝗧 𝗣𝗘𝗠𝗕𝗘𝗟𝗜𝗔𝗡</b>\n\nʙᴇʀɪᴋᴜᴛ ᴀᴅᴀʟᴀʜ 𝟻 ᴀᴋᴜɴ ᴛᴇʀᴀᴋʜɪʀ ʏᴀɴɢ ᴀɴᴅᴀ ʙᴇʟɪ:\n\n"
            for o in recent_orders:
                label = o.get('label', '-')
                phone = o.get('phone', '-')
                text_riwayat += f"{Config.bulattitik} {label} | <code>{phone}</code>\n"
            text_riwayat += f"\n<i>ᴜɴᴛᴜᴋ ᴍᴇɴᴄᴀʀɪ ᴀᴋᴜɴ ʟᴀɪɴ, ɢᴜɴᴀᴋᴀɴ ᴛᴏᴍʙᴏʟ ᴄᴀʀɪ ᴅɪ ʙᴀᴡᴀʜ.</i></blockquote>"
            
        btns = [
            [InlineKeyboardButton("ᴄᴀʀɪ ʀɪᴡᴀʏᴀᴛ ᴀᴋᴜɴ", callback_data="search_history", icon_custom_emoji_id=extract_id(Config.cekdevice))],
            [InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]
        ]
        
        try:
            if query.message.photo: await query.message.edit_caption(caption=text_riwayat, reply_markup=InlineKeyboardMarkup(btns))
            else: await query.message.edit_text(text=text_riwayat, reply_markup=InlineKeyboardMarkup(btns))
        except Exception: pass

    elif data == "search_history":
        user_states[u_id] = {"action": "wait_search_history"}
        try: await query.message.delete()
        except: pass
        
        await client.send_message(
            u_id,
            f"<blockquote><b>{Config.cekdevice} 𝗖𝗔𝗥𝗜 𝗥𝗜𝗪𝗔𝗬𝗔𝗧 𝗔𝗞𝗨𝗡</b>\n\n"
            f"sɪʟᴀʜᴋᴀɴ ʙᴀʟᴀs (ʀᴇᴘʟʏ) ᴘᴇsᴀɴ ɪɴɪ ᴅᴇɴɢᴀɴ ᴍᴇɴɢᴇᴛɪᴋ <b>𝗣𝗿𝗲𝗳𝗶𝘅 𝗜𝗗</b> (ᴄᴏɴᴛᴏʜ: 8919) ᴀᴛᴀᴜ <b>𝗡𝗼𝗺𝗼𝗿 𝗛𝗣</b> ᴀᴋᴜɴ ʏᴀɴɢ ɪɴɢɪɴ ᴅɪᴄᴀʀɪ:</blockquote>",
            reply_markup=ForceReply(selective=True)
        )

        
    # ============================================================
    # (B) SHORTCUT ADMIN MENU DARI PANEL (BERBOBOT FULL PROTEKSI)
    # ============================================================
    elif data == "admin_cek_omset":
        if u_id != Config.OWNER_ID: 
            return
        await query.answer(f"{Config.loading} Menghitung total omset pendapatan dari database...", show_alert=False)
        try:
            omset_data = await database.get_omset_stats()
            text_omset = (
                f"<blockquote><b>{Config.harga} 𝗥 Ｅ 𝗣 𝗢 𝗥 𝗧 𝗢 𝗠 Ｓ Ｅ 𝗧</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.statistik} <b>Pᴇɴᴅᴀᴘᴀᴛᴀɴ Kᴏᴛᴏʀ (Rᴇᴠᴇɴᴜᴇ)</b>\n\n"
                f"{Config.bulattitik} <b>Hᴀʀɪ Iɴɪ :</b> <code>Rᴘ {omset_data.get('today', 0):,}</code>\n"
                f"{Config.bulattitik} <b>Mɪɴɢɢᴜ Iɴɪ:</b> <code>Rᴘ {omset_data.get('this_week', 0):,}</code>\n"
                f"{Config.bulattitik} <b>Bᴜʟᴀɴ Iɴɪ :</b> <code>Rᴘ {omset_data.get('this_month', 0):,}</code>\n"
                f"{Config.mahkota} <b>Tᴏᴛᴀʟ Aʟʟ :</b> <code>Rᴘ {omset_data.get('all_time', 0):,}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.catatan} <i>Dᴀᴛᴀ ᴅɪᴀᴍʙɪʟ sᴇᴄᴀʀᴀ ʀᴇᴀʟᴛɪᴍᴇ ᴅᴀʀɪ\n"
                f"ᴛʀᴀɴsᴀᴋsɪ ᴘᴇɴᴊᴜᴀʟᴀɴ sᴛᴏᴋ & sᴄʀɪᴘᴛ ʏᴀɴɢ sᴏʟᴅ.</i></blockquote>"
            )
            
            # Perbaikan: Kedua tombol disatukan dalam list [] milik InlineKeyboardMarkup
            btns = InlineKeyboardMarkup([
                [InlineKeyboardButton("ʀᴇғʀᴇsʜ ᴅᴀᴛᴀ", callback_data="admin_cek_omset", icon_custom_emoji_id=extract_id(Config.putar))],
                [InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]
            ])
            
            if query.message.photo:
                await query.message.edit_caption(caption=text_omset, reply_markup=btns)
            else:
                await query.message.edit_text(text=text_omset, reply_markup=btns)

        except Exception as e:
            logger.error(f"Error Cek Omset: {e}")
            await query.answer(f"{Config.silang} Gagal mengambil data omset dari database!", show_alert=True)

    elif data == "admin_cek_omset":
        if u_id != Config.OWNER_ID: 
            return
        await query.answer(f"{Config.loading} Menghitung total omset pendapatan dari database...", show_alert=False)
        try:
            omset_data = await database.get_omset_stats()
            text_omset = (
                f"<blockquote><b>{Config.harga} 𝗥 Ｅ 𝗣 𝗢 𝗥 𝗧 𝗢 𝗠 Ｓ Ｅ 𝗧</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.statistik} <b>Pᴇɴᴅᴀᴘᴀᴛᴀɴ Kᴏᴛᴏʀ (Rᴇᴠᴇɴᴜᴇ)</b>\n\n"
                f"{Config.bulattitik} <b>Hᴀʀɪ Iɴɪ :</b> <code>Rᴘ {omset_data.get('today', 0):,}</code>\n"
                f"{Config.bulattitik} <b>Mɪɴɢɢᴜ Iɴɪ:</b> <code>Rᴘ {omset_data.get('this_week', 0):,}</code>\n"
                f"{Config.bulattitik} <b>Bᴜʟᴀɴ Iɴɪ :</b> <code>Rᴘ {omset_data.get('this_month', 0):,}</code>\n"
                f"{Config.mahkota} <b>Tᴏᴛᴀʟ Aʟʟ :</b> <code>Rᴘ {omset_data.get('all_time', 0):,}</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.catatan} <i>Dᴀᴛᴀ ᴅɪᴀᴍʙɪʟ sᴇᴄᴀʀᴀ ʀᴇᴀʟᴛɪᴍᴇ ᴅᴀʀɪ\n"
                f"ᴛʀᴀɴsᴀᴋsɪ ᴘᴇɴᴊᴜᴀʟᴀɴ sᴛᴏᴋ & sᴄʀɪᴘᴛ ʏᴀɴɢ sᴏʟᴅ.</i></blockquote>"
            )
            
            btns = InlineKeyboardMarkup([
                [InlineKeyboardButton("ʀᴇғʀᴇsʜ ᴅᴀᴛᴀ", callback_data="admin_cek_omset", icon_custom_emoji_id=extract_id(Config.putar))],
                [InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]
            ])
            
            if query.message.photo:
                await query.message.edit_caption(caption=text_omset, reply_markup=btns)
            else:
                await query.message.edit_text(text=text_omset, reply_markup=btns)
        except Exception as e:
            try:
                await query.answer(f"❌ Gagal memuat omset: {e}", show_alert=True)
            except:
                pass

    elif data == "admin_addstok":
        if u_id != Config.OWNER_ID: 
            return
        user_states[u_id] = {"action": "wait_stok_data"}
        text = (
            f"<blockquote><b>{Config.masukin} ɪɴᴘᴜᴛ ᴅᴀᴛᴀ sᴛᴏᴋ ᴀᴋᴜɴ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"ғᴏʀᴍᴀᴛ ᴡᴀᴊɪʙ:\n"
            f"<code>UID|DC|PHONE|REGION|LIMIT|EMAIL|BENEFIT|PASS</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.catatan} ɪɴᴘᴜᴛ ʙᴜʟᴋ: ɢᴜɴᴀᴋᴀɴ 'ᴇɴᴛᴇʀ' ᴜɴᴛᴜᴋ ʙᴀʀɪs ʙᴀʀᴜ\n"
            f"{Config.catatan} ɪɴᴘᴜᴛ sɪɴɢʟᴇ: ᴋɪʀɪᴍ 𝟷 ʙᴀʀɪs ᴜɴᴛᴜᴋ ᴠᴇʀɪғɪᴋᴀsɪ ᴏᴛᴘ</blockquote>"
        )
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
        return await query.message.edit_text(text, reply_markup=btns)

    elif data == "next_bulk_stok":
        if u_id != Config.OWNER_ID: return
        return await trigger_next_bulk_stok(client, query.message, u_id)

    elif data == "admin_req_ubahharga":
        if u_id != Config.OWNER_ID: return
        user_states[u_id] = {"action": "admin_wait_ubahharga"}
        try: await query.message.delete()
        except: pass
        return await client.send_message(
            u_id,
            f"<blockquote><b>{Config.ubahharga} 𝗨 𝗕 𝗔 𝗛 𝗛 𝗔 𝗥 𝗚 𝗔</b>\n\n{Config.inputteks} sɪʟᴀʜᴋᴀɴ ᴋᴇᴛɪᴋ ᴜɪᴅ ᴀᴋᴜɴ ᴅᴀɴ ʜᴀʀɢᴀ ʙᴀʀᴜ ᴅᴇɴɢᴀɴ sᴘᴀsɪ:\n<code>[UID] [Harga_Baru]</code>\n\nCᴏɴᴛᴏʜ: <code>81918282 6500</code></blockquote>",
            reply_markup=ForceReply(selective=True)
        )

    elif data == "admin_bc":
        if u_id != Config.OWNER_ID: 
            return
        text_bc = (
            f"<blockquote><b>{Config.broadcast} ʙʀᴏᴀᴅᴄᴀsᴛ ᴘᴇsᴀɴ (ᴘᴇɴɢᴜᴍᴜᴍᴀɴ)</b>\n\n"
            f"ᴜɴᴛᴜᴋ ᴍᴇɴɢɪʀɪᴍ ʙʀᴏᴀᴅᴄᴀsᴛ ᴋᴇ sᴇʟᴜʀᴜʜ ᴜsᴇʀ, sɪʟᴀʜᴋᴀɴ 'ʀᴇᴘʟʏ' sᴇʙᴜᴀʜ ᴘᴇsᴀɴ "
            f"ᴀᴘᴀᴘᴜɴ (ᴛᴇᴋs, ɢᴀᴍʙᴀʀ, ᴀᴛᴀᴜ ᴠɪᴅᴇᴏ) ᴅᴇɴɢᴀɴ ᴍᴇɴɢᴇᴛɪᴋ ᴘᴇʀɪɴᴛᴀʜ <code>/bc</code>.</blockquote>"
        )
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
        return await query.message.edit_text(text_bc, reply_markup=btns)

    elif data == "admin_req_clearsaldo":
        if u_id != Config.OWNER_ID: return
        user_states[u_id] = {"action": "admin_wait_clearsaldo"}
        try: await query.message.delete()
        except: pass
        return await client.send_message(
            u_id,
            f"<blockquote><b>{Config.clear} ʀᴇsᴇᴛ sᴀʟᴅᴏ ᴜsᴇʀ ᴋᴇ ɴᴏʟ</b>\n\n{Config.inputteks} sɪʟᴀʜᴋᴀɴ ᴋᴇᴛɪᴋ <b>ɪᴅ ᴜsᴇʀ (ᴜsᴇʀ ɪᴅ)</b> ʏᴀɴɢ ɪɴɢɪɴ ᴅɪ-ʀᴇsᴇᴛ sᴀʟᴅᴏɴʏᴀ ᴍᴇɴᴊᴀᴅɪ 0 ʀᴜᴘɪᴀʜ:</blockquote>",
            reply_markup=ForceReply(selective=True)
        )

    elif data == "admin_req_clearuid":
        if u_id != Config.OWNER_ID: return
        user_states[u_id] = {"action": "admin_wait_clearuid"}
        try: await query.message.delete()
        except: pass
        return await client.send_message(
            u_id,
            f"<blockquote><b>{Config.cekdevice} ʜᴀᴘᴜs sᴛᴏᴋ ʙᴇʀᴅᴀsᴀʀᴋᴀɴ ᴜɪᴅ</b>\n\n{Config.inputteks} sɪʟᴀʜᴋᴀɴ ᴋᴇᴛɪᴋ <b>ᴜɪᴅ ᴀᴛᴀᴜ ᴘʀᴇғɪx</b> ᴀᴋᴜɴ ʏᴀɴɢ ɪɴɢɪɴ ᴅɪʜᴀᴘᴜs ᴅᴀʀɪ ᴅᴀᴛᴀʙᴀsᴇ:</blockquote>",
            reply_markup=ForceReply(selective=True)
        )

    elif data == "admin_backup":
        if u_id != Config.OWNER_ID: return
        await query.message.edit_text(f"<blockquote><b>{Config.loading} ᴍᴇᴍᴘʀᴏsᴇs ʙᴀᴄᴋᴜᴘ sᴇʟᴜʀᴜʜ ᴅᴀᴛᴀʙᴀsᴇ...</b>\nᴍᴏʜᴏɴ ᴊᴀɴɢᴀɴ ᴍᴇɴᴇᴋᴀɴ ᴀᴘᴀᴘᴜɴ.</blockquote>")
        try:
            stocks = await database.stocks_col.find({}).to_list(length=None)
            backup_data = []
            for s in stocks:
                s['_id'] = str(s['_id'])
                s['created_at'] = s['created_at'].strftime('%Y-%m-%d %H:%M:%S') if 'created_at' in s else ""
                s['sold_at'] = s['sold_at'].strftime('%Y-%m-%d %H:%M:%S') if 'sold_at' in s else ""
                backup_data.append(s)

            file_backup_name = f"backup_noktel_vvip_{int(time.time())}.json"
            with open(file_backup_name, "w") as f:
                json.dump(backup_data, f, indent=4)

            await client.send_document(
                chat_id=u_id,
                document=file_backup_name,
                caption=f"<blockquote><b>{Config.backup} 𝗕𝗔𝗖𝗞𝗨𝗣 𝗗𝗔𝗧𝗔𝗕𝗔𝗦𝗘 𝗦𝗨𝗞𝗦𝗘𝗦</b>\nᴛᴏᴛᴀʟ ᴅᴀᴛᴀ ᴛᴇʀʙᴀᴄᴋᴜᴘ: <b>{len(backup_data)} ᴀᴋᴜɴ</b></blockquote>"
            )
            os.remove(file_backup_name) # Auto cleanup
            await send_panel_menu(client, query.message, u_id)
        except Exception as e:
            logger.error(f"Error backup database: {e}")
            btns = InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])

            await query.message.edit_text(f"<blockquote><b>{Config.silang} Gagal Melakukan Backup: {e}</b>\nSistem gagal membuat file JSON.</blockquote>", reply_markup=btns)

    # ============================================================
    # TAHAP 1: CEGATAN KONFIRMASI (Mencegah Pencet Tidak Sengaja)
    # ============================================================
    elif data == "clear_all_stok":  # Ganti callback_data di tombol panel lu ke "clear_all_stok"
        if u_id != Config.OWNER_ID: 
            return
        
        text_konfirmasi = (
            f"<blockquote>{Config.peringatan} <b>𝗣𝗘𝗥𝗜𝗡𝗚𝗔𝗧𝗔𝗡 𝗧𝗜𝗡𝗗𝗔𝗞𝗔𝗡 𝗙𝗔𝗧𝗔𝗟</b> {Config.peringatan}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"ᴀᴘᴀᴋᴀʜ ᴀɴᴅᴀ ʙᴇɴᴀʀ-ʙᴇɴᴀʀ ʏᴀᴋɪɴ ɪɴɢɪɴ <b>ᴍᴇɴɢʜᴀᴘᴜs sᴇᴍᴜᴀ sᴛᴏᴋ ʀᴇᴀᴅʏ</b>?\n\n"
            f"🔴 <b>ᴋᴏɴsᴇᴋᴜᴇɴsɪ:</b>\n"
            f"𝟷. sᴇᴍᴜᴀ ᴀᴋᴜɴ ʙᴇʀsᴛᴀᴛᴜs 'ʀᴇᴀᴅʏ' ᴀᴋᴀɴ <b>ᴅɪʟᴏɢᴏᴜᴛ</b> ᴅᴀʀɪ sᴇʀᴠᴇʀ ᴛᴇʟᴇɢʀᴀᴍ.\n"
            f"𝟸. ᴅᴀᴛᴀ ᴀᴋᴀɴ ᴅɪʜᴀᴘᴜs <b>ᴘᴇʀᴍᴀɴᴇɴ</b> ᴅᴀʀɪ ᴅᴀᴛᴀʙᴀsᴇ.\n\n"
            f"<i>ᴛɪɴᴅᴀᴋᴀɴ ɪɴɪ ᴛɪᴅᴀᴋ ᴅᴀᴘᴀᴛ ᴅɪʙᴀᴛᴀʟᴋᴀɴ ᴅᴇɴɢᴀɴ ᴄᴀʀᴀ ᴀᴘᴀ ᴘᴜɴ!</i></blockquote>"
        )
        
        btns = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("ᴛɪᴅᴀᴋ, ʙᴀᴛᴀʟᴋᴀɴ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.silang)),
                InlineKeyboardButton("ʏᴀ, ʜᴀᴘᴜs sᴇᴍᴜᴀ", callback_data="confirm_clear_all", icon_custom_emoji_id=extract_id(Config.centanghijau))
            ]
        ])
        return await query.message.edit_text(text_konfirmasi, reply_markup=btns)

    # ============================================================
    # TAHAP 2: EKSEKUSI (Hanya jalan jika benar-benar diklik "YA")
    # ============================================================
    elif data == "confirm_clear_all":
        if u_id != Config.OWNER_ID: 
            return
        await query.answer("ᴍᴇᴍᴘʀᴏsᴇs ᴘᴇᴍʙᴇʀsɪʜᴋᴀɴ ᴀᴍᴀɴ...", show_alert=False)
        try:
            # Mengambil semua stok ready untuk di-logout satu persatu
            all_ready = await database.stocks_col.find({"status": "ready"}).to_list(length=None)
            
            if not all_ready:
                return await query.message.edit_text(
                    f"<blockquote>{Config.silang} <b>𝗚𝗔𝗚𝗔𝗟 𝗣𝗘𝗠𝗕𝗘𝗥𝗦𝗜𝗛𝗞𝗔𝗡</b>\nᴛɪᴅᴀᴋ ᴀᴅᴀ sᴛᴏᴋ ʙᴇʀᴋᴀᴛᴇɢᴏʀɪ 'ʀᴇᴀᴅʏ' ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ sᴀᴀᴛ ɪɴɪ.</blockquote>",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
                )

            # Mengubah pesan menjadi loading agar admin tahu proses sedang berjalan
            await query.message.edit_text(f"<blockquote>{Config.loading} ᴍᴇʟᴏɢᴏᴜᴛ {len(all_ready)} sᴇsɪ ᴅᴀʀɪ sᴇʀᴠᴇʀ ᴛᴇʟᴇɢʀᴀᴍ... ᴍᴏʜᴏɴ ᴛᴜɴɢɢᴜ.</blockquote>")

            for stok in all_ready:
                if stok.get("session"):
                    asyncio.create_task(perform_bot_logout(stok["session"], u_id))
            
            ready_count = len(all_ready)
            sold_count = await database.stocks_col.count_documents({"status": "sold"})
            
            # Wipe Collection DB Khusus yang Ready saja
            result = await database.stocks_col.delete_many({"status": "ready"})
            await database.db["bulk_sessions"].delete_many({}) # Bersihkan sisa sesi borongan

            try: 
                await query.message.delete()
            except: 
                pass
            
            report_text = (
                f"<blockquote>{Config.clearall} <b>𝗗𝗔𝗧𝗔𝗕𝗔𝗦𝗘 𝗦𝗧𝗢𝗞 𝗧𝗘𝗟𝗔𝗛 𝗗𝗜𝗕𝗘𝗥𝗦𝗜𝗛𝗞𝗔𝗡</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.tongsampah} ᴛᴏᴛᴀʟ ᴅɪʜᴀᴘᴜs : <b>{result.deleted_count} ᴀᴄᴄ</b>\n"
                f"🔌 ᴛᴏᴛᴀʟ ʟᴏɢᴏᴜᴛ : <b>{ready_count} sᴇsɪ (ʙᴏᴛ sᴀᴊᴀ)</b>\n"
                f"{Config.statistik} ᴀᴋᴜɴ sᴏʟᴅ (ᴀᴡᴇᴛ): <b>{sold_count} ᴀᴋᴜɴ ᴛᴇʀᴊᴜᴀʟ</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.centanghijau} sᴇᴍᴜᴀ ᴀᴋᴜɴ 'ʀᴇᴀᴅʏ' ʙᴇʀʜᴀsɪʟ ᴅɪʟᴏɢᴏᴜᴛ ᴅᴀʀɪ sᴇʀᴠᴇʀ ᴛᴇʟᴇɢʀᴀᴍ\n"
                f"ᴅᴀɴ ᴅɪʜᴀᴘᴜs sᴇᴄᴀʀᴀ ᴘᴇʀᴍᴀɴᴇɴ ᴅᴀʀɪ ᴅᴀᴛᴀʙᴀsᴇ sɪsᴛᴇᴍ ᴋᴀᴍɪ.</blockquote>"
            )
            btns = InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]])

            await client.send_message(u_id, text=report_text, reply_markup=btns)
            
        except Exception as e:
            logger.error(f"Error clear all execution: {e}")
            await query.message.edit_text(
                f"<blockquote>{Config.silang} <b>𝗘𝗥𝗥𝗢𝗥 𝗦𝗔𝗔𝗧 𝗣𝗘𝗠𝗕𝗘𝗥𝗦𝗜𝗛𝗞𝗔𝗡</b>\n<code>{str(e)}</code></blockquote>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
            )

    # ============================================================
    # (C) FITUR DEPOSIT SYSTEM (TOP-UP SALDO) BERBOBOT
    # ============================================================
    elif data == "deposit_menu":
        text = (
            f"<blockquote><b>{Config.kredit} 𝗠 𝗘 𝗡 𝗨 𝗗 𝗘 𝗣 𝗢 𝗦 𝗜 𝗧</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ɴᴏᴍɪɴᴀʟ ᴅᴇᴘᴏsɪᴛ ʏᴀɴɢ ᴛᴇrsᴇᴅɪᴀ,\n"
            f"ᴀᴛᴀᴜ ᴋᴇᴛɪᴋ ᴍᴀɴᴜᴀʟ ᴊᴜᴍʟᴀʜ ʏᴀɴɢ ᴀɴᴅᴀ ᴅɪɪɴɢɪɴᴋᴀɴ:</blockquote>"
        )
        btns = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Rp 10.000", callback_data="depo_10000", icon_custom_emoji_id=extract_id(Config.ubahharga)), 
                InlineKeyboardButton("Rp 25.000", callback_data="depo_25000", icon_custom_emoji_id=extract_id(Config.ubahharga))
            ],
            [
                InlineKeyboardButton("Rp 50.000", callback_data="depo_50000", icon_custom_emoji_id=extract_id(Config.ubahharga)), 
                InlineKeyboardButton("Rp 100.000", callback_data="depo_100000", icon_custom_emoji_id=extract_id(Config.ubahharga))
            ],
            [
                InlineKeyboardButton("ᴋᴇᴛɪᴋ ɴᴏᴍɪɴᴀʟ ᴍᴀɴᴜᴀʟ", callback_data="depo_manual", icon_custom_emoji_id=extract_id(Config.inputteks))
            ],
            [
                InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ʜᴏᴍᴇ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))
            ]
        ])

        if query.message.photo:
            await query.message.edit_caption(caption=text, reply_markup=btns)
        else:
            await query.message.edit_text(text=text, reply_markup=btns)

    elif data == "depo_manual":
        user_states[u_id] = {"action": "wait_deposit_amount"}
        try: await query.message.delete()
        except: pass
        await client.send_message(
            u_id,
            f"<blockquote><b>{Config.inputteks} ᴋᴇᴛɪᴋ ɴᴏᴍɪɴᴀʟ ᴅᴇᴘᴏsɪᴛ (ᴍɪɴ. Rp 5.000):</b>\n\n{Config.catatan} <i>Cᴏɴᴛᴏʜ ᴘᴇɴᴜʟɪsᴀɴ ʏᴀɴɢ ʙᴇɴᴀʀ: 15000</i>\n(Tᴀɴᴘᴀ ᴛɪᴛɪᴋ ᴀᴛᴀᴜ ᴋᴏᴍᴀ)</blockquote>",
            reply_markup=ForceReply(selective=True)
        )

    elif data.startswith("depo_") and data != "depo_manual":
        try:
            amount = int(data.split("_")[1])
            formatted_amount = format_rupiah(amount)
            text_pilih = (
                f"<blockquote><b>{Config.kredit} 𝗠 𝗘 𝗧 𝗢 𝗗 𝗘 𝗗 𝗘 𝗣 𝗢 𝗦 𝗜 𝗧</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.harga} ᴊᴜᴍʟᴀʜ ᴅᴇᴘᴏsɪᴛ ᴀɴᴅᴀ : <b>{formatted_amount}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ᴍᴇᴛᴏᴅᴇ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ:</blockquote>"
            )
            btns = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs (ᴘᴀᴋᴀsɪʀ)", callback_data=f"pAut_D_{amount}", icon_custom_emoji_id=extract_id(Config.belifast))],
                [InlineKeyboardButton(text="ǫʀɪs ᴍᴀɴᴜᴀʟ / ᴅᴀɴᴀ", callback_data=f"pMan_D_{amount}", icon_custom_emoji_id=extract_id(Config.bank))],
                [InlineKeyboardButton(text="ʙᴀᴛᴀʟᴋᴀɴ ᴛʀᴀɴsᴀᴋsɪ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.silang))]
            ])
            if query.message.photo:
                await query.edit_message_caption(caption=text_pilih, reply_markup=btns)

            else:
                await query.message.edit_text(text=text_pilih, reply_markup=btns)
        except Exception as e:
            logger.error(f"Error parse deposit payload: {e}")

    elif data.startswith("pAut_D_") or data.startswith("pMan_D_"):
        is_auto = data.startswith("pAut_D_")
        amount = int(data.split("_")[2])
        
        # =========================================================
        # 🚧 PROTEKSI MINIMAL 50K KHUSUS DEPOSIT QRIS OTOMATIS
        # =========================================================
        if is_auto and amount < 50000:
            pesan_tolak = (
                f"<blockquote><b>{Config.silang} 𝗠𝗜𝗡𝗜𝗠𝗔𝗟 𝗗𝗘𝗣𝗢𝗦𝗜𝗧 𝗤𝗥𝗜𝗦 𝗢𝗧𝗢𝗠𝗔𝗧𝗜𝗦</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.peringatan} ᴍɪɴɪᴍᴀʟ ᴛʀᴀɴsᴀᴋsɪ ᴠɪᴀ ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs ᴀᴅᴀʟᴀʜ <b>ʀᴘ 𝟻𝟶.𝟶𝟶𝟶</b>.\n"
                f"ɴᴏᴍɪɴᴀʟ ᴀɴᴅᴀ: <b>{format_rupiah(amount)}</b>\n\n"
                f"<i>{Config.catatan} sɪʟᴀᴋᴀɴ ɢᴜɴᴀᴋᴀɴ ᴍᴇᴛᴏᴅᴇ <b>ǫʀɪs ᴍᴀɴᴜᴀʟ</b> ᴜɴᴛᴜᴋ ɴᴏᴍɪɴᴀʟ ɪɴɪ!</i></blockquote>"
            )
            btns_tolak = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="ᴋᴇᴍʙᴀʟɪ ᴘɪʟɪʜ ᴍᴇᴛᴏᴅᴇ", 
                    callback_data=f"depo_{amount}", 
                    icon_custom_emoji_id=extract_id(Config.kembali)
                )]
            ])

            if query.message.photo:
                return await query.edit_message_caption(caption=pesan_tolak, reply_markup=btns_tolak)
            else:
                return await query.message.edit_text(text=pesan_tolak, reply_markup=btns_tolak)
        # =========================================================
        
        oid_request = f"DEP{int(time.time())}" 
        sid_pass = f"DEP-{oid_request}-{amount}"
        
        if is_auto:
            # 🔥 INI BARIS YANG HILANG: Memanggil API Pakasir VVIP 🔥
            try:
                await query.edit_message_caption(caption=f"<blockquote><b>{Config.loading} ᴍᴇɴɢʜᴀsɪʟᴋᴀɴ ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs ᴅᴀʀɪ ᴘᴀᴋᴀsɪʀ...</b></blockquote>")
            except:
                pass
                
            qr_img, final_price = await PaymentGateway.generate_qris(amount, oid_request)
            
            if not qr_img:
                pesan_error = f"<blockquote><b>{Config.silang} ɢᴀᴛᴇᴡᴀʏ ᴘᴀᴋᴀsɪʀ sᴇᴅᴀɴɢ ᴇʀʀᴏʀ ᴀᴛᴀᴜ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ!</b>\nCᴏʙᴀ ɢᴜɴᴀᴋᴀɴ Qʀɪs Mᴀɴᴜᴀʟ.</blockquote>"
                btns_error = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ", callback_data=f"depo_{amount}", icon_custom_emoji_id=extract_id(Config.kembali))]
                ])
                if query.message.photo:
                    return await query.message.edit_caption(caption=pesan_error, reply_markup=btns_error)
                else:
                    return await query.message.edit_text(text=pesan_error, reply_markup=btns_error)
            
            real_oid = qr_img.name.split("_")[1].split(".")[0]
            
            caption_pay = (
                f"<blockquote><b>{Config.struk} 𝗜 𝗡 𝗩 𝗢 𝗜 𝗖 𝗘 𝗗 𝗘 𝗣 𝗢 𝗦 𝗜 𝗧</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.oid} ᴏʀᴅᴇʀ ɪᴅ : <code>{real_oid}</code>\n"
                f"{Config.user} ᴘᴇᴍʙᴇʟɪ : <b>{u_name}</b>\n"
                f"{Config.harga} ᴛᴏᴛᴀʟ : <b>{format_rupiah(final_price)}</b>\n"
                f"{Config.loading} ᴇxᴘɪʀᴇᴅ : <b>𝟷𝟶 ᴍᴇɴɪᴛ ᴋᴇ ᴅᴇᴘᴀɴ</b>\n"
                f"{Config.tanggal} ᴛᴀɴɢɢᴀʟ : <b>{datetime.now(WIB).strftime('%d/%m/%Y %H:%M')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.pin} <b>ᴘᴀɴᴅᴜᴀɴ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴏᴛᴏᴍᴀᴛɪs:</b>\n"
                f"1. sɪʟᴀʜᴋᴀɴ sᴄᴀɴ ɢᴀᴍʙᴀʀ ǫʀɪs ᴅɪ ᴀᴛᴀs.\n"
                f"2. ᴘᴀsᴛɪᴋᴀɴ ɴᴏᴍɪɴᴀʟ ᴛʀᴀɴsғᴇʀ sᴇsᴜᴀɪ ᴅᴇɴɢᴀɴ ᴛᴀɢɪʜᴀɴ.\n"
                f"3. ᴊɪᴋᴀ sᴜᴅᴀʜ, ᴋʟɪᴋ ᴛᴏᴍʙᴏʟ ᴄᴇᴋ sᴛᴀᴛᴜs ᴅɪ ʙᴀᴡᴀʜ.\n"
                f"4. sᴀʟᴅᴏ ᴀᴋᴀɴ ᴍᴀsᴜᴋ ᴏᴛᴏᴍᴀᴛɪs ᴋᴇ ᴀᴋᴜɴ ᴀɴᴅᴀ.</blockquote>"
            )
            
            btns = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="ᴄᴇᴋ sᴛᴀᴛᴜs ᴘᴇᴍʙᴀʏᴀʀᴀɴ", callback_data=f"checkD_{real_oid}_{amount}", icon_custom_emoji_id=extract_id(Config.putar))],
                [InlineKeyboardButton(text="ʙᴀᴛᴀʟᴋᴀɴ ᴛʀᴀɴsᴀᴋsɪ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.silang))]
            ])

            try: 
                await query.message.delete()
            except: 
                pass
                
            await client.send_photo(chat_id=u_id, photo=qr_img, caption=caption_pay, reply_markup=btns)

        else:
            # --- SIMPAN DETAIL DEPOSIT MANUAL & TIMER ---
            waiting_manual_proof[u_id] = {
                "sid": sid_pass,
                "price": amount,
                "product": "Deposit Saldo"
            }
            asyncio.create_task(auto_cancel_order(sid_pass, u_id, client))
            
            caption_pay = (
                f"<blockquote><b>{Config.struk} 𝗜 𝗡 𝗩 𝗢 𝗜 𝗖 𝗘 𝗠 𝗔 𝗡 𝗨 𝗔 𝗟</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.user} ᴘᴇᴍʙᴇʟɪ : <b>{u_name}</b>\n"
                f"{Config.harga} ᴛᴏᴛᴀʟ : <b>{format_rupiah(amount)}</b>\n"
                f"{Config.tanggal} ᴛᴀɴɢɢᴀʟ : <b>{datetime.now(WIB).strftime('%d/%m/%Y %H:%M')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.pin} <b>ɪɴsᴛʀᴜᴋsɪ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴍᴀɴᴜᴀʟ:</b>\n"
                f"1. sɪʟᴀʜᴋᴀɴ sᴄᴀɴ ǫʀɪs ᴘᴀᴅᴀ ɢᴀᴍʙᴀʀ ᴅɪ ᴀᴛᴀs.\n"
                f"2. ᴛʀᴀɴsғᴇʀ ᴛᴇᴘᴀᴛ sᴇʙᴇsᴀʀ <code>{amount}</code>.\n"
                f"3. ᴋɪʀɪᴍ ғᴏᴛᴏ ʙᴜᴋᴛɪ ᴛʀᴀɴsғᴇʀ ᴋᴇ ᴄʜᴀᴛ ɪɴɪ sᴇᴋᴀʀᴀɴɢ ᴊᴜɢᴀ!\n\n"
                f"{Config.kredit} <b>DANA / E-Wallet :</b> <code>{Config.DANA_NUMBER}</code>\n"
                f"{Config.peringatan} <i>ᴅᴇᴘᴏsɪᴛ ᴀᴋᴀɴ ᴅɪᴠᴇʀɪғɪᴋᴀsɪ sᴇᴄᴀʀᴀ ᴍᴀɴᴜᴀʟ ᴏʟᴇʜ ᴀᴅᴍɪɴ.</i></blockquote>"
            )
            try: await query.message.delete()
            except: pass
            await client.send_photo(
                chat_id=u_id, 
                photo=Config.QRIS_MANUAL_URL, 
                caption=caption_pay, 
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="ʙᴀᴛᴀʟᴋᴀɴ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.silang))]
                ])
            )


    elif data.startswith("checkD_"):
        parts = data.split("_", 2)
        oid, amount = parts[1], int(parts[2])
        status_msg = await client.send_message(u_id, f"<blockquote><b>{Config.cekdevice} ᴍᴇɴɢᴇᴄᴇᴋ ᴍᴜᴛᴀsɪ ᴅᴀɴᴀ ᴅɪ sᴇʀᴠᴇʀ ᴘᴀᴋᴀsɪʀ...</b>\nᴍᴏʜᴏɴ ᴛᴜɴɢɢᴜ sᴇʙᴇɴᴛᴀʀ...</blockquote>")
        
        is_paid = False
        for _ in range(4): # Loop checker advanced
            if await PaymentGateway.is_confirmed(oid, amount):
                is_paid = True
                break
            await asyncio.sleep(2)
            
        if is_paid:
            try:
                await query.message.delete()
                await status_msg.delete()
            except: pass
            
            await database.update_balance(u_id, amount)
            await client.send_message(
                u_id, 
                f"<blockquote><b>{Config.centanghijau} 𝗗𝗘𝗣𝗢𝗦𝗜𝗧 𝗦𝗨𝗞𝗦𝗘𝗦!</b>\n\n{Config.harga} sᴀʟᴅᴏ sᴇʙᴇsᴀʀ <b>{format_rupiah(amount)}</b> ᴛᴇʟᴀʜ ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ ᴋᴇ ᴀᴋᴜɴ ᴀɴᴅᴀ. ᴛᴇʀɪᴍᴀ ᴋᴀsɪʜ!</blockquote>", 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ ᴜᴛᴀᴍᴀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]])
            )

            await Logger.log_deposit(client, u_id, u_name, amount, oid)
        else:
            try: await status_msg.delete()
            except: pass
            await query.answer(f"{Config.peringatan} ᴘᴇᴍʙᴀʏᴀʀᴀɴ ʙᴇʟᴜᴍ ᴍᴀsᴜᴋ ᴀᴛᴀᴜ ʙᴇʟᴜᴍ ᴛᴇʀᴅᴇᴛᴇᴋsɪ ᴏʟᴇʜ sɪsᴛᴇᴍ! Sɪʟᴀᴋᴀɴ ᴛᴜɴɢɢᴜ 1 ᴍᴇɴɪᴛ ᴅᴀɴ ᴄᴏʙᴀ ʟᴀɢɪ.", show_alert=True)

    elif data.startswith("accD_"):
        parts = data.split("_", 2)
        if len(parts) < 3:
            return await query.answer(f"{Config.silang} Format Callback Data Tidak Valid!", show_alert=True)

        target_id = int(parts[1])
        sid = parts[2]
        
        try:
            amount = int(sid.split("-")[2])
        except (IndexError, ValueError):
            return await query.answer(f"{Config.silang} Gagal mendapatkan nominal deposit!", show_alert=True)
            
        await query.answer(f"{Config.centanghijau} Memproses deposit...", show_alert=False)

        # --- AMBIL DATA BUYER SEBELUM EDIT CAPTION ---
        try:
            b_user = await client.get_users(target_id)
            buyer_name = f"@{b_user.username}" if b_user.username else b_user.first_name
        except:
            buyer_name = f"ᴜsᴇʀ {target_id}"

        waktu_tf = datetime.now(WIB).strftime('%d/%m/%Y %H:%M')

        caption_success = (
            f"<blockquote><b>{Config.centanghijau} ᴅᴇᴘᴏsɪᴛ ᴍᴀɴᴜᴀʟ ʙᴇʀʜᴀsɪʟ ᴅɪᴋᴏɴғɪʀᴍᴀsɪ!</b>\n\n"
            f"{Config.user} ʙᴜʏᴇʀ : <b>{buyer_name}</b>\n"
            f"{Config.uid} ɪᴅ : <code>{target_id}</code>\n"
            f"{Config.box} ᴘʀᴏᴅᴜᴋ : <b>ᴅᴇᴘᴏsɪᴛ sᴀʟᴅᴏ</b>\n"
            f"{Config.folder} ᴋᴀᴛᴇɢᴏʀɪ : <b>ᴛᴏᴘ ᴜᴘ</b>\n"
            f"{Config.harga} ᴛᴏᴛᴀʟ ᴛғ : <code>{format_rupiah(amount)}</code>\n"
            f"{Config.tanggal} ᴡᴀᴋᴛᴜ ᴛғ : <b>{waktu_tf}</b>\n\n"
            f"sɪsᴛᴇᴍ sᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏsᴇs ᴅᴀᴛᴀ ᴅᴀɴ ᴍᴇɴɢɪʀɪᴍ ɴᴏᴛɪғɪᴋᴀsɪ...</blockquote>"
        )

        try:
            await query.edit_message_caption(caption=caption_success)
        except: pass

        try:
            proof_file_id = query.message.photo.file_id if query.message.photo else None
            
            # Update saldo di database
            await database.update_balance(target_id, amount)
            
            # Kirim pesan ke user
            await client.send_message(
                chat_id=target_id, 
                text=f"<blockquote><b>{Config.centanghijau} 𝗗𝗘𝗣𝗢𝗦𝗜𝗧 𝗠𝗔𝗡𝗨𝗔𝗟 𝗗𝗜𝗧𝗘𝗥𝗜𝗠𝗔!</b>\n\n{Config.harga} sᴀʟᴅᴏ sᴇʙᴇsᴀʀ <b>{format_rupiah(amount)}</b> ᴛᴇʟᴀʜ ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ ᴋᴇ ᴀᴋᴜɴ ᴀɴᴅᴀ ᴏʟᴇʜ ᴀᴅᴍɪɴ. Sᴇʟᴀᴍᴀᴛ ʙᴇʀʙᴇʟᴀɴᴊᴀ!</blockquote>"
            )
            
            # Catat ke log deposit
            await Logger.log_deposit(client, target_id, buyer_name, amount, sid, "ᴍᴀɴᴜᴀʟ")
            
        except Exception as e:
            logger.error(f"Error acc deposit: {e}")
            await query.answer(f"{Config.silang} Error saat verifikasi deposit manual!", show_alert=True)

    elif data.startswith("decD_"):
        parts = data.split("_", 2)
        target_id = int(parts[1])
        
        await query.answer(f"{Config.silang} Menolak deposit...", show_alert=False)

        # --- DETAIL BUYER UNTUK CAPTION TOLAK ---
        try:
            b_user = await client.get_users(target_id)
            buyer_name = f"@{b_user.username}" if b_user.username else b_user.first_name
        except:
            buyer_name = f"ᴜsᴇʀ {target_id}"

        caption_reject = (
            f"<blockquote><b>{Config.silang} ᴅᴇᴘᴏsɪᴛ ᴅɪᴛᴏʟᴀᴋ (ᴛɪᴅᴀᴋ ᴠᴀʟɪᴅ)</b>\n\n"
            f"{Config.user} ʙᴜʏᴇʀ : <b>{buyer_name}</b>\n"
            f"{Config.uid} ɪᴅ : <code>{target_id}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴛᴇʟᴀʜ ᴅɪᴛᴏʟᴀᴋ ᴏʟᴇʜ ᴀᴅᴍɪɴ.</blockquote>"
        )

        try:
            await query.edit_message_caption(caption=caption_reject)
        except: pass

        await client.send_message(
            chat_id=target_id, 
            text=f"<blockquote><b>{Config.silang} 𝗗𝗘𝗣𝗢𝗦𝗜𝗧 𝗔𝗡𝗗𝗔 𝗗𝗜𝗧𝗢𝗟𝗔𝗞!</b>\n\nMᴀᴀғ, ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴀɴᴅᴀ ᴅɪᴛᴏʟᴀᴋ ᴏʟᴇʜ ᴀᴅᴍɪɴ ᴋᴀᴍɪ. Pᴀsᴛɪᴋᴀɴ ʙᴜᴋᴛɪ ᴛʀᴀɴsꜰᴇʀ ʏᴀɴɢ Aɴᴅᴀ ᴋɪʀɪᴍ ᴊᴇʟᴀs ᴅᴀɴ ɴᴏᴍɪɴᴀʟ sᴇsᴜᴀɪ ᴅᴇɴɢᴀɴ ᴛᴀɢɪʜᴀɴ. Hᴜʙᴜɴɢɪ ᴀᴅᴍɪɴ ᴜɴᴛᴜᴋ ɪɴғᴏ ʟᴇʙɪʜ ʟᴀɴᴊᴜᴛ.</blockquote>"
        )



    # ============================================================
    # (D) ETALASE TOKO & ECERAN (SISTEM MULTI-LEVEL / 3 LAYER)
    # ============================================================
    elif data == "pilih_stok" or data == "open_store":
        text = (
            f"<blockquote><b>{Config.box} 𝗘 𝗧 𝗔 𝗟 𝗔 𝗦 𝗘   𝗧 𝗢 𝗞 𝗢</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ᴋᴀᴛᴇɢᴏʀɪ ᴀᴋᴜɴ\n"
            f"ʏᴀɴɢ ɪɴɢɪɴ ᴀɴᴅᴀ ʙᴇʟɪ:</blockquote>"
        )
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ᴛᴀɢ ꜱᴄᴀᴍ", callback_data="et_scam", icon_custom_emoji_id=extract_id(Config.scam))],
            [InlineKeyboardButton(text="ᴛᴀɢ ꜰᴀᴋᴇ", callback_data="et_fake", icon_custom_emoji_id=extract_id(Config.fake))],
            [InlineKeyboardButton(text="ᴘᴏʟᴏꜱᴀɴ", callback_data="et_polos", icon_custom_emoji_id=extract_id(Config.polosan))],
            [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ ᴜᴛᴀᴍᴀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]
        ])
        
        if query.message.photo: await query.message.edit_caption(caption=text, reply_markup=btns)
        else: await query.message.edit_text(text=text, reply_markup=btns)

    elif data.startswith("et_"):
        tipe_tag = data.split("_")[1] # Mendapatkan 'fake', 'scam', atau 'polos'
        
        text = (
            f"<blockquote><b>{Config.box} 𝗞𝗔𝗧𝗘𝗚𝗢𝗥𝗜: {tipe_tag.upper()}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Pɪʟɪʜ ᴊᴇɴɪs ʟɪᴍɪᴛ ᴀᴋᴜɴ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ:</blockquote>"
        )
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ᴀᴄᴄ ʟɪᴍᴘᴇʀ (ʟɪᴍɪᴛ ᴏɴ)", callback_data=f"ets_limp_{tipe_tag}", icon_custom_emoji_id=extract_id(Config.api))],
            [InlineKeyboardButton(text="ᴀᴄᴄ ɴᴏ ᴍɪɴᴜs (ʟɪᴍɪᴛ ᴏғғ)", callback_data=f"ets_nom_{tipe_tag}", icon_custom_emoji_id=extract_id(Config.berlian1))],
            [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ", callback_data="open_store", icon_custom_emoji_id=extract_id(Config.kembali))]
        ])
        await query.message.edit_text(text=text, reply_markup=btns)

    elif data.startswith("ets_"):
        parts = data.split("_", 2)
        cat_str = parts[1] 
        tipe_tag = parts[2] 
        
        is_limper_bool = (cat_str == "limp")
        limit_target = "ON" if is_limper_bool else "OFF"
        
        emoji_head = Config.api if is_limper_bool else Config.berlian1
        label_head = f"{emoji_head} 𝗟𝗜𝗠𝗣𝗘𝗥 ({tipe_tag.upper()})" if is_limper_bool else f"{emoji_head} 𝗡𝗢 𝗠𝗜𝗡𝗨𝗦 ({tipe_tag.upper()})"
        
        all_ready = await database.stocks_col.find({"status": "ready", "is_sold": False, "limit": limit_target, "tipe_tag": tipe_tag}).to_list(length=None)
        
        if not all_ready:
            return await query.message.edit_text(
                f"<blockquote><b>{Config.peringatan} Sᴛᴏᴋ ᴜɴᴛᴜᴋ ᴋᴀᴛᴇɢᴏʀɪ {label_head} sᴇᴅᴀɴɢ ᴋᴏsᴏɴɢ ᴀᴛᴀᴜ ʜᴀʙɪs!</b></blockquote>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ", callback_data=f"et_{tipe_tag}", icon_custom_emoji_id=extract_id(Config.kembali))]])
            )
            
        grouped_data = {}
        for s in all_ready:
            uid_str = str(s.get("uid", ""))
            dc_val = str(s.get("dc", "1"))
            r_code = s.get("region_code", "UN")
            r_flag = extract_flag_only(s.get("region", "🏳️"))
            if not uid_str: continue
            
            prefix = uid_str[0]
            group_key = f"{r_code}_{prefix}_{dc_val}"
            
            if group_key not in grouped_data:
                grouped_data[group_key] = {
                    "count": 0, "flag": r_flag, "rcode": r_code, 
                    "pref": prefix, "dc": dc_val, 
                    "custom_price": s.get("custom_price", 0) 
                }
            grouped_data[group_key]["count"] += 1
            
        text = f"<blockquote><b>{Config.keranjang} 𝗘𝗧𝗔𝗟𝗔𝗦𝗘 {label_head} :</b>\n━━━━━━━━━━━━━━━━━━━━━\nsɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ɪᴅ, ᴅᴄ & ɴᴇɢᴀʀᴀ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ:</blockquote>"
        btns_list = []
        
        
        for k, v in sorted(grouped_data.items()):
            price = v["custom_price"]
            label_name = Config.LABELS.get(v['pref'], f"Id {v['pref']}xxx")
            cb_data = f"bch_{cat_str}_{tipe_tag}_{v['rcode']}_{v['pref']}_{v['dc']}"
            
            flag_premium_id = extract_id(v['flag'])
            if flag_premium_id:
                text_btn = f"{label_name} (DC {v['dc']}) | Rp {price:,} [{v['count']} ᴀᴄᴄ]"
                btns_list.append([InlineKeyboardButton(text=text_btn, callback_data=cb_data, icon_custom_emoji_id=flag_premium_id)])
            else:
                clean_flag = re.sub(r'<[^>]+>', '', v['flag']).strip()
                text_btn = f"{clean_flag} {label_name} (DC {v['dc']}) | Rp {price:,} [{v['count']} ᴀᴄᴄ]".strip()
                btns_list.append([InlineKeyboardButton(text=text_btn, callback_data=cb_data)])
            
        btns_list.append([InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ", callback_data=f"et_{tipe_tag}", icon_custom_emoji_id=extract_id(Config.kembali))])
        await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(btns_list))

    elif data.startswith("bch_"):
        parts = data.split("_", 5)
        cat_str, tipe_tag, rcode, pref, dc_val = parts[1], parts[2], parts[3], parts[4], parts[5]
        limit_val = "ON" if cat_str == "limp" else "OFF"
        
        stock_count = await database.stocks_col.count_documents({
            "status": "ready", "is_sold": False, "limit": limit_val, "tipe_tag": tipe_tag,
            "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val
        })
        
        if stock_count == 0:
            return await query.message.edit_text(
                text=f"<blockquote><b>{Config.peringatan} Mᴀᴀғ, sᴛᴏᴋ ᴋᴀᴛᴇɢᴏʀɪ ɪɴɪ sᴜᴅᴀʜ ʜᴀʙɪs ᴛᴇʀᴊᴜᴀʟ!</b></blockquote>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ", callback_data=f"ets_{cat_str}_{tipe_tag}", icon_custom_emoji_id=extract_id(Config.kembali))]])
            )
            
        sample_stock = await database.stocks_col.find_one({
            "status": "ready", "is_sold": False, "limit": limit_val, "tipe_tag": tipe_tag,
            "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val
        })
        
        price_each = sample_stock.get("custom_price", 0)
        if not price_each: price_each = Config.get_price(pref, dc_val, rcode, limit_val == "ON")
        
        tipe_name = "𝗟𝗜𝗠𝗣𝗘𝗥" if cat_str == "limp" else "𝗡𝗢 𝗠𝗜𝗡𝗨𝗦"
        label = Config.LABELS.get(pref, f"Id {pref}xxx")
        
        text = (
            f"<blockquote><b>{Config.box} 𝗗𝗘𝗧𝗔𝗜𝗟 𝗞𝗔𝗧𝗘𝗚𝗢𝗥𝗜 𝗔𝗞𝗨𝗡</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.globe} <b>Rᴇɢɪᴏɴ   :</b> {rcode}\n"
            f"{Config.uid} <b>Pʀᴇғɪx   :</b> {label}\n"
            f"{Config.antena} <b>DC Aᴋᴜɴ  :</b> {dc_val}\n"
            f"{Config.proteksi} <b>Tɪᴘᴇ     :</b> {tipe_name} ({tipe_tag.upper()})\n"
            f"{Config.harga} <b>Hᴀʀɢᴀ    :</b> Rᴘ {price_each:,} / Sᴇsɪ\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.keranjang} <b>Tᴇʀsᴇᴅɪᴀ : {stock_count} Sᴇsɪ Rᴇᴀᴅʏ</b>\n\n"
            f"<i>Sɪʟᴀᴋᴀɴ ᴘɪʟɪʜ ᴍᴇᴛᴏᴅᴇ ᴘᴇᴍʙᴇʟɪᴀɴ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ:</i></blockquote>"
        )
        
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ʙᴇʟɪ sᴀᴛᴜᴀɴ (ᴇᴄᴇʀ)", callback_data=f"buy_BLK_{cat_str}_{rcode}_{pref}_{dc_val}_1", icon_custom_emoji_id=extract_id(Config.satu))],
            [InlineKeyboardButton(text="ʙᴇʟɪ ʙᴜʟᴋ (ᴍᴀssᴀʟ)", callback_data=f"abq_{cat_str}_{rcode}_{pref}_{dc_val}", icon_custom_emoji_id=extract_id(Config.dua))],
            [InlineKeyboardButton(text="ʙᴇʟɪ ғɪʟᴇ sᴇssɪᴏɴ (.sᴇssɪᴏɴ)", callback_data=f"sess_{cat_str}_{rcode}_{pref}_{dc_val}", icon_custom_emoji_id=extract_id(Config.tiga))],
            [InlineKeyboardButton(text="ᴘɪʟɪʜ ᴜɪᴅ ᴍᴀɴᴜᴀʟ", callback_data=f"lst_{cat_str}_{tipe_tag}_{rcode}_{pref}_{dc_val}_0", icon_custom_emoji_id=extract_id(Config.empat))],
            [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ", callback_data=f"ets_{cat_str}_{tipe_tag}", icon_custom_emoji_id=extract_id(Config.kembali))]
        ])
        await query.message.edit_text(text, reply_markup=btns)

    # =========================================================
    # HANDLER BARU: sess_ (FITUR FILE SESSION)
    # =========================================================
    elif data.startswith("sess_"):
        parts = data.split("_", 4)
        type_str, rcode, pref, dc_val = parts[1], parts[2], parts[3], parts[4]
        u_id = query.from_user.id
        
        limit_val = "ON" if type_str == "limp" else "OFF"
        stock_count = await database.stocks_col.count_documents({
            "status": "ready", "limit": limit_val, "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val
        })
        
        if stock_count == 0:
            return await query.answer(f"{Config.silang} Maaf bosku, stok saat ini kosong!", show_alert=True)
            
        # Simpan state untuk ditangkap message handler text
        user_states[u_id] = {"action": f"wsess_{type_str}_{rcode}_{pref}_{dc_val}"}
        
        try: await query.message.delete()
        except: pass
        
        label = Config.LABELS.get(pref, f"Id {pref}xxx")
        teks_prompt = (
            f"<blockquote><b>{Config.folder} 𝗕𝗘𝗟𝗜 𝗙𝗜𝗟𝗘 𝗦𝗘𝗦𝗦𝗜𝗢𝗡 (.𝘀𝗲𝘀𝘀𝗶𝗼𝗻)</b>\n\n"
            f"{Config.box} <b>Kᴀᴛᴇɢᴏʀɪ:</b> {label} (DC {dc_val} - {rcode})\n"
            f"{Config.keranjang} <b>Sᴛᴏᴋ Tᴇʀsᴇᴅɪᴀ:</b> {stock_count} Aᴋᴜɴ\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.peringatan} <i>Mɪɴɪᴍᴀʟ ᴘᴇᴍʙᴇʟɪᴀɴ <b>1</b> ᴀᴄᴄ ᴅᴀɴ Mᴀᴋsɪᴍᴀʟ <b>{stock_count}</b> ᴀᴄᴄ.</i>\n\n"
            f"{Config.inputteks} <b>Sɪʟᴀᴋᴀɴ ᴋᴇᴛɪᴋ ᴊᴜᴍʟᴀʜ ᴀᴋᴜɴ ʏᴀɴɢ ɪɴɢɪɴ ᴅɪʙᴇʟɪ (ᴀɴɢᴋᴀ sᴀᴊᴀ):</b></blockquote>"
        )
        await client.send_message(u_id, teks_prompt, reply_markup=ForceReply(selective=True))
     
    elif data.startswith("lst_"):
        try:
            parts = data.split("_", 6)
            cat_str, tipe_tag, rcode, pref, dc_val, page = parts[1], parts[2], parts[3], parts[4], parts[5], int(parts[6])
            limit_val = "ON" if cat_str == "limp" else "OFF"
            
            stocks = await database.stocks_col.find({
                "status": "ready", "is_sold": False, "limit": limit_val, "tipe_tag": tipe_tag,
                "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val
            }).to_list(length=None)
            
            total = len(stocks)
            if total == 0:
                return await query.message.edit_text(
                    text=f"<blockquote><b>{Config.peringatan} Mᴀᴀғ, sᴛᴏᴋ ᴛᴇʀsᴇʙᴜᴛ ʙᴀʀᴜ sᴀᴊᴀ ʜᴀʙɪs ᴀᴛᴀᴜ ᴛᴇʀᴊᴜᴀʟ ᴋᴇ ᴏʀᴀɴɢ ʟᴀɪɴ!</b></blockquote>",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ", callback_data=f"ets_{cat_str}_{tipe_tag}", icon_custom_emoji_id=extract_id(Config.kembali))]])
                )
                
            items_per_page = 10
            total_pages = math.ceil(total / items_per_page)
            if page >= total_pages: page = 0
            if page < 0: page = total_pages - 1
            
            start_idx = page * items_per_page
            end_idx = start_idx + items_per_page
            page_stocks = stocks[start_idx:end_idx]
            
            btns = []
            color_map = {
                0: Config.love_red, 1: Config.love_orange, 2: Config.love_ungu, 
                3: Config.love_green, 4: Config.love_birumuda, 5: Config.love_birutua, 6: Config.love_pink
            }
            
            
            for s in page_stocks:
                price_item = s.get("custom_price", 0)
                if not price_item: price_item = Config.get_price(pref, dc_val, rcode, limit_val == "ON")
                uid_str = str(s.get('uid', '-'))
                
                try:
                    color_index = int(uid_str) % 7
                    love = color_map.get(color_index, Config.gembokputih)
                except ValueError:
                    love = Config.gembokputih 
                
                flag = extract_flag_only(s.get("region", "🏳️"))
                clean_flag = re.sub(r'<[^>]+>', '', flag).strip()
                
                btn_text = f"{uid_str} (DC {dc_val}) {clean_flag} - Rp {price_item:,}".replace(",", ".")
                btns.append([InlineKeyboardButton(text=btn_text, callback_data=f"vdet_{s['_id']}_{page}", icon_custom_emoji_id=extract_id(love))])
            
            nav_row = []
            if total_pages > 1:
                nav_row.append(InlineKeyboardButton(text="⬅️ ᴘʀᴇᴠ", callback_data=f"lst_{cat_str}_{tipe_tag}_{rcode}_{pref}_{dc_val}_{page - 1}"))
                nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
                nav_row.append(InlineKeyboardButton(text="ɴᴇxᴛ ➡️", callback_data=f"lst_{cat_str}_{tipe_tag}_{rcode}_{pref}_{dc_val}_{page + 1}"))
                btns.append(nav_row)
                
            btns.append([InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴇᴛᴀʟᴀsᴇ", callback_data=f"ets_{cat_str}_{tipe_tag}", icon_custom_emoji_id=extract_id(Config.kembali))])
            
            label_head = "𝗟𝗜𝗠𝗣𝗘𝗥" if limit_val == "ON" else "𝗡𝗢 𝗠𝗜𝗡𝗨𝗦"
            text = (
                f"<blockquote><b>{Config.keranjang} 𝗗𝗔𝗙𝗧𝗔𝗥 𝗔𝗞𝗨𝗡 {label_head}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"Pɪʟɪʜ sᴀʟᴀʜ sᴀᴛᴜ ᴀᴋᴜɴ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ ᴜɴᴛᴜᴋ ᴍᴇʟɪʜᴀᴛ ᴅᴇᴛᴀɪʟ & ᴍᴇᴍʙᴇʟɪ:</blockquote>"
            )
            await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(btns))
        except Exception as e:
            logger.error(f"Error di lst_: {e}")
            await query.answer("Terjadi kesalahan sistem navigasi!", show_alert=True)

    elif data.startswith("vdet_"):
        try:
            parts = data.split("_")
            sid = parts[1]
            page = int(parts[2])
            
            from bson.objectid import ObjectId
            s = await database.stocks_col.find_one({"_id": ObjectId(sid)})
            if not s:
                return await query.answer("Maaf, stok ini baru saja terjual ke orang lain!", show_alert=True)
                
            is_limp = (s.get("limit", "OFF").upper() == "ON")
            pref = str(s.get("uid"))[0]
            dc_val = s.get("dc", "1")
            rcode = s.get("region_code", "DEFAULT")
            price_item = s.get("custom_price", 0)
            
            if not price_item: 
                price_item = Config.get_price(pref, dc_val, rcode, is_limp)
            
            detail = (
                f"<blockquote><b>{Config.box} 𝗗 𝗘 𝗧 𝗔 𝗜 𝗟 𝗦 𝗧 𝗢 𝗞</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.uid} ᴜɪᴅ : <code>{s.get('uid', '-')}</code>\n"
                f"{Config.globe} ʀᴇɢ : <b>{s.get('region', '-')}</b>\n"
                f"{Config.antena} ᴅᴄ : <b>{s.get('dc', '-')}</b>\n"
                f"{Config.email} sᴜʀᴇʟ : <b>{s.get('email', '-')}</b>\n"
                f"{Config.peringatan} ʟɪᴍɪᴛ : <b>{s.get('limit', '-')}</b>\n"
                f"{Config.hadiah} ʙᴇɴᴇғɪᴛ : <b>{s.get('benefit', '-')}</b>\n"
                f"{Config.harga} ʜᴀʀɢᴀ : <b>{format_rupiah(price_item)}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.belifast} Sɪʟᴀᴋᴀɴ ᴋʟɪᴋ 'Bᴇʟɪ Sᴇᴋᴀʀᴀɴɢ' ᴜɴᴛᴜᴋ ᴍᴇʟᴀɴᴊᴜᴛᴋᴀɴ ᴋᴇ ᴘᴇᴍʙᴀʏᴀʀᴀɴ.</blockquote>"
            )
            
            cat_str = "limp" if is_limp else "nom"
            tipe_tag = s.get("tipe_tag", "polos")
            back_cb = f"lst_{cat_str}_{tipe_tag}_{rcode}_{pref}_{dc_val}_{page}"
            
            btns = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="ʙᴇʟɪ ᴀᴋᴜɴ ɪɴɪ sᴇᴋᴀʀᴀɴɢ", callback_data=f"buy_SGL_{s['_id']}", icon_custom_emoji_id=extract_id(Config.belifast))],
                [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴅᴀғᴛᴀʀ", callback_data=back_cb, icon_custom_emoji_id=extract_id(Config.kembali))]
            ])
            await query.message.edit_text(text=detail, reply_markup=btns)
        except Exception as e:
            logger.error(f"Error di vdet_: {e}")
            await query.answer("Terjadi kesalahan load detail!", show_alert=True)
            
    # ============================================================
    # (E) STATISTIK GLOBAL & STOK CHECKER
    # ============================================================
    elif data == "check_all_stock":
        report = f"<blockquote><b>{Config.statistik} 𝗟 𝗜 𝗦 𝗧 𝗦 𝗧 𝗢 𝗞 𝗥 𝗘 𝗔 𝗗 𝗬</b>\n━━━━━━━━━━━━━━━━━━━━━\nBᴇʀɪᴋᴜᴛ ᴀᴅᴀʟᴀʜ ʀɪɴᴄɪᴀɴ sᴛᴏᴋ ʏᴀɴɢ sɪᴀᴘ ᴅɪʙᴇʟɪ:\n\n"
        has_stock = False
        for pref, label in Config.LABELS.items():
            stocks = await database.stocks_col.find({"status": "ready", "uid": {"$regex": f"^{re.escape(pref)}"}}).to_list(length=None)
            if stocks:
                has_stock = True
                report += f"{Config.pin} <b>{label}</b> [ 𝗧𝗼𝘁𝗮𝗹: {len(stocks)} ᴀᴄᴄ ]\n"
                for s in stocks:
                    uid_asli = s.get('uid', '-')
                    dc_asli = s.get('dc', '1')
                    is_limit = s.get('limit', 'OFF').upper() == "ON"
                    suffix = " (ʟɪᴍᴘᴇʀ)" if is_limit else ""
                    r_flag = extract_flag_only(s.get("region", ""))
                    report += f" ➥ <code>{uid_asli}</code> | DC {dc_asli}{suffix} {r_flag}\n"
                report += "━━━━━━━━━━━━━━━━━━━━━\n"
                
        if not has_stock:
            report += f"{Config.silang} ᴍᴀᴀғ ʙᴏsᴋᴜ, sᴇʟᴜʀᴜʜ sᴛᴏᴋ ᴅɪ sɪsᴛᴇᴍ sᴇᴅᴀɴɢ ᴋᴏsᴏɴɢ ᴀᴛᴀᴜ ʜᴀʙɪs ᴛᴇʀᴊᴜᴀʟ!\n"
            
        report += "</blockquote>"
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ ᴜᴛᴀᴍᴀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]])

        if query.message.photo:
            await query.message.edit_caption(caption=report, reply_markup=btns)
        else:
            await query.message.edit_text(text=report, reply_markup=btns)

    elif data == "open_stats":
        stats = await database.get_global_stats()
        from datetime import datetime
        text = (
            f"<blockquote><b>{Config.statistik} 𝗗 𝗔 𝗦 𝗛 𝗕 𝗢 𝗔 𝗥 𝗗 𝗦 𝗜 𝗦 𝗧 𝗘 𝗠</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.orang} ᴛᴏᴛᴀʟ ᴜsᴇʀ ʙᴏᴛ : <b>{stats.get('users', 0)}</b> ᴏʀᴀɴɢ\n"
            f"{Config.box} sᴛᴏᴋ ᴀᴋᴜɴ ʀᴇᴀᴅʏ : <b>{stats.get('ready', 0)}</b> ᴀᴋᴜɴ\n"
            f"{Config.harga} ᴀᴋᴜɴ ᴛᴇʀᴊᴜᴀʟ : <b>{stats.get('sold', 0)}</b> ᴀᴋᴜɴ\n"
            f"{Config.script} sᴄʀɪᴘᴛ ᴛᴇʀᴊᴜᴀʟ : <b>{stats.get('scripts_sold', 0)}</b> ᴋᴀʟɪ\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🕒 ᴛᴇʀᴀᴋʜɪʀ ᴅɪᴘᴇʀʙᴀʀᴜɪ: {datetime.now().strftime('%d/%m/%Y %H:%M')}</blockquote>"
        )
        await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ ᴜᴛᴀᴍᴀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]]))

    # ============================================================
    # (F) MENU BORONGAN (BULK BUY ENGINE) - FULL FIX CUSTOM EMOJI
    # ============================================================
    elif data == "open_bulk":
        btns = []
        for pref, label in Config.LABELS.items():
            count = await database.stocks_col.count_documents({"status": "ready", "uid": {"$regex": f"^{re.escape(pref)}"}})
            if count > 0:
                btns.append([InlineKeyboardButton(text=f"{label} - [ᴛᴇʀsᴇᴅɪᴀ {count} ᴀᴋᴜɴ]", callback_data=f"bulk_T_{pref}", icon_custom_emoji_id=extract_id(Config.box))])
                
        btns.append([InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ ᴜᴛᴀᴍᴀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))])
        bulk_text = f"<blockquote><b>{Config.box} 𝗠𝗘𝗡𝗨 𝗕𝗢𝗥𝗢𝗡𝗚𝗔𝗡</b>\n━━━━━━━━━━━━━━━━━━━━━\nsɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ᴋᴀᴛᴇɢᴏʀɪ ᴀᴋᴜɴ ʏᴀɴɢ ɪɴɢɪɴ ᴀɴᴅᴀ ʙᴏʀᴏɴɢ:</blockquote>"
        
        if query.message.photo: await query.message.edit_caption(caption=bulk_text, reply_markup=InlineKeyboardMarkup(btns))
        else: await query.message.edit_text(text=bulk_text, reply_markup=InlineKeyboardMarkup(btns))

    elif data.startswith("bulk_T_"):
        parts = data.split("_", 2)
        pref = parts[2]
        label = Config.LABELS.get(pref)
        
        all_ready = await database.stocks_col.find({"status": "ready", "is_sold": False, "uid": {"$regex": f"^{re.escape(pref)}"}}).to_list(length=None)
        if not all_ready:
            return await query.message.edit_text(
                text=f"<blockquote><b>{Config.peringatan} 𝗠𝗔𝗔𝗙 𝗕𝗢𝗦𝗞𝗨, 𝗦𝗧𝗢𝗞 𝗞𝗢𝗦𝗢𝗡𝗚!</b>\nsᴛᴏᴋ ᴜɴᴛᴜᴋ ᴋᴀᴛᴇɢᴏʀɪ ɪɴɪ sᴀᴀᴛ ɪɴɪ sᴇᴅᴀɴɢ ᴛɪᴅᴀᴋ ᴛᴇʀsᴇᴅɪᴀ.</blockquote>", 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ ʙᴏʀᴏɴɢᴀɴ", callback_data="open_bulk", icon_custom_emoji_id=extract_id(Config.kembali))]])
            )
            
        grouped = {}
        for s in all_ready:
            limit = s.get('limit', 'OFF').upper()
            dc_val = s.get('dc', '1')
            r_code = s.get("region_code", "DEFAULT")
            r_flag = extract_flag_only(s.get("region", ""))
            c_price = s.get("custom_price")
            
            key = f"{r_code}_{limit}_{dc_val}"
            if key not in grouped: grouped[key] = {"count":0, "flag": r_flag, "rcode": r_code, "lmt": limit, "dc": dc_val, "custom_price": c_price}
            grouped[key]["count"] += 1
            
        btns = []
        
        for k, v in sorted(grouped.items()):
            is_lmp = (v['lmt'] == "ON")
            tipe_name = "ʟɪᴍᴘᴇʀ" if is_lmp else "ɴᴏ ᴍɪɴᴜs"
            
            hrg = v["custom_price"] or Config.get_price(pref, v['dc'], v['rcode'], is_lmp)
            cb_data = f"bch_{'limp' if is_lmp else 'nom'}_{v['rcode']}_{pref}_{v['dc']}"
            
            flag_premium_id = extract_id(v['flag'])
            if flag_premium_id:
                btn_txt = f"{tipe_name} (DC {v['dc']}) | {v['count']} ᴀᴄᴄ | {format_rupiah(hrg)}"
                btns.append([InlineKeyboardButton(text=btn_txt, callback_data=cb_data, icon_custom_emoji_id=flag_premium_id)])
            else:
                clean_flag = re.sub(r'<[^>]+>', '', v['flag']).strip()
                btn_txt = f"{clean_flag} {tipe_name} (DC {v['dc']}) | {v['count']} ᴀᴄᴄ | {format_rupiah(hrg)}".strip()
                btns.append([InlineKeyboardButton(text=btn_txt, callback_data=cb_data)])
            
        btns.append([InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ", callback_data="open_bulk", icon_custom_emoji_id=extract_id(Config.kembali))])
        
        label_upper = label.upper() if label else ""
        await query.message.edit_text(
            text=f"<blockquote><b>{Config.box} 𝗕𝗢𝗥𝗢𝗡𝗚 {label_upper}</b>\n━━━━━━━━━━━━━━━━━━━━━\nᴘɪʟɪʜ ɴᴇɢᴀʀᴀ & ᴊᴇɴɪs ʏᴀɴɢ ɪɴɢɪɴ ᴅɪʙᴏʀᴏɴɢ ᴅᴀʀɪ ᴅᴀғᴛᴀʀ ᴅɪ ʙᴀᴡᴀʜ :</blockquote>",
            reply_markup=InlineKeyboardMarkup(btns)
        )

    elif data.startswith("abq_"):
        parts = data.split("_", 4)
        type_str, rcode, pref, dc_val = parts[1], parts[2], parts[3], parts[4]
        u_id = query.from_user.id
        user_states[u_id] = {"action": f"wbq_{type_str}_{rcode}_{pref}_{dc_val}"}
        
        try: await query.message.delete()
        except: pass
        
        await client.send_message(
            u_id,
            f"<blockquote><b>{Config.inputteks} ᴋᴇᴛɪᴋ ᴊᴜᴍʟᴀʜ ᴀᴋᴜɴ ʏᴀɴɢ ɪɴɢɪɴ ᴅɪʙᴇʟɪ:</b>\n\n"
            f"{Config.box} <b>Kᴀᴛᴇɢᴏʀɪ:</b> {Config.LABELS[pref]} (DC {dc_val} - {rcode})\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n{Config.catatan} <i>Cᴏɴᴛᴏʜ ᴘᴇɴᴜʟɪsᴀɴ: 15</i> (Tᴀɴᴘᴀ ʜᴜʀᴜғ/sᴘᴀsɪ)</blockquote>",
            reply_markup=ForceReply(selective=True)
        )
        
    elif data.startswith("buy_"):
        parts = data.split("_", 6)
        if len(parts) < 3: return
        mode = parts[1] 
        u_id = query.from_user.id
        
        # MENERIMA MODE "BLK" (Teks Biasa) DAN "SES" (File Session)
        if mode in ["BLK", "SES"]:
            type_str, rcode, pref, dc_val, qty = parts[2], parts[3], parts[4], parts[5], int(parts[6])
            is_limp = (type_str == "limp")
            limit_val = "ON" if is_limp else "OFF"
            
            stock_count = await database.stocks_col.count_documents({
                "status": "ready", "limit": limit_val, "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val
            })
            if stock_count < qty:
                return await query.answer(f"{Config.silang} Mᴀᴀꜰ, sᴛᴏᴋ ɪɴɪ sᴇᴅᴀɴɢ ᴅᴀʟᴀᴍ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴏʟᴇʜ ᴜsᴇʀ ʟᴀɪɴ!", show_alert=True)
            
            sample_stock = await database.stocks_col.find_one({"status": "ready", "limit": limit_val, "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val})
            price_each = sample_stock.get("custom_price") if sample_stock else 0
            if not price_each: price_each = Config.get_price(pref, dc_val, rcode, is_limp)
            
            initial_price = price_each * qty
            label_view = f"{Config.LABELS.get(pref)} (DC {dc_val} - {rcode}) [{qty} ᴀᴄᴄ]"
            
            payload_saldo = f"paySld_{mode}_{type_str}_{rcode}_{pref}_{dc_val}_{qty}"
            # Kita arahkan QR sama dengan logic lama (otomatis ditangani API payment lu)
            payload_qris = f"buyQR_{mode}_{type_str}_{rcode}_{pref}_{dc_val}_{qty}"
        else:
            sid = parts[2]
            from bson.objectid import ObjectId
            stok = await database.get_stock_by_id(sid)
            
            if not stok or stok.get("status") != "ready": 
                return await query.answer(f"{Config.silang} Mᴀᴀꜰ, sᴛᴏᴋ ɪɴɪ sᴇᴅᴀɴɢ ᴅᴀʟᴀᴍ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴏʟᴇʜ ᴜsᴇʀ ʟᴀɪɴ!", show_alert=True)
            
            is_limp = (stok.get('limit', 'OFF').upper() == "ON")
            pref = str(stok.get("uid"))[0]
            dc_val = stok.get("dc")
            rcode = stok.get("region_code", "DEFAULT")
            
            initial_price = stok.get("custom_price") or Config.get_price(pref, dc_val, rcode, is_limp)
            label_view = f"{Config.LABELS.get(pref)} (DC {dc_val} - {rcode})"
            
            payload_saldo = f"paySld_S_{sid}"
            payload_qris = f"buyQR_SGL_{sid}"

        user_data, _ = await database.get_user(u_id)
        current_saldo = user_data.get("balance", 0)
        
        info_tambahan = " <i>(Format File .session)</i>" if mode == "SES" else ""

        text_pilih = (
            f"<blockquote><b>{Config.kredit} 𝗠𝗘𝗧𝗢𝗗𝗘 𝗕𝗔𝗬𝗔𝗥</b>\n\n"
            f"{Config.box} ᴘʀᴏᴅᴜᴋ   : <b>{label_view}</b>{info_tambahan}\n"
            f"{Config.harga} ᴛᴏᴛᴀʟ    : <code>{format_rupiah(initial_price)}</code>\n"
            f"{Config.saldouser} sᴀʟᴅᴏ ᴍᴜ : <code>{format_rupiah(current_saldo)}</code>\n\n"
            f"{Config.pin} sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ᴍᴇᴛᴏᴅᴇ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ:</blockquote>"
        )
        
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ʙᴀʏᴀʀ ᴠɪᴀ sᴀʟᴅᴏ", callback_data=payload_saldo, icon_custom_emoji_id=extract_id(Config.tumpukanuang))],
            [InlineKeyboardButton(text="ʙᴀʏᴀʀ ᴠɪᴀ ǫʀɪs", callback_data=payload_qris, icon_custom_emoji_id=extract_id(Config.bank))],
            [InlineKeyboardButton(text="ʙᴀᴛᴀʟᴋᴀɴ ᴏʀᴅᴇʀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.silang))]
        ])
        
        if query.message.photo: await query.message.edit_caption(caption=text_pilih, reply_markup=btns)
        else: await query.message.edit_text(text=text_pilih, reply_markup=btns)

    elif data.startswith("buyQR_"):
        parts = data.split("_")
        mode = parts[1]
        
        # Menerima baik BLK maupun SES
        if mode in ["BLK", "SES"]:
            type_str, rcode, pref, dc_val, qty = parts[2], parts[3], parts[4], parts[5], parts[6]
            payload_auto = f"pAut_{mode}_{type_str}_{rcode}_{pref}_{dc_val}_{qty}"
            payload_man = f"pMan_{mode}_{type_str}_{rcode}_{pref}_{dc_val}_{qty}"
        else:
            sid = parts[2]
            payload_auto = f"pAut_S_{sid}"
            payload_man = f"pMan_S_{sid}"

        text_pilih = f"<blockquote>{Config.kredit} <b>𝗣𝗜𝗟𝗜𝗛 𝗤𝗥𝗜𝗦</b>\n\n{Config.pin} sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ᴊᴇɴɪs ǫʀɪs ʏᴀɴɢ ɪɴɢɪɴ ᴀɴᴅᴀ ɢᴜɴᴀᴋᴀɴ:</blockquote>"
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs (ᴘᴀᴋᴀsɪʀ)", callback_data=payload_auto, icon_custom_emoji_id=extract_id(Config.belifast))],
            [InlineKeyboardButton(text="ǫʀɪs ᴍᴀɴᴜᴀʟ / ᴅᴀɴᴀ", callback_data=payload_man, icon_custom_emoji_id=extract_id(Config.bank))],
            [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]
        ])
        if query.message.photo: await query.edit_message_caption(caption=text_pilih, reply_markup=btns)
        else: await query.message.edit_text(text=text_pilih, reply_markup=btns)

    elif data.startswith("paySld_"):
        # AMANKAN IMPORT DI AWAL BIAR GAK CRASH / UNBOUND ERROR
        import io, zipfile, json, time
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        from bson.objectid import ObjectId

        parts = data.split("_", 6)
        mode = parts[1] 
        u_id = query.from_user.id
        
        # --- BLOK MODE PEMBELIAN ---
        if mode == "S":
            sid = parts[2]
            stocks = await database.stocks_col.find({"_id": ObjectId(sid), "status": "ready"}).to_list(length=1)
            qty = 1
            if not stocks:
                return await query.answer("sᴛᴏᴋ ᴛɪᴅᴀᴋ ᴛᴇʀsᴇᴅɪᴀ ᴀᴛᴀᴜ sᴜᴅᴀʜ ᴛᴇʀᴊᴜᴀʟ!", show_alert=True)
            
            is_limp = (stocks[0].get("limit", "OFF") == "ON")
            price_each = stocks[0].get("custom_price") or Config.get_price(str(stocks[0]["uid"])[0], stocks[0].get("dc"), stocks[0].get("region_code", "DEFAULT"), is_limp)
            total_harga = price_each
            mode_is_ses = False
            limit_val = "ON" if is_limp else "OFF"
            
        elif mode in ["B", "BLK", "SES"]:
            type_str, rcode, pref, dc_val, qty = parts[2], parts[3], parts[4], parts[5], int(parts[6])
            is_limp = (type_str == "limp")
            limit_val = "ON" if is_limp else "OFF"
                                   
            stocks = await database.stocks_col.find({
                "status": "ready", "is_sold": False, "limit": limit_val,
                "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val
            }).limit(qty).to_list(length=None)
            
            if len(stocks) < qty:
                return await query.answer(f"sᴛᴏᴋ ᴋᴜʀᴀɴɢ! ᴛᴇʀsɪsᴀ {len(stocks)} ᴀᴋᴜɴ.", show_alert=True)
                
            price_each = stocks[0].get("custom_price") or Config.get_price(pref, dc_val, rcode, is_limp)
            total_harga = price_each * qty
            mode_is_ses = (mode == "SES")
        else:
            return await query.answer("ғᴏʀᴍᴀᴛ ᴅᴀᴛᴀ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴛɪᴅᴀᴋ ᴠᴀʟɪᴅ!", show_alert=True)
            
        # VALIDASI SALDO STRICT ANTI BOCOR
        user_data, _ = await database.get_user(u_id)
        current_balance = user_data.get("balance", 0)
        
        if current_balance < total_harga:
            try: await query.message.delete()
            except: pass
            kurang = total_harga - current_balance
            pesan_gagal = (
                f"<blockquote>{Config.silang} <b>𝗦𝗔𝗟𝗗𝗢 𝗧𝗜𝗗𝗔𝗞 𝗠𝗘𝗡𝗖𝗨𝗞𝗨𝗣𝗜</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
                f"{Config.harga} ʜᴀʀɢᴀ {qty} ᴀᴋᴜɴ : <code>ʀᴘ {total_harga:,}</code>\n"
                f"{Config.saldouser} sᴀʟᴅᴏ ᴀɴᴅᴀ  : <code>ʀᴘ {current_balance:,}</code>\n"
                f"{Config.peringatan} ᴋᴇᴋᴜʀᴀɴɢᴀɴ  : <code>ʀᴘ {kurang:,}</code>\n\n"
                f"<i>sɪʟᴀʜᴋᴀɴ ʟᴀᴋᴜᴋᴀɴ ᴅᴇᴘᴏsɪᴛ sᴀʟᴅᴏ ᴛᴇʀʟᴇʙɪʜ ᴅᴀʜᴜʟᴜ.</i></blockquote>".replace(",", ".")
            )
            return await client.send_message(
                chat_id=u_id, text=pesan_gagal, 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💰 𝗗𝗲𝗽𝗼𝘀𝗶𝘁 𝗦𝗮𝗹𝗱𝗼", callback_data="deposit_menu")], [InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data="back_home")]])
            )
        
        success_deduct = await database.deduct_balance(u_id, total_harga)
        if not success_deduct: return await query.answer("ɢᴀɢᴀʟ ᴍᴇᴍᴏᴛᴏɴɢ sᴀʟᴅᴏ!", show_alert=True)
        
        msg = await query.message.edit_text(
            f"<blockquote><b>{Config.loading} 𝗠𝗘𝗠𝗣𝗥𝗢𝗦𝗘𝗦 𝗣𝗘𝗠𝗕𝗘𝗟𝗜𝗔𝗡 {qty} 𝗔𝗞𝗨𝗡...</b>\n━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>sᴀʟᴅᴏ ᴅɪᴘᴏᴛᴏɴɢ sᴇᴍᴇɴᴛᴀʀᴀ ʀᴘ {total_harga:,}. ʙᴏᴛ sᴇᴅᴀɴɢ ᴍᴇʟᴀᴋᴜᴋᴀɴ ʟɪᴠᴇ ᴄʜᴇᴄᴋ ᴋᴇ sᴇʀᴠᴇʀ ᴛᴇʟᴇɢʀᴀᴍ ᴜɴᴛᴜᴋ ᴍᴇᴍᴀsᴛɪᴋᴀɴ sᴇᴍᴜᴀ sᴇssɪᴏɴ ᴀᴋᴛɪғ. ʜᴀʀᴀᴘ ᴛᴜɴɢɢᴜ...</i></blockquote>".replace(",", ".")
        )
        
        sesi_sukses = []
        sesi_cacat = []
        
        # PROSES CEK SESI (LIVE CHECK)
        for s in stocks:
            is_alive = False
            telethon_string = s.get("session")
            t_client = TelegramClient(StringSession(telethon_string), Config.API_ID, Config.API_HASH)
            
            try:
                await t_client.connect()
                if await t_client.is_user_authorized():
                    is_alive = True
            except Exception:
                pass
            finally:
                if t_client.is_connected():
                    await t_client.disconnect()
                    
            if is_alive:
                sesi_sukses.append(s)
                await database.stocks_col.update_one(
                    {"_id": s["_id"]}, 
                    {"$set": {"is_sold": True, "status": "sold", "buyer_id": u_id, "buy_date": int(time.time())}}
                )
            else:
                sesi_cacat.append(s)
                await database.stocks_col.update_one(
                    {"_id": s["_id"]}, 
                    {"$set": {"status": "mati", "is_sold": False}}
                )
                
        jumlah_cacat = len(sesi_cacat)
        uang_refund = jumlah_cacat * price_each
        if uang_refund > 0: await database.add_user_balance(u_id, uang_refund)
        saldo_akhir = (current_balance - total_harga) + uang_refund
        jumlah_sukses = len(sesi_sukses)
        
        if jumlah_sukses == 0:
            return await msg.edit_text(f"<blockquote><b>{Config.silang} 𝗣𝗘𝗠𝗕𝗘𝗟𝗜𝗔𝗡 𝗚𝗔𝗚𝗔𝗟 𝗧𝗢𝗧𝗔𝗟!</b>\nsᴇᴍᴜᴀ {qty} sᴇsɪ ʏᴀɴɢ ᴅɪᴄᴇᴋ ᴍᴀᴛɪ/ᴄᴀᴄᴀᴛ. sᴀʟᴅᴏ ᴀɴᴅᴀ ʀᴘ {total_harga:,} ᴛᴇʟᴀʜ ᴅɪ-ʀᴇғᴜɴᴅ 100% ᴜᴛᴜʜ.</blockquote>".replace(",", "."))
            
        tipe_akun = "Limper" if limit_val == "ON" else "No Minus"
        refund_teks = f"\n{Config.peringatanseru} <b>ᴀᴜᴛᴏ-ʀᴇғᴜɴᴅ:</b> ʀᴘ {uang_refund:,} ({jumlah_cacat} sᴇsɪ ᴍᴀᴛɪ)" if jumlah_cacat > 0 else ""
            
        struk_text = (
            f"<blockquote><b>{Config.centanghijau} 𝗣𝗘𝗠𝗕𝗘𝗟𝗜𝗔𝗡 𝗕𝗘𝗥𝗛𝗔𝗦𝗜𝗟!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.struk} <b>ʀɪɴᴄɪᴀɴ ᴛʀᴀɴsᴀᴋsɪ:</b>\n"
            f"• ɪᴛᴇᴍ : <b>ᴀᴋᴜɴ {tipe_akun}</b>\n"
            f"• ᴅɪᴍɪɴᴛᴀ: <b>{qty} sᴇsɪ</b>\n"
            f"• sᴜᴋsᴇs : <b>{jumlah_sukses} sᴇsɪ</b> (ʜɪᴅᴜᴘ)\n"
            f"• ɢᴀɢᴀʟ  : <b>{jumlah_cacat} sᴇsɪ</b> (ᴍᴀᴛɪ){refund_teks}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{Config.saldouser} <b>sɪsᴀ sᴀʟᴅᴏ: ʀᴘ {saldo_akhir:,}</b>\n\n"
            f"👇 <i>sɪʟᴀʜᴋᴀɴ ᴄᴇᴋ ᴏʀᴅᴇʀ ᴀɴᴅᴀ ᴅɪ ʙᴀᴡᴀʜ.</i></blockquote>"
        ).replace(",", ".")
        
        btns_success = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ʙᴜᴋᴀ ᴏʀᴅᴇʀ sᴀʏᴀ", callback_data="my_orders", icon_custom_emoji_id=extract_id(Config.box))]
        ])       
        await msg.edit_text(text=struk_text, reply_markup=btns_success)


        if mode_is_ses:
            await client.send_message(
                chat_id=u_id, 
                text=f"<blockquote><b>{Config.folder} 𝗠𝗘𝗡𝗚𝗜𝗥𝗜𝗠𝗞𝗔𝗡 𝗙𝗜𝗟𝗘 𝗭𝗜𝗣 𝗦𝗘𝗦𝗦𝗜𝗢𝗡...</b>\nᴍᴏʜᴏɴ ᴛᴜɴɢɢᴜ sᴇʙᴇɴᴛᴀʀ, ғɪʟᴇ sᴇsɪ & ᴊsᴏɴ sᴇᴅᴀɴɢ ᴅɪ-ᴘᴀᴄᴋɪɴɢ ᴍᴇɴᴊᴀᴅɪ sᴀᴛᴜ ʙᴜɴᴅʟᴇ ᴢɪᴘ...</blockquote>"
            )
            
            import os
            from telethon.sessions import StringSession, SQLiteSession
            
            zip_buffer = io.BytesIO()
            zip_buffer.name = f"Bundle_{jumlah_sukses}_Akun_{int(time.time())}.zip"
            rekap_txt = f"--- BUNDLE {len(sesi_sukses)} AKUN ---\n\n"
            
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for idx, akun in enumerate(sesi_sukses, 1):
                    # FIX: PASTIKAN SELALU ADA + DI DEPAN NOMOR UNTUK ZIP
                    phone_raw = str(akun.get('phone', f'Akun_{idx}'))
                    if phone_raw.isdigit(): phone_str = f"+{phone_raw}"
                    elif not phone_raw.startswith('+') and not phone_raw.startswith('Akun'): phone_str = f"+{phone_raw}"
                    else: phone_str = phone_raw

                    uid = akun.get('uid', 0)
                    pwd = str(akun.get('password', ''))
                    session_data = akun.get('session', '')
                    is_limit = akun.get('limit', 'OFF')
                    first_name = akun.get('first_name', 'Edn')
                    
                    # ========================================================
                    # MEGA FIX: CONVERT STRING SESSION -> SQLITE ASLI
                    # Biar file .session bener-bener bisa di /addzip lagi
                    # ========================================================
                    try:
                        if isinstance(session_data, bytes):
                            session_data = session_data.decode('utf-8')
                            
                        # 1. Parse Telethon String
                        parsed_session = StringSession(session_data)
                        
                        # 2. Bikin file .session (SQLite) sementara di VPS
                        temp_db_name = f"temp_{phone_str}_{int(time.time())}.session"
                        
                        sql_session = SQLiteSession(temp_db_name)
                        sql_session.set_dc(parsed_session.dc_id, parsed_session.server_address, parsed_session.port)
                        sql_session.auth_key = parsed_session.auth_key
                        sql_session.save()
                        sql_session.close()
                        
                        # 3. Baca db sqlite-nya ke dalam format bytes
                        with open(temp_db_name, "rb") as db_file:
                            valid_sqlite_bytes = db_file.read()
                            
                        # 4. Tulis ke dalam ZIP
                        zip_file.writestr(f"{phone_str}.session", valid_sqlite_bytes)
                        
                        # 5. Hapus file sementaranya biar VPS lu ga nyampah!
                        if os.path.exists(temp_db_name):
                            os.remove(temp_db_name)
                    except Exception as convert_err:
                        print(f"⚠️ [WARNING] Gagal convert ke SQLite untuk {phone_str}: {convert_err}")
                        # Fallback aman kalo error convert
                        if isinstance(session_data, str):
                            zip_file.writestr(f"{phone_str}_string.session", session_data.encode('utf-8'))
                        else:
                            zip_file.writestr(f"{phone_str}_string.session", session_data)
                    # ========================================================
                        
                    json_data = {
                        "session_file": phone_str,
                        "phone": phone_str,
                        "user_id": int(uid) if str(uid).isdigit() else uid,
                        "app_id": 2040,
                        "app_hash": "b18441a1ff607e10a989891a5462e627",
                        "sdk": "Windows 11 x64",
                        "app_version": "6.3.6 x64",
                        "device": "ASUS TUF Gaming A15",
                        "device_token": None,
                        "device_token_secret": None,
                        "device_secret": None,
                        "signature": None,
                        "certificate": None,
                        "safetynet": None,
                        "perf_cat": 2,
                        "tz_offset": 23400,
                        "register_time": int(time.time()),
                        "last_check_time": int(time.time()),
                        "avatar": "img/default.png",
                        "first_name": first_name,
                        "last_name": None,
                        "username": None,
                        "sex": 0,
                        "lang_code": "en",
                        "system_lang_code": "en-US",
                        "lang_pack": "tdesktop",
                        "twoFA": pwd,
                        "proxy": None,
                        "ipv6": False,
                        "module": "AddAccount",
                        "program": "Telegram.org",
                        "work": 0
                    }
                    zip_file.writestr(f"{phone_str}.json", json.dumps(json_data, indent=2))
                    rekap_txt += f"[{idx}] ɴᴏ: {phone_str} | ᴜɪᴅ: {uid} | 2ғᴀ: {pwd} | ʟɪᴍɪᴛ: {is_limit}\n"
                
                zip_file.writestr("detail_akun.txt", rekap_txt)
            
            zip_buffer.seek(0)
            
    elif data.startswith("pAut_BLK_") or data.startswith("pAut_SES_") or data.startswith("pMan_BLK_") or data.startswith("pMan_SES_") or data.startswith("pAut_S_") or data.startswith("pMan_S_"):
        # AMANKAN SEMUA IMPORT DISINI BIAR GAK ERROR UNBOUND LOCAL
        import random, asyncio
        from datetime import datetime
        from bson.objectid import ObjectId
        try:
            import pytz
            WIB = pytz.timezone('Asia/Jakarta')
        except: pass 

        u_id = query.from_user.id 
        is_auto = data.startswith("pAut_")
        parts = data.split("_", 6)
        mode = parts[1]
        
        # --- BLOK PEMBELIAN BORONGAN (BULK) ---
        if mode in ["BLK", "SES"]:
            type_str, rcode, pref, dc_val, qty = parts[2], parts[3], parts[4], parts[5], int(parts[6])
            is_limp = (type_str == "limp")
            limit_val = "ON" if is_limp else "OFF"
            sample_stock = await database.stocks_col.find_one({"status": "ready", "limit": limit_val, "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val})
            
            price_each = sample_stock.get("custom_price") if sample_stock else 0
            if not price_each: price_each = Config.get_price(pref, dc_val, rcode, is_limp)
            initial_price = price_each * qty
            
            label_name = f"{Config.LABELS.get(pref, pref)} (DC {dc_val} - {rcode}) [{qty} ᴀᴄᴄ]"
            
            if is_auto and initial_price < 50000:
                pesan_tolak = (
                    f"<blockquote><b>{Config.silang} 𝗠𝗜𝗡𝗜𝗠𝗔𝗟 𝗧𝗥𝗔𝗡𝗦𝗔𝗞𝗦𝗜 𝗤𝗥𝗜𝗦 𝗢𝗧𝗢𝗠𝗔𝗧𝗜𝗦</b>\n\n"
                    f"{Config.peringatan} ᴍɪɴɪᴍᴀʟ ᴛʀᴀɴsᴀᴋsɪ ᴠɪᴀ ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs ᴀᴅᴀʟᴀʜ <b>ʀᴘ 50.000</b>.\n"
                    f"ᴛᴏᴛᴀʟ ʙᴇʟᴀɴᴊᴀ ᴀɴᴅᴀ: <b>{format_rupiah(initial_price)}</b>\n\n"
                    f"{Config.pin} sɪʟᴀᴋᴀɴ ɢᴜɴᴀᴋᴀɴ ᴍᴇᴛᴏᴅᴇ <b>{Config.bank} ǫʀɪs ᴍᴀɴᴜᴀʟ</b> ᴜɴᴛᴜᴋ ɴᴏᴍɪɴᴀʟ ɪɴɪ!</blockquote>"
                )
                btns_tolak = InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]])
                if query.message.photo: return await query.edit_message_caption(caption=pesan_tolak, reply_markup=btns_tolak)
                return await query.message.edit_text(text=pesan_tolak, reply_markup=btns_tolak)

            available_stocks = await database.stocks_col.find({
                "status": "ready", "limit": limit_val, "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val
            }).to_list(length=qty)
            
            if len(available_stocks) < qty:
                return await query.answer(f"{Config.silang} ᴍᴀᴀғ, sᴛᴏᴋ ɪɴɪ sᴇᴅᴀɴɢ ᴅᴀʟᴀᴍ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴏʟᴇʜ ᴜsᴇʀ ʟᴀɪɴ!", show_alert=True)
                
            if is_auto:
                oid_request = f"AUTO{random.randint(100,999)}{int(time.time())}"
                stock_ids = [s["_id"] for s in available_stocks]
                await database.stocks_col.update_many({"_id": {"$in": stock_ids}}, {"$set": {"status": f"pending_{oid_request}"}})
                asyncio.create_task(auto_cancel_order(oid_request, u_id, client))
                sid_check = f"BULK-{oid_request}"
            else:
                sid_pass = f"BULKMAN-{int(time.time())}"
                stock_ids = [s["_id"] for s in available_stocks]
                await database.stocks_col.update_many({"_id": {"$in": stock_ids}}, {"$set": {"status": f"pending_{sid_pass}"}})
                asyncio.create_task(auto_cancel_order(sid_pass, u_id, client))

        # --- BLOK PEMBELIAN SINGLE (SATUAN) ---
        else:
            sid = parts[2]
            stok = await database.get_stock_by_id(sid)
            if not stok or stok.get("status") != "ready": 
                return await query.answer(f"{Config.silang} ᴍᴀᴀғ, sᴛᴏᴋ ɪɴɪ sᴇᴅᴀɴɢ ᴅᴀʟᴀᴍ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴏʟᴇʜ ᴜsᴇʀ ʟᴀɪɴ!", show_alert=True)
            
            is_limp = (stok.get('limit', 'OFF').upper() == "ON")
            pref = str(stok.get("uid"))[0]
            dc_val = stok.get("dc")
            rcode = stok.get("region_code", "DEFAULT")
            initial_price = stok.get("custom_price") or Config.get_price(pref, dc_val, rcode, is_limp)
            label_name = f"{Config.LABELS.get(pref)} (DC {dc_val} - {rcode})"
            
            if is_auto and initial_price < 50000:
                pesan_tolak = (
                    f"<blockquote><b>{Config.silang} 𝗠𝗜𝗡𝗜𝗠𝗔𝗟 𝗧𝗥𝗔𝗡𝗦𝗔𝗞𝗦𝗜 𝗤𝗥𝗜𝗦 𝗢𝗧𝗢𝗠𝗔𝗧𝗜𝗦</b>\n\n"
                    f"{Config.peringatan} ᴍɪɴɪᴍᴀʟ ᴛʀᴀɴsᴀᴋsɪ ᴠɪᴀ ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs ᴀᴅᴀʟᴀʜ <b>ʀᴘ 50.000</b>.\n"
                    f"ᴛᴏᴛᴀʟ ʙᴇʟᴀɴᴊᴀ ᴀɴᴅᴀ: <b>{format_rupiah(initial_price)}</b>\n\n"
                    f"{Config.pin} sɪʟᴀᴋᴀɴ ɢᴜɴᴀᴋᴀɴ ᴍᴇᴛᴏᴅᴇ <b>{Config.bank} ǫʀɪs ᴍᴀɴᴜᴀʟ</b> ᴜɴᴛᴜᴋ ɴᴏᴍɪɴᴀʟ ɪɴɪ!</blockquote>"
                )
                btns_tolak = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴍᴇɴᴜ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]
                ])
                if query.message.photo: return await query.edit_message_caption(caption=pesan_tolak, reply_markup=btns_tolak)
                return await query.message.edit_text(text=pesan_tolak, reply_markup=btns_tolak)

            if is_auto:
                oid_request = f"TRX{int(time.time())}"
                await database.stocks_col.update_one({"_id": ObjectId(sid)}, {"$set": {"status": f"pending_{oid_request}"}})
                asyncio.create_task(auto_cancel_order(oid_request, u_id, client))
                sid_check = sid
            else:
                sid_pass = f"SGLMAN-{sid}-{int(time.time())}"
                await database.stocks_col.update_one({"_id": ObjectId(sid)}, {"$set": {"status": f"pending_{sid_pass}"}})
                asyncio.create_task(auto_cancel_order(sid_pass, u_id, client))

        # --- BLOK PROSES KIRIM QRIS / INVOICE ---
        if is_auto:
            u_name = query.from_user.first_name
            await query.edit_message_caption(caption=f"<blockquote><b>{Config.loading} ᴍᴇɴɢʜᴀsɪʟᴋᴀɴ ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs ᴅᴀʀɪ sᴇʀᴠᴇʀ...</b></blockquote>")
            qr_img, final_price = await PaymentGateway.generate_qris(initial_price, oid_request)
            
            if not qr_img:
                if mode in ["BLK", "SES"]: 
                    await database.stocks_col.update_many({"status": f"pending_{oid_request}"}, {"$set": {"status": "ready"}})
                else: 
                    await database.stocks_col.update_one({"_id": ObjectId(sid)}, {"$set": {"status": "ready"}})
                
                return await query.answer(f"{Config.silang} ɢᴀᴛᴇᴡᴀʏ ᴘᴀᴋᴀsɪʀ ᴇʀʀᴏʀ ᴀᴛᴀᴜ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ!", show_alert=True)

            real_oid = qr_img.name.split("_")[1].split(".")[0]
            
            try: waktu_sekarang = datetime.now(WIB).strftime('%d/%m/%Y %H:%M')
            except: waktu_sekarang = datetime.now().strftime('%d/%m/%Y %H:%M')
                
            caption_pay = (
                f"<blockquote><b>{Config.struk} 𝗜 𝗡 𝗩 𝗢 𝗜 𝗖 𝗘   𝗢 𝗧 𝗢 𝗠 𝗔 𝗧 𝗜 𝗦</b>\n\n"
                f"{Config.oid} ᴏʀᴅᴇʀ ɪᴅ : <code>{real_oid}</code>\n"
                f"{Config.user} ᴘᴇᴍʙᴇʟɪ  : <b>{u_name}</b>\n"
                f"{Config.box} ᴘʀᴏᴅᴜᴋ   : <b>{label_name}</b>\n"
                f"{Config.harga} ᴛᴏᴛᴀʟ    : <code>{format_rupiah(final_price)}</code>\n"
                f"{Config.loading} ᴇxᴘɪʀᴇᴅ  : <b>10 ᴍᴇɴɪᴛ</b>\n"
                f"{Config.tanggal} ᴛᴀɴɢɢᴀʟ  : <b>{waktu_sekarang}</b>\n\n"
                f"{Config.pin} ᴄᴀʀᴀ ᴘᴇᴍʙᴀʏᴀʀᴀɴ:\n"
                f"1. sᴄᴀɴ ǫʀɪs ᴅɪ ᴀᴛᴀs.\n"
                f"2. ᴘᴀsᴛɪᴋᴀɴ ɴᴏᴍɪɴᴀʟ sᴇsᴜᴀɪ ᴛᴀɢɪʜᴀɴ.\n"
                f"3. ᴛʀᴀɴsᴀᴋsɪ ᴀᴋᴀɴ ᴅɪᴘʀᴏsᴇs ᴏᴛᴏᴍᴀᴛɪs.</blockquote>"
            )
            btns = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="ᴄᴇᴋ sᴛᴀᴛᴜs ʙᴀʏᴀʀ", callback_data=f"check_{real_oid}_{sid_check}", icon_custom_emoji_id=extract_id(Config.putar))], 
                [InlineKeyboardButton(text="ʙᴀᴛᴀʟᴋᴀɴ ᴏʀᴅᴇʀ", callback_data=f"cancel_{real_oid}", icon_custom_emoji_id=extract_id(Config.silang))]
            ])

            try: await query.message.delete()
            except: pass
            await client.send_photo(chat_id=u_id, photo=qr_img, caption=caption_pay, reply_markup=btns)
            
        else:
            u_name = query.from_user.first_name
            waiting_manual_proof[u_id] = {
                "sid": sid_pass, 
                "price": initial_price, 
                "product": label_name 
            }
            asyncio.create_task(auto_cancel_order(sid_pass, u_id, client))
            
            try: waktu_sekarang = datetime.now(WIB).strftime('%d/%m/%Y %H:%M')
            except: waktu_sekarang = datetime.now().strftime('%d/%m/%Y %H:%M')
                
            caption_pay = (
                f"<blockquote><b>{Config.struk} 𝗜 𝗡 𝗩 𝗢 𝗜 𝗖 𝗘   𝗠 𝗔 𝗡 𝗨 𝗔 𝗟</b>\n\n"
                f"{Config.user} ᴘᴇᴍʙᴇʟɪ  : <b>{u_name}</b>\n"
                f"{Config.box} ᴘʀᴏᴅᴜᴋ   : <b>{label_name}</b>\n"
                f"{Config.harga} ᴛᴏᴛᴀʟ    : <code>{format_rupiah(initial_price)}</code>\n"
                f"{Config.tanggal} ᴛᴀɴɢɢᴀʟ  : <b>{waktu_sekarang}</b>\n\n"
                f"{Config.pin} ɪɴsᴛʀᴜᴋsɪ ᴘᴇᴍʙᴀʏᴀʀᴀɴ:\n"
                f"1. sᴄᴀɴ ǫʀɪs ᴘᴀᴅᴀ ɢᴀᴍʙᴀʀ ᴅɪ ᴀᴛᴀs.\n"
                f"2. ᴛʀᴀɴsғᴇʀ ᴛᴇᴘᴀᴛ sᴇʙᴇsᴀʀ <code>{initial_price}</code>.\n"
                f"3. ᴋɪʀɪᴍ ғᴏᴛᴏ ʙᴜᴋᴛɪ ᴛʀᴀɴsғᴇʀ ᴋᴇ ᴄʜᴀᴛ ɪɴɪ sᴇᴋᴀʀᴀɴɢ ᴊᴜɢᴀ!\n\n"
                f"{Config.kredit} <b>DANA / E-Wallet :</b> <code>{Config.DANA_NUMBER}</code>\n"
                f"{Config.peringatan} ᴘᴇsᴀɴᴀɴ ᴀᴋᴀɴ ᴅɪᴠᴇʀɪғɪᴋᴀsɪ ᴍᴀɴᴜᴀʟ ᴏʟᴇʜ ᴀᴅᴍɪɴ.</blockquote>"
            )
            
            try: await query.message.delete()
            except: pass
                
            await client.send_photo(
                chat_id=u_id, 
                photo=Config.QRIS_MANUAL_URL, 
                caption=caption_pay, 
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="ʙᴀᴛᴀʟᴋᴀɴ ᴏʀᴅᴇʀ", callback_data=f"cancel_{sid_pass}", icon_custom_emoji_id=extract_id(Config.silang))]
                ])
            )

    elif data.startswith("accM_"):
        # AMANKAN IMPORT
        from datetime import datetime
        try:
            import pytz
            WIB = pytz.timezone('Asia/Jakarta')
        except: pass

        parts = data.split("_", 2)
        if len(parts) < 3: 
            return await query.answer(f"{Config.silang} ғᴏʀᴍᴀᴛ ᴄᴀʟʟʙᴀᴄᴋ ᴅᴀᴛᴀ ᴛɪᴅᴀᴋ ᴠᴀʟɪᴅ!", show_alert=True)
            
        target_id = int(parts[1])
        sid_pass = parts[2]
        
        await query.answer(f"{Config.centanghijau} ᴍᴇᴍᴘʀᴏsᴇs ᴀᴄᴄ & ᴍᴇɴɢɪʀɪᴍ ᴀᴋᴜɴ...", show_alert=False)

        try:
            b_user = await client.get_users(target_id)
            buyer_name = f"@{b_user.username}" if b_user.username else b_user.first_name
        except:
            buyer_name = f"ᴜsᴇʀ {target_id}"

        pending_stocks = await database.stocks_col.find({
            "status": {"$in": [f"verifying_{sid_pass}", f"pending_{sid_pass}"]}
        }).to_list(length=None)
        
        if not pending_stocks:
            try: await query.edit_message_caption(caption=f"{Config.silang} <b>ᴇʀʀᴏʀ:</b> ᴅᴀᴛᴀ sᴛᴏᴋ ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ᴀᴛᴀᴜ sᴜᴅᴀʜ ᴅɪᴘʀᴏsᴇs!")
            except: pass
            return

        total_harga_semua = 0
        categories = set()
        products = set()
        
        for item in pending_stocks:
            total_harga_semua += item.get("custom_price", 0)
            if "category" in item: categories.add(str(item["category"]))
            if "product" in item: products.add(str(item["product"]))
            else: products.add("ᴀᴋᴜɴ ɴᴏᴋᴛᴇʟ")

        prod_text = ", ".join(products) if products else "ᴀᴋᴜɴ ɴᴏᴋᴛᴇʟ"
        cat_text = ", ".join(categories) if categories else "-"
        
        try: waktu_tf = datetime.now(WIB).strftime('%d/%m/%Y %H:%M')
        except: waktu_tf = datetime.now().strftime('%d/%m/%Y %H:%M')

        caption_success = (
            f"<blockquote><b>{Config.centanghijau} 𝗧𝗥𝗔𝗡𝗦𝗔𝗞𝗦𝗜 𝗕𝗘𝗥𝗛𝗔𝗦𝗜𝗟 𝗗𝗜𝗞𝗢𝗡𝗙𝗜𝗥𝗠𝗔𝗦𝗜!</b>\n\n"
            f"{Config.user} ʙᴜʏᴇʀ : <b>{buyer_name}</b>\n"
            f"{Config.uid} ɪᴅ : <code>{target_id}</code>\n"
            f"{Config.box} ᴘʀᴏᴅᴜᴋ : <b>{prod_text}</b>\n"
            f"{Config.folder} ᴋᴀᴛᴇɢᴏʀɪ : <b>{cat_text}</b>\n"
            f"{Config.harga} ᴛᴏᴛᴀʟ ᴛғ : <code>{format_rupiah(total_harga_semua)}</code>\n"
            f"{Config.tanggal} ᴡᴀᴋᴛᴜ ᴛғ : <b>{waktu_tf}</b>\n\n"
            f"sɪsᴛᴇᴍ sᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏsᴇs ᴅᴀᴛᴀ ᴅᴀɴ ᴍᴇɴɢɪʀɪᴍ ɴᴏᴛɪғɪᴋᴀsɪ...</blockquote>"
        )

        try: await query.edit_message_caption(caption=caption_success)
        except: pass

        for item in pending_stocks:
            await database.mark_as_sold(item['_id'], target_id)

        if pending_stocks:
            try:
                sample_stok = pending_stocks[0]
                await Logger.log_buy_stok(
                    client=client, 
                    user_id=target_id, 
                    name=buyer_name, 
                    stok=sample_stok, 
                    oid=sid_pass, 
                    method="ǫʀɪs ᴍᴀɴᴜᴀʟ", 
                    qty=len(pending_stocks),
                    total_harga=total_harga_semua
                )
            except Exception as e: print(f"LOG ERROR: {e}")

        try: waiting_manual_proof.pop(target_id, None)
        except: pass

        try:
            await database.db.orders_col.update_many(
                {"$or": [{"oid": sid_pass}, {"user_id": target_id, "status": "pending"}]}, 
                {"$set": {"status": "PAID"}}
            )
        except Exception: pass

        success_text = (
            f"<blockquote><b>{Config.centanghijau} 𝗣𝗘𝗠𝗕𝗔𝗬𝗔𝗥𝗔𝗡 𝗗𝗜𝗧𝗘𝗥𝗜𝗠𝗔</b>\n\n"
            f"ᴘᴇᴍʙᴇʟɪᴀɴ <b>{len(pending_stocks)} ᴀᴋᴜɴ</b> ᴛᴇʟᴀʜ sᴜᴋsᴇs!\n\n"
            f"{Config.box} sɪʟᴀʜᴋᴀɴ ʙᴜᴋᴀ ᴍᴇɴᴜ <b>ᴏʀᴅᴇʀ sᴀʏᴀ</b> ᴅɪ ʜᴀʟᴀᴍᴀɴ ᴜᴛᴀᴍᴀ ᴜɴᴛᴜᴋ ᴍᴇʟɪʜᴀᴛ ᴅᴇᴛᴀɪʟ ᴀᴋᴜɴ.</blockquote>"
        )
        try:
            await client.send_message(
                chat_id=target_id, 
                text=success_text, 
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="ʙᴜᴋᴀ ᴏʀᴅᴇʀ sᴀʏᴀ", callback_data="my_orders", icon_custom_emoji_id=extract_id(Config.box))]
                ])
            )
        except Exception: pass

    elif data.startswith("decM_"):
        # AMANKAN IMPORT
        from datetime import datetime
        try:
            import pytz
            WIB = pytz.timezone('Asia/Jakarta')
        except: pass

        parts = data.split("_", 2)
        if len(parts) < 3: return
        target_id = int(parts[1])
        sid_pass = parts[2]
        
        await query.answer(f"{Config.silang} ᴍᴇɴᴏʟᴀᴋ ᴘᴇᴍʙᴀʏᴀʀᴀɴ...", show_alert=False)

        try:
            b_user = await client.get_users(target_id)
            buyer_name = f"@{b_user.username}" if b_user.username else b_user.first_name
        except:
            buyer_name = f"ᴜsᴇʀ {target_id}"

        pending_stocks = await database.stocks_col.find({
            "status": {"$in": [f"verifying_{sid_pass}", f"pending_{sid_pass}"]}
        }).to_list(length=None)

        total_harga_semua = sum(item.get("custom_price", 0) for item in pending_stocks)
        categories = ", ".join(set(str(item["category"]) for item in pending_stocks if "category" in item)) or "-"
        products = ", ".join(set(str(item["product"]) for item in pending_stocks if "product" in item)) or "ᴀᴋᴜɴ ɴᴏᴋᴛᴇʟ"
        
        try: waktu_tf = datetime.now(WIB).strftime('%d/%m/%Y %H:%M')
        except: waktu_tf = datetime.now().strftime('%d/%m/%Y %H:%M')

        caption_reject = (
            f"<blockquote><b>{Config.silang} 𝗣𝗘𝗠𝗕𝗔𝗬𝗔𝗥𝗔𝗡 𝗗𝗜𝗧𝗢𝗟𝗔𝗞 𝗢𝗟𝗘𝗛 𝗔𝗗𝗠𝗜𝗡</b>\n\n"
            f"{Config.user} ʙᴜʏᴇʀ : <b>{buyer_name}</b>\n"
            f"{Config.uid} ɪᴅ : <code>{target_id}</code>\n"
            f"{Config.box} ᴘʀᴏᴅᴜᴋ : <b>{products}</b>\n"
            f"{Config.folder} ᴋᴀᴛᴇɢᴏʀɪ : <b>{categories}</b>\n"
            f"{Config.harga} ᴛᴏᴛᴀʟ ᴛғ : <code>{format_rupiah(total_harga_semua)}</code>\n"
            f"{Config.tanggal} ᴡᴀᴋᴛᴜ ᴛғ : <b>{waktu_tf}</b>\n\n"
            f"sᴛᴏᴋ ᴛᴇʟᴀʜ ᴅɪᴋᴇᴍʙᴀʟɪᴋᴀɴ ᴋᴇ ᴇᴛᴀʟᴀsᴇ.</blockquote>"
        )

        try: await query.edit_message_caption(caption=caption_reject)
        except: pass

        await database.stocks_col.update_many(
            {"status": {"$in": [f"pending_{sid_pass}", f"verifying_{sid_pass}"]}}, 
            {"$set": {"status": "ready"}}
        )
        waiting_manual_proof.pop(target_id, None)
        
        try:
            fail_text = (
                f"<blockquote><b>{Config.silang} 𝗣𝗘𝗠𝗕𝗔𝗬𝗔𝗥𝗔𝗡 𝗗𝗜𝗧𝗢𝗟𝗔𝗞</b>\n\n"
                f"ᴍᴏʜᴏɴ ᴍᴀᴀғ, ʙᴜᴋᴛɪ ᴛʀᴀɴsғᴇʀ ᴀɴᴅᴀ ᴛɪᴅᴀᴋ ᴠᴀʟɪᴅ.\n\n"
                f"{Config.peringatan} sɪʟᴀʜᴋᴀɴ ᴏʀᴅᴇʀ ᴜʟᴀɴɢ ᴅᴀɴ ᴘᴀsᴛɪᴋᴀɴ ғᴏᴛᴏ ʙᴜᴋᴛɪ ᴛʀᴀɴsғᴇʀ ᴛᴇʀʟɪʜᴀᴛ ᴊᴇʟᴀs.</blockquote>"
            )
            await client.send_message(target_id, fail_text)
        except: pass


    elif data.startswith("accSC_"):
        parts = data.split("_", 2)
        if len(parts) < 3: return
        target_id = int(parts[1])
        sid = parts[2]
        proof_file_id = query.message.photo.file_id if query.message.photo else None
        
        sc_parts = sid.split("-")
        if len(sc_parts) < 3:
            return await query.answer(f"{Config.silang} Format OID Script Rusak!", show_alert=True)
            
        script_type = sc_parts[1]
        price = int(sc_parts[2])
        role_name = Config.SCRIPT_PRICES.get(script_type, {}).get("name", script_type)
        
        await query.answer(f"{Config.centanghijau} Memproses ACC Script...", show_alert=False)

        # --- AMBIL DATA BUYER SEBELUM EDIT CAPTION ---
        try:
            b_user = await client.get_users(target_id)
            buyer_name = f"@{b_user.username}" if b_user.username else b_user.first_name
        except:
            buyer_name = f"ᴜsᴇʀ {target_id}"

        try:
            from datetime import datetime
            import pytz
            waktu_tf = datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%d/%m/%Y %H:%M')
        except:
            from datetime import datetime
            waktu_tf = datetime.now().strftime('%d/%m/%Y %H:%M')

        caption_success = (
            f"<blockquote><b>{Config.centanghijau} ᴘᴇᴍʙᴀʏᴀʀᴀɴ sᴄʀɪᴘᴛ ᴅɪᴋᴏɴғɪʀᴍᴀsɪ!</b>\n\n"
            f"{Config.user} ʙᴜʏᴇʀ : <b>{buyer_name}</b>\n"
            f"{Config.uid} ɪᴅ : <code>{target_id}</code>\n"
            f"{Config.box} ᴘʀᴏᴅᴜᴋ : <b>sᴄʀɪᴘᴛ ʙᴏᴛ ({role_name})</b>\n"
            f"{Config.folder} ᴋᴀᴛᴇɢᴏʀɪ : <b>sᴄʀɪᴘᴛ ᴠɪᴘ</b>\n"
            f"{Config.harga} ᴛᴏᴛᴀʟ ᴛғ : <code>{format_rupiah(price)}</code>\n"
            f"{Config.tanggal} ᴡᴀᴋᴛᴜ ᴛғ : <b>{waktu_tf}</b>\n\n"
            f"sɪsᴛᴇᴍ sᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏsᴇs ᴅᴀᴛᴀ ᴅᴀɴ ᴍᴇɴɢɪʀɪᴍ ғɪʟᴇ ᴋᴇ ᴘᴇᴍʙᴇʟɪ...</blockquote>"
        )

        try:
            await query.edit_message_caption(caption=caption_success)
        except: pass
        
        await database.record_script_sale(target_id, script_type, price)
        await Logger.log_buy_script(client, target_id, buyer_name, role_name, price, proof_file_id)
        waiting_manual_proof.pop(target_id, None)

        success_text = (
            f"<blockquote><b>{Config.centanghijau} sᴄʀɪᴘᴛ sᴜᴋsᴇs ᴅɪ ᴋɪʀɪᴍ</b>\n\n"
            f"sɪʟᴀʜᴋᴀɴ ʙᴇʀɢᴀʙᴜɴɢ ᴋᴇ ɢʀᴜᴘ ɪɴɪ\n"
            f"{Config.pin} https://t.me/+f582KJNhZ4IxNjFl\n"
            f"ᴜɴᴛᴜᴋ ɪɴғᴏ ʟᴇʙɪʜ ʟᴀɴᴊᴜᴛ.\n\n"
            f"{Config.peringatan} <b>ᴘᴇʀɪɴɢᴀᴛᴀɴ: ᴡᴀᴊɪʙ ᴘᴀᴛᴜʜɪ sᴇᴍᴜᴀ ʀᴜʟᴇs ɪɴɪ</b>\n"
            f"𝟷. ᴅɪʟᴀʀᴀɴɢ sᴇʙᴀʀ sᴄ sᴇᴄᴀʀᴀ ғʀᴇᴇ\n"
            f"𝟸. ɴᴏ ʙᴛ/ᴛᴛ\n"
            f"𝟹. ᴊɪᴋᴀ ᴀᴅᴀ ᴀᴘᴀ-ᴀᴘᴀ ʙɪsᴀ ʟᴀɴɢsᴜɴɢ ʜᴜʙᴜɴɢɪ ᴀᴅᴍɪɴ ᴜᴛᴀᴍᴀ.</blockquote>"
        )
        try:
            await client.send_document(
                chat_id=target_id,
                document=Config.SCRIPT_ZIP_PATH,
                caption=success_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ʜᴏᴍᴇ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]
                ])
            )
        except Exception as e:
            logger.error(f"Gagal kirim zip script ke user: {e}")
            await client.send_message(target_id, f"{Config.silang} Terjadi kesalahan saat mengirim file zip.")

    elif data.startswith("decSC_"):
        parts = data.split("_", 2)
        if len(parts) < 3: return
        target_id = int(parts[1])
        sid = parts[2]
        
        await query.answer(f"{Config.silang} Menolak pembayaran script...", show_alert=False)

        # --- AMBIL DATA BUYER & SCRIPT DETAIL UNTUK CAPTION REJECT ---
        try:
            b_user = await client.get_users(target_id)
            buyer_name = f"@{b_user.username}" if b_user.username else b_user.first_name
        except:
            buyer_name = f"ᴜsᴇʀ {target_id}"

        sc_parts = sid.split("-")
        if len(sc_parts) >= 3:
            script_type = sc_parts[1]
            price = int(sc_parts[2])
            role_name = Config.SCRIPT_PRICES.get(script_type, {}).get("name", script_type)
            prod_text = f"sᴄʀɪᴘᴛ ʙᴏᴛ ({role_name})"
            price_text = format_rupiah(price)
        else:
            prod_text = "sᴄʀɪᴘᴛ ʙᴏᴛ"
            price_text = "-"

        try:
            from datetime import datetime
            import pytz
            waktu_tf = datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%d/%m/%Y %H:%M')
        except:
            from datetime import datetime
            waktu_tf = datetime.now().strftime('%d/%m/%Y %H:%M')

        caption_reject = (
            f"<blockquote><b>{Config.silang} ᴘᴇᴍʙᴀʏᴀʀᴀɴ sᴄʀɪᴘᴛ ᴅɪᴛᴏʟᴀᴋ</b>\n\n"
            f"{Config.user} ʙᴜʏᴇʀ : <b>{buyer_name}</b>\n"
            f"{Config.uid} ɪᴅ : <code>{target_id}</code>\n"
            f"{Config.box} ᴘʀᴏᴅᴜᴋ : <b>{prod_text}</b>\n"
            f"{Config.folder} ᴋᴀᴛᴇɢᴏʀɪ : <b>sᴄʀɪᴘᴛ ᴠɪᴘ</b>\n"
            f"{Config.harga} ᴛᴏᴛᴀʟ ᴛғ : <code>{price_text}</code>\n"
            f"{Config.tanggal} ᴡᴀᴋᴛᴜ ᴛғ : <b>{waktu_tf}</b>\n\n"
            f"ᴘᴇᴍʙᴀʏᴀʀᴀɴ sᴄʀɪᴘᴛ ᴛᴇʟᴀʜ ᴅɪᴛᴏʟᴀᴋ ᴏʟᴇʜ ᴀᴅᴍɪɴ.</blockquote>"
        )

        try:
            await query.edit_message_caption(caption=caption_reject)
        except: pass
        
        waiting_manual_proof.pop(target_id, None)
        
        try:
            await client.send_message(
                chat_id=target_id, 
                text=f"<blockquote><b>{Config.silang} <b>𝗣𝗘𝗠𝗕𝗔𝗬𝗔𝗥𝗔𝗡 𝗦𝗖𝗥𝗜𝗣𝗧 𝗗𝗜𝗧𝗢𝗟𝗔𝗞!</b></b>\nPᴀsᴛɪᴋᴀɴ ʙᴜᴋᴛɪ ᴛʀᴀɴsꜰᴇʀ ᴊᴇʟᴀs ᴅᴀɴ ɴᴏᴍɪɴᴀʟ sᴇsᴜᴀɪ ᴛᴀɢɪʜᴀɴ ᴀɢᴀʀ ᴅᴀᴘᴀᴛ ᴅɪᴠᴇʀɪꜰɪᴋᴀsɪ ᴀᴅᴍɪɴ.</blockquote>"
            )
        except: pass


    elif data.startswith("cancel_"):
        parts = data.split("_", 1)
        if len(parts) > 1:
            oid = parts[1]
            await database.stocks_col.update_many(
                {"status": f"pending_{oid}"}, 
                {"$set": {"status": "ready"}}
            )
            await query.answer(f"{Config.silang} ᴏʀᴅᴇʀ ᴛᴇʟᴀʜ ᴅɪʙᴀᴛᴀʟᴋᴀɴ", show_alert=True)
            try: await query.message.delete()
            except: pass
            await send_main_menu(client, chat_id, u_id)
            
    elif data.startswith("checkSC_"):
        parts = data.split("_", 3)
        if len(parts) < 4: return
        oid, script_type, price = parts[1], parts[2], int(parts[3])
        
        status_msg = await client.send_message(
            u_id, 
            f"<blockquote><b>{Config.cekdevice} ᴍᴇɴɢᴇᴄᴇᴋ ᴍᴜᴛᴀsɪ ᴅᴀɴᴀ ᴅɪ sᴇʀᴠᴇʀ ᴘᴀᴋᴀsɪʀ...</b>\nᴍᴏʜᴏɴ ᴛᴜɴɢɢᴜ sᴇʙᴇɴᴛᴀʀ ʙᴏsᴋᴜ.</blockquote>"
        )
        buyer_name = f"@{query.from_user.username}" if query.from_user.username else query.from_user.first_name
        
        is_paid = False
        for _ in range(4):
            if await PaymentGateway.is_confirmed(oid, price): 
                is_paid = True
                break
            await asyncio.sleep(2)
            
        if is_paid:
            try:
                await query.message.delete()
                await status_msg.delete()
            except: pass
            
            role_name = Config.SCRIPT_PRICES.get(script_type, {}).get("name", script_type)
            await database.record_script_sale(u_id, script_type, price)
            await Logger.log_buy_script(client, u_id, buyer_name, role_name, price)
            
            success_text = (
                f"<blockquote><b>{Config.centanghijau} sᴄʀɪᴘᴛ sᴜᴋsᴇs ᴅɪ ᴋɪʀɪᴍ</b>\n\n"
                f"sɪʟᴀʜᴋᴀɴ ʙᴇʀɢᴀʙᴜɴɢ ᴋᴇ ɢʀᴜᴘ ɪɴɪ\n"
                f"{Config.pin} https://t.me/+f582KJNhZ4IxNjFl\n"
                f"ᴜɴᴛᴜᴋ ɪɴғᴏ ʟᴇʙɪʜ ʟᴀɴᴊᴜᴛ.</blockquote>"
            )
            try:
                await client.send_document(
                    chat_id=u_id,
                    document=Config.SCRIPT_ZIP_PATH,
                    caption=success_text,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ʜᴏᴍᴇ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]
                    ])
                )
            except: 
                pass

        else:
            try: await status_msg.delete()
            except: pass
            await query.answer(f"{Config.peringatan} ᴘᴇᴍʙᴀʏᴀʀᴀɴ ʙᴇʟᴜᴍ ᴍᴀsᴜᴋ! Silakan coba lagi dalam 1 menit.", show_alert=True)

    elif data.startswith("check_"):
        parts = data.split("_", 2)
        if len(parts) < 3: return
        oid, sid_check = parts[1], parts[2]
        
        # Pastikan u_id terdefinisi di scope ini (opsional tapi sangat disarankan)
        u_id = query.from_user.id
        
        status_msg = await client.send_message(
            u_id, 
            f"<blockquote><b>{Config.cekdevice} ᴍᴇɴɢᴇᴄᴇᴋ ᴍᴜᴛᴀsɪ ᴅᴀɴᴀ ᴅɪ sᴇʀᴠᴇʀ ᴘᴀᴋᴀsɪʀ...</b>\nᴍᴏʜᴏɴ ᴛᴜɴɢɢᴜ sᴇʙᴇɴᴛᴀʀ ʙᴏsᴋᴜ.</blockquote>"
        )
        buyer_name = f"@{query.from_user.username}" if query.from_user.username else query.from_user.first_name
            
        is_paid = False
        for _ in range(4):
            if await PaymentGateway.is_confirmed(oid): 
                is_paid = True
                break
            await asyncio.sleep(2)

        if is_paid:
            try:
                await query.message.delete()
                await status_msg.delete()
            except: pass

            pending_stocks = await database.stocks_col.find({"status": f"pending_{oid}"}).to_list(length=None)
            if not pending_stocks: 
                return await client.send_message(u_id, f"{Config.silang} Mᴀᴀꜰ ʙᴏsᴋᴜ, ᴅᴀᴛᴀ ᴘᴇsᴀɴᴀɴ ᴛᴇʀsᴇʙᴜᴛ sᴜᴅᴀʜ ᴅɪᴘʀosᴇs!")
                
            for item in pending_stocks:
                await database.mark_as_sold(item['_id'], u_id)
            
            # --- FIX: AMBIL HARGA & QTY DARI DATABASE (ANTI CRASH / ANTI 0) ---
            harga_total_aman = sum(item.get("custom_price", 0) for item in pending_stocks)
            qty_aman = len(pending_stocks)
            
            # --- FIX: VARIABEL LOGGER ---
            await Logger.log_buy_stok(
                client=client, 
                user_id=u_id, 
                name=buyer_name, 
                stok=pending_stocks[0],  # Ambil data dari list array pertama
                oid=oid,                 # Gunakan oid dari split data
                method="ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs", 
                qty=qty_aman, 
                total_harga=harga_total_aman
            )
            
            success_text = (
                f"<blockquote><b>{Config.centanghijau} 𝗣𝗘𝗠𝗕𝗔𝗬𝗔𝗥𝗔𝗡 𝗕𝗘𝗥𝗛𝗔𝗦𝗜𝗟</b>\n\n"
                f"ᴘᴇᴍʙᴇʟɪᴀɴ <b>{qty_aman} ᴀᴋᴜɴ</b> ᴛᴇʟᴀʜ sᴜᴋsᴇs!\n\n"
                f"{Config.box} sɪʟᴀʜᴋᴀɴ ʙᴜᴋᴀ ᴍᴇɴᴜ <b>ᴏʀᴅᴇʀ sᴀʏᴀ</b>.</blockquote>"
            )
            await client.send_message(
                chat_id=u_id, 
                text=success_text, 
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="ʙᴜᴋᴀ ᴏʀᴅᴇʀ sᴀʏᴀ", callback_data="my_orders", icon_custom_emoji_id=extract_id(Config.box))]
                ])
            )

        else:
            try: await status_msg.delete()
            except: pass
            await query.answer(f"{Config.peringatan} ᴘᴇᴍʙᴀʏᴀʀᴀɴ ʙᴇʟᴜᴍ ᴍᴀsᴜᴋ! Silakan coba lagi.", show_alert=True)

    elif data == "my_orders":
        u_id = query.from_user.id
        orders = await database.stocks_col.find({
            "buyer_id": u_id, 
            "status": "sold", 
            "is_hidden": {"$ne": True}
        }).to_list(length=None)
        
        if not orders:
            text_empty = (
                f"<blockquote><b>{Config.box} 𝗠𝗘𝗡𝗨  𝗢𝗥𝗗𝗘𝗥  𝗦𝗔𝗬𝗔</b>\n\n"
                f"{Config.silang} Mᴀᴀꜰ ʙᴏsᴋᴜ, ᴀɴᴅᴀ ʙᴇʟᴜᴍ ᴍᴇᴍɪʟɪᴋɪ sᴛᴏᴋ ᴘᴇᴍʙᴇʟɪᴀɴ ᴀᴛᴀᴜ\n"
                f"sᴇᴍᴜᴀ ᴀᴋᴜɴ sᴜᴅᴀʜ ᴅɪʜᴀᴘᴜs sᴇsɪɴʏᴀ (ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴏʀᴅᴇʀ ᴀᴋᴛɪғ).</blockquote>"
            )
            btns_empty = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ʜᴏᴍᴇ", 
                    callback_data="back_home", 
                    icon_custom_emoji_id=extract_id(Config.kembali)
                )]
            ])
            try:
                if query.message.photo: 
                    return await query.message.edit_caption(caption=text_empty, reply_markup=btns_empty)
                else: 
                    return await query.message.edit_text(text=text_empty, reply_markup=btns_empty)
            except Exception:
                return await query.answer("Gagal memuat menu kosong.", show_alert=True)
        
        text = (
            f"<blockquote><b>{Config.box} 𝗠𝗘𝗡𝗨  𝗢𝗥𝗗𝗘𝗥  𝗦𝗔𝗬𝗔</b>\n\n"
            f"sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ʟᴏɢɪɴ sᴇsᴜᴀɪ sᴛᴏᴋ ʏᴀɴɢ\n"
            f"sᴜᴅᴀʜ ᴋᴀᴍᴜ ᴘɪʟɪʜ ᴅɪ ʙᴀᴡᴀʜ:</blockquote>"
        )
        
        btns = []
        for o in orders:
            label = o.get('label', 'Unknown')
            phone = o.get('phone', 'NoPhone')
            btns.append([InlineKeyboardButton(
                text=f"{label} {phone}", 
                callback_data=f"ord_det_{o['_id']}", 
                icon_custom_emoji_id=extract_id(Config.bulattitik)
            )])
            
        btns.append([InlineKeyboardButton(
            text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ʜᴏᴍᴇ", 
            callback_data="back_home", 
            icon_custom_emoji_id=extract_id(Config.kembali)
        )])

        if query.message.photo: 
            await query.message.edit_caption(caption=text, reply_markup=InlineKeyboardMarkup(btns))
        else: 
            await query.message.edit_text(text=text, reply_markup=InlineKeyboardMarkup(btns))


    elif data.startswith("ord_det_"):
        sid = data.split("_")[2]
        stok = await database.get_stock_by_id(sid)
        if not stok: return await query.answer(f"{Config.silang} Stok tidak ditemukan di server!", show_alert=True)
        
        text = (
            f"<blockquote><b>{Config.box} 𝗗𝗘𝗧𝗔𝗜𝗟 𝗦𝗧𝗢𝗞</b>\n\n"
            f"{Config.id} ɪᴅ ᴀᴋᴜɴ : <code>{stok.get('uid', '-')}</code>\n"
            f"{Config.uid} ʟᴀʙᴇʟ ɪᴅ : <code>{stok.get('label', '-')}</code>\n"
            f"{Config.nomer} ɴᴏᴍᴏʀ ɴʏᴀ : <code>{stok.get('phone', '-')}</code>\n"
            f"{Config.gembok} ᴘᴡ ɴʏᴀ : <code>{stok.get('password', '-')}</code>\n\n"
            f"sɪʟᴀʜᴋᴀɴ ʟᴏɢɪɴ ᴅᴀɴ ᴍɪɴᴛᴀ ᴏᴛᴘ ᴅɪ ʙᴀᴡᴀʜ</blockquote>"
        )
        
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ᴍɪɴᴛᴀ ᴏᴛᴘ ᴛᴇʟᴇɢʀᴀᴍ", callback_data=f"getotp_{sid}", icon_custom_emoji_id=extract_id(Config.pesansurat))],
            [InlineKeyboardButton(text="ʜᴀᴘᴜs sᴇssɪᴏɴ", callback_data=f"delsess_{sid}", icon_custom_emoji_id=extract_id(Config.hapus))],
            [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴏʀᴅᴇʀ sᴀʏᴀ", callback_data="my_orders", icon_custom_emoji_id=extract_id(Config.kembali))]
        ])

        
        try: await query.message.edit_text(text, reply_markup=btns)
        except: await client.send_message(u_id, text, reply_markup=btns)

    elif data.startswith("getotp_"):
        parts = data.split("_", 1)
        if len(parts) < 2: return
        sid = parts[1]
        
        await query.answer("Mengambil OTP dari server Telegram pusat...", show_alert=False)
        stok = await database.get_stock_by_id(sid)
        if not stok or not stok.get("session"): 
            return await query.answer(f"{Config.silang} Sesi tidak ditemukan di Database! Pastikan Anda belum menghapusnya.", show_alert=True)

        current_markup = query.message.reply_markup

        base_text = (
            f"<blockquote><b>{Config.box} 𝗗𝗘𝗧𝗔𝗜𝗟 𝗦𝗧𝗢𝗞</b>\n\n"
            f"{Config.id} ɪᴅ ᴀᴋᴜɴ : <code>{stok.get('uid', '-')}</code>\n"
            f"{Config.uid} ʟᴀʙᴇʟ ɪᴅ : <code>{stok.get('label', '-')}</code>\n"
            f"{Config.nomer} ɴᴏᴍᴏʀ ɴʏᴀ : <code>{stok.get('phone', '-')}</code>\n"
            f"{Config.gembok} ᴘᴡ ɴʏᴀ : <code>{stok.get('password', '-')}</code>\n\n"
        )

        await query.message.edit_text(base_text + f"<b>{Config.antena} ᴍᴇɴɢʜᴜʙᴜɴɢᴋᴀɴ ᴋᴇ sᴇʀᴠᴇʀ ᴛᴇʟᴇɢʀᴀᴍ...</b></blockquote>", reply_markup=current_markup)
        
        t_client = TelegramClient(StringSession(stok["session"]), Config.API_ID, Config.API_HASH)
        try:
            await t_client.connect()
            if not await t_client.is_user_authorized(): 
                return await query.message.edit_text(base_text + f"<b>{Config.silang} sᴇsɪ ᴍᴀᴛɪ ᴀᴛᴀᴜ sᴜᴅᴀʜ ᴅɪʟᴏɢᴏᴜᴛ ᴅᴀʀɪ ᴘᴇʀᴀɴɢᴋᴀᴛ ʟᴀɪɴ!</b></blockquote>", reply_markup=current_markup)
                
            messages = await t_client.get_messages(777000, limit=3)
            otp_text = None
            for m in messages:
                if m.message and any(k in m.message.lower() for k in ["code", "kode", "login"]):
                    otp_text = m.message
                    break
            
            if otp_text: 
                await query.message.edit_text(base_text + f"<b>{Config.pesansurat} 𝗜 𝗡 𝗕 𝗢 𝗫 :</b>\n\n<code>{otp_text}</code></blockquote>", reply_markup=current_markup)
            else: 
                await query.message.edit_text(base_text + f"<b>{Config.peringatan} ʙᴇʟᴜᴍ ᴀᴅᴀ ᴏᴛᴘ (777000) ʏᴀɴɢ ᴍᴀsᴜᴋ.</b>\nᴛᴜɴɢɢᴜ ʙᴇʙᴇʀᴀᴘᴀ ᴅᴇᴛɪᴋ ᴅᴀɴ ᴋʟɪᴋ ᴛᴏᴍʙᴏʟɴʏᴀ ʟᴀɢɪ.</blockquote>", reply_markup=current_markup)
        except FloodWait as e:
            await query.message.edit_text(base_text + f"<b>{Config.peringatan} ᴛᴇʀʟᴀʟᴜ ʙᴀɴʏᴀᴋ ᴘᴇʀᴍɪɴᴛᴀᴀɴ ᴏᴛᴘ!</b> ᴛᴜɴɢɢᴜ <code>{e.value}</code> ᴅᴇᴛɪᴋ ᴜɴᴛᴜᴋ ᴍᴇɴᴄᴏʙᴀ ʟᴀɢɪ.</blockquote>", reply_markup=current_markup)
        except Exception as e: 
            logger.error(f"Error fetching OTP: {e}")
            await query.message.edit_text(base_text + f"<b>{Config.silang} ɢᴀɢᴀʟ ᴍᴇɴɢᴀᴍʙɪʟ ᴏᴛᴘ ᴋᴀʀᴇɴᴀ sɪsᴛᴇᴍ ᴇʀʀᴏʀ:</b>\n{e}</blockquote>", reply_markup=current_markup)
        finally:
            if t_client.is_connected(): 
                await t_client.disconnect()

    elif data.startswith("delsess_") and "confirm" not in data:
        sid = data.split("_")[1]
        text_warn = (
            f"<blockquote><b>{Config.peringatan} 𝗣 𝗘 𝗥 𝗜 𝗡 𝗚 𝗔 𝗧 𝗔 𝗡</b>\n\n"
            f"ᴀɴᴅᴀ ʏᴀᴋɪɴ ᴜɴᴛᴜᴋ ʟᴏɢᴏᴜᴛ ᴘᴇʀᴀɴɢᴋᴀᴛ ʙᴏᴛ ɪɴɪ? ᴊɪᴋᴀ sᴜᴅᴀʜ ʏᴀᴋɪɴ ᴅᴀɴ ᴛᴇʀʟᴏɢᴏᴜᴛ ᴍᴀᴋᴀ ᴀᴋᴜɴ sᴜᴅᴀʜ ʙᴜᴋᴀɴ ᴛᴀɴɢɢᴜɴɢ ᴊᴀᴡᴀʙ ᴀᴅᴍɪɴ ʟᴀɢɪ</blockquote>"
        )
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ʏᴀᴋɪɴ", callback_data=f"delsess_confirm_{sid}", icon_custom_emoji_id=extract_id(Config.centanghijau))], 
            [InlineKeyboardButton(text="ʙᴀᴛᴀʟ", callback_data="del_msg", icon_custom_emoji_id=extract_id(Config.silang))]
        ])
        
        await client.send_message(u_id, text=text_warn, reply_markup=btns)

    elif data == "del_msg":
        try: await query.message.delete()
        except: pass

    elif data.startswith("delsess_confirm_"):
        sid = data.split("_")[2]
        from bson.objectid import ObjectId
        stok = await database.get_stock_by_id(sid)
        
        if stok and stok.get("session"):
            await query.answer("Menghapus session dari server Telegram...", show_alert=False)
            asyncio.create_task(perform_bot_logout(stok["session"], u_id))
            
        await database.stocks_col.update_one({"_id": ObjectId(sid)}, {"$set": {"is_hidden": True}})

        text_done = (
            f"<blockquote><b>{Config.centanghijau} 𝗦 𝗨 𝗞 𝗦 𝗘 𝗦</b>\n\n"
            f"ʙᴏᴛ ʙᴇʀʜᴀsɪʟ ᴍᴇʟᴇᴘᴀs sᴇsɪᴏɴ ᴀᴋᴜɴ ᴛᴇʀsᴇʙᴜᴛ, ʙᴏᴛ sᴜᴅᴀʜ ᴛɪᴅᴀᴋ ʙɪsᴀ ᴍᴇɴɢᴀᴍʙɪʟ ᴏᴛᴘ, ᴊɪᴋᴀ ᴋᴀᴍᴜ sᴜᴅᴀʜ ʟᴏɢᴏᴜᴛ ᴛᴀᴘɪ ʙᴇʟᴜᴍ ʟᴏɢɪɴ, ᴍᴀᴋᴀ ɪᴛᴜ ʙᴜᴋᴀɴ ᴛᴀɴɢɢᴜɴɢ ᴊᴀᴡᴀʙ ᴀᴅᴍɪɴ</blockquote>"
        )
        btns = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ʜᴏᴍᴇ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali)), 
                InlineKeyboardButton(text="ᴏʀᴅᴇʀ sᴀʏᴀ", callback_data="my_orders", icon_custom_emoji_id=extract_id(Config.box))
            ]
        ])
        
        await query.message.edit_text(text=text_done, reply_markup=btns)

    elif data == "open_script_menu":
        text = (
            f"<blockquote><b>{Config.script} 𝗕𝗘𝗟𝗜  𝗦𝗖𝗥𝗜𝗣𝗧  𝗜𝗡𝗜</b>\n\n"
            f"ᴘɪʟɪʜ ᴠᴀʀɪᴀsɪ sᴄʀɪᴘᴛ ʏᴀɴɢ ɪɴɢɪɴ ᴅɪʙᴇʟɪ:\n\n"
            f"{Config.bulattitik} <b>FULL UP</b>: Rp 20.000\n\n"
            f"{Config.SCRIPT_BENEFITS}</blockquote>"
        )
        # Tombol NO UP dan UP 1X Dihapus, Sisakan FULL UP saja
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ʙᴇʟɪ ғᴜʟʟ ᴜᴘ (20ᴋ)", callback_data="buySC_FULL_UP", icon_custom_emoji_id=extract_id(Config.keranjang))],
            [InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ʜᴏᴍᴇ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.kembali))]
        ])

        if query.message.photo: 
            await query.message.edit_caption(caption=text, reply_markup=btns)
        else: 
            await query.message.edit_text(text=text, reply_markup=btns)

            
    elif data.startswith("buySC_"):
        script_type = data.split("_", 1)[1]
        if script_type not in Config.SCRIPT_PRICES: return
        
        sc_info = Config.SCRIPT_PRICES[script_type]
        price = sc_info["price"]
        name = sc_info["name"]
        
        text_pilih = (
            f"<blockquote><b>{Config.kredit} 𝗠 𝗘 𝗧 𝗢 𝗗 𝗘   𝗕 𝗔 𝗬 𝗔 𝗥</b>\n\n"
            f"{Config.box} ᴘʀᴏᴅᴜᴋ   : <b>sᴄʀɪᴘᴛ ʙᴏᴛ ({name})</b>\n"
            f"{Config.harga} ᴛᴏᴛᴀʟ    : <code>{format_rupiah(price)}</code>\n\n"
            f"{Config.pin} sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ᴊᴇɴɪs ǫʀɪs ᴜɴᴛᴜᴋ ᴍᴇʟᴀɴᴊᴜᴛᴋᴀɴ:</blockquote>"
        )
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs (ᴘᴀᴋᴀsɪʀ)", callback_data=f"payAutoSC_{script_type}", icon_custom_emoji_id=extract_id(Config.belifast))],
            [InlineKeyboardButton(text="ǫʀɪs ᴍᴀɴᴜᴀʟ / ᴅᴀɴᴀ", callback_data=f"payManSC_{script_type}", icon_custom_emoji_id=extract_id(Config.bank))],
            [InlineKeyboardButton(text="ʙᴀᴛᴀʟᴋᴀɴ", callback_data="open_script_menu", icon_custom_emoji_id=extract_id(Config.silang))]
        ])
        if query.message.photo: await query.edit_message_caption(caption=text_pilih, reply_markup=btns)
        else: await query.message.edit_text(text=text_pilih, reply_markup=btns)
        
    elif data.startswith("payAutoSC_") or data.startswith("payManSC_"):
        is_auto = data.startswith("payAutoSC_")
        script_type = data.split("_", 1)[1]
        sc_info = Config.SCRIPT_PRICES[script_type]
        price = sc_info["price"]
        name = sc_info["name"]
        
        if is_auto:
            oid_request = f"SC{int(time.time())}"
            await query.edit_message_caption(caption=f"<blockquote><b>{Config.loading} ᴍᴇɴɢʜᴀsɪʟᴋᴀɴ ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs ᴅᴀʀɪ ᴘᴀᴋᴀsɪʀ...</b></blockquote>")
            qr_img, final_price = await PaymentGateway.generate_qris(price, oid_request)
            if not qr_img: 
                return await query.answer(f"{Config.silang} ɢᴀᴛᴇᴡᴀʏ ᴘᴀᴋᴀsɪʀ ᴇʀʀᴏʀ ᴀᴛᴀᴜ sᴇᴅᴀɴɢ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ!", show_alert=True)
            
            real_oid = qr_img.name.split("_")[1].split(".")[0]
            
            try:
                import pytz
                waktu_sekarang = datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%d/%m/%Y %H:%M')
            except:
                waktu_sekarang = datetime.now().strftime('%d/%m/%Y %H:%M')
                
            caption_pay = (
                f"<blockquote><b>{Config.struk} 𝗜 𝗡 𝗩 𝗢 𝗜 𝗖 𝗘   𝗦 𝗖 𝗥 𝗜 𝗣 𝗧</b>\n\n"
                f"{Config.oid} ᴏʀᴅᴇʀ ɪᴅ : <code>{real_oid}</code>\n"
                f"{Config.user} ᴘᴇᴍʙᴇʟɪ  : <b>{u_name}</b>\n"
                f"{Config.box} ᴘʀᴏᴅᴜᴋ   : <b>sᴄʀɪᴘᴛ {name}</b>\n"
                f"{Config.harga} ᴛᴏᴛᴀʟ    : <code>{format_rupiah(final_price)}</code>\n"
                f"{Config.loading} ᴇxᴘɪʀᴇᴅ  : <b>𝟷𝟶 ᴍᴇɴɪᴛ</b>\n"
                f"{Config.tanggal} ᴛᴀɴɢɢᴀʟ  : <b>{waktu_sekarang}</b>\n\n"
                f"{Config.pin} ᴄᴀʀᴀ ᴘᴇᴍʙᴀʏᴀʀᴀɴ:\n"
                f"1. sᴄᴀɴ ǫʀɪs ᴅɪ ᴀᴛᴀs ᴍᴇɴɢɢᴜɴᴀᴋᴀɴ ᴇ-ᴡᴀʟʟᴇᴛ.\n"
                f"2. ᴘᴀsᴛɪᴋᴀɴ ɴᴏᴍɪɴᴀʟ sᴇsᴜᴀɪ ᴛᴀɢɪʜᴀɴ.\n"
                f"3. ᴛʀᴀɴsᴀᴋsɪ ᴀᴋᴀɴ ᴅɪᴘʀᴏsᴇs ᴏᴛᴏᴍᴀᴛɪs.</blockquote>"
            )
            btns = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="ᴄᴇᴋ sᴛᴀᴛᴜs ʙᴀʏᴀʀ", callback_data=f"checkSC_{real_oid}_{script_type}_{final_price}", icon_custom_emoji_id=extract_id(Config.putar))], 
                [InlineKeyboardButton(text="ʙᴀᴛᴀʟ ᴏʀᴅᴇʀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.silang))]
            ])

            try: await query.message.delete()
            except: pass
            await client.send_photo(chat_id=u_id, photo=qr_img, caption=caption_pay, reply_markup=btns)
        else:
            sid_pass = f"SC-{script_type}-{price}-{int(time.time())}"
            waiting_manual_proof[u_id] = {"sid": sid_pass, "price": price, "product": f"Script {name}"}
            asyncio.create_task(auto_cancel_order(sid_pass, u_id, client))
            
            try:
                import pytz
                waktu_sekarang = datetime.now(pytz.timezone('Asia/Jakarta')).strftime('%d/%m/%Y %H:%M')
            except:
                waktu_sekarang = datetime.now().strftime('%d/%m/%Y %H:%M')
                
            caption_pay = (
                f"<blockquote><b>{Config.struk} 𝗜 𝗡 𝗩 𝗢 𝗜 𝗖 𝗘   𝗠 𝗔 𝗡 𝗨 𝗔 𝗟</b>\n\n"
                f"{Config.user} ᴘᴇᴍʙᴇʟɪ  : <b>{u_name}</b>\n"
                f"{Config.box} ᴘʀᴏᴅᴜᴋ   : <b>sᴄʀɪᴘᴛ {name}</b>\n"
                f"{Config.harga} ᴛᴏᴛᴀʟ    : <code>{format_rupiah(price)}</code>\n"
                f"{Config.tanggal} ᴛᴀɴɢɢᴀʟ  : <b>{waktu_sekarang}</b>\n\n"
                f"{Config.pin} ɪɴsᴛʀᴜᴋsɪ ᴘᴇᴍʙᴀʏᴀʀᴀɴ:\n"
                f"1. sᴄᴀɴ ǫʀɪs ᴘᴀᴅᴀ ɢᴀᴍʙᴀʀ ᴅɪ ᴀᴛᴀs.\n"
                f"2. ᴛʀᴀɴsғᴇʀ ᴛᴇᴘᴀᴛ <code>{price}</code>.\n"
                f"3. ᴋɪʀɪᴍ ғᴏᴛᴏ ʙᴜᴋᴛɪ ᴛʀᴀɴsғᴇʀ ᴋᴇ ᴄʜᴀᴛ ɪɴɪ sᴇᴋᴀʀᴀɴɢ ᴊᴜɢᴀ!\n\n"
                f"{Config.kredit} <b>DANA / E-Wallet :</b> <code>{Config.DANA_NUMBER}</code>\n"
                f"{Config.peringatan} ᴘᴇsᴀɴᴀɴ ᴀᴋᴀɴ ᴅɪᴠᴇʀɪғɪᴋᴀsɪ ᴍᴀɴᴜᴀʟ ᴏʟᴇʜ ᴀᴅᴍɪɴ.</blockquote>"
            )
            try:
                await query.message.delete()
            except:
                pass

            await client.send_photo(
                chat_id=u_id,
                photo=Config.QRIS_MANUAL_URL,
                caption=caption_pay,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text="ʙᴀᴛᴀʟᴋᴀɴ ᴏʀᴅᴇʀ", 
                        callback_data="open_script_menu", 
                        icon_custom_emoji_id=extract_id(Config.silang)
                    )]
                ])
            )


@bot.on_message(filters.private & (filters.text | filters.photo | filters.document), group=1)
async def handle_all_text_inputs(client: Client, message: Message):
    u_id = message.from_user.id
    txt = (message.text or "").strip()

    # Hapus state kalau user ngetik command /
    if txt.startswith("/"):
        user_states.pop(u_id, None)
        if 'LoginState' in globals(): LoginState.pop(u_id, None)

    # Ambil state aman! Variabel lama 'status' udah gua musnahkan, kita konsisten pake 'action'
    action = user_states.get(u_id, {}).get("action", "")

    # PROTEKSI: Kalo pesan bukan command (gak ada /) DAN user gak punya state/action, abaikan!
    # Ini bikin command admin tetep lolos meski gak punya action!
    if not txt.startswith("/") and not action:
        return

    # ==========================================
    # LOGIK STATE INPUT BERJALAN DI SINI
    # ==========================================
    if action == "admin_wait_clearsaldo" and u_id == Config.OWNER_ID:
        if not txt.isdigit():
            return await message.reply(
                text=f"<blockquote><b>{Config.silang} ɪᴅ ᴜsᴇʀ ʜᴀʀᴜs ʙᴇʀᴜᴘᴀ ᴀɴɢᴋᴀ ʏᴀɴɢ ᴠᴀʟɪᴅ!</b></blockquote>", 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
            )
        
        target_id = int(txt)
        msg_proses = await message.reply(f"<blockquote><b>{Config.loading} ᴍᴇᴍᴘʀᴏsᴇs ʀᴇsᴇᴛ sᴀʟᴅᴏ sɪsᴛᴇᴍ...</b></blockquote>")
        success = await database.reset_balance(target_id)
        user_states.pop(u_id, None)
        
        if success:
            return await msg_proses.edit_text(
                text=f"<blockquote><b>{Config.centanghijau} sᴜᴄᴄᴇss!</b>\n{Config.harga} sᴀʟᴅᴏ ᴜsᴇʀ <code>{target_id}</code> ʙᴇʀʜᴀsɪʟ ᴅɪʀᴇsᴇᴛ ᴍᴇɴᴊᴀᴅɪ ʀᴘ 0.</blockquote>", 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
            )
        else:
            return await msg_proses.edit_text(
                text=f"<blockquote><b>{Config.peringatan} ɢᴀɢᴀʟ ᴅɪʀᴇsᴇᴛ!</b>\nᴜsᴇʀ <code>{target_id}</code> ᴍᴜɴɢᴋɪɴ ʙᴇʟᴜᴍ ᴛᴇʀᴅᴀғᴛᴀʀ ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ ᴀᴛᴀᴜ sᴀʟᴅᴏ ᴍᴇᴍᴀɴɢ sᴜᴅᴀʜ 0.</blockquote>", 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
            )

    elif action == "admin_wait_clearuid" and u_id == Config.OWNER_ID:
        target = txt.strip()
        stocks_to_delete = await database.stocks_col.find({"uid": {"$regex": f"^{target}"}}).to_list(length=None)
        
        if not stocks_to_delete:
            user_states.pop(u_id, None)
            return await message.reply(
                text=f"<blockquote><b>{Config.silang} ᴅᴀᴛᴀ ᴜɪᴅ <code>{target}</code> ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ!</b>\nPᴀsᴛɪᴋᴀɴ ᴘʀᴇғɪx ᴀᴛᴀᴜ ᴜɪᴅ sᴜᴅᴀʜ ʙᴇɴᴀʀ.</blockquote>", 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
            )

        msg_del = await message.reply(f"<blockquote><b>{Config.loading} ᴍᴇʟᴏɢᴏᴜᴛ sᴇsɪ ᴅᴀɴ ᴍᴇɴɢʜᴀᴘᴜs ᴅᴀᴛᴀ ᴀᴋᴜɴ ᴅᴀʀɪ ᴅᴀᴛᴀʙᴀsᴇ...</b></blockquote>")
        deleted_count = 0
        
        for s in stocks_to_delete:
            if s.get("session"): asyncio.create_task(perform_bot_logout(s["session"], u_id))
            deleted_count += 1
        
        await database.stocks_col.delete_many({"uid": {"$regex": f"^{target}"}})
        user_states.pop(u_id, None)
        return await msg_del.edit_text(
            text=f"<blockquote><b>{Config.centanghijau} sᴜᴄᴄᴇss!</b>\n{Config.hapus} <b>{deleted_count} ᴀᴋᴜɴ</b> ᴅᴇɴɢᴀɴ ᴛᴀʀɢᴇᴛ <code>{target}</code> ʙᴇʀʜᴀsɪʟ ᴅɪʟᴏɢᴏᴜᴛ ᴅᴀɴ ᴅɪʜᴀᴘᴜs sᴇᴄᴀʀᴀ ᴘᴇʀᴍᴀɴᴇɴ.</blockquote>", 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
        )

    elif action == "wait_deposit_amount":
        if not txt.isdigit(): 
            return await message.reply(f"<blockquote><b>{Config.peringatan} Mᴏʜᴏɴ ᴍᴀsᴜᴋᴋᴀɴ ᴀɴɢᴋᴀ sᴀᴊᴀ ᴛᴀɴᴘᴀ ʜᴜʀᴜғ, ᴛɪᴛɪᴋ, ᴀᴛᴀᴜ sᴘᴀsɪ!</b></blockquote>")
        amount = int(txt)
        if amount < 1000:
            return await message.reply(f"<blockquote><b>{Config.silang} ᴍɪɴɪᴍᴀʟ ᴅᴇᴘᴏsɪᴛ ᴀᴅᴀʟᴀʜ Rᴘ 5.000!</b></blockquote>")
        
        user_states.pop(u_id, None)
        text_pilih = (
            f"<blockquote><b>{Config.kredit} 𝗠 𝗘 𝗧 𝗢 𝗗 𝗘   𝗗 𝗘 𝗣 𝗢 𝗦 𝗜 𝗧</b>\n\n"
            f"{Config.harga} ᴊᴜᴍʟᴀʜ ᴅᴇᴘᴏsɪᴛ : <code>{format_rupiah(amount)}</code>\n\n"
            f"sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ᴍᴇᴛᴏᴅᴇ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ.</blockquote>"
        )
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ǫʀɪs ᴏᴛᴏᴍᴀᴛɪs (ᴘᴀᴋᴀsɪʀ)", callback_data=f"pAut_D_{amount}", icon_custom_emoji_id=extract_id(Config.belifast))],
            [InlineKeyboardButton(text="ǫʀɪs ᴍᴀɴᴜᴀʟ / ᴅᴀɴᴀ", callback_data=f"pMan_D_{amount}", icon_custom_emoji_id=extract_id(Config.bank))],
            [InlineKeyboardButton(text="ʙᴀᴛᴀʟᴋᴀɴ ᴛʀᴀɴsᴀᴋsɪ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.silang))]
        ])
        return await message.reply(text=text_pilih, reply_markup=btns)

    elif action.startswith("wbq_"):
        parts = action.split("_")
        type_str, rcode, pref, dc_val = parts[1], parts[2], parts[3], parts[4]

        if not txt.isdigit(): 
            return await message.reply(f"<blockquote><b>{Config.peringatan} Mᴏʜᴏɴ ᴍᴀsᴜᴋᴋᴀɴ ᴀɴɢᴋᴀ sᴀᴊᴀ ᴛᴀɴᴘᴀ ʜᴜʀᴜғ, ᴛɪᴛɪᴋ, ᴀᴛᴀᴜ sᴘᴀsɪ!</b></blockquote>")
        qty = int(txt)
        is_limp = (type_str == "limp")
        limit_val = "ON" if is_limp else "OFF"
        
        # 1. Cek ketersediaan stok dulu di awal
        stock_count = await database.stocks_col.count_documents({
            "status": "ready", "limit": limit_val, "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val
        })
        
        if qty <= 0: return await message.reply(f"<blockquote><b>{Config.silang} ᴍɪɴɪᴍᴀʟ ᴘᴇᴍʙᴇʟɪᴀɴ ᴀᴅᴀʟᴀʜ 1 ᴀᴄᴄ!</b></blockquote>")
        if qty > stock_count: return await message.reply(f"<blockquote><b>{Config.peringatan} sᴛᴏᴋ ᴛɪᴅᴀᴋ ᴍᴇɴᴄᴜᴋᴜᴘɪ! sɪsᴀ sᴛᴏᴋ sᴀᴀᴛ ɪɴɪ ʜᴀɴʏᴀ ᴀᴅᴀ {stock_count} ᴀᴄᴄ.</b></blockquote>")

        # 2. FIX TOTAL: Ambil sample data dari DB untuk ngecek custom_price
        sample_stock = await database.stocks_col.find_one({
            "status": "ready", "limit": limit_val, "region_code": rcode, "uid": {"$regex": f"^{re.escape(pref)}"}, "dc": dc_val
        })
        
        # 3. Logic penentuan harga (Prioritaskan Custom Price, kalau kosong fallback ke Config)
        price_each = sample_stock.get("custom_price") if sample_stock else 0
        if not price_each: 
            price_each = Config.get_price(pref, dc_val, rcode, is_limp)

        total_price = price_each * qty
        user_states.pop(u_id, None) 
        
        label = f"{Config.LABELS.get(pref)} (DC {dc_val} - {rcode})"
        text = (
            f"<blockquote><b>{Config.keranjang} 𝗖 𝗛 𝗘 𝗖 𝗞 𝗢 𝗨 𝗧</b>\n\n"
            f"{Config.box} ᴘʀᴏᴅᴜᴋ: <b>{label}</b>\n"
            f"{Config.inputteks} ᴊᴜᴍʟᴀʜ: <b>{qty} ᴀᴄᴄ</b>\n"
            f"{Config.harga} ᴛᴏᴛᴀʟ : <code>{format_rupiah(total_price)}</code>\n\n"
            f"{Config.kredit} sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ᴍᴇᴛᴏᴅᴇ ʙᴀʏᴀʀ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ:</blockquote>"
        )
        
        payload_saldo = f"paySld_B_{type_str}_{rcode}_{pref}_{dc_val}_{qty}"
        payload_qris = f"buyQR_BLK_{type_str}_{rcode}_{pref}_{dc_val}_{qty}"
        
        btns = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="ʙᴀʏᴀʀ ᴠɪᴀ sᴀʟᴅᴏ", callback_data=payload_saldo, icon_custom_emoji_id=extract_id(Config.tumpukanuang))],
            [InlineKeyboardButton(text="ʙᴀʏᴀʀ ᴠɪᴀ ǫʀɪs", callback_data=payload_qris, icon_custom_emoji_id=extract_id(Config.bank))],
            [InlineKeyboardButton(text="ʙᴀᴛᴀʟᴋᴀɴ ᴏʀᴅᴇʀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.silang))]
        ])
        return await message.reply(text, reply_markup=btns)

    elif action.startswith("wsess_"):
            try:
                parts = action.split("_", 5)
                type_str, rcode, pref, dc_val = parts[1], parts[2], parts[3], parts[4]
                limit_val = "ON" if type_str == "limp" else "OFF"
                
                qty = int(message.text.strip())
                
                # 🔥 FIX REGEX: Amankan prefix uid dengan re.escape agar tanda '+' tidak bikin crash        
                safe_pref = re.escape(pref)
                
                # Cek ketersediaan stok dengan prefix yang sudah aman
                stock_count = await database.stocks_col.count_documents({
                    "status": "ready", 
                    "limit": limit_val, 
                    "region_code": rcode, 
                    "uid": {"$regex": f"^{safe_pref}"}, 
                    "dc": dc_val
                })
                
                if qty < 1 or qty > stock_count:
                    return await message.reply(
                        f"<blockquote><b>{Config.silang} ɢᴀɢᴀʟ!</b>\n"
                        f"ᴊᴜᴍʟᴀʜ ᴛɪᴅᴀᴋ ᴠᴀʟɪᴅ. ᴍɪɴɪᴍᴀʟ ᴘᴇᴍʙᴇʟɪᴀɴ <b>1</b> ᴅᴀɴ ᴍᴀᴋsɪᴍᴀʟ <b>{stock_count}</b> ᴀᴋᴜɴ!</blockquote>"
                    )
                
                # Bersihkan state biar ga stuck minta input terus
                del user_states[u_id] 
                
                # Lempar ke sistem invoice dengan mode "SES" (File Session)
                payload_inv = f"buy_SES_{type_str}_{rcode}_{pref}_{dc_val}_{qty}"
                
                # Panggil tombol Lanjut Bayar
                btns = InlineKeyboardMarkup([
                    [InlineKeyboardButton(text="💳 ʟᴀɴᴊᴜᴛ ᴘᴇᴍʙᴀʏᴀʀᴀɴ", callback_data=payload_inv)],
                    [InlineKeyboardButton(text="ʙᴀᴛᴀʟᴋᴀɴ ᴏʀᴅᴇʀ", callback_data="back_home", icon_custom_emoji_id=extract_id(Config.silang))]
                ])
                
                await message.reply(
                    f"<blockquote><b>{Config.centanghijau} ʙᴇʀʜᴀsɪʟ ᴍᴇᴍᴀsᴜᴋᴋᴀɴ ᴊᴜᴍʟᴀʜ!</b>\n"
                    f"ᴀɴᴅᴀ ᴀᴋᴀɴ ᴍᴇᴍʙᴇʟɪ ғɪʟᴇ .sᴇssɪᴏɴ sᴇʙᴀɴʏᴀᴋ <b>{qty} ᴀᴋᴜɴ</b>.\n\n"
                    f"ᴋʟɪᴋ ᴛᴏᴍʙᴏʟ ᴅɪ ʙᴀᴡᴀʜ ᴜɴᴛᴜᴋ ᴍᴇᴍɪʟɪʜ ᴍᴇᴛᴏᴅᴇ ᴘᴇᴍʙᴀʏᴀʀᴀɴ.</blockquote>", 
                    reply_markup=btns
                )
                
            except (ValueError, IndexError):
                return await message.reply(
                    f"<blockquote><b>{Config.silang} ᴍᴀᴀғ!</b>\n"
                    f"ʜᴀʀᴀᴘ ᴍᴀsᴜᴋᴋᴀɴ ғᴏʀᴍᴀᴛ <b>ᴀɴɢᴋᴀ</b> sᴀᴊᴀ (ᴄᴏɴᴛᴏʜ: 5)</blockquote>"
                )

    # ============================================================
    # BLOK KHUSUS OWNER (COMMANDS YANG BOLEH DIBACA DI DALAM HANDLER)
    # ============================================================
    if u_id == Config.OWNER_ID:
        
        if txt.startswith("/ubahharga") or action == "admin_wait_ubahharga":
            if action == "admin_wait_ubahharga":
                user_states.pop(u_id, None)
                args_text = txt
            else:
                args_text = txt.split(" ", 1)[1] if len(txt.split(" ", 1)) > 1 else ""

            if not args_text:
                return await message.reply(f"<blockquote><b>{Config.silang} ғᴏʀᴍᴀᴛ sᴀʟᴀʜ!</b>\n{Config.bulattitik} <b>Sᴀᴛᴜᴀɴ:</b> <code>81918282 6500</code>\n{Config.bulattitik} <b>Mᴀssᴀʟ:</b> <code>id8,2500,Indonesia,limper</code></blockquote>")

            smallcaps_trans = str.maketrans("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ")

            if "," in args_text:
                parts = [p.strip() for p in args_text.split(",")]
                if len(parts) != 4:
                    return await message.reply(f"<blockquote><b>{Config.silang} ғᴏʀᴍᴀᴛ ᴍᴀssᴀʟ sᴀʟᴀʜ!</b>\nCᴏɴᴛᴏʜ: <code>id8,2500,Indonesia,limper</code></blockquote>")
                
                prefix_raw = parts[0].lower().replace("id", "")
                prefix_val = prefix_raw[0] if prefix_raw else "0"
                
                try: new_price = int(parts[1])
                except ValueError: return await message.reply(f"<blockquote><b>{Config.silang} ʜᴀʀɢᴀ ʜᴀʀᴜs ᴀɴɢᴋᴀ!</b></blockquote>")
                    
                region_val = parts[2]
                region_smallcaps = str(region_val).translate(smallcaps_trans)
                
                input_tipe = parts[3].lower()
                limit_val = "ON" if input_tipe in ["limper", "on", "limit"] else "OFF"
                
                teks_limit_display = "ʟɪᴍᴘᴇʀ (ʟɪᴍɪᴛ ᴏɴ)" if limit_val == "ON" else "ɴᴏ ᴍɪɴᴜs (ʟɪᴍɪᴛ ᴏғғ)"
                kat_bulk_aman = "ʟɪᴍᴘᴇʀ" if limit_val == "ON" else "ɴᴏ ᴍɪɴᴜs"
                
                modified_count = await database.update_stock_price_bulk(prefix_val, region_val, limit_val, new_price)
                
                if modified_count > 0:
                    await Logger.log_ubah_harga_bulk(client=client, prefix=prefix_val, region=region_smallcaps, limit_text=kat_bulk_aman, new_price=new_price, count=modified_count)
                    await message.reply(
                        text=f"<blockquote><b>{Config.centanghijau} ʜᴀʀɢᴀ ᴍᴀssᴀʟ ʙᴇʀʜᴀsɪʟ ᴅɪᴜʙᴀʜ!</b>\n\n"
                        f"{Config.uid} ᴘʀᴇғɪx : <b>ɪᴅ {prefix_val}xxx</b>\n"
                        f"{Config.globe} ɴᴇɢᴀʀᴀ : <b>{region_smallcaps}</b>\n"
                        f"{Config.proteksi} ʟɪᴍɪᴛ : <b>{teks_limit_display}</b>\n"
                        f"{Config.harga} ʜᴀʀɢᴀ ʙᴀʀᴜ: <b>ʀᴘ {new_price:,}</b>\n\n"
                        f"{Config.box} ᴛᴏᴛᴀʟ ᴅɪᴜʙᴀʜ: <b>{modified_count} ᴀᴋᴜɴ</b>\n"
                        f"<i>ɴᴏᴛɪғɪᴋᴀsɪ ᴍᴀssᴀʟ ᴛᴇʟᴀʜ ᴅɪʙʟᴀsᴛ ᴋᴇ ᴄʜᴀɴɴᴇʟ.</i></blockquote>".replace(',', '.'),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Kᴇᴍʙᴀʟɪ ᴋᴇ Pᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
                    )
                else:
                    await message.reply(f"<blockquote><b>{Config.silang} ɢᴀɢᴀʟ ᴍᴇɴɢᴜʙᴀʜ ᴍᴀssᴀʟ!</b>\nᴛɪᴅᴀᴋ ᴀᴅᴀ sᴛᴏᴋ ʀᴇᴀᴅʏ ʏᴀɴɢ ᴄᴏᴄᴏᴋ ᴅᴇɴɢᴀɴ ᴋʀɪᴛᴇʀɪᴀ.</blockquote>")
                return

            else:
                args = args_text.split()
                if len(args) != 2: return await message.reply(f"<blockquote><b>{Config.silang} ғᴏʀᴍᴀᴛ sᴀʟᴀʜ!</b>\nCᴏɴᴛᴏʜ Sᴀᴛᴜᴀɴ: <code>81918282 6500</code></blockquote>")
                uid_target = args[0]
                try: new_price = int(args[1])
                except ValueError: return await message.reply(f"<blockquote><b>{Config.silang} ʜᴀʀɢᴀ ʜᴀʀᴜs ᴀɴɢᴋᴀ!</b></blockquote>")

                stock = await database.stocks_col.find_one({"uid": uid_target})
                if not stock: return await message.reply(f"<blockquote><b>{Config.silang} ᴜɪᴅ ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ!</b></blockquote>")

                old_price = stock.get("custom_price")
                if old_price is None:
                    pref = uid_target[0] if uid_target else "0"
                    dc_val = stock.get("dc", "0")
                    is_limp = (stock.get("limit", "").upper() == "ON")
                    region_code = stock.get("region_code", "DEFAULT")
                    old_price = Config.get_price(pref, dc_val, region_code, is_limp)

                if new_price == old_price: return await message.reply(f"<blockquote><b>{Config.peringatan} ʜᴀʀɢᴀ sᴜᴅᴀʜ sᴀᴍᴀ ᴅᴇɴɢᴀɴ sᴇʙᴇʟᴜᴍɴʏᴀ!</b></blockquote>")

                success = await database.update_stock_price(uid_target, new_price)
                if success:
                    reg_aman = stock.get("region", "UNKNOWN")
                    reg_smallcaps = str(reg_aman).translate(smallcaps_trans)
                    kat_aman = "ʟɪᴍᴘᴇʀ" if stock.get("limit", "OFF") == "ON" else "ɴᴏ ᴍɪɴᴜs"

                    await Logger.log_ubah_harga(client=client, uid=uid_target, old_price=old_price, new_price=new_price, region=reg_smallcaps, kategori=kat_aman)
                    await message.reply(
                        text=f"<blockquote><b>{Config.centanghijau} ʜᴀʀɢᴀ ᴀᴋᴜɴ ʙᴇʀʜᴀsɪʟ ᴅɪᴜʙᴀʜ!</b>\n\n"
                        f"{Config.uid} ᴜɪᴅ ᴀᴋᴜɴ : <code>{uid_target}</code>\n"
                        f"{Config.harga} ʜᴀʀɢᴀ ʙᴀʀᴜ: <b>ʀᴘ {new_price:,}</b>\n\n"
                        f"<i>ɴᴏᴛɪғɪᴋᴀsɪ ᴘᴇʀᴜʙᴀʜᴀɴ ᴛᴇʟᴀʜ ᴅɪʙʟᴀsᴛ ᴋᴇ ᴄʜᴀɴɴᴇʟ.</i></blockquote>".replace(',', '.'),
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Kᴇᴍʙᴀʟɪ ᴋᴇ Pᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]])
                    )
                else:
                    await message.reply(f"<blockquote><b>{Config.silang} ɢᴀɢᴀʟ ᴍᴇɴɢᴜʙᴀʜ ʜᴀʀɢᴀ!</b></blockquote>")
                return
    
        elif txt.startswith("/clearsaldo"):
            if txt == "/clearsaldo" or txt == "/clearsaldo ":
                return await message.reply(f"<blockquote><b>{Config.silang} ғᴏʀᴍᴀᴛ sᴀʟᴀʜ!</b>\nɢᴜɴᴀᴋᴀɴ: /clearsaldo [ID_USER]\nᴄᴏɴᴛᴏʜ: /clearsaldo 1234567890</blockquote>")
            try:
                target_id = txt.split(" ", 1)[1].strip()
                if not target_id.isdigit(): return await message.reply(f"<blockquote><b>{Config.silang} ɪᴅ ᴜsᴇʀ ʜᴀʀᴜs ʙᴇʀᴜᴘᴀ ᴀɴɢᴋᴀ!</b></blockquote>")
                
                target_id = int(target_id)
                msg_proses = await message.reply(f"<blockquote><b>{Config.loading} ᴍᴇᴍᴘʀᴏsᴇs ʀᴇsᴇᴛ sᴀʟᴅᴏ...</b></blockquote>")
                
                success = await database.reset_balance(target_id)
                if success: await msg_proses.edit_text(f"<blockquote><b>{Config.centanghijau} sᴜᴄᴄᴇss!</b>\n{Config.harga} sᴀʟᴅᴏ ᴜsᴇʀ <code>{target_id}</code> ʙᴇʀʜᴀsɪʟ ᴅɪʀᴇsᴇᴛ ᴍᴇɴᴊᴀᴅɪ ʀᴘ 0.</blockquote>")
                else: await msg_proses.edit_text(f"<blockquote><b>{Config.peringatan} ɢᴀɢᴀʟ!</b>\nᴜsᴇʀ <code>{target_id}</code> ᴍᴜɴɢᴋɪɴ ʙᴇʟᴜᴍ ᴛᴇʀᴅᴀғᴛᴀʀ ᴀᴛᴀᴜ sᴀʟᴅᴏ ᴍᴇᴍᴀɴɢ sᴜᴅᴀʜ 0.</blockquote>")
            except Exception as e:
                return await message.reply(f"<blockquote><b>{Config.silang} ᴇʀʀᴏʀ:</b> {e}</blockquote>")

        elif txt.startswith("/clearall"):
            btns = InlineKeyboardMarkup([[InlineKeyboardButton(text="ʏᴀ, ʜᴀᴘᴜs sᴇᴍᴜᴀ", callback_data="confirm_clear_all", icon_custom_emoji_id=extract_id(Config.centanghijau))], [InlineKeyboardButton(text="ʙᴀᴛᴀʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.silang))]])
            return await message.reply(f"<blockquote><b>{Config.peringatan} ᴡᴀʀɴɪɴɢ: ᴅᴇsᴛʀᴜᴄᴛɪᴠᴇ ᴀᴄᴛɪᴏɴ!</b>\nʏᴀᴋɪɴ ʜᴀᴘᴜs sᴇʟᴜʀᴜʜ sᴛᴏᴋ ʀᴇᴀᴅʏ ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ?</blockquote>", reply_markup=btns)

        elif txt.startswith("/clear"):
            if txt == "/clear" or txt == "/clear ": return await message.reply(f"<blockquote><b>{Config.silang} ғᴏʀᴍᴀᴛ sᴀʟᴀʜ!</b>\nɢᴜɴᴀᴋᴀɴ: /clear [UID atau Prefix]\nᴄᴏɴᴛᴏʜ: /clear 6212345</blockquote>")
            try:
                target = txt.split(" ", 1)[1].strip()
                stocks_to_delete = await database.stocks_col.find({"uid": {"$regex": f"^{target}"}}).to_list(length=None)
                
                if not stocks_to_delete: return await message.reply(f"<blockquote><b>{Config.silang} ᴅᴀᴛᴀ ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ ᴅɪ ᴅᴀᴛᴀʙᴀsᴇ!</b></blockquote>")
                
                msg_del = await message.reply(f"<blockquote><b>{Config.loading} ᴍᴇʟᴏɢᴏᴜᴛ sᴇsɪ ᴅᴀɴ ᴍᴇɴɢʜᴀᴘᴜs ᴅᴀᴛᴀ...</b></blockquote>")
                deleted_count = 0
                
                for s in stocks_to_delete:
                    if s.get("session"): asyncio.create_task(perform_bot_logout(s["session"], u_id))
                    deleted_count += 1
                
                await database.stocks_col.delete_many({"uid": {"$regex": f"^{target}"}})
                return await msg_del.edit_text(f"<blockquote><b>{Config.centanghijau} sᴜᴄᴄᴇss!</b>\n{Config.hapus} {deleted_count} ᴀᴋᴜɴ ᴅᴇɴɢᴀɴ ᴛᴀʀɢᴇᴛ <code>{target}</code> ʙᴇʀʜᴀsɪʟ ᴅɪʟᴏɢᴏᴜᴛ ᴅᴀɴ ᴅɪʜᴀᴘᴜs.</blockquote>")
            except Exception as e: 
                return await message.reply(f"<blockquote><b>{Config.silang} ғᴏʀᴍᴀᴛ: /clear [UID/Prefix]</b>\nError: {e}</blockquote>")

        elif txt.startswith("/ping") or txt.startswith("/stats"):
            ping_start = time.time()
            msg_ping = await message.reply(f"<blockquote><b>{Config.loading} ᴍᴇɴɢᴀᴍʙɪʟ ᴅᴀᴛᴀ sᴇʀᴠᴇʀ...</b></blockquote>")
            ping_end = time.time()
            ping_time = round((ping_end - ping_start) * 1000, 2)
            
            stats = await database.get_global_stats()
            stats_text = (
                f"<blockquote><b>{Config.script} 𝗦𝗘𝗥𝗩𝗘𝗥 𝗦𝗧𝗔𝗧𝗨𝗦</b>\n\n"
                f"{Config.belifast} ᴘɪɴɢ     : <b>{ping_time} ᴍs</b>\n"
                f"{Config.loading} ᴜᴘᴛɪᴍᴇ   : <b>{get_uptime()}</b>\n"
                f"{Config.user} ᴜsᴇʀs    : <b>{stats.get('users', 0)} ᴀᴋᴜɴ</b>\n"
                f"{Config.box} sᴛᴏᴋ     : <b>{stats.get('ready', 0)} ᴀᴋᴜɴ</b>\n"
                f"{Config.harga} ᴛᴇʀᴊᴜᴀʟ  : <b>{stats.get('sold', 0)} ᴀᴋᴜɴ</b>\n\n"
                f"{Config.centanghijau} sɪsᴛᴇᴍ ʙᴇʀᴊᴀʟᴀɴ ɴᴏʀᴍᴀʟ!</blockquote>"
            )
            return await msg_ping.edit_text(stats_text)

        elif txt.startswith("/addstok"):
            user_states[u_id] = {"action": "wait_stok_data"}
            text_inst = (
                f"<blockquote><b>{Config.masukin} 𝗜𝗡𝗣𝗨𝗧 𝗦𝗧𝗢𝗞 𝗔𝗞𝗨𝗡</b>\n\n"
                f"Kɪʀɪᴍ ᴅᴀᴛᴀ ᴀᴋᴜɴ ᴅᴇɴɢᴀɴ ғᴏʀᴍᴀᴛ ʙᴀʀᴜ ɪɴɪ:\n"
                f"<code>ID|DC|NOMER|LIMIT|BENEFIT|PASSWORD|HARGA</code>\n\n"
                f"<i>Cᴏɴᴛᴏʜ:</i>\n"
                f"<code>8123|5|+628123|ON|Tag Fake VIP|pwbebas123|6000</code>\n\n"
                f"{Config.pin} Bᴏᴛ ᴀᴋᴀɴ ᴏᴛᴏᴍᴀᴛɪs ᴍᴇɴɢᴇᴄᴇᴋ Rᴇɢɪᴏɴ, Eᴍᴀɪʟ, ᴅᴀɴ ᴍᴇɴʏᴏʀᴛɪʀ Eᴛᴀʟᴀsᴇ ʙᴇʀᴅᴀsᴀʀᴋᴀɴ Bᴇɴᴇғɪᴛ!</blockquote>"
            )
            return await message.reply(text=text_inst, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴋᴇᴍʙᴀʟɪ ᴋᴇ ᴘᴀɴᴇʟ", callback_data="back_panel", icon_custom_emoji_id=extract_id(Config.kembali))]]))

        elif txt.startswith("/bc"):
            if not message.reply_to_message: return await message.reply(f"<blockquote><b>{Config.peringatan} ʀᴇᴘʟʏ ᴘᴇsᴀɴ ʏᴀɴɢ ᴀᴋᴀɴ ᴅɪ-ʙʀᴏᴀᴅᴄᴀsᴛ!</b></blockquote>")
            users = await database.users_col.find().to_list(length=None)
            count = 0
            status_bc = await message.reply(f"<blockquote><b>{Config.roketputih} sᴇɴᴅɪɴɢ ʙʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ ᴜsᴇʀs...</b></blockquote>")
            for u in users:
                try:
                    await message.reply_to_message.forward(u['user_id'])
                    count += 1
                    await asyncio.sleep(0.05)
                except Exception as bce: pass
            return await status_bc.edit_text(f"<blockquote><b>{Config.centanghijau} ʙʀᴏᴀᴅᴄᴀsᴛ sᴇʟᴇsᴀɪ ᴋᴇ {count} ᴜsᴇʀ!</b></blockquote>")

        elif txt.startswith("/backup"):
            msg_backup = await message.reply(f"<blockquote><b>{Config.loading} ᴍᴇᴍᴘʀᴏsᴇs ʙᴀᴄᴋᴜᴘ ᴅᴀᴛᴀʙᴀsᴇ...</b></blockquote>")
            try:
                stocks = await database.stocks_col.find({}).to_list(length=None)
                backup_data = []
                for s in stocks:
                    s['_id'] = str(s['_id'])
                    s['created_at'] = s['created_at'].strftime('%Y-%m-%d %H:%M:%S') if 'created_at' in s else ""
                    s['sold_at'] = s['sold_at'].strftime('%Y-%m-%d %H:%M:%S') if 'sold_at' in s else ""
                    backup_data.append(s)
                
                file_name = f"backup_db_{int(time.time())}.json"
                with open(file_name, "w") as f: json.dump(backup_data, f, indent=4)
                    
                await client.send_document(chat_id=u_id, document=file_name, caption=f"<blockquote><b>{Config.backup} 𝗕𝗔𝗖𝗞𝗨𝗣 𝗗𝗔𝗧𝗔𝗕𝗔𝗦𝗘 𝗦𝗨𝗞𝗦𝗘𝗦</b>\nTotal Data: {len(backup_data)} Akun</blockquote>")
                os.remove(file_name)
                await msg_backup.delete()
            except Exception as e:
                await msg_backup.edit_text(f"<blockquote><b>{Config.silang} Gagal Backup: {e}</b></blockquote>")

        elif action == "wait_stok_data" and "|" in txt:
            lines = [l.strip() for l in txt.split("\n") if l.strip() and "|" in l]
            if not lines: return await message.reply(f"<blockquote><b>{Config.silang} ғᴏʀᴍᴀᴛ sᴀʟᴀʜ ᴀᴛᴀᴜ ᴋᴏsᴏɴɢ!</b>\nᴘᴀsᴛɪᴋᴀɴ ᴍᴇᴍᴀsᴜᴋᴋᴀɴ ғᴏʀᴍᴀᴛ ʏᴀɴɢ ᴠᴀʟɪᴅ.</blockquote>")
            
            bulk_queue_state[u_id] = []
            for line in lines:
                parts = line.split("|")
                if len(parts) >= 7: bulk_queue_state[u_id].append(line)
                else: await message.reply(f"{Config.silang} Baris dilewati karena format kurang (wajib 7 parameter): `{line}`")

            if not bulk_queue_state[u_id]: return await message.reply("Semua baris gagal diproses. Format salah.")
                
            user_states[u_id] = {"action": "process_bulk_queue"} 
            restock_summary[u_id] = {"count": 0, "items": {}} 
            
            await message.reply(f"<blockquote><b>{Config.loading} ᴍᴇᴍᴘʀᴏsᴇs ᴅᴀᴛᴀ ᴀɴᴛʀᴇᴀɴ... ({len(bulk_queue_state[u_id])} ᴀᴋᴜɴ)</b></blockquote>")
            await trigger_next_bulk_stok(client, message, u_id)
            return

        elif action == "wait_stok_otp":
            
            otp_code = re.sub(r'\D', '', txt)
            if not otp_code: return await message.reply(f"<blockquote><b>{Config.silang} KODE OTP HARUS ANGKA!</b>\nSilakan ketik ulang kode OTP-nya.</blockquote>")

            login_info = LoginState.get(u_id) if 'LoginState' in globals() else None
            if not login_info or "client" not in login_info:
                user_states.pop(u_id, None)
                return await message.reply(f"<blockquote><b>{Config.silang} sᴇsɪ ʜɪʟᴀɴɢ ᴀᴛᴀᴜ ᴇxᴘɪʀᴇᴅ!</b>\nsɪʟᴀʜᴋᴀɴ ɪɴᴘᴜᴛ ғᴏʀᴍᴀᴛ sᴛᴏᴋ ᴜʟᴀɴɢ ᴅᴀʀɪ ᴀᴡᴀʟ.</blockquote>")
                
            t_client = login_info["client"]
            msg_wait = await message.reply(f"<blockquote><b>{Config.loading} ᴠᴇʀɪғʏɪɴɢ ᴏᴛᴘ...</b>\nᴍᴇɴᴄᴏᴄᴏᴋᴋᴀɴ ᴋᴏᴅᴇ ᴅᴇɴɢᴀɴ sᴇʀᴠᴇʀ ᴛᴇʟᴇɢʀᴀᴍ.</blockquote>")
            
            try:
                from telethon import errors 
                await t_client.sign_in(phone=login_info.get("phone"), code=otp_code, phone_code_hash=login_info.get("hash"))
                await save_stok_final(client, t_client, login_info.get("data", []), u_id)
                
                queue = bulk_queue_state.get(u_id, []) if 'bulk_queue_state' in globals() else []
                if queue: queue.pop(0)
                if 'bulk_queue_state' in globals(): bulk_queue_state[u_id] = queue
                
                if queue:
                    await msg_wait.edit_text(f"<blockquote><b>{Config.centanghijau} sᴛᴏᴋ ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ!</b>\nᴏᴛᴏᴍᴀᴛɪs ʟᴀɴᴊᴜᴛ ᴋᴇ ᴀɴᴛʀᴇᴀɴ ʙᴇʀɪᴋᴜᴛɴʏᴀ... {Config.putar}</blockquote>")
                    await asyncio.sleep(1)
                    return await trigger_next_bulk_stok(client, message, u_id)
                else:
                    await msg_wait.edit_text(f"<blockquote><b>{Config.centanghijau} sᴛᴏᴋ ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ!</b>\nᴀɴᴛʀᴇᴀɴ sᴇʟᴇsᴀɪ.</blockquote>")
                    return await trigger_next_bulk_stok(client, message, u_id)

            except errors.PhoneCodeInvalidError:
                return await msg_wait.edit_text(f"<blockquote><b>{Config.silang} ᴏᴛᴘ sᴀʟᴀʜ ᴀᴛᴀᴜ ᴛʏᴘᴏ!</b>\n{Config.bulattitik} sɪʟᴀᴋᴀɴ ᴋᴇᴛɪᴋ ᴜʟᴀɴɢ ᴏᴛᴘ ʏᴀɴɢ ʙᴇɴᴀʀ (Lᴀɴɢsᴜɴɢ ᴋᴇᴛɪᴋ ᴀᴊᴀ):</blockquote>")
            except errors.PhoneCodeExpiredError:
                queue = bulk_queue_state.get(u_id, [])
                if queue: queue.pop(0)
                bulk_queue_state[u_id] = queue
                await msg_wait.edit_text(f"<blockquote><b>{Config.silang} ᴏᴛᴘ ᴋᴀᴅᴀʟᴜᴀʀsᴀ!</b>\nsᴋɪᴘ ᴋᴇ ᴀᴋᴜɴ ʙᴇʀɪᴋᴜᴛɴʏᴀ...</blockquote>")
                return await trigger_next_bulk_stok(client, message, u_id)
            except errors.SessionPasswordNeededError:
                try:
                    data_list = login_info.get("data", [])
                    auto_pass = str(data_list[5]).strip() if len(data_list) > 5 else ""
                    if not auto_pass or auto_pass == "-" or auto_pass.lower() == "none": raise ValueError("Password kosong")
                        
                    await t_client.sign_in(password=auto_pass)
                    await save_stok_final(client, t_client, data_list, u_id)
                    
                    queue = bulk_queue_state.get(u_id, [])
                    if queue: queue.pop(0)
                    bulk_queue_state[u_id] = queue
                    
                    if queue:
                        await msg_wait.edit_text(f"<blockquote><b>{Config.centanghijau} sᴛᴏᴋ ʙᴇʀʜᴀsɪʟ (ᴀᴜᴛᴏ 𝟸ғᴀ)!</b>\nᴏᴛᴏᴍᴀᴛɪs ʟᴀɴᴊᴜᴛ... {Config.putar}</blockquote>")
                        await asyncio.sleep(1)
                        return await trigger_next_bulk_stok(client, message, u_id)
                    else:
                        await msg_wait.edit_text(f"<blockquote><b>{Config.centanghijau} sᴛᴏᴋ ʙᴇʀʜᴀsɪʟ (ᴀᴜᴛᴏ 𝟸ғᴀ)!</b>\nᴀɴᴛʀᴇᴀɴ sᴇʟᴇsᴀɪ.</blockquote>")
                        return await trigger_next_bulk_stok(client, message, u_id)
                except Exception as auto_err:
                    user_states[u_id] = {"action": "wait_stok_pw"}
                    return await msg_wait.edit_text(f"<blockquote><b>{Config.gembok} 𝟸ғᴀ ᴀᴋᴛɪғ!</b>\nᴀᴋᴜɴ ᴍᴇᴍʙᴜᴛᴜʜᴋᴀɴ ᴘᴀssᴡᴏʀᴅ.\n{Config.bulattitik} ɪɴᴘᴜᴛ ᴘᴀssᴡᴏʀᴅ 𝟸ғᴀ sᴇᴄᴀʀᴀ ᴍᴀɴᴜᴀʟ (Lᴀɴɢsᴜɴɢ ᴋᴇᴛɪᴋ ᴀᴊᴀ):</blockquote>")
            except Exception as e:
                queue = bulk_queue_state.get(u_id, [])
                if queue: queue.pop(0)
                bulk_queue_state[u_id] = queue
                
                await msg_wait.edit_text(
                    f"<blockquote><b>{Config.peringatan} ᴇʀʀᴏʀ ɪɴᴛᴇʀɴᴀʟ ᴛᴇʟᴇɢʀᴀᴍ:</b>\n<code>{str(e)}</code>\n\n(sᴛᴏᴋ ᴅɪ-sᴋɪᴘ ᴋᴀʀᴇɴᴀ ᴇʀʀᴏʀ)</blockquote>", 
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="sᴋɪᴘ ᴋᴇ sᴛᴏᴋ sᴇʟᴀɴᴊᴜᴛɴʏᴀ", callback_data="next_bulk_stok", icon_custom_emoji_id=extract_id(Config.bulattitik) if 'extract_id' in globals() else None)]])
                )
                try: await t_client.disconnect()
                except: pass
                if 'LoginState' in globals(): LoginState.pop(u_id, None)

        elif action == "wait_stok_pw":
            login_info = LoginState.get(u_id) if 'LoginState' in globals() else None
            if not login_info or "client" not in login_info:
                user_states.pop(u_id, None)
                return await message.reply(f"<blockquote><b>{Config.silang} sᴇsɪ ʜɪʟᴀɴɢ!</b>\nsɪʟᴀʜᴋᴀɴ ɪɴᴘᴜᴛ sᴛᴏᴋ ᴜʟᴀɴɢ.</blockquote>")
            
            t_client = login_info["client"]
            msg_wait = await message.reply(f"<blockquote><b>{Config.loading} ᴄʜᴇᴄᴋɪɴɢ ᴘᴀssᴡᴏʀᴅ...</b>\nᴍᴇᴍᴠᴇʀɪғɪᴋᴀsɪ 𝟸ғᴀ ᴄʟᴏᴜᴅ ᴘᴀssᴡᴏʀᴅ.</blockquote>")
            
            try:
                clean_pw_manual = txt.strip()
                await t_client.sign_in(password=clean_pw_manual)
                await save_stok_final(client, t_client, login_info.get("data", []), u_id)
                
                queue = bulk_queue_state.get(u_id, [])
                if queue: queue.pop(0)
                bulk_queue_state[u_id] = queue
                
                if queue:
                    await msg_wait.edit_text(f"<blockquote><b>{Config.centanghijau} sᴛᴏᴋ ʙᴇʀʜᴀsɪʟ (ᴍᴀɴᴜᴀʟ 𝟸ғᴀ)!</b>\nᴏᴛᴏᴍᴀᴛɪs ʟᴀɴᴊᴜᴛ... {Config.putar}</blockquote>")
                    await asyncio.sleep(1)
                    return await trigger_next_bulk_stok(client, message, u_id)
                else:
                    await msg_wait.edit_text(f"<blockquote><b>{Config.centanghijau} sᴛᴏᴋ ʙᴇʀʜᴀsɪʟ (ᴍᴀɴᴜᴀʟ 𝟸ғᴀ)!</b>\nᴀɴᴛʀᴇᴀɴ sᴇʟᴇsᴀɪ.</blockquote>")
                    return await trigger_next_bulk_stok(client, message, u_id)
                    
            except Exception as e:
                if "password" in str(e).lower() and "invalid" in str(e).lower():
                     return await msg_wait.edit_text(f"<blockquote><b>{Config.silang} ᴘᴀssᴡᴏʀᴅ sᴀʟᴀʜ!</b>\nSɪʟᴀᴋᴀɴ ᴋᴇᴛɪᴋ ᴜʟᴀɴɢ ᴘᴀssᴡᴏʀᴅ ʏᴀɴɢ ʙᴇɴᴀʀ:</blockquote>")
                
                queue = bulk_queue_state.get(u_id, [])
                if queue: queue.pop(0)
                bulk_queue_state[u_id] = queue
                
                await msg_wait.edit_text(
                    text=f"<blockquote><b>{Config.silang} ɢᴀɢᴀʟ ʟᴏɢɪɴ 𝟸ғᴀ:</b>\n<code>{str(e).lower()}</code></blockquote>",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="sᴋɪᴘ ᴋᴇ sᴛᴏᴋ sᴇʟᴀɴᴊᴜᴛɴʏᴀ", callback_data="next_bulk_stok", icon_custom_emoji_id=extract_id(Config.bulattitik) if 'extract_id' in globals() else None)]])
                )
                try: await t_client.disconnect()
                except: pass
                if 'LoginState' in globals(): LoginState.pop(u_id, None)


# ============================================================
# FUNGSI SAVE STOK FINAL (SUDAH AMAN & LOG JALAN 100%)
# ============================================================
async def save_stok_final(client_pyro: Client, t_client: TelegramClient, p: list, u_id: int):
    try:
        if not p or len(p) < 7:
            print(f"Error Save Stok: Data list 'p' tidak lengkap (terdeteksi hanya {len(p) if p else 0} elemen).")
            return

        try:
            from telethon.tl.functions.account import GetPasswordRequest
            pwd_info = await t_client(GetPasswordRequest())
            email_status = "ON (Aktif)" if pwd_info.has_recovery else "OFF (Kosong)"
        except Exception as err:
            email_status = "OFF (Tidak Ada)"

        session_str = t_client.session.save()
        
        uid_full = str(p[0]).strip()
        dc_val = str(p[1]).strip()
        phone = str(p[2]).strip()
        limit_val = str(p[3]).strip().upper()
        benefit_val = str(p[4]).strip()
        password_val = str(p[5]).strip()
        
        try:
            custom_price = int(str(p[6]).strip())
        except ValueError:
            custom_price = 0
        
        prefix_uid = uid_full[0] if len(uid_full) > 0 else "0"
        label_fix = Config.LABELS.get(prefix_uid, f"Id {prefix_uid}xxx")
        
        region_flag, region_code = get_auto_region(phone)
        
        tipe_tag_lower = benefit_val.lower()
        if "fake" in tipe_tag_lower:
            tipe_tag_db = "fake"
        elif "scam" in tipe_tag_lower:
            tipe_tag_db = "scam"
        else:
            tipe_tag_db = "polos"

        stok_obj = {
            "uid": uid_full, 
            "dc": dc_val, 
            "phone": phone, 
            "region": region_flag,
            "region_code": region_code,
            "limit": limit_val, 
            "email": email_status, 
            "benefit": benefit_val,
            "password": password_val, 
            "custom_price": custom_price,
            "tipe_tag": tipe_tag_db,
            "label": label_fix, 
            "session": session_str, 
            "status": "ready", 
            "is_sold": False, 
        }
        
        # FIX FATAL ERROR: Ganti ke format insert_one yang bener!
        await database.stocks_col.insert_one(stok_obj) 
        
        # FIX LOGIC LOG: Memastikan wadah summary selalu terisi untuk dikirim ke channel
        if u_id in restock_summary: 
            restock_summary[u_id]["count"] += 1
            
            if "items" not in restock_summary[u_id]:
                restock_summary[u_id]["items"] = {}

            group_key = f"{region_code}_{limit_val}_{prefix_uid}_{dc_val}"
            if group_key not in restock_summary[u_id]["items"]:
                restock_summary[u_id]["items"][group_key] = {
                    "count": 0, "region": region_flag, "limit": limit_val,
                    "prefix": prefix_uid, "dc": dc_val, "price": custom_price
                }
            restock_summary[u_id]["items"][group_key]["count"] += 1
           
            
    except Exception as e:
        import traceback
        print(f"Error Save Stok: {e}")
        traceback.print_exc()
    finally:
        try: await t_client.disconnect()
        except: pass
        if 'LoginState' in globals(): LoginState.pop(u_id, None)



if __name__ == "__main__":
    BLUE = "\033[94m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    print(f"{CYAN}{'=' * 75}{RESET}")
    print(f" {BLUE}{BOLD}🚀 ( ʙᴏᴛ ᴠᴠɪᴘ ᴇɴᴛᴇʀᴘʀɪsᴇ ʙᴇʀʜᴀsɪʟ ᴅɪ ᴀᴋᴛɪꜰᴋᴀɴ ) 🚀{RESET} ")
    print(f" {YELLOW}© Cᴏᴘʏʀɪɢʜᴛ Sʏsᴛᴇᴍ: Iǫʙᴀʟ Zᴏɴᴇ | Vᴇʀsɪᴏɴ: 36.0 Pʀᴏ Mᴀx{RESET}")
    print(f" {RED}ᴅᴇᴠ: @Zyexe | @Zyexe{RESET} ")
    print(f" {BLUE}ᴍᴇᴍᴘʀᴏsᴇs ᴘᴇɴɢᴀᴍʙɪʟᴀɴ sᴛᴏᴋ ᴜʟᴀɴɢ ᴅᴀʀɪ ᴍᴏɴɢᴏᴅʙ...{RESET} ")
    print(f"{CYAN}{'=' * 75}{RESET}")
    
    try:
        bot.run()
    except Exception as run_err:
        print(f"\n{RED}{BOLD}❗ CRITICAL FATAL ERROR (BOT CRASHED): {run_err}{RESET}")
        print(f"Silahkan cek konfigurasi API atau koneksi jaringan VPS Anda.\n") 