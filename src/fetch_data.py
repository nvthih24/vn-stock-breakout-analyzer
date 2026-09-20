from vnstock import Vnstock
import pandas as pd

# Khởi tạo đối tượng cổ phiếu HPG với nguồn dữ liệu VCI
symbol = "HPG"
stock = Vnstock().stock(symbol=symbol, source="VCI")

print(f"-> Đang tải dữ liệu giao dịch của {symbol}...")

# Lấy dữ liệu lịch sử nến ngày (1D)
df = stock.quote.history(start="2024-01-01", end="2026-09-20", interval="1D")

# In 5 phiên gần nhất
print("\n=== 5 PHIÊN GIAO DỊCH GẦN NHẤT ===")
print(df.tail())

# Xuất ra file CSV
output_file = f"data/{symbol}_data.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\n-> Đã lưu thành công dữ liệu vào: {output_file}")