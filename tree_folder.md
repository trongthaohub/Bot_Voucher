├── main.py                  # Khởi chạy bot + scheduler
├── config.py                # Token, group_id, topic_id
├── database.py              # Quản lý DB
├── telegram_bot.py          # Gửi tin nhắn
├── scheduler.py             # Lập lịch kiểm tra voucher
│
├── apis/
│   ├── __init__.py
│   ├── shopee_official.py   # API 1
│   ├── affiliate_api.py     # API 2
│   └── flash_sale_api.py    # API 3
│
└── models/
    └── voucher.py           # Model Voucher