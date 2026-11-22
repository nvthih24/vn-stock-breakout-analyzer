import os
import pandas as pd
import requests


def send_telegram_message(message: str):
    """Hàm gửi tin nhắn qua Telegram Bot."""
    bot_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("[!] Thiếu Telegram Token hoặc Chat ID. Chỉ in kết quả ra màn hình.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        resp = requests.post(url, data=payload, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Lỗi khi gửi Telegram: {e}")


def scan_market(data_dir: str = "data"):
    print("=== 🔎 BỘ QUÉT TÍN HIỆU DÒNG TIỀN ĐỘT BIẾN (VN30) ===")
    results = []

    if not os.path.isdir(data_dir):
        print(f"[!] Không tìm thấy thư mục {data_dir}")
        return

    for file_name in sorted(os.listdir(data_dir)):
        if not file_name.endswith("_data.csv"):
            continue

        symbol = file_name.split("_")[0]
        file_path = os.path.join(data_dir, file_name)

        try:
            df = pd.read_csv(file_path)
            df = df.sort_values("time").reset_index(drop=True)
            if len(df) < 20:
                continue

            df["pct_change"] = df["close"].pct_change() * 100
            df["vol_ma20"] = df["volume"].rolling(20).mean()
            df["rvol"] = df["volume"] / df["vol_ma20"]

            last_row = df.iloc[-1]

            if last_row["rvol"] >= 2.0 and last_row["pct_change"] >= 2.0:
                stoploss = round(last_row["low"], 2)
                results.append(
                    f"🟢 <b>{symbol}</b> | Giá: {round(last_row['close'], 2)} (+{round(last_row['pct_change'], 2)}%)\n"
                    f"📦 Vol: {int(last_row['volume']):,} (RVol: {round(last_row['rvol'], 2)}x)\n"
                    f"🛑 Cắt lỗ: Kích hoạt bán nếu thủng {stoploss} (Đáy nến)"
                )
        except Exception as e:
            print(f"[!] Lỗi xử lý {symbol}: {e}")

    if results:
        msg = "🚀 <b>PHÁT HIỆN DÒNG TIỀN VN30 PHIÊN GẦN NHẤT:</b>\n\n" + "\n\n".join(results)
    else:
        msg = "💤 <b>Thị trường bình yên</b>\nKhông có mã VN30 nào Breakout phiên gần nhất."

    print(msg)
    send_telegram_message(msg)


if __name__ == "__main__":
    scan_market()