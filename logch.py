import logging
import re
import traceback
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ɪǫʙᴀʟsʜᴏᴘ_ʟᴏɢ")

def extract_id(emoji_val):
    if not emoji_val: return None
    match = re.search(r'\d+', str(emoji_val))
    return int(match.group()) if match else None

# Helper untuk ubah teks jadi smallcaps (hanya untuk barang/region)
def to_smallcaps(text):
    trans = str.maketrans(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", 
        "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
    )
    return str(text).translate(trans)

# Helper buat ngirim ke Owner kalau Channel Log gagal
async def send_fallback_to_owner(client: Client, text: str, btns=None):
    try:
        owners = Config.OWNER_ID if isinstance(Config.OWNER_ID, list) else [Config.OWNER_ID]
        if owners:
            await client.send_message(
                chat_id=owners[0], 
                text=f"⚠️ <b>𝗙𝗔𝗜𝗟 𝗦𝗘𝗡𝗗 𝗟𝗢𝗚 𝗖𝗛𝗔𝗡𝗡𝗘𝗟!</b>\n<i>Laporan diteruskan ke Admin:</i>\n\n{text}", 
                reply_markup=btns
            )
    except Exception as e:
        logger.error(f"Fallback ke Owner juga gagal: {e}")

class Logger:
    @staticmethod
    async def log_new_user(client: Client, user_id: int, name: str, username: str):
        try:
            uname_text = f"@{username}" if username else "ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴜsᴇʀɴᴀᴍᴇ"
            # 🔥 FIX: Hapus smallcaps untuk nama orang
            
            text = (
                f"<blockquote><b>{Config.roketputih} 𝗨𝗦𝗘𝗥 𝗝𝗢𝗜𝗡 𝗕𝗢𝗧</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"├⌑ {Config.orang} ɴᴀᴍᴀ : <b>{name}</b>\n"
                f"├⌑ {Config.uid} ᴜsᴇʀ ɪᴅ : <code>{user_id}</code>\n"
                f"╰⌑ {Config.globe} ᴜsᴇʀɴᴀᴍᴇ : <b>{uname_text}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"📅 <b>ᴡᴀᴋᴛᴜ ᴊᴏɪɴ :</b>\n"
                f"<i>{datetime.now(WIB).strftime('%A, %d %B %Y | %H:%M WIB')}</i>\n\n"
                f"🍂 <b>ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ʙᴏᴛ ɴᴏᴋᴛᴇʟ ʙʏ ᴢʏᴇɢʀᴀᴍ!</b></blockquote>"
            )
            
            btns = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "ᴄᴇᴋ ᴘʀᴏғɪʟ", 
                    url=f"tg://openmessage?user_id={user_id}",
                    icon_custom_emoji_id=extract_id(Config.mata)
                )
            ]])
            
            try:
                await client.send_message(Config.ID_CH_LOG, text, reply_markup=btns)
            except Exception as e:
                logger.warning(f"ID_CH_LOG gagal: {e}. Coba via Username Channel...")
                try:
                    await client.send_message(f"@{Config.CHANNEL_USERNAME}", text, reply_markup=btns)
                except:
                    await send_fallback_to_owner(client, text, btns)
                
            logger.info(f"✅ Log New User terkirim untuk {user_id}")
        except Exception as e:
            logger.error(f"❌ Gagal kirim log new user: {e}")

    @staticmethod
    async def log_addzip_summary(client: Client, count: int, item_name: str, prefix_id: str, price: int, owner_username: str, region: str):
        target_channel = getattr(Config, 'ID_CH_LOG_ADDZIP', getattr(Config, 'ID_CH_LOG', None))
        if not target_channel: return
            
        try:
            bot_info = await client.get_me()
            # 🔥 FIX: Hapus ?start=open_store jadi ?start=start biasa
            bot_link = f"https://t.me/{bot_info.username}?start=start"
            
            region_smallcaps = to_smallcaps(region)
            item_name_sc = to_smallcaps(item_name)
            id_display = f"{prefix_id}xxx" if prefix_id else "ᴜɴᴋɴᴏᴡɴ"

            text = (
                f"<blockquote><b>{Config.bintang} 𝗦𝗧𝗢𝗞 𝗭𝗜𝗣 𝗕𝗔𝗥𝗨 𝗠𝗔𝗦𝗨𝗞 {Config.bintang}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"ᴋᴀʙᴀʀ ʙᴀɪᴋ! ʀɪʙᴜᴀɴ sᴛᴏᴋ ᴀᴋᴜɴ ɴᴏᴋᴛᴇʟ ᴠɪᴀ ᴢɪᴘ ᴛᴇʟᴀʜ ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ.\n\n"
                f"{Config.saldouser} <b>ɪɴғᴏʀᴍᴀsɪ ᴘʀᴏᴅᴜᴋ (ᴢɪᴘ) :</b>\n"
                f"├⌑ {Config.market} ᴋᴀᴛᴇɢᴏʀɪ : <b>{item_name_sc}</b>\n"
                f"├⌑ {Config.globe} ɴᴇɢᴀʀᴀ : <b>{region_smallcaps}</b>\n"
                f"├⌑ {Config.uid} ɪᴅ ᴀᴋᴜɴ : <b>{id_display}</b>\n"
                f"├⌑ {Config.taskarung} ʜᴀʀɢᴀ/ᴀᴋᴜɴ : <b>ʀᴘ {price:,}</b>\n"
                f"╰⌑ {Config.box} ᴛᴏᴛᴀʟ ᴍᴀsᴜᴋ : <b>{count} ᴀᴋᴜɴ ʀᴇᴀᴅʏ</b>\n\n"
                f"{Config.mahkota} <i>ᴅɪ-sᴜᴘᴘʟʏ ᴏʟᴇʜ : {owner_username}</i>\n\n"
                f"{Config.jampasir} <i>ɢᴀs ᴄʜᴇᴄᴋᴏᴜᴛ sᴇᴋᴀʀᴀɴɢ ᴠɪᴀ ᴛᴏᴍʙᴏʟ ᴅɪ ʙᴀᴡᴀʜ!</i></blockquote>"
            ).replace(',', '.')
            
            btns = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "ʙᴇʟᴀɴᴊᴀ sᴇᴋᴀʀᴀɴɢ", 
                    url=bot_link,
                    icon_custom_emoji_id=extract_id(Config.keranjang)
                )
            ]])
            
            try:
                await client.send_message(chat_id=target_channel, text=text, reply_markup=btns, disable_web_page_preview=True)
            except Exception:
                await send_fallback_to_owner(client, text, btns)
        except Exception as e:
            logger.error(f"Gagal kirim log addzip summary: {e}")

    @staticmethod
    async def log_system_action(client: Client, admin_name: str, admin_id: int, fitur_target: str, status_text: str):
        try:
            if not hasattr(Config, 'ID_CH_LOG') or not Config.ID_CH_LOG: return

            waktu_sekarang = datetime.now(WIB).strftime("%d %B %Y | %H:%M WIB")
            fitur_sc = to_smallcaps(fitur_target)
            status_sc = to_smallcaps(status_text)

            log_text = (
                f"<blockquote><b>{Config.proteksi} 𝗦𝗜𝗦𝗧𝗘𝗠 𝗞𝗢𝗡𝗧𝗥𝗢𝗟 𝗙𝗜𝗧𝗨𝗥</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"ᴀᴅᴍɪɴ ᴍᴇɴɢᴜʙᴀʜ ᴀᴋsᴇs ꜰɪᴛᴜʀ ʙᴏᴛ!\n\n"
                f"{Config.mahkota} ᴀᴅᴍɪɴ ᴇxᴇᴄ  : <b>{admin_name}</b> (<code>{admin_id}</code>)\n"
                f"{Config.rodaputarputih} ꜰɪᴛᴜʀ       : <b>{fitur_sc}</b>\n"
                f"{Config.statistik} sᴛᴀᴛᴜs      : <b>{status_sc}</b>\n"
                f"{Config.jampasir} ᴡᴀᴋᴛᴜ       : {waktu_sekarang}\n"
                f"━━━━━━━━━━━━━━━━━━━━━</blockquote>"
            )
            try:
                await client.send_message(Config.ID_CH_LOG, log_text)
            except:
                await send_fallback_to_owner(client, log_text)
        except Exception as e:
            logger.error(f"❌ Gagal mengirim log system action: {e}")
            
    @staticmethod
    async def log_deposit(client: Client, user_id: int, name: str, amount: int, oid: str, method: str = "ǫʀɪs"):
        try:
            method_sc = to_smallcaps(method)
            text = (
                f"<blockquote><b>{Config.kredit} 𝗗𝗘𝗣𝗢𝗦𝗜𝗧 𝗦𝗨𝗞𝗦𝗘𝗦</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"├⌑ {Config.notasi} ᴏɪᴅ : <code>{oid}</code>\n"
                f"├⌑ {Config.orang} ʙᴜʏᴇʀ : <b>{name}</b>\n"
                f"├⌑ {Config.uid} ᴜsᴇʀ ɪᴅ : <code>{user_id}</code>\n"
                f"├⌑ {Config.taskarung} ᴊᴜᴍʟᴀʜ : <b>ʀᴘ {amount:,} sᴀʟᴅᴏ</b>\n"
                f"╰⌑ {Config.bank} ᴍᴇᴛᴏᴅᴇ : <b>{method_sc}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"{Config.centanghijau} sᴛᴀᴛᴜs : <b>ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ</b>\n"
                f"{Config.tanggal} ᴡᴀᴋᴛᴜ : <b>{datetime.now(WIB).strftime('%Y-%m-%d | %H:%M WIB')}</b></blockquote>"
            ).replace(',', '.')
            try:
                await client.send_message(Config.ID_CH_LOG, text)
            except:
                try:
                    await client.send_message(f"@{Config.CHANNEL_USERNAME}", text)
                except:
                    await send_fallback_to_owner(client, text)
        except Exception as e:
            logger.error(f"❌ Gagal kirim log deposit: {e}")

    @staticmethod
    async def log_restock_summary(client: Client, count: int, item_name: str, prefix_id: str, price: int, owner_username: str, region: str):
        if not hasattr(Config, 'ID_CH_LOG') or not Config.ID_CH_LOG: return
            
        try:
            bot_info = await client.get_me()
            # 🔥 FIX: Hapus ?start=open_store jadi ?start=start biasa
            bot_link = f"https://t.me/{bot_info.username}?start=start"
            
            region_smallcaps = to_smallcaps(region)
            item_name_sc = to_smallcaps(item_name)
            id_display = f"{prefix_id}xxx" if prefix_id else "ᴜɴᴋɴᴏᴡɴ"

            text = (
                f"<blockquote><b>{Config.bintang} 𝗦𝗧𝗢𝗞 𝗕𝗔𝗥𝗨 𝗧𝗘𝗥𝗦𝗘𝗗𝗜𝗔 {Config.bintang}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"ᴋᴀʙᴀʀ ʙᴀɪᴋ! sᴛᴏᴋ ᴀᴋᴜɴ ɴᴏᴋᴛᴇʟ ᴛᴇʀʙᴀʀᴜ ᴛᴇʟᴀʜ ʙᴇʀʜᴀsɪʟ ᴅɪᴛᴀᴍʙᴀʜᴋᴀɴ ᴋᴇ ᴅᴀʟᴀᴍ ᴅᴀᴛᴀʙᴀsᴇ ᴋᴀᴍɪ. sɪʟᴀʜᴋᴀɴ sᴇɢᴇʀᴀ ᴍᴇʟᴀᴋᴜᴋᴀɴ ᴘᴇᴍᴇsᴀɴᴀɴ sᴇʙᴇʟᴜᴍ ᴘᴇʀsᴇᴅɪᴀᴀɴ ʜᴀʙɪs {Config.roketputih}\n\n"
                f"{Config.saldouser} <b>ɪɴғᴏʀᴍᴀsɪ ᴘʀᴏᴅᴜᴋ :</b>\n"
                f"├⌑ {Config.market} ᴋᴀᴛᴇɢᴏʀɪ : <b>{item_name_sc}</b>\n"
                f"├⌑ {Config.globe} ɴᴇɢᴀʀᴀ : <b>{region_smallcaps}</b>\n"
                f"├⌑ {Config.uid} ɪᴅ ᴀᴋᴜɴ : <b>{id_display}</b>\n"
                f"╰⌑ {Config.box} ᴛᴏᴛᴀʟ ᴍᴀsᴜᴋ : <b>{count} ᴀᴋᴜɴ ʀᴇᴀᴅʏ</b>\n\n"
                f"{Config.mahkota} <i>ᴅɪ-sᴜᴘᴘʟʏ ᴏʟᴇʜ : {owner_username}</i>\n\n"
                f"{Config.jampasir} <i>ɢᴀs ᴄʜᴇᴄᴋᴏᴜᴛ sᴇᴋᴀʀᴀɴɢ ᴠɪᴀ ᴛᴏᴍʙᴏʟ ᴅɪ ʙᴀᴡᴀʜ!</i></blockquote>"
            )
            
            btns = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "ʙᴇʟᴀɴᴊᴀ sᴇᴋᴀʀᴀɴɢ", 
                    url=bot_link,
                    icon_custom_emoji_id=extract_id(Config.keranjang)
                )
            ]])
            
            try:
                await client.send_message(chat_id=Config.ID_CH_LOG, text=text, reply_markup=btns, disable_web_page_preview=True)
            except:
                await send_fallback_to_owner(client, text, btns)
        except Exception as e:
            logger.error(f"Gagal kirim log restock summary: {e}")

    @staticmethod
    async def log_buy_stok(client: Client, user_id: int, name: str, stok: dict, oid: str, method: str = "ǫʀɪs", qty: int = 1, total_harga: int = 0):
        try:
            bot_info = await client.get_me()
            bot_username = bot_info.username
            
            dc_val = str(stok.get('dc', '1'))
            label_val = to_smallcaps(stok.get('label', 'ᴀᴋᴜɴ ɴᴏᴋᴛᴇʟ'))
            region_val = to_smallcaps(stok.get('region', 'ᴜɴᴋɴᴏᴡɴ'))
            limit_val = str(stok.get('limit', 'OFF')).upper()
            
            if limit_val == "ON":
                tipe_akun = f"{label_val} (ʟɪᴍᴘᴇʀ | ᴅᴄ {dc_val})"
            else:
                tipe_akun = f"{label_val} (ɴᴏ ᴍɪɴᴜs | ᴅᴄ {dc_val})"
                
            region_code = str(stok.get('region_code', 'DEFAULT')).upper()
            
            if not region_code or region_code == "DEFAULT":
                raw_region = str(stok.get('region', 'INDONESIA')).upper()
                if "MALAYSIA" in raw_region: region_code = "MY"
                elif "THAILAND" in raw_region: region_code = "TH"
                elif "FILIPINA" in raw_region or "PHILIPPINES" in raw_region: region_code = "PH"
                elif "VIETNAM" in raw_region: region_code = "VN"
                elif "AMERIKA" in raw_region or "USA" in raw_region: region_code = "US"
                else: region_code = "ID"
            
            bold_map = {
                'A': '𝗔', 'B': '𝗕', 'C': '𝗖', 'D': '𝗗', 'E': '𝗘', 'F': '𝗙', 'G': '𝗚', 'H': '𝗛', 'I': '𝗜',
                'J': '𝗝', 'K': '𝗞', 'L': '𝗟', 'M': '𝗠', 'N': '𝗡', 'O': '𝗢', 'P': '𝗣', 'Q': '𝗤', 'R': '𝗥',
                'S': '𝗦', 'T': '𝗧', 'U': '𝗨', 'V': '𝗩', 'W': '𝗪', 'X': '𝗫', 'Y': '𝗬', 'Z': '𝗭'
            }
            prefix = "".join(bold_map.get(char, char) for char in region_code)
            
            if total_harga == 0:
                try:
                    harga_satuan = stok.get('custom_price', 0)
                    if not harga_satuan:
                        uid_str = str(stok.get('uid', '0'))
                        pref_val = uid_str[0] if uid_str else "0"
                        config_region_val = str(stok.get('region', 'DEFAULT')).upper()
                        is_limper = (limit_val == "ON")
                        harga_satuan = Config.get_price(pref_val, dc_val, config_region_val, is_limper)
                    total_harga = harga_satuan * qty
                except Exception as e:
                    logger.error(f"Gagal narik harga dari Config di Log Buy Stok: {e}")
                    total_harga = 0 

            WaktuFormatStruk = datetime.now(WIB).strftime("%d %B %Y | %H:%M WIB")

            text = (
                f"<blockquote>"
                f"{Config.notasi} <b>𝗦𝗧𝗥𝗨𝗞 𝗣𝗘𝗠𝗕𝗘𝗟𝗜𝗔𝗡 𝗣𝗥𝗢𝗗𝗨𝗞</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"{Config.orang} <b>ɪᴅᴇɴᴛɪᴛᴀs ᴘᴇᴍʙᴇʟɪ</b>\n"
                f"├⌑ {Config.orangtanpaplus} ɴᴀᴍᴀ : <b>{name}</b>\n"
                f"╰⌑ {Config.uid} ɪᴅ : <code>{user_id}</code>\n\n"
                f"{Config.saldouser} <b>ᴅᴀᴛᴀ ᴘʀᴏᴅᴜᴋ</b>\n"
                f"├⌑ {Config.keranjang} ᴘʀᴏᴅᴜᴋ : <b>{tipe_akun}</b>\n"
                f"├⌑ {Config.globe} ɴᴇɢᴀʀᴀ : <b>{region_val}</b>\n"
                f"├⌑ {Config.uid} ᴘʀᴇғɪx : <b>{prefix}</b>\n"
                f"├⌑ {Config.box} ᴊᴜᴍʟᴀʜ : <b>{qty} ᴀᴋᴜɴ</b>\n"
                f"├⌑ {Config.taskarung} ʜᴀʀɢᴀ : <b>ʀᴘ {total_harga:,}</b>\n"
                f"╰⌑ {Config.tanggal} ᴡᴀᴋᴛᴜ : <b>{WaktuFormatStruk}</b>\n\n"
                f"{Config.pesan} <b>ᴛᴇʀɪᴍᴀᴋᴀsɪʜ sᴜᴅᴀʜ ʙᴇʟᴀɴᴊᴀ</b>\n"
                f"</blockquote>"
            ).replace(',', '.') 
            
            btns = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "ʙᴇʟɪ ᴀᴋᴜɴ ʟᴀɢɪ", 
                    # 🔥 FIX: Hapus ?start=open_store jadi ?start=start biasa
                    url=f"https://t.me/{bot_username}?start=start",
                    icon_custom_emoji_id=extract_id(Config.keranjang)
                )
            ]])

            try:
                await client.send_message(Config.ID_CH_LOG, text, reply_markup=btns)
            except Exception as e1:
                logger.warning(f"Gagal kirim log via ID: {e1}. Mencoba via username...")
                try:
                    await client.send_message(f"@{Config.CHANNEL_USERNAME}", text, reply_markup=btns)
                except Exception as e2:
                    logger.warning(f"Gagal kirim log via Username: {e2}. Mengirim ke Owner...")
                    await send_fallback_to_owner(client, text, btns)
                
            logger.info(f"✅ [LOG SUCCESS] OID: {oid} | Buyer: {user_id} | Qty: {qty} | Total Harga: {total_harga}")
            
        except Exception as e:
            err_detail = traceback.format_exc()
            logger.error(f"❌ [LOG ERROR FATAL] Gagal eksekusi log_buy_stok:\n{err_detail}")

    @staticmethod
    async def log_buy_script(client: Client, user_id: int, buyer_username: str, script_role: str, price: int):
        try:
            bot_info = await client.get_me()
            bot_username = bot_info.username
            
            role_sc = to_smallcaps(script_role)
            
            text = (
                f"<blockquote><b>{Config.taskarung} 𝗧𝗥𝗔𝗡𝗦𝗔𝗞𝗦𝗜 𝗗𝗢𝗡𝗘</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"├⌑ {Config.box} ᴘʀᴏᴅᴜᴋ : <b>sᴄʀɪᴘᴛ ʙᴏᴛ ᴠᴠɪᴘ</b>\n"
                f"├⌑ {Config.orang} ʙᴜʏᴇʀ : <b>@{buyer_username}</b>\n"
                f"├⌑ {Config.uid} ᴜsᴇʀ ɪᴅ : <code>{user_id}</code>\n"
                f"├⌑ {Config.mahkota} ʀᴏʟᴇ : <b>{role_sc}</b>\n"
                f"╰⌑ {Config.dolar} ʜᴀʀɢᴀ : <b>ʀᴘ {price:,}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"{Config.centanghijau} sᴛᴀᴛᴜs : <b>ʟᴜɴᴀs (sᴄʀɪᴘᴛ sᴇɴᴛ)</b>\n"
                f"{Config.tanggal} ᴡᴀᴋᴛᴜ : <b>{datetime.now(WIB).strftime('%Y-%m-%d | %H:%M WIB')}</b></blockquote>"
            ).replace(',', '.')
            
            btns = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "ᴋᴇ ʙᴏᴛ sᴇᴋᴀʀᴀɴɢ", 
                    url=f"https://t.me/{bot_username}?start=start",
                    icon_custom_emoji_id=extract_id(Config.roketputih)
                )
            ]])

            try:
                await client.send_message(Config.ID_CH_LOG, text, reply_markup=btns)
            except:
                try:
                    await client.send_message(f"@{Config.CHANNEL_USERNAME}", text, reply_markup=btns)
                except:
                    await send_fallback_to_owner(client, text, btns)
        except Exception as e:
            logger.error(f"Gagal kirim log script: {e}")

    @staticmethod
    async def log_ubah_harga_bulk(client: Client, prefix: str, region: str, limit_text: str, new_price: int, count: int):
        if not hasattr(Config, 'ID_CH_LOG') or not Config.ID_CH_LOG: return
            
        try:
            bot_info = await client.get_me()
            # 🔥 FIX: Hapus ?start=open_store jadi ?start=start biasa
            bot_link = f"https://t.me/{bot_info.username}?start=start"
            
            limit_sc = to_smallcaps(limit_text)
            region_sc = to_smallcaps(region)
            
            text = (
                f"<blockquote><b>{Config.bintang} 𝗛𝗔𝗥𝗚𝗔 𝗔𝗞𝗨𝗡 𝗗𝗜𝗨𝗕𝗔𝗛 (𝗠𝗔𝗦𝗦𝗔𝗟) {Config.bintang}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"ɪɴғᴏʀᴍᴀsɪ ᴘᴇʀᴜʙᴀʜᴀɴ ʜᴀʀɢᴀ ᴇᴛᴀʟᴀsᴇ ᴛᴇʀʙᴀʀᴜ:\n\n"
                f"├⌑ {Config.market} ᴋᴀᴛᴇɢᴏʀɪ : <b>{limit_sc}</b>\n"
                f"├⌑ {Config.globe} ɴᴇɢᴀʀᴀ : <b>{region_sc}</b>\n"
                f"├⌑ {Config.uid} ᴘʀᴇғɪx : <b>{prefix}</b>\n"
                f"├⌑ {Config.tumpukanuang} ʜᴀʀɢᴀ ʙᴀʀᴜ : <b>ʀᴘ {new_price:,}</b>\n"
                f"╰⌑ {Config.box} ᴛᴏᴛᴀʟ ᴀᴋᴜɴ : <b>{count} ᴀᴋᴜɴ</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"{Config.jampasir} <i>sɪʟᴀʜᴋᴀɴ ᴄᴇᴋ ᴇᴛᴀʟᴀsᴇ sᴇᴋᴀʀᴀɴɢ!</i></blockquote>"
            ).replace(',', '.')
            
            btns = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "ᴄᴇᴋ ᴇᴛᴀʟᴀsᴇ sᴇᴋᴀʀᴀɴɢ", 
                    url=bot_link,
                    icon_custom_emoji_id=extract_id(Config.keranjang)
                )
            ]])
            
            try:
                await client.send_message(Config.ID_CH_LOG, text, reply_markup=btns, disable_web_page_preview=True)
            except:
                await send_fallback_to_owner(client, text, btns)
        except Exception as e:
            print(f"Gagal log ubah harga massal: {e}")

    @staticmethod
    async def log_ubah_harga(client: Client, uid: str, old_price: int, new_price: int, region: str = "TIDAK DIKETAHUI", kategori: str = "AKUN NOKTEL"):
        if not hasattr(Config, 'ID_CH_LOG') or not Config.ID_CH_LOG: return
            
        try:
            bot_info = await client.get_me()
            # 🔥 FIX: Hapus ?start=open_store jadi ?start=start biasa
            bot_link = f"https://t.me/{bot_info.username}?start=start"
            
            diff = new_price - old_price
            if diff < 0:
                status_diff = f"{Config.stats_turun} sᴛᴀᴛᴜs : <b>ᴛᴜʀᴜɴ ʀᴘ {abs(diff):,}</b>"
            elif diff > 0:
                status_diff = f"{Config.stats_naik} sᴛᴀᴛᴜs : <b>ɴᴀɪᴋ ʀᴘ {diff:,}</b>"
            else:
                return 
                
            region_sc = to_smallcaps(region)
            kategori_sc = to_smallcaps(kategori)
                
            text = (
                f"<blockquote><b>{Config.bintang} 𝗛𝗔𝗥𝗚𝗔 𝗔𝗞𝗨𝗡 𝗗𝗜𝗨𝗕𝗔𝗛 (𝗦𝗔𝗧𝗨𝗔𝗡) {Config.bintang}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"ɪɴғᴏʀᴍᴀsɪ ᴘᴇʀᴜʙᴀʜᴀɴ ʜᴀʀɢᴀ sᴛᴏᴋ ᴛᴇʀʙᴀʀᴜ:\n\n"
                f"├⌑ {Config.market} ᴋᴀᴛᴇɢᴏʀɪ : <b>{kategori_sc}</b>\n"
                f"├⌑ {Config.globe} ɴᴇɢᴀʀᴀ : <b>{region_sc}</b>\n"
                f"├⌑ {Config.uid} ɪᴅ ᴀᴋᴜɴ : <code>{uid}</code>\n"
                f"├⌑ {Config.taskarung} ʜᴀʀɢᴀ ᴀᴡᴀʟ : <b>ʀᴘ {old_price:,}</b>\n"
                f"├⌑ {Config.tumpukanuang} ʜᴀʀɢᴀ ʙᴀʀᴜ : <b>ʀᴘ {new_price:,}</b>\n"
                f"╰⌑ {status_diff}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
                f"{Config.jampasir} <i>sɪʟᴀʜᴋᴀɴ ᴄᴇᴋ ᴇᴛᴀʟᴀsᴇ sᴇᴋᴀʀᴀɴɢ!</i></blockquote>"
            ).replace(',', '.')
            
            btns = InlineKeyboardMarkup([[
                InlineKeyboardButton(
                    "ᴄᴇᴋ ᴇᴛᴀʟᴀsᴇ sᴇᴋᴀʀᴀɴɢ", 
                    url=bot_link,
                    icon_custom_emoji_id=extract_id(Config.keranjang)
                )
            ]])
            
            try:
                await client.send_message(Config.ID_CH_LOG, text, reply_markup=btns, disable_web_page_preview=True)
            except:
                await send_fallback_to_owner(client, text, btns)
        except Exception as e:
            print(f"Gagal log ubah harga: {e}")
