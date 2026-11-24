import os
from datetime import datetime
import pandas as pd
import requests


def send_telegram_message(message: str):
    """Gửi tin nhắn qua Telegram Bot (tự chia đoạn nếu vượt giới hạn 4096 ký tự)."""
    bot_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("[!] Thiếu Telegram Token hoặc Chat ID. Chỉ in kết quả ra màn hình.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    max_len = 4000
    chunks = [message[i : i + max_len] for i in range(0, len(message), max_len)]

    for chunk in chunks:
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        try:
            resp = requests.post(url, data=payload, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            print(f"Lỗi khi gửi Telegram: {e}")


def _format_price(val: float) -> str:
    """Định dạng giá: nếu giá lớn hơn hoặc bằng 500 thì làm tròn nguyên, nhỏ hơn thì giữ 2 số lẻ."""
    if abs(val) >= 500:
        return f"{round(val):,}"
    return f"{val:,.2f}"


def _format_pct(pct: float) -> str:
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.2f}%"


def scan_market(data_dir: str = "data", rvol_min: float = 2.0, pct_min: float = 2.0):
    print("=== 🔎 BỘ QUÉT TÍN HIỆU DÒNG TIỀN ĐỘT BIẾN (VN30) ===")
    signals = []
    watchlist_rows = []
    latest_dates = []

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
            if len(df) < 21:
                continue

            df["pct_change"] = df["close"].pct_change() * 100
            df["vol_ma20"] = df["volume"].rolling(20).mean()
            df["rvol"] = df["volume"] / df["vol_ma20"]

            last_row = df.iloc[-1]
            latest_dates.append(str(last_row["time"])[:10])

            rvol = float(last_row["rvol"])
            pct = float(last_row["pct_change"])
            close_val = float(last_row["close"])
            low_val = float(last_row["low"])
            vol_val = int(last_row["volume"])

            if pd.isna(rvol) or pd.isna(pct):
                continue

            watchlist_rows.append({
                "symbol": symbol,
                "close": close_val,
                "pct": pct,
                "rvol": rvol,
                "volume": vol_val,
            })

            if rvol >= rvol_min and pct >= pct_min:
                signals.append(
                    f"🟢 <b>{symbol}</b> — Giá: <code>{_format_price(close_val)}</code> (<b>{_format_pct(pct)}</b>)\n"
                    f"• Vol: <code>{vol_val:,}</code> (<b>RVol: {rvol:.2f}x</b>)\n"
                    f"• Cắt lỗ (thủng đáy nến): <code>{_format_price(low_val)}</code>"
                )
        except Exception as e:
            print(f"[!] Lỗi xử lý {symbol}: {e}")

    session_date = max(latest_dates) if latest_dates else datetime.now().strftime("%Y-%m-%d")

    if signals:
        body = "\n\n".join(signals)
        msg = (
            f"🚀 <b>VN30 BREAKOUT SIGNAL</b> | <i>{session_date}</i>\n"
            f"Điều kiện: <code>RVol ≥ {rvol_min:.1f}x</code> &amp; <code>Tăng ≥ +{pct_min:.1f}%</code> (<b>{len(signals)}</b> mã)\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{body}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Báo cáo tự động cuối phiên (EOD). Tham khảo quản trị rủi ro.</i>"
        )
    else:
        top3 = sorted(watchlist_rows, key=lambda x: x["rvol"], reverse=True)[:3]
        if top3:
            top_lines = "\n".join(
                f"{idx}. <b>{row['symbol']}</b> — RVol: <code>{row['rvol']:.2f}x</code> | Giá: <code>{_format_price(row['close'])}</code> (<code>{_format_pct(row['pct'])}</code>)"
                for idx, row in enumerate(top3, 1)
            )
            watchlist_block = f"\n\n📌 <b>Top 3 RVol cao nhất phiên để theo dõi:</b>\n{top_lines}"
        else:
            watchlist_block = ""

        msg = (
            f"💤 <b>VN30 — KHÔNG CÓ TÍN HIỆU BREAKOUT</b> | <i>{session_date}</i>\n"
            f"Điều kiện: <code>RVol ≥ {rvol_min:.1f}x</code> &amp; <code>Tăng ≥ +{pct_min:.1f}%</code>"
            f"{watchlist_block}"
        )

    print(msg)
    send_telegram_message(msg)


if __name__ == "__main__":
    scan_market()