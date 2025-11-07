# scheduler.py
from apis import get_piggi_vouchers, get_accesstrade_vouchers
from database import is_voucher_sent, mark_voucher_sent
from telegram_bot import send_voucher_to_topic
from datetime import datetime, timezone, timedelta
import asyncio

# === DANH SÁCH API ===
API_FUNCTIONS = [
    get_piggi_vouchers,
    get_accesstrade_vouchers,
]

# Bộ nhớ tạm: tránh gửi trùng trong cùng phiên
current_scheduled_vouchers = set()

# === CẬP NHẬT PANEL CLI (TỪ main.py) ===
def update_panel(vouchers, message):
    try:
        from main import update_shared_data
        update_shared_data(vouchers, message)
    except:
        pass  # main.py chưa khởi động

async def check_and_schedule_vouchers():
    global current_scheduled_vouchers
    now = datetime.now(timezone(timedelta(hours=7)))

    # Reset bộ nhớ tạm
    current_scheduled_vouchers = set()

    # LẤY DỮ LIỆU TỪ CẢ 2 API
    all_vouchers = []
    for api_func in API_FUNCTIONS:
        try:
            vouchers = api_func()
            all_vouchers.extend(vouchers)
            print(f"[API] {api_func.__name__}: {len(vouchers)} voucher")
        except Exception as e:
            print(f"[API Error] {api_func.__name__}: {e}")

    total = len(all_vouchers)
    print(f"[Scheduler] Tổng: {total} voucher mới")

    # CẬP NHẬT PANEL: HIỂN THỊ VOUCHER SẮP MỞ
    upcoming = [v for v in all_vouchers if v.start_time > now and v.code != "Không có mã"]
    update_panel(upcoming, f"Lấy {total} voucher | Sắp mở: {len(upcoming)}")

    # LẬP LỊCH GỬI
    for v in all_vouchers:
        if (v.code and 
            v.code != "Không có mã" and 
            v.start_time > now and 
            not is_voucher_sent(v.code) and 
            v.code not in current_scheduled_vouchers):

            delay = (v.start_time - now - timedelta(seconds=15)).total_seconds()
            if delay > 0:
                current_scheduled_vouchers.add(v.code)
                asyncio.create_task(schedule_send(v, delay))

async def schedule_send(voucher, delay: float):
    await asyncio.sleep(delay)
    
    if not is_voucher_sent(voucher.code):
        success = await send_voucher_to_topic(voucher)
        if success:
            mark_voucher_sent(voucher.code)
            msg = f"ĐÃ GỬI: {voucher.code} | {voucher.name[:40]}"
            print(msg)
            update_panel([], msg)  # Cập nhật log
        else:
            msg = f"GỬI THẤT BẠI: {voucher.code}"
            print(msg)
            update_panel([], msg)
    else:
        msg = f"ĐÃ GỬI TRƯỚC: {voucher.code}"
        print(msg)
        update_panel([], msg)