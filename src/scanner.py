import os
import pandas as pd

def scan_market(data_dir="data"):
    print("=== 🔎 BỘ QUÉT TÍN HIỆU DÒNG TIỀN ĐỘT BIẾN (VN30) ===")
    results = []

    # Quét toàn bộ file CSV trong thư mục data/
    for file_name in os.listdir(data_dir):
        if not file_name.endswith("_data.csv"):
            continue
            
        symbol = file_name.split("_")[0]
        file_path = os.path.join(data_dir, file_name)
        
        try:
            # Đọc dữ liệu
            df = pd.read_csv(file_path)
            if len(df) < 20: 
                continue # Bỏ qua nếu dữ liệu quá ngắn không đủ tính MA20
            
            # Tính toán các đặc trưng (Features)
            df['pct_change'] = df['close'].pct_change() * 100
            df['vol_ma20'] = df['volume'].rolling(20).mean()
            df['rvol'] = df['volume'] / df['vol_ma20']
            
            # Chỉ lấy dữ liệu của phiên giao dịch GẦN NHẤT (dòng cuối cùng)
            last_row = df.iloc[-1]
            
            # ĐIỀU KIỆN LỌC: Khối lượng gấp đôi trung bình & Giá tăng hơn 2%
            if last_row['rvol'] >= 2.0 and last_row['pct_change'] >= 2.0:
                results.append({
                    'Mã CP': symbol,
                    'Ngày': last_row['time'],
                    'Giá Đóng': round(last_row['close'], 2),
                    '% Tăng': f"+{round(last_row['pct_change'], 2)}%",
                    'Khối lượng': f"{int(last_row['volume']):,}",
                    'Đột biến (RVol)': f"{round(last_row['rvol'], 2)}x"
                })
        except Exception as e:
            print(f"[!] Lỗi khi phân tích mã {symbol}: {e}")

    # In kết quả
    if results:
        print(f"\n🚀 PHÁT HIỆN {len(results)} MÃ CÓ DÒNG TIỀN LỚN NHẬP CUỘC PHIÊN GẦN NHẤT:")
        res_df = pd.DataFrame(results)
        print("-" * 75)
        print(res_df.to_string(index=False))
        print("-" * 75)
    else:
        print("\n💤 Thị trường bình yên. Không có mã nào thỏa mãn điều kiện Breakout ở phiên gần nhất.")

if __name__ == "__main__":
    scan_market()