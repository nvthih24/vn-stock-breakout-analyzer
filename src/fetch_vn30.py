import os
import time
from datetime import datetime, timedelta
import pandas as pd
import requests

VN30_SYMBOLS = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
]

VCI_CHART_URL = "https://trading.vietcap.com.vn/api/chart/OHLCChart/gap-chart"
VCI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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


def get_expected_session_date(now_dt: datetime | None = None) -> str:
    """Tính ngày phiên giao dịch mới nhất kỳ vọng (lùi về Thứ Sáu nếu cuối tuần)."""
    dt = now_dt or datetime.now()
    d = dt.date()

    if d.weekday() == 5:  # Thứ 7
        d = d - timedelta(days=1)
    elif d.weekday() == 6:  # Chủ Nhật
        d = d - timedelta(days=2)
    elif dt.hour < 15:
        d = d - timedelta(days=1)
        if d.weekday() == 6:
            d = d - timedelta(days=2)
        elif d.weekday() == 5:
            d = d - timedelta(days=1)

    return d.strftime("%Y-%m-%d")


def is_csv_up_to_date(file_path: str, expected_date: str) -> tuple[bool, str | None]:
    """Chỉ bỏ qua file CSV khi file đã có nến cập nhật đến phiên giao dịch mới nhất."""
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