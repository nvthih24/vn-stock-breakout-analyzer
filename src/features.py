import pandas as pd

# 1. Đọc dữ liệu OHLCV
df = pd.read_csv("data/HPG_data.csv")

# 2. Tạo các đặc trưng (Features)
df['pct_change'] = df['close'].pct_change() * 100
df['vol_ma20'] = df['volume'].rolling(window=20).mean()
df['rvol'] = df['volume'] / df['vol_ma20']

# 3. Tính toán Forward Return (Lợi nhuận tương lai nếu mua ở giá đóng cửa hôm nay)
# Hàm .shift(-t) dùng để dịch chuyển hàng lên trên, lấy giá đóng cửa sau t phiên
for t in [3, 5, 10, 20]:
    df[f'return_T{t}'] = (df['close'].shift(-t) - df['close']) / df['close'] * 100

# 4. Lọc các phiên phát tín hiệu nổ Volume (RVol >= 2 và Giá tăng >= 2%)
signals = df[(df['rvol'] >= 2.0) & (df['pct_change'] >= 2.0)].copy()

# Chọn các cột cần xem
columns_to_show = ['time', 'close', 'pct_change', 'rvol', 'return_T3', 'return_T5', 'return_T10']
display_df = signals[columns_to_show].copy()
display_df['rvol'] = display_df['rvol'].round(2)
display_df['pct_change'] = display_df['pct_change'].round(2)
display_df['return_T3'] = display_df['return_T3'].round(2)
display_df['return_T5'] = display_df['return_T5'].round(2)
display_df['return_T10'] = display_df['return_T10'].round(2)

print("=== CHI TIẾT CÁC PHIÊN TÍN HIỆU VÀ LỢI NHUẬN TƯƠNG LAI ===")
print(display_df.tail(8))

# 5. Thống kê tỷ lệ thắng (Win Rate) và Lợi nhuận trung bình
print("\n" + "="*50)
print("=== THỐNG KÊ HIỆU SUẤT ĐỊNH LƯỢNG (QUANT PERFORMANCE) ===")
print("="*50)

for t in [3, 5, 10, 20]:
    valid_returns = signals[f'return_T{t}'].dropna()
    total_trades = len(valid_returns)
    win_trades = len(valid_returns[valid_returns > 0])
    win_rate = (win_trades / total_trades) * 100
    avg_return = valid_returns.mean()
    
    print(f"Khung T+{t:2d} | Tỷ lệ thắng: {win_rate:5.1f}% ({win_trades}/{total_trades} lệnh) | Lãi/Lỗ TB: {avg_return:+.2f}%")