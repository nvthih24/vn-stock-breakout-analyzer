import os
import time
from datetime import datetime, timedelta, timezone
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
VN_TZ = timezone(timedelta(hours=7))


def _now_vn() -> datetime:
    return datetime.now(VN_TZ)


def _to_end_stamp(end_date: str | None = None) -> int:
    if end_date is None:
        dt = _now_vn().replace(hour=23, minute=59, second=59)
    else:
        dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=VN_TZ, hour=23, minute=59, second=59)
    return int(dt.timestamp())


def get_expected_session_date(now_vn: datetime | None = None) -> str:
    """Tính ngày phiên giao dịch mới nhất kỳ vọng theo giờ Việt Nam (+07)."""
    dt = now_vn or _now_vn()
    d = dt.date()

    # Cuối tuần: lùi về Thứ Sáu
    if d.weekday() == 5:  # Thứ 7
        d = d - timedelta(days=1)
    elif d.weekday() == 6:  # Chủ Nhật
        d = d - timedelta(days=2)
    else:
        # Ngày thường: nếu trước 15:00 thì dữ liệu EOD của phiên hôm nay có thể chưa chốt
        if dt.hour < 15:
            d = d - timedelta(days=1)
            if d.weekday() == 6:
                d = d - timedelta(days=2)
            elif d.weekday() == 5:
                d = d - timedelta(days=1)

    return d.strftime("%Y-%m-%d")


def is_csv_up_to_date(file_path: str, expected_date: str) -> tuple[bool, str | None]:
    """Kiểm tra file CSV có tồn tại, đọc được và có nến mới nhất >= expected_date hay không."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) < 100:
        return False, None

    try:
        df = pd.read_csv(file_path)
        if df.empty or "time" not in df.columns or "close" not in df.columns:
            return False, None

        times = pd.to_datetime(df["time"], errors="coerce").dropna()
        if times.empty:
            return False, None

        last_date_str = times.max().strftime("%Y-%m-%d")
        return last_date_str >= expected_date, last_date_str
    except Exception:
        return False, None


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

    item = raw[0] if isinstance(raw, list) and raw else raw
    if not isinstance(item, dict) or not item.get("t"):
        return pd.DataFrame()

    ts_num = pd.to_numeric(pd.Series(item.get("t", [])), errors="coerce")
    df = pd.DataFrame({
        "time": pd.to_datetime(ts_num, unit="s", utc=True, errors="coerce")
        .dt.tz_convert("Asia/Ho_Chi_Minh")
        .dt.tz_localize(None),
        "open": item.get("o", []),
        "high": item.get("h", []),
        "low": item.get("l", []),
        "close": item.get("c", []),
        "volume": item.get("v", []),
    })

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return (
        df.dropna(subset=["time", "close"])
        .sort_values("time")
        .drop_duplicates(subset=["time"], keep="last")
        .reset_index(drop=True)
    )


def main():
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)

    expected_date = get_expected_session_date()
    print(f"=== PIPELINE TẢI DỮ LIỆU VN30 ({len(VN30_SYMBOLS)} MÃ) | PHIÊN KỲ VỌNG: {expected_date} ===")
    start_time = time.time()
    success_count = 0

    for idx, sym in enumerate(VN30_SYMBOLS, 1):
        file_path = os.path.join(output_dir, f"{sym}_data.csv")

        up_to_date, last_date = is_csv_up_to_date(file_path, expected_date)
        if up_to_date:
            print(f"[{idx:02d}/30] {sym}: ⏩ Đã cập nhật đến {last_date}, bỏ qua.")
            success_count += 1
            continue

        reason = f"chỉ có dữ liệu tới {last_date}" if last_date else "chưa có file hoặc file lỗi"
        print(f"[{idx:02d}/30] Đang tải {sym} ({reason})...", end=" ", flush=True)

        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                df = fetch_history(sym)
                if df is not None and not df.empty:
                    df.to_csv(file_path, index=False, encoding="utf-8-sig")
                    new_last = pd.to_datetime(df["time"]).max().strftime("%Y-%m-%d")
                    print(f"✅ Hoàn tất ({len(df)} phiên, mới nhất: {new_last})")
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

        time.sleep(3.5)

    elapsed = round(time.time() - start_time, 1)
    print("\n" + "=" * 50)
    print(f"Tổng kết: Sẵn sàng {success_count}/30 mã | Thời gian: {elapsed}s")


if __name__ == "__main__":
    main()