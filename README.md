# 🚀 VN30 Quant Breakout Analyzer & Telegram Alert Bot

Hệ thống giao dịch định lượng tự động (Quantitative Trading Bot) chuyên quét dòng tiền lớn và phát hiện các cơ hội bùng nổ (Breakout) cho rổ cổ phiếu **VN30**, tự động hóa toàn bộ trên đám mây và cảnh báo trực tiếp về Telegram.

---

## 📌 1. Giới thiệu dự án (Overview)

Dự án được xây dựng nhằm giải quyết bài toán tự động hóa việc sàng lọc cổ phiếu dựa trên hành vi dòng tiền thực tế thay vì cảm tính cá nhân. Hệ thống tự động cào dữ liệu cuối phiên, tính toán các chỉ báo kỹ thuật cốt lõi và gửi tín hiệu cảnh báo ngay khi xuất hiện dòng tiền thông minh (Smart Money) bước vào thị trường.

---

## ⚙️ 2. Chiến lược giao dịch (Strategy Rule)

Hệ thống kích hoạt tín hiệu mua (Alert) khi một cổ phiếu trong rổ VN30 thỏa mãn đồng thời các điều kiện khắt khe:

* **Biến động giá mạnh:** Giá tăng $\ge 2\%$ trong phiên giao dịch gần nhất[cite: 5].
* **Đột biến khối lượng (RVol):** Khối lượng giao dịch đạt từ **2.0x trở lên** so với mức trung bình lịch sử[cite: 5].
* **Quản trị rủi ro tự động:** Tự động tính toán điểm cắt lỗ (Stoploss) ngay tại mức **đáy của cây nến breakout**, giúp bảo vệ vốn tối ưu[cite: 5].

---

## 🛠️ 3. Công nghệ sử dụng (Tech Stack)

* **Language:** Python 3.10+
* **Data Source:** Thư viện `vnstock` [Lấy dữ liệu chứng khoán Việt Nam](cite: 5)
* **Data Analysis:** `pandas`, `numpy`
* **Automation (CI/CD):** GitHub Actions [Chạy định kỳ tự động qua Cron Schedule](cite: 2)
* **Notification:** Telegram Bot API (Gửi tin nhắn định dạng Markdown thời gian thực)

---

## 📂 4. Cấu trúc thư mục (Project Structure)

vn-stock-breakout-analyzer/
├── 📁 .github
│   └── 📁 workflows
│       └── ⚙️ bot.yml
├── 📁 data
│   ├── 📄 ACB_data.csv
│   ├── 📄 BCM_data.csv
│   ├── 📄 BID_data.csv
│   ├── 📄 BVH_data.csv
│   ├── 📄 CTG_data.csv
│   ├── 📄 FPT_data.csv
│   ├── 📄 GAS_data.csv
│   ├── 📄 GVR_data.csv
│   ├── 📄 HDB_data.csv
│   ├── 📄 HPG_data.csv
│   ├── 📄 MBB_data.csv
│   ├── 📄 MSN_data.csv
│   ├── 📄 MWG_data.csv
│   ├── 📄 PLX_data.csv
│   ├── 📄 POW_data.csv
│   ├── 📄 SAB_data.csv
│   ├── 📄 SHB_data.csv
│   ├── 📄 SSB_data.csv
│   ├── 📄 SSI_data.csv
│   ├── 📄 STB_data.csv
│   ├── 📄 TCB_data.csv
│   ├── 📄 TPB_data.csv
│   ├── 📄 VCB_data.csv
│   ├── 📄 VHM_data.csv
│   ├── 📄 VIB_data.csv
│   ├── 📄 VIC_data.csv
│   ├── 📄 VJC_data.csv
│   ├── 📄 VNM_data.csv
│   ├── 📄 VPB_data.csv
│   └── 📄 VRE_data.csv
├── 📁 images
│   ├── 🖼️ HPG_breakout_20240227.png
│   ├── 🖼️ HPG_breakout_20240515.png
│   ├── 🖼️ HPG_breakout_20241111.png
│   ├── 🖼️ HPG_breakout_20241205.png
│   ├── 🖼️ HPG_breakout_20250224.png
│   ├── 🖼️ HPG_breakout_20250227.png
│   ├── 🖼️ HPG_breakout_20250411.png
│   ├── 🖼️ HPG_breakout_20250612.png
│   ├── 🖼️ HPG_breakout_20250708.png
│   ├── 🖼️ HPG_breakout_20250805.png
│   ├── 🖼️ HPG_breakout_20251226.png
│   ├── 🖼️ HPG_breakout_20260112.png
│   ├── 🖼️ HPG_breakout_20260204.png
│   ├── 🖼️ HPG_breakout_20260224.png
│   ├── 🖼️ HPG_breakout_20260225.png
│   ├── 🖼️ HPG_breakout_20260408.png
│   ├── 🖼️ MSN_breakout_20231207.png
│   ├── 🖼️ MSN_breakout_20231208.png
│   ├── 🖼️ MSN_breakout_20240219.png
│   ├── 🖼️ MSN_breakout_20240229.png
│   ├── 🖼️ MSN_breakout_20240305.png
│   ├── 🖼️ MSN_breakout_20240517.png
│   ├── 🖼️ MSN_breakout_20241009.png
│   ├── 🖼️ MSN_breakout_20241010.png
│   ├── 🖼️ MSN_breakout_20250124.png
│   ├── 🖼️ MSN_breakout_20250313.png
│   ├── 🖼️ MSN_breakout_20250411.png
│   ├── 🖼️ MSN_breakout_20250605.png
│   ├── 🖼️ MSN_breakout_20250627.png
│   ├── 🖼️ MSN_breakout_20250811.png
│   ├── 🖼️ MSN_breakout_20251016.png
│   ├── 🖼️ MSN_breakout_20251203.png
│   ├── 🖼️ MSN_breakout_20260129.png
│   ├── 🖼️ MSN_breakout_20260507.png
│   └── 🖼️ MSN_breakout_20260922.png
├── 📁 src
│   ├── 🐍 chart_zoom.py
│   ├── 🐍 features.py
│   ├── 🐍 fetch_data.py
│   ├── 🐍 fetch_vn30.py
│   └── 🐍 scanner.py
├── ⚙️ .gitignore
├── 📝 README.md
├── 📄 requirements.txt
└── 📄 run_scanner.bat

## ⚙️ 5. Hướng dẫn cài đặt & Vận hành (Quick Start)
1. Clone repository về máy:
git clone [https://github.com/nvthih24/vn-stock-breakout-analyzer.git](https://github.com/nvthih24/vn-stock-breakout-analyzer.git)
cd vn-stock-breakout-analyzer
2. Cài đặt các thư viện cần thiết:
pip install -r requirements.txt
3. Cấu hình biến môi trường (Environment Variables):
Tạo token Telegram Bot và Chat ID của ông, sau đó cấu hình vào GitHub Secrets (TELEGRAM_TOKEN, TELEGRAM_CHAT_ID) nếu chạy trên Cloud, hoặc cấu hình trực tiếp trong file chạy cục bộ.
4. Chạy thủ công:
python src/fetch_data.py
python src/scan_breakout.py

Developed by Nguyen Van Thinh — Software Engineer & Quant Trader.
