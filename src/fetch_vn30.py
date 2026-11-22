import os
import sys
import time
from datetime import datetime
from unittest.mock import MagicMock
import pandas as pd

# Mock thư viện chart để vnstock nạp đầy đủ explorer/VCI trên runner
sys.modules.setdefault("vnstock_ezchart", MagicMock())
sys.modules.setdefault("vnstock_chart", MagicMock())

# Tắt thông báo telemetry để terminal gọn gàng
os.environ["VNSTOCK_TELEMETRY"] = "off"

from vnstock.explorer.vci import quote as vci_quote
from vnstock.explorer.vci.quote import Quote as VCIQuote

# Nếu optimize_execution bị mock thành MagicMock, trả về hàm pass-through để gọi thực thi bình thường
if isinstance(getattr(vci_quote, "optimize_execution", None), MagicMock):
    def _passthrough_optimize_execution(func=None, *args, **kwargs):
        if callable(func):
            def _wrapper(*f_args, **f_kwargs):
                return func(*f_args, **f_kwargs)
            return _wrapper
        return lambda f: f
    vci_quote.optimize_execution = _passthrough_optimize_execution

VN30_SYMBOLS = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
]

def fetch_history(symbol, start_date="2024-01-01", end_date=None):
    """Lấy dữ liệu lịch sử ngày từ VCIQuote"""
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    q = VCIQuote(symbol=symbol)
    df = q.history(start=start_date, end=end_date, interval="1D")

    # Phòng trường hợp decorator vẫn trả về MagicMock
    if isinstance(df, MagicMock) and hasattr(q, "_history"):
        df = q._history(start=start_date, end=end_date, interval="1D")

    return df

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
    print("\n" + "="*50)
    print(f"Tổng kết: Sẵn sàng {success_count}/30 mã | Thời gian: {elapsed}s")

if __name__ == "__main__":
    main()