import os
import time
from datetime import datetime
import pandas as pd

# Tắt thông báo telemetry để terminal gọn gàng
os.environ["VNSTOCK_TELEMETRY"] = "off"

try:
    from vnstock.api.quote import Quote
except ImportError:
    from vnstock import Vnstock
    Quote = None

VN30_SYMBOLS = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
]

def fetch_history(symbol, start_date="2024-01-01", end_date=None):
    """Lấy dữ liệu theo chuẩn Quote mới hoặc fallback về Vnstock cũ"""
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
        
    if Quote is not None:
        q = Quote(symbol=symbol, source="VCI")
        return q.history(start=start_date, end=end_date, interval="1D")
    else:
        stock = Vnstock().stock(symbol=symbol, source="VCI")
        return stock.quote.history(start=start_date, end=end_date, interval="1D")

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
                if "Rate limit" in err_msg or "rate limit" in err_msg or attempt < max_retries:
                    print(f"⏳ Chạm giới hạn, nghỉ 25s trước khi thử lại...")
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