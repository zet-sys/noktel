# ==============================================================================
# Dev : @supiqbalubot
# ==============================================================================

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from bson.errors import InvalidId
from config import Config
from datetime import datetime, timezone, timedelta

# ============================================================
# 🕒 ZONA WAKTU & KONFIGURASI LOGGER
# ============================================================
# Setting Waktu Indonesia Barat (WIB)
WIB = timezone(timedelta(hours=7))

# Konfigurasi Log agar error/info terlihat rapi di terminal VPS
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ɪǫʙᴀʟ_ᴅᴀᴛᴀʙᴀsᴇ")

# ============================================================
# 🔌 INISIALISASI KONEKSI MONGODB
# ============================================================

# Definisi Warna untuk Database
RED     = "\033[91m"
YELLOW  = "\033[93m"
RESET   = "\033[0m"
BOLD    = "\033[1m"

try:
    # Membuka koneksi ke server MongoDB Async
    client = AsyncIOMotorClient(Config.MONGO_URL)
    db = client[Config.DB_NAME]
    
    # Koleksi / Tabel Database
    users_col = db["users"]
    stocks_col = db["stocks"]
    bulk_sessions = db["bulk_sessions"]
    script_sales = db["script_sales"] # 🔥 TAMBAHAN UNTUK REKAP JUAL SCRIPT
    
    # Log Sukses (KUNING)
    logger.info(f"{YELLOW}{BOLD}✅ ᴍᴏɴɢᴏᴅʙ ᴄᴏɴɴᴇᴄᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!{RESET}")

except Exception as e:
    # Log Gagal (MERAH)
    logger.critical(f"{RED}{BOLD}❌ ᴍᴏɴɢᴏᴅʙ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ғᴀɪʟᴇᴅ. ᴄᴇᴋ ᴜʀʟ ᴍᴏɴɢᴏ ᴀɴᴅᴀ. Error: {e}{RESET}")

    
# ============================================================
# 👥 USER MANAGEMENT & SALDO (DEPOSIT) SYSTEM
# ============================================================

async def get_user(user_id):
    """
    Mengambil data user dari database.
    Jika belum ada, otomatis membuat data baru dengan saldo 0.
    
    RETURN: (user_data: dict, is_new_user: bool)
    Penjelasan: is_new_user (True) berfungsi memicu Log Welcome 1x di Main Menu.
    """
    try:
        user = await users_col.find_one({"user_id": int(user_id)})
        if not user:
            # Format Data User Baru
            new_user = {
                "user_id": int(user_id), 
                "balance": 0,          
                "total_order": 0,      
                "status": "member",
                "joined_at": datetime.now(WIB)
            }
            await users_col.insert_one(new_user)
            logger.info(f"🆕 User Baru Terdaftar di Database: {user_id}")
            return new_user, True # True = Pendaftar Baru
            
        return user, False # False = User Lama
    except Exception as e:
        logger.error(f"❌ Error pada fungsi get_user ({user_id}): {e}")
        return None, False

async def get_all_users():
    """Mengambil semua data user (Biasanya dipakai untuk Broadcast Admin)"""
    try:
        return await users_col.find({}).to_list(length=None)
    except Exception as e:
        logger.error(f"❌ Error pada fungsi get_all_users: {e}")
        return []

async def update_balance(user_id, amount):
    """
    Menambahkan saldo ke user (SISTEM DEPOSIT).
    Aman menggunakan $inc (Increment), sehingga tidak akan menimpa saldo saat ini.
    """
    try:
        await users_col.update_one(
            {"user_id": int(user_id)},
            {"$inc": {"balance": int(amount)}}, 
            upsert=True
        )
        # Verifikasi saldo terbaru setelah deposit
        user = await users_col.find_one({"user_id": int(user_id)})
        new_balance = user["balance"] if user else 0
        logger.info(f"💰 Saldo User {user_id} ditambahkan Rp {amount:,}. Total Saldo: Rp {new_balance:,}")
        return new_balance
    except Exception as e:
        logger.error(f"❌ Error pada fungsi update_balance (Deposit): {e}")
        return 0

