# telegram_bot.py
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import TELEGRAM_TOKEN, GROUP_ID, TOPIC_ID
import asyncio

bot = Bot(token=TELEGRAM_TOKEN)

async def send_voucher_to_topic(v) -> bool:
    # Cắt mô tả ngắn gọn
    desc = (v.description or "")[:180]
    if len(v.description or "") > 180:
        desc += "..."

    # Tạo nút "Dùng ngay"
    keyboard = [
        [InlineKeyboardButton("Dùng ngay", url=v.link)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Tin nhắn
    message = f"""
*VOUCHER SẮP MỞ - CHỈ CÒN 15 GIÂY!*

*Tên:* {v.name}
*Mã:* `{v.code}`
*Giảm:* {v.value}
*Thời gian:* `{v.start_time.strftime('%H:%M %d/%m')}` → `{v.end_time.strftime('%H:%M %d/%m')}`

_{desc}_
    """.strip()

    try:
        # Ưu tiên gửi ảnh + nút
        photo_url = None
        if hasattr(v, 'avatar') and v.avatar:
            photo_url = v.avatar
        elif "cf.shopee.vn" in v.link:
            photo_url = v.link.split("?")[0]

        if photo_url:
            await bot.send_photo(
                chat_id=GROUP_ID,
                photo=photo_url,
                caption=message,
                parse_mode="Markdown",
                reply_markup=reply_markup,
                message_thread_id=TOPIC_ID
            )
        else:
            await bot.send_message(
                chat_id=GROUP_ID,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                message_thread_id=TOPIC_ID
            )
        return True
    except Exception as e:
        print(f"[Telegram] Gửi thất bại: {e}")
        return False