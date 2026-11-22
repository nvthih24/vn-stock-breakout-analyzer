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

VCI_CHART_URL = "https://trading.vietcap.com.vn/api/chart/OHLCChart/gap-chart"
VCI_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://trading.vietcap.com.vn",
    "Referer": "https://trading.vietcap.com.vn/",
}


def _to_end_stamp(end_date: str | None = None) -> int:
    if end_date is None:
        dt = datetime.now().replace(hour=23, minute=59, second=59)
    else:
        dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
    return int(dt.timestamp())

def _parse_ts_series(ts_values) -> pd.Series:
    s = pd.to_numeric(pd.Series(ts_values), errors="coerce").dropna()
    if s.empty:
        return pd.Series(dtype="datetime64[ns]")
    max_val = s.max()
    # Tự nhận diện giây (10 chữ số) vs mili-giây (13 chữ số)
    unit = "ms" if max_val > 1e11 else "s"
    dt = pd.to_datetime(s, unit=unit, utc=True, errors="coerce")
    return dt.dt.tz_convert("Asia/Ho_Chi_Minh").dt.tz_localize(None)

def fetch_history(symbol: str, end_date: str | None = None, count_back: int = 750) -> pd.DataFrame:
    """Lấy dữ liệu lịch sử ngày trực tiếp từ API OHLCChart của VCI."""
    payload = {
        "timeFrame": "ONE_DAY",
        "symbols": [symbol],
        "to": _to_end_stamp(end_date),
        "countBack": count_back,
    }

    resp = requests.post(VCI_CHART_URL, json=payload, headers=VCI_HEADERS, timeout=20)
    resp.raise_for_status()
    raw = resp.json()

    if isinstance(raw, dict) and "data" in raw:
        raw = raw["data"]

    if not raw:
        return pd.DataFrame()

    # Trường hợp 1: API trả danh sách từng nến [{"t": ..., "o": ..., "h": ..., "l": ..., "c": ..., "v": ...}]
    if isinstance(raw, list) and isinstance(raw[0], dict) and "t" in raw[0]:
        df = pd.DataFrame(raw)
        rename_map = {"t": "time", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
        df["time"] = _parse_ts_series(df["time"])
    else:
        # Trường hợp 2: API trả dict hoặc list chứa dict dạng cột {"t": [...], "o": [...], ...}
        item = raw[0] if isinstance(raw, list) else raw
        if not isinstance(item, dict) or not item.get("t"):
            return pd.DataFrame()
        df = pd.DataFrame({
            "time": _parse_ts_series(item.get("t", [])),
            "open": item.get("o", []),
            "high": item.get("h", []),
            "low": item.get("l", []),
            "close": item.get("c", []),
            "volume": item.get("v", []),
        })

    for col in ["open", "high", "low", "close", "volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.dropna(subset=["time", "close"]).sort_values("time").reset_index(drop=True)


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