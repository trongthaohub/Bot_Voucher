# apis/piggi_api.py
from models.voucher import Voucher  # IMPORT VOUCHER TRƯỚC
import requests
from datetime import datetime, timezone, timedelta

PIGGI_API_URL = "https://portal.piggi.vn/api/voucher?slugSupplier=shopee"

def parse_time(ts: str | None) -> datetime:
    if not ts:
        return datetime.now(timezone.utc).astimezone()
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.astimezone(timezone(timedelta(hours=7)))

def get_piggi_vouchers():
    try:
        resp = requests.get(PIGGI_API_URL, timeout=15)
        resp.raise_for_status()
        items = resp.json().get("data", {}).get("data", [])

        vouchers = []
        for item in items:
            if not item.get("voucherCode") or item.get("status") != "publish":
                continue
            if not item.get("startAt"):
                continue

            try:
                min_spend = int(item["minSpend"] or 0) // 1000
                max_disc = int(item["maxDiscount"] or 0) // 1000
                percent = item["voucherAmount"]

                value = f"Giảm {percent}%"
                if max_disc > 0:
                    value += f" tối đa {max_disc}K"
                if min_spend > 0:
                    value += f" đơn từ {min_spend}K"

                link = item.get("detailLink") or item.get("affLink") or "https://shopee.vn"

                v = Voucher(
                    name=item["title"],
                    code=item["voucherCode"],
                    value=value,
                    start_time=parse_time(item["startAt"]),
                    end_time=parse_time(item["expiredAt"]),
                    link=link,
                    description=item.get("longDescription") or item.get("note"),
                    source="piggi_shopee",
                    avatar=item.get("avatar")  # Có ảnh
                )
                vouchers.append(v)
            except Exception as e:
                print(f"[Parse error] {e}")
                continue
        return vouchers
    except Exception as e:
        print(f"[Piggi API] Lỗi: {e}")
        return []