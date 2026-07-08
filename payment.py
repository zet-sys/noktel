# ==============================================================================
# Dev : @supiqbalubot
# ==============================================================================

import aiohttp
import logging
import json
import re
import asyncio
from io import BytesIO
from datetime import datetime, timezone, timedelta
from config import Config

# ============================================================
# 🕒 SETTING ZONA WAKTU & LOGGER
# ============================================================
WIB = timezone(timedelta(hours=7))

# Konfigurasi Logger khusus Payment agar rapi di terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ɪǫʙᴀʟ_ᴘᴀʏᴍᴇɴᴛ")

class PaymentGateway:
    # ============================================================
    # 🛡️ 1. OID CLEANER (Keamanan Format Payload)
    # ============================================================
    @staticmethod
    def clean_oid(oid: str) -> str:
        """
        Merapikan format Order ID agar selalu valid saat dikirim ke API Pakasir.
        Sangat penting untuk transaksi Deposit, Akun Noktel, dan Pembelian Script Bot.
        [FIXED]: Membiarkan tanda strip (-) dan underscore (_) agar ID tidak rusak.
        """
        if not oid: 
            return ""
        # Hanya membiarkan huruf, angka, strip, dan underscore
        return re.sub(r'[^a-zA-Z0-9_\-]', '', str(oid))

    # ============================================================
    # ⚡ 2. QRIS GENERATOR (Hit API Pakasir & QuickChart)
    # ============================================================
    @staticmethod
    async def generate_qris(amount: int, oid: str):
        """
        Membuat request QRIS Dinamis ke API Pakasir.
        Mengembalikan gambar QR (BytesIO) dan nominal yang sudah disesuaikan.
        
        RETURN: (gambar_qris_bytes, nominal_final)
        """
        url = "https://app.pakasir.com/api/transactioncreate/qris"
        safe_oid = PaymentGateway.clean_oid(oid)
        
        # Payload VVIP sesuai standar API Pakasir
        payload = {
            "project": Config.PROJECT_SLUG,
            "api_key": Config.PAKASIR_KEY,
            "order_id": safe_oid,
            "amount": int(amount)
        }
        
        logger.info(f"🔄 Meminta pembuatan QRIS untuk OID: {safe_oid} (Rp {amount:,})")
        
        # Async session untuk kecepatan & performa Non-Blocking Server
        async with aiohttp.ClientSession() as session:
            try:
                # Setup Timeout 25 detik agar bot tidak nyangkut jika server Pakasir lemot
                async with session.post(url, json=payload, timeout=25) as resp:
                    res_text = await resp.text()
                    
                    if resp.status != 200:
                        logger.error(f"❌ API Pakasir Error [HTTP {resp.status}]: {res_text}")
                        return None, None
                    
                    # Parsing JSON Response
                    try:
                        data = json.loads(res_text)
                    except json.JSONDecodeError:
                        logger.error(f"❌ Gagal memparsing JSON dari Pakasir: {res_text}")
                        return None, None
                    
                    # Ekstraksi Data Pakasir yang terkadang formatnya berubah-ubah
                    p = data.get("data") or data.get("payment") or data
                    final_amount = p.get("amount") or amount
                    q_str = p.get("payment_number") or p.get("qris_string")
                    
                    if not q_str: 
                        logger.error(f"❌ String QRIS (payment_number) Tidak Ditemukan: {data}")
                        return None, None

                    logger.info(f"✅ String QRIS didapat (OID: {safe_oid}). Mengubah jadi gambar HD...")
                    
                    # Generator Gambar QR Code VVIP (Margin 2, Size 600px HD)
                    qr_url = f"https://quickchart.io/qr?text={q_str}&size=600&margin=2"
                    async with session.get(qr_url, timeout=15) as qr_resp:
                        if qr_resp.status == 200:
                            img = BytesIO(await qr_resp.read())
                            img.name = f"qris_{safe_oid}.png"
                            logger.info(f"✅ Gambar QRIS Selesai Digenerate! File: {img.name}")
                            return img, final_amount
                        else:
                            logger.error(f"❌ QuickChart API Error [HTTP {qr_resp.status}]: Gagal merender gambar QRIS.")
                            return None, None
                            
            except asyncio.TimeoutError:
                logger.error(f"❌ Timeout: API Pakasir / QuickChart tidak merespon dalam batas waktu (OID: {safe_oid}).")
            except aiohttp.ClientError as req_err:
                logger.error(f"❌ Network Error saat request QRIS: {req_err}")
            except Exception as e:
                logger.error(f"❌ Critical Error pada generate_qris: {e}")
                
        return None, None

    # ============================================================
    # 🔍 3. MUTASI STATUS CHECKER (Verifikasi API)
    # ============================================================
    @staticmethod
    async def is_confirmed(oid: str, amount: int = None) -> bool:
        """
        Mengecek status pembayaran di server Pakasir secara Live.
        Support untuk verifikasi pembelian Akun, Deposit, dan Script Bot.
        
        RETURN: True jika LUNAS, False jika belum lunas / pending / gagal.
        """
        url = "https://app.pakasir.com/api/transactiondetail"
        safe_oid = PaymentGateway.clean_oid(oid)
        
        # Parameter Checker VVIP (100% Mengikuti standar Pakasir)
        params = {
            "project": Config.PROJECT_SLUG,
            "api_key": Config.PAKASIR_KEY,
            "order_id": safe_oid
        }
        
        # Ekstra Proteksi: Pengecekan by Amount (Jika dibutuhkan)
        if amount:
            params["amount"] = int(amount)
            
        async with aiohttp.ClientSession() as session:
            try:
                # Timeout lebih cepat (15s) karena fungsi ini dipanggil secara looping (berkala)
                async with session.get(url, params=params, timeout=15) as resp:
                    if resp.status != 200:
                        logger.debug(f"⚠️ Pakasir HTTP {resp.status} saat cek mutasi OID: {safe_oid}")
                        return False
                    
                    try:
                        data_json = await resp.json()
                    except json.JSONDecodeError:
                        logger.error(f"❌ Gagal memparsing JSON saat cek mutasi: {await resp.text()}")
                        return False
                    
                    # Ekstraksi Status Pembayaran VVIP
                    tx = data_json.get("transaction") or data_json.get("data") or data_json
                    status_raw = str(tx.get("status", "")).upper()
                    
                    # Kamus Array: Status Lunas / Sukses dari berbagai jenis respons API
                    list_lunas = ["PAID", "SUCCESS", "BERHASIL", "COMPLETED", "SETTLEMENT"]
                    
                    if any(x in status_raw for x in list_lunas):
                        logger.info(f"✅ MANTAP! TRX {safe_oid} LUNAS! Status API: {status_raw}")
                        return True
                        
                    # Jika belum masuk list_lunas, berarti masih pending
                    logger.debug(f"⏳ TRX {safe_oid} Masih Pending. Status API: {status_raw}")
                    return False
                    
            except asyncio.TimeoutError:
                logger.warning(f"⏳ Timeout saat mengecek TRX {safe_oid} ke API Pakasir.")
                return False
            except aiohttp.ClientError as req_err:
                logger.warning(f"⏳ Gangguan jaringan saat cek mutasi: {req_err}")
                return False
            except Exception as e:
                logger.error(f"❌ API ERROR (Check Confirm Mutasi): {e}")
                return False
                
    @staticmethod
    async def cancel_order(oid: str):
        """
        Fungsi wajib untuk membatalkan order di database 
        dan mengembalikan stok ke status ready.
        """
        # 1. Hapus Order dari database orders
        from database import db  # Import db di dalam fungsi agar tidak circular import
        
        order = await db.orders_col.find_one({"oid": oid})
        if order and "stok_uid" in order:
            # 2. Kembalikan stok ke 'ready'
            await db.stocks_col.update_one(
                {"uid": order["stok_uid"]},
                {"$set": {"status": "ready", "is_sold": False}}
            )
        
        # 3. Hapus invoice
        await db.orders_col.delete_one({"oid": oid})
        logger.info(f"✅ Order {oid} dibatalkan & Stok dikembalikan ke READY.")
        return True
                        