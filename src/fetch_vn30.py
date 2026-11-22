import os
import time
from datetime import datetime
import pandas as pd
import requests

VN30_SYMBOLS = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
]

VCI_CHART_URL = "https://trading.vietcap.com.vn/api/chart/OHChart/gap-chart"
VCI_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://trading.vietcap.com.vn",
    "Referer": "https://trading.vietcap.com.vn/",
}


def _to_unix_ts(date_str: str, end_of_day: bool = False) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    if end_of_day:
        dt = dt.replace(hour=23, minute=59, second=59)
    return int(dt.timestamp())


def fetch_history(symbol: str, start_date: str = "2024-01-01", end_date: str | None = None) -> pd.DataFrame:
    """Lấy dữ liệu lịch sử ngày trực tiếp từ API VCI bằng requests + pandas."""
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    payload = {
        "timeFrame": "ONE_DAY",
        "symbols": [symbol],
        "from": _to_unix_ts(start_date, end_of_day=False),
        "to": _to_unix_ts(end_date, end_of_day=True),
    }

    resp = requests.post(VCI_CHART_URL, json=payload, headers=VCI_HEADERS, timeout=20)
    resp.raise_for_status()
    raw = resp.json()

    item = raw[0] if isinstance(raw, list) and raw else raw
    if not isinstance(item, dict) or not item.get("t"):
        return pd.DataFrame()

    df = pd.DataFrame({
        "time": pd.to_datetime(item["t"], unit="s", utc=True)
        .tz_convert("Asia/Ho_Chi_Minh")
        .tz_localize(None),
        "open": item.get("o", []),
        "high": item.get("h", []),
        "low": item.get("l", []),
        "close": item.get("c", []),
        "volume": item.get("v", []),
    })

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["close"]).reset_index(drop=True)


def main():
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    print(f"=== TIẾP TỤC PIPELINE TẢI DỮ LIỆU VN30 ({len(VN30_SYMBOLS)} MÃ) ===")
    start_time = time.time()
    success_count = 0

    for idx, sym in enumerate(VN30_SYMBOLS, 1):
        file_path = os.path.join(output_dir, f"{sym}_data.csv")

        # 1. Cơ chế Resume: Nếu file đã có dữ liệu, bỏ qua để tiết kiệm quota API
        if os.path.exists(file_path) and os.path.getsize(file_path) > 500:
            print(f"[{idx:02d}/30] {sym}: ⏩ Đã có sẵn trong data/, bỏ qua.")
            success_count += 1
            continue

        print(f"[{idx:02d}/30] Đang tải {sym}...", end=" ", flush=True)

        # 2. Cơ chế Retry tự động nếu gặp Rate Limit
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                df = fetch_history(sym)
                if df is not None and not df.empty:
                    df.to_csv(file_path, index=False, encoding="utf-8-sig")
                    print(f"✅ Hoàn tất ({len(df)} phiên)")
                    success_count += 1
                    break
                else:
                    print("❌ Không có dữ liệu")
                    break
            except Exception as e:
                err_msg = str(e)
                is_rate_limit = any(k in err_msg.lower() for k in ("rate limit", "429", "too many requests"))
                if is_rate_limit and attempt < max_retries:
                    print("⏳ Chạm giới hạn, nghỉ 25s trước khi thử lại...")
                    time.sleep(25)
                else:
                    print(f"❌ Lỗi: {err_msg}")
                    break

        # Nghỉ 3.5s giữa các mã để giữ tốc độ dưới ngưỡng 20 requests/phút
        time.sleep(3.5)

    elapsed = round(time.time() - start_time, 1)
    print("\n" + "=" * 50)
    print(f"Tổng kết: Sẵn sàng {success_count}/30 mã | Thời gian: {elapsed}s")


if __name__ == "__main__":
    main()