async def deduct_balance(user_id, amount):
    """
    Memotong saldo saat user checkout menggunakan metode "Via Saldo".
    SISTEM ANTI MINUS: Mengecek ketersediaan saldo terlebih dahulu.
    
    RETURN: True jika sukses dipotong, False jika saldo tidak cukup / error.
    """
    try:
        user = await users_col.find_one({"user_id": int(user_id)})
        
        # Validasi ketat Anti-Minus
        if not user or user.get("balance", 0) < int(amount):
            logger.warning(f"⚠️ User {user_id} gagal bayar via saldo. Saldo tidak mencukupi. (Tagihan: {amount})")
            return False 
            
        # Potong Saldo
        await users_col.update_one(
            {"user_id": int(user_id)},
            {"$inc": {"balance": -int(amount)}} 
        )
        logger.info(f"✅ Saldo User {user_id} sukses dipotong sebesar Rp {amount:,} untuk pembelian stok.")
        return True
    except Exception as e:
        logger.error(f"❌ Error pada fungsi deduct_balance: {e}")
        return False

async def check_balance(user_id):
    """Pengecekan jumlah saldo user saat ini (Display Info)"""
    try:
        user = await users_col.find_one({"user_id": int(user_id)})
        if user:
            return user.get("balance", 0)
        return 0
    except Exception as e:
        logger.error(f"❌ Error pada fungsi check_balance: {e}")
        return 0

async def reset_balance(user_id):
    """
    ENGINE CLEAR SALDO:
    Fungsi khusus Admin untuk mereset/menghapus saldo user menjadi 0.
    Tidak akan merusak data history total order milik user.
    """
    try:
        res = await users_col.update_one(
            {"user_id": int(user_id)},
            {"$set": {"balance": 0}} # $set digunakan agar nilai dipaksa menjadi 0
        )
        
        if res.modified_count > 0:
            logger.info(f"⚠️ FORCE RESET: Saldo User {user_id} berhasil diubah menjadi Rp 0 oleh sistem.")
            return True
            
        logger.warning(f"⚠️ Reset Saldo gagal: User {user_id} mungkin belum terdaftar atau saldo sudah 0.")
        return False
    except Exception as e:
        logger.error(f"❌ Error pada fungsi reset_balance: {e}")
        return False


# ============================================================
# 📦 STOCK MANAGEMENT (ADD, DELETE, STATUS UPDATE)
# ============================================================

async def add_stock(data):
    """
    Menambahkan stok akun Noktel baru ke Database.
    Dilengkapi dengan Engine Auto-Region Parser & Label Fallback VVIP.
    """
    try:
        # 1. Normalisasi Flag Limit
        limit_raw = str(data.get("limit", "OFF")).strip().upper()
        data["limit"] = "ON" if limit_raw in ["ON", "LIMPER", "YES", "ADA", "TRUE"] else "OFF"
        
        # 2. Set Status Default
        data["status"] = "ready" 
        data["is_sold"] = False
        
        if "buyer_id" not in data:
            data["buyer_id"] = None
        if "created_at" not in data:
            data["created_at"] = datetime.now(WIB)

        # 3. 🌟 AUTO REGION CODE PARSER (Jantung Sistem Harga 3D)
        region_str = str(data.get("region", "")).lower()
        if "indo" in region_str: r_code = "ID"
        elif "malay" in region_str: r_code = "MY"
        elif "thai" in region_str: r_code = "TH"
        elif "filip" in region_str or "phil" in region_str: r_code = "PH"
        elif "mesir" in region_str: r_code = "MR"
        elif "us" in region_str or "amerika" in region_str: r_code = "US"
        elif "viet" in region_str: r_code = "VN"
        elif "inggris" in region_str or "uk" in region_str: r_code = "GB"
        else: r_code = "DEFAULT"
        
        data["region_code"] = r_code 
        
        # 4. Standarisasi Data Center (DC) & Prefix Label
        uid_str = str(data.get("uid", "")).strip()
        if uid_str:
            prefix = uid_str[0]
            
            # Jika DC kosong saat admin input, gunakan prefix UID sebagai default DC
            if "dc" not in data or str(data["dc"]).strip() == "":
                data["dc"] = prefix
            else:
                data["dc"] = str(data["dc"]).strip()
                
            # Pasang Label otomatis berdasarkan Config VVIP
            if "label" not in data or not data["label"]:
                labels = getattr(Config, "LABELS", {})
                data["label"] = labels.get(prefix, f"Id {prefix}xxx")

        # Eksekusi Injeksi ke Database
        await stocks_col.insert_one(data)
        logger.info(f"📥 Stok UID {data.get('uid')} (Region: {r_code}) berhasil ditambahkan ke Database!")
        return True
    except Exception as e:
        logger.error(f"❌ Error pada saat add_stock: {e}")
        return False

