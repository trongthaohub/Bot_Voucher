# apis/accesstrade_api.py
import requests
from datetime import datetime, timezone, timedelta
from models.voucher import Voucher
from config import ACCESSTRADE_TOKEN
from typing import List

# === CẤU HÌNH API ===
BASE_URL = "https://api.accesstrade.vn/v1/offers_informations/coupon"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "vi;q=0.7",
    "Authorization": f"Token {ACCESSTRADE_TOKEN}",
    "Cache-Control": "no-cache",
    "Content-Type": "application/json",
    "Origin": "https://trainghiemmuasam.com",
    "Pragma": "no-cache",
    "Referer": "https://trainghiemmuasam.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Sec-GPC": "1",
    "sec-ch-ua": '"Chromium";v="142", "Brave";v="142", "Not_A Brand";v="99"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"'
}

# === HÀM CHUYỂN ĐỔI THỜI GIAN ===
def parse_accesstrade_time(time_str: str) -> datetime:
    """
    Chuyển '2025/11/10 17:00' → datetime có múi giờ GMT+7
    """
    try:
        dt = datetime.strptime(time_str, "%Y/%m/%d %H:%M")
        # AccessTrade trả về giờ Việt Nam → gắn múi giờ GMT+7
        return dt.replace(tzinfo=timezone(timedelta(hours=7)))
    except:
        return datetime.now(timezone(timedelta(hours=7))) + timedelta(hours=1)

# === HÀM LẤY VOUCHER ===
def get_accesstrade_vouchers() -> List[Voucher]:
    params = {
        "page": 1,
        "limit": 50,
        "merchant": "4742147753565840242,5869368934302265056,5897572472879914453",
        "campaign": "4751584435713464237",
        "is_next_day_coupon": "True"
    }

    try:
        resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json().get("data", [])

        vouchers = []
        for item in data:
            try:
                # Lấy mã + mô tả từ coupons[0]
                coupon = item["coupons"][0] if item.get("coupons") else {}
                code = coupon.get("coupon_code", "Không có mã")
                desc = coupon.get("coupon_desc", "")

                # Xử lý giá trị giảm
                if item["discount_percentage"] > 0:
                    value = f"Giảm {item['discount_percentage']}%"
                    if item["max_value"] > 0:
                        value += f" tối đa {item['max_value']//1000}K"
                else:
                    value = f"Giảm {item['discount_value']//1000}K"

                if item["min_spend"] > 0:
                    value += f" đơn từ {item['min_spend']//1000}K"

                # Link ưu tiên aff_link
                link = item.get("aff_link") or item.get("link") or "https://shopee.vn"

                # Thời gian
                start_time = parse_accesstrade_time(item["start_time"])
                end_time = parse_accesstrade_time(item["end_time"])

                # Tạo Voucher
                v = Voucher(
                    name=item["name"],
                    code=code,
                    value=value,
                    start_time=start_time,
                    end_time=end_time,
                    link=link,
                    description=desc or item.get("content"),
                    source="accesstrade",
                    avatar=item.get("image")
                )
                vouchers.append(v)
            except Exception as e:
                print(f"[AccessTrade] Parse error: {e}")
                continue

        print(f"[AccessTrade] Lấy được {len(vouchers)} voucher")
        return vouchers

    except Exception as e:
        print(f"[AccessTrade API] Lỗi: {e}")
        return []