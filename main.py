# main.py
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scheduler import check_and_schedule_vouchers
from database import init_db
from datetime import datetime, timezone, timedelta
import logging
from pystyle import Colors, Colorate, Center
import threading
import time

# === CẤU HÌNH LOGGING ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === BIẾN CHIA SẺ GIỮA BOT & PANEL ===
shared_data = {
    "last_vouchers": [],
    "last_logs": [],
    "next_check": datetime.now(timezone(timedelta(hours=7))) + timedelta(seconds=20)
}

# === HÀM CẬP NHẬT DỮ LIỆU ===
def update_shared_data(vouchers, log_msg):
    shared_data["last_vouchers"] = vouchers[-5:]  # 5 voucher gần nhất
    shared_data["last_logs"].append(f"{datetime.now(timezone(timedelta(hours=7))).strftime('%H:%M:%S')} | {log_msg}")
    shared_data["last_logs"] = shared_data["last_logs"][-10:]  # 10 log mới nhất
    shared_data["next_check"] = datetime.now(timezone(timedelta(hours=7))) + timedelta(seconds=20)

# === PANEL CLI (CHẠY TRONG THREAD RIÊNG) ===
def cli_panel():
    print(Colorate.Horizontal(Colors.green_to_cyan, Center.XCenter("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                     SHOPEE VOUCHER BOT CLI                      ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)))

    while True:
        try:
            now = datetime.now(timezone(timedelta(hours=7)))
            countdown = max(0, int((shared_data["next_check"] - now).total_seconds()))
            status = "ĐANG CHẠY" if countdown > 0 else "ĐANG LẤY DỮ LIỆU..."

            # Header
            header = f"""
┌────────────────────────────────────────────────────────────────────┐
│ {Colors.cyan}Bot Status:{Colors.white} {status.ljust(20)} │
│ {Colors.yellow}Làm mới sau:{Colors.white} {f'{countdown:02d}s'.rjust(15)} │
│ {Colors.purple}Khởi động:{Colors.white} {datetime.now(timezone(timedelta(hours=7))).strftime('%H:%M:%S %d/%m')} │
└────────────────────────────────────────────────────────────────────┘
            """.strip()

            # Voucher sắp mở
            vouchers_text = "\n".join([
                f"│ {Colors.green}• {v.code[:15]:<15}{Colors.white} {v.name[:30]:<30} {Colors.red}{v.start_time.strftime('%H:%M')} {Colors.reset}"
                for v in shared_data["last_vouchers"]
            ]) or f"│ {Colors.gray}Chưa có voucher sắp mở...{Colors.reset}"

            voucher_block = f"""
┌────────────────── VOUCHER SẮP MỞ ({len(shared_data['last_vouchers'])}) ──────────────────┐
{vouchers_text}
└────────────────────────────────────────────────────────────────────┘
            """.strip()

            # Log
            logs_text = "\n".join([
                f"│ {Colors.blue}{log.split('|')[0]}{Colors.white} | {log.split('|', 1)[1] if '|' in log else log}{Colors.reset}"
                for log in shared_data["last_logs"]
            ]) or f"│ {Colors.gray}Chưa có log...{Colors.reset}"

            log_block = f"""
┌────────────────────── LOG HOẠT ĐỘNG ──────────────────────┐
{logs_text}
└────────────────────────────────────────────────────────────────────┘
            """.strip()

            # Xóa màn hình + in
            print("\033[H\033[2J", end="")  # Xóa màn hình
            print(Colorate.Horizontal(Colors.green_to_cyan, header))
            print(Colorate.Horizontal(Colors.blue_to_purple, voucher_block))
            print(Colorate.Horizontal(Colors.red_to_yellow, log_block))
            print(f"\n{Colors.gray}Nhấn Ctrl+C để thoát{Colors.reset}")

            time.sleep(1)
        except:
            break

# === MAIN BOT ===
async def main():
    init_db()

    # BẮT ĐẦU PANEL CLI TRONG THREAD RIÊNG
    panel_thread = threading.Thread(target=cli_panel, daemon=True)
    panel_thread.start()

    scheduler = AsyncIOScheduler(timezone=timezone(timedelta(hours=7)))
    scheduler.add_job(
        lambda: asyncio.create_task(wrap_check()),
        "interval",
        seconds=20,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60
    )

    async def wrap_check():
        try:
            vouchers = []  # Lấy từ API
            # GỌI HÀM CHÍNH
            await check_and_schedule_vouchers()
            # CẬP NHẬT PANEL
            update_shared_data(shared_data.get("last_vouchers", []), "Lấy dữ liệu thành công")
        except Exception as e:
            update_shared_data([], f"Lỗi: {e}")

    try:
        scheduler.start()
        logger.info("Bot Shopee Voucher đang chạy...")
        update_shared_data([], "Bot khởi động thành công")
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Đang dừng bot...")
        scheduler.shutdown()
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        update_shared_data([], f"Lỗi nghiêm trọng: {e}")

# === CHẠY AN TOÀN TRÊN WINDOWS ===
if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())