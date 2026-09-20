import pandas as pd
import numpy as np
import mplfinance as mpf
import os

def export_breakout_chart(symbol, target_date, df, pre_days=20, post_days=25):
    """Hàm vẽ và lưu biểu đồ nến zoom quanh một phiên giao dịch mục tiêu"""
    target_idx = df.index.get_loc(target_date)
    start_idx = max(0, target_idx - pre_days)
    end_idx = min(len(df), target_idx + post_days + 1)
    
    zoom_df = df.iloc[start_idx:end_idx]

    # Đánh dấu mũi tên tím trên đỉnh cây nến Breakout
    marker = pd.Series(np.nan, index=zoom_df.index)
    marker.loc[target_date] = zoom_df.loc[target_date, 'High'] * 1.02
    breakout_plot = mpf.make_addplot(marker, type='scatter', markersize=120, marker='v', color='purple')

    # Định dạng tên file: images/HPG_breakout_YYYYMMDD.png
    os.makedirs("images", exist_ok=True)
    date_str = target_date.strftime('%Y-%m-%d')
    date_clean = target_date.strftime('%Y%m%d')
    output_path = f"images/{symbol}_breakout_{date_clean}.png"

    custom_style = mpf.make_mpf_style(base_mpf_style='yahoo', rc={'font.size': 10})
    mpf.plot(
        zoom_df,
        type='candle',
        volume=True,
        mav=(10, 20),
        addplot=breakout_plot,
        style=custom_style,
        title=f'{symbol} - Breakout {date_str}',
        ylabel='Gia (nghin VND)',
        ylabel_lower='Khoi luong',
        figratio=(14, 8),
        savefig=dict(fname=output_path, dpi=200, bbox_inches='tight') # DPI 200 giúp render nhanh và file nhẹ
    )
    print(f"-> Đã xuất: {output_path}")

# ================= CHƯƠNG TRÌNH CHÍNH =================
symbol = "HPG"
df = pd.read_csv(f"data/{symbol}_data.csv")
df['time'] = pd.to_datetime(df['time'])
df.set_index('time', inplace=True)
df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

# 1. Tính toán điều kiện Breakout
pct_change = df['Close'].pct_change() * 100
vol_ma20 = df['Volume'].rolling(20).mean()
rvol = df['Volume'] / vol_ma20

# 2. Tự động trích xuất danh sách các ngày thỏa mãn (RVol >= 2 và Giá tăng >= 2%)
breakout_dates = df[(rvol >= 2.0) & (pct_change >= 2.0)].index

print(f"-> Tìm thấy {len(breakout_dates)} phiên Breakout. Bắt đầu xuất biểu đồ...")

# 3. Chạy tự động xuất toàn bộ ảnh
for dt in breakout_dates:
    export_breakout_chart(symbol=symbol, target_date=dt, df=df)

print("-> Hoàn tất 100%! Tất cả ảnh đã nằm trong thư mục 'images/'.")