async def get_stock_by_id(stock_id):
    """
    Mengambil detail satu stok berdasarkan _id unik MongoDB.
    Dilengkapi Anti-Crash jika String ID tidak valid.
    """
    try:
        # Konversi Aman ke ObjectId
        if isinstance(stock_id, str):
            try:
                stock_id = ObjectId(stock_id)
            except InvalidId:
                logger.warning(f"⚠️ Invalid ObjectId format yang diminta: {stock_id}")
                return None
                
        return await stocks_col.find_one({"_id": stock_id})
    except Exception as e:
        logger.error(f"❌ Error get_stock_by_id: {e}")
        return None

async def get_all_stock_by_label(label):
    """Mengambil list semua stok ready untuk satu label tertentu."""
    try:
        return await stocks_col.find({"status": "ready", "is_sold": False, "label": label}).to_list(length=None)
    except Exception as e:
        logger.error(f"❌ Error get_all_stock_by_label: {e}")
        return []

async def count_stock(label):
    """Menghitung total akun yang statusnya ready pada label tertentu."""
    try:
        return await stocks_col.count_documents({"status": "ready", "is_sold": False, "label": label})
    except Exception as e:
        logger.error(f"❌ Error count_stock: {e}")
        return 0

async def update_stock_status(stock_id, status):
    """Mengubah status stok (Misalnya dari 'ready' menjadi 'pending_PAYMENT')."""
    try:
        if isinstance(stock_id, str):
            try:
                stock_id = ObjectId(stock_id)
            except InvalidId:
                return False
                
        await stocks_col.update_one({"_id": stock_id}, {"$set": {"status": status}})
        return True
    except Exception as e:
        logger.error(f"❌ Error update_stock_status: {e}")
        return False

async def mark_as_sold(stock_id, buyer_id):
    """
    Eksekutor Final saat transaksi Pembelian Berhasil (LUNAS).
    1. Mengubah status akun menjadi 'sold'.
    2. Mencatat waktu pembelian & ID Pembeli.
    3. Meningkatkan statistik total_order milik Pembeli.
    """
    try:
        if isinstance(stock_id, str):
            try:
                stock_id = ObjectId(stock_id)
            except InvalidId:
                return False
            
        res = await stocks_col.update_one(
            {"_id": stock_id},
            {
                "$set": {
                    "status": "sold", 
                    "is_sold": True, 
                    "buyer_id": int(buyer_id), 
                    "sold_at": datetime.now(WIB)
                }
            }
        )
        
        # Tambahkan poin ke history pembeli jika update dokumen stok sukses
        if res.modified_count > 0:
            await users_col.update_one({"user_id": int(buyer_id)}, {"$inc": {"total_order": 1}})
            logger.info(f"✅ Stok {stock_id} resmi menjadi milik User {buyer_id} (Status: SOLD)")
            return True
            
        return False
    except Exception as e:
        logger.error(f"❌ Error mark_as_sold: {e}")
        return False

async def clear_all_stock_data():
    """Menghapus SEMUA stok READY dari DB. Stok yang SOLD tidak akan disentuh (Aman)."""
    try:
        res = await stocks_col.delete_many({"status": "ready"})
        await bulk_sessions.delete_many({}) # Hapus sesi borongan yang menggantung
        logger.info(f"🗑️ Cleared {res.deleted_count} ready stocks. (Data Sold Aman)")
        return True
    except Exception as e:
        logger.error(f"❌ Error clear_all_stock_data: {e}")
        return False

async def delete_stock_by_uid(uid):
    """Menghapus akun berdasarkan Prefix atau UID spesifik."""
    try:
        res = await stocks_col.delete_many({"uid": {"$regex": f"^{uid}"}})
        return res.deleted_count
    except Exception as e:
        logger.error(f"❌ Error delete_stock_by_uid: {e}")
        return 0


# ============================================================
# 🛒 BULK SESSION MANAGEMENT (Fitur Beli Borongan)
# ============================================================

async def save_bulk_session(user_id, order_id, ids_list):
    """
    Menyimpan sesi order borongan ke MongoDB.
    Digunakan agar buyer bisa mengklik 'Nomor Selanjutnya' secara berurutan.
    """
    try:
        await bulk_sessions.update_one(
            {"user_id": int(user_id), "order_id": str(order_id)},
            {"$set": {
                "user_id": int(user_id), 
                "order_id": str(order_id), 
                "ids": ids_list, 
                "created_at": datetime.now(WIB)
            }},
            upsert=True
        )
        logger.info(f"📦 Bulk Session (Order ID: {order_id}) berhasil disimpan untuk User {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Error save_bulk_session: {e}")
        return False

async def get_bulk_session(user_id, order_id):
    """Membaca antrian sesi akun borongan berdasarkan Order ID pembayaran"""
    try:
        return await bulk_sessions.find_one({"user_id": int(user_id), "order_id": str(order_id)})
    except Exception as e:
        logger.error(f"❌ Error get_bulk_session: {e}")
        return None


# ============================================================
# 📜 SCRIPT BOT SALES MANAGEMENT (FITUR BARU)
# ============================================================

async def record_script_sale(buyer_id, script_type, price):
    """
    Menyimpan data transaksi pembelian script ke database.
    Meningkatkan total order milik buyer secara otomatis.
    """
    try:
        sale_data = {
            "buyer_id": int(buyer_id),
            "script_type": script_type, # NO_UP, UP_1X, atau FULL_UP
            "price": int(price),
            "sold_at": datetime.now(WIB)
        }
        await script_sales.insert_one(sale_data)
        
        # Tambahkan poin total order ke pembeli
        await users_col.update_one({"user_id": int(buyer_id)}, {"$inc": {"total_order": 1}})
        logger.info(f"✅ SCRIPT TERJUAL: {script_type} laku seharga Rp {price:,} dibeli oleh {buyer_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Error record_script_sale: {e}")
        return False


# ============================================================
# 📊 STATISTIK PANEL GLOBAL & OMSET (TERMASUK SCRIPT)
# ============================================================

async def get_global_stats():
    """Mengambil rekapan data: Total Member, Stok Ready, Akun Terjual, & Script Terjual"""
    try:
        total_users = await users_col.count_documents({})
        ready = await stocks_col.count_documents({"status": "ready", "is_sold": False})
        sold = await stocks_col.count_documents({"status": "sold"})
        scripts_sold = await script_sales.count_documents({}) # 🔥 Menghitung script yang laku
        
        return {
            "users": total_users, 
            "ready": ready, 
            "sold": sold,
            "scripts_sold": scripts_sold
        }
    except Exception as e:
        logger.error(f"❌ Error pada panel get_global_stats: {e}")
        # Default aman jika MongoDB sedang lag
        return {"users": 0, "ready": 0, "sold": 0, "scripts_sold": 0}

async def get_omset_stats():
    """
    Menghitung total pendapatan (Omset) berdasarkan histori akun yang SOLD 
    DITAMBAH dengan pendapatan dari penjualan SCRIPT BOT.
    Menghitung omset untuk Hari Ini, Minggu Ini, Bulan Ini, dan Keseluruhan.
    """
    try:
        now = datetime.now(WIB)
        # Setup batasan waktu untuk filter (Reset jam 00:00 WIB)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday()) # Mulai hari Senin
        month_start = today_start.replace(day=1)

        # 1. Ambil semua data akun yang sudah laku (sold)
        sold_stocks = await stocks_col.find({"status": "sold"}).to_list(length=None)
        
        # 2. Ambil semua data script yang sudah laku
        sold_scripts = await script_sales.find({}).to_list(length=None)

        omset_today = 0
        omset_week = 0
        omset_month = 0
        omset_all = 0

        # === KALKULASI OMSET DARI AKUN NOKTEL ===
        for s in sold_stocks:
            uid_str = str(s.get("uid", "0"))
            prefix = uid_str[0] if uid_str else "0"
            dc_val = s.get("dc", "1")
            r_code = s.get("region_code", "DEFAULT")
            is_limp = s.get("limit", "OFF").upper() == "ON"

            price = Config.get_price(prefix, dc_val, r_code, is_limp)
            omset_all += price

            sold_at = s.get("sold_at")
            if sold_at:
                if sold_at.tzinfo is None:
                    sold_at = sold_at.replace(tzinfo=timezone.utc).astimezone(WIB)
                else:
                    sold_at = sold_at.astimezone(WIB)
                
                if sold_at >= today_start:
                    omset_today += price
                if sold_at >= week_start:
                    omset_week += price
                if sold_at >= month_start:
                    omset_month += price

        # === KALKULASI OMSET DARI JUAL SCRIPT BOT ===
        for sc in sold_scripts:
            price = sc.get("price", 0)
            omset_all += price

            sold_at = sc.get("sold_at")
            if sold_at:
                if sold_at.tzinfo is None:
                    sold_at = sold_at.replace(tzinfo=timezone.utc).astimezone(WIB)
                else:
                    sold_at = sold_at.astimezone(WIB)
                
                if sold_at >= today_start:
                    omset_today += price
                if sold_at >= week_start:
                    omset_week += price
                if sold_at >= month_start:
                    omset_month += price

        return {
            "today": omset_today,
            "this_week": omset_week,
            "this_month": omset_month,
            "all_time": omset_all
        }
    except Exception as e:
        logger.error(f"❌ Error pada saat menghitung get_omset_stats: {e}")
        return {"today": 0, "this_week": 0, "this_month": 0, "all_time": 0}
        
async def add_user_balance(user_id: int, amount: int) -> bool:
    """Menambah saldo user berdasarkan ID (Khusus Command Admin)"""
    try:
        # Gunakan $inc untuk menambah saldo dari saldo saat ini
        result = await users_col.update_one(
            {"user_id": user_id},
            {"$inc": {"balance": amount}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"❌ Error add_user_balance: {e}")
        return False
              
async def update_stock_price(uid: str, new_price: int) -> bool:
    """Mengubah harga spesifik untuk UID akun tertentu (Config Aman)"""
    try:
        # Pake $set biar dia bikin data 'custom_price' di akun tersebut
        result = await stocks_col.update_many(
            {"uid": str(uid)},
            {"$set": {"custom_price": int(new_price)}}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"❌ Error update_stock_price: {e}")
        return False
 
async def update_stock_price_bulk(prefix: str, region_name: str, limit_status: str, new_price: int) -> int:
    """Mengubah harga massal berdasarkan prefix, region, dan limit"""
    try:
        # Kita cari murni pakai field "limit", sesuai SC asli lu!
        query = {
            "uid": {"$regex": f"^{prefix}"},
            "region": {"$regex": region_name, "$options": "i"}, 
            "limit": limit_status,
            "status": "ready",
            "is_sold": False
        }
        result = await stocks_col.update_many(
            query,
            {"$set": {"custom_price": int(new_price)}}
        )
        return result.modified_count
    except Exception as e:
        logger.error(f"❌ Error update_stock_price_bulk: {e}")
        return 0
                           
                                                       