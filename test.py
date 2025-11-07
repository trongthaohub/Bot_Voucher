# test.py
import asyncio
from datetime import datetime, timezone, timedelta
from apis import get_piggi_vouchers, get_accesstrade_vouchers  # DÙNG CẢ 2 API
from telegram_bot import send_voucher_to_topic
from config import TELEGRAM_TOKEN, GROUP_ID, TOPIC_ID

# === IN THÔNG TIN CẤU HÌNH ===
print(f"Bot Token: {TELEGRAM_TOKEN[:10]}...{TELEGRAM_TOKEN[-4:]}")
print(f"Group ID: {GROUP_ID}")
print(f"Topic ID: {TOPIC_ID}")

async def test_send_real_voucher():
    print("\nĐang lấy voucher THỰC TẾ từ 2 API: Piggi + AccessTrade...")

    # LẤY DỮ LIỆU TỪ CẢ 2 NGUỒN
    piggi_vouchers = get_piggi_vouchers()
    at_vouchers = get_accesstrade_vouchers()

    all_vouchers = piggi_vouchers + at_vouchers
    print(f"Piggi: {len(piggi_vouchers)} voucher | AccessTrade: {len(at_vouchers)} voucher")
    print(f"Tổng cộng: {len(all_vouchers)} voucher")

    if not all_vouchers:
        print("Không lấy được voucher nào từ cả 2 API.")
        return

    # LỌC VOUCHER SẮP MỞ (trong tương lai + có mã)
    now = datetime.now(timezone(timedelta(hours=7)))
    upcoming = [
        v for v in all_vouchers
        if v.start_time > now and v.code != "Không có mã"
    ]

    if not upcoming:
        print("Không có voucher nào sắp mở.")
        return

    # CHỌN VOUCHER GẦN NHẤT
    upcoming.sort(key=lambda x: x.start_time)
    test_v = upcoming[0]

    print(f"\nVOUCHER ĐƯỢC CHỌN (gần nhất):")
    print(f"  Nguồn: {test_v.source.upper()}")
    print(f"  Tên: {test_v.name}")
    print(f"  Mã: `{test_v.code}`")
    print(f"  Giảm: {test_v.value}")
    print(f"  Mở lúc: {test_v.start_time.strftime('%H:%M %d/%m')}")
    print(f"  Hết hạn: {test_v.end_time.strftime('%H:%M %d/%m')}")

    # GỬI NGAY LẬP TỨC VÀO GROUP
    print(f"\nĐang gửi vào group {GROUP_ID} | topic {TOPIC_ID}...")
    success = await send_voucher_to_topic(test_v)
    
    if success:
        print("TEST THÀNH CÔNG!")
        print(f"Đã gửi voucher `{test_v.code}` từ {test_v.source.upper()} vào topic!")
        print("Kiểm tra group ngay!")
    else:
        print("GỬI THẤT BẠI!")
        print("Nguyên nhân có thể:")
        print("  1. Bot chưa được thêm vào group")
        print("  2. Bot không phải admin (cần quyền gửi tin vào topic)")
        print("  3. Topic ID sai (dùng @getidsbot để kiểm tra)")

# === CHẠY AN TOÀN TRÊN WINDOWS ===
if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_send_real_voucher())