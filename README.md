# 🚀 VN30 Quant Breakout Analyzer & Telegram Alert Bot

Hệ thống giao dịch định lượng tự động (Quantitative Trading Bot) chuyên quét dòng tiền lớn và phát hiện các cơ hội bùng nổ (Breakout) cho rổ cổ phiếu **VN30**, tự động hóa toàn bộ trên đám mây và cảnh báo trực tiếp về Telegram.

---

## 📌 1. Giới thiệu dự án (Overview)

Dự án được xây dựng nhằm giải quyết bài toán tự động hóa việc sàng lọc cổ phiếu dựa trên hành vi dòng tiền thực tế thay vì cảm tính cá nhân. Hệ thống tự động cào dữ liệu cuối phiên, tính toán các chỉ báo kỹ thuật cốt lõi và gửi tín hiệu cảnh báo ngay khi xuất hiện dòng tiền thông minh (Smart Money) bước vào thị trường.

---

## ⚙️ 2. Chiến lược giao dịch (Strategy Rule)

Hệ thống kích hoạt tín hiệu mua (Alert) khi một cổ phiếu trong rổ VN30 thỏa mãn đồng thời các điều kiện khắt khe:

* **Biến động giá mạnh:** Giá tăng $\ge 2\%$ trong phiên giao dịch gần nhất.
* **Đột biến khối lượng (RVol):** Khối lượng giao dịch đạt từ **2.0x trở lên** so với mức trung bình lịch sử.
* **Quản trị rủi ro tự động:** Tự động tính toán điểm cắt lỗ (Stoploss) ngay tại mức **đáy của cây nến breakout**, giúp bảo vệ vốn tối ưu.

---

## 🛠️ 3. Công nghệ sử dụng (Tech Stack)

* **Language:** Python 3.10+
* **Data Source:** Thư viện `vnstock` (Lấy dữ liệu chứng khoán Việt Nam)
* **Data Analysis:** `pandas`, `numpy`
* **Automation (CI/CD):** GitHub Actions (Chạy định kỳ tự động qua Cron Schedule)
* **Notification:** Telegram Bot API (Gửi tin nhắn định dạng Markdown thời gian thực)

---

## 📂 4. Cấu trúc thư mục (Project Structure)

```text
vn-stock-breakout-analyzer/
│
├── .github/
│   └── workflows/
│       └── bot.yml               # Cấu hình GitHub Actions chạy tự động định kỳ
├── data/                         # Thư mục lưu trữ dữ liệu CSV lịch sử (VN30)
├── images/                       # Lưu trữ các biểu đồ breakout minh họa (`.png`)
├── src/
│   ├── chart_zoom.py             # Module vẽ và trực quan hóa biểu đồ
│   ├── features.py               # Tính toán các chỉ báo kỹ thuật & RVol
│   ├── fetch_data.py             # Script tải dữ liệu thô
│   ├── fetch_vn30.py             # Cấu hình danh sách mã rổ VN30
│   └── scanner.py                # Core logic quét tín hiệu & bắn Telegram
│
├── .gitignore                    # Cấu hình bỏ qua file rác / biến môi trường
├── README.md                     # Tài liệu mô tả dự án
├── requirements.txt              # Danh sách thư viện phụ thuộc
└── run_scanner.bat               # Script chạy nhanh trên môi trường Local (Windows)

## ⚙️ 5. Hướng dẫn cài đặt & Vận hành (Quick Start)
1. Clone repository về máy:
```bash
git clone [https://github.com/nvthih24/vn-stock-breakout-analyzer.git](https://github.com/nvthih24/vn-stock-breakout-analyzer.git)
cd vn-stock-breakout-analyzer

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt

3. Cấu hình biến môi trường (Environment Variables):
```bash
Tạo token Telegram Bot và Chat ID của ông, sau đó cấu hình vào GitHub Secrets (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID) nếu chạy trên Cloud, hoặc cấu hình trực tiếp trong file chạy cục bộ.

4. Chạy thủ công:
```bash
python src/fetch_data.py
python src/scan_breakout.py

Developed by Nguyen Van Thinh — Software Engineer & Quant Trader.
