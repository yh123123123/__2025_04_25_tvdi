# predict_tomorrow.py
import pandas as pd
import numpy as np
import joblib
from datetime import timedelta
from tensorflow.keras.models import load_model
from utils_lstm import load_and_clean_data

# --- 1. 設定 ---
folder_path = "./"
all_data_files = [
    folder_path + "investing_gold_2020_2025Feb.csv",
    folder_path + "Gold_202503.csv"
]
model_path = folder_path + "lstm_gold_predictor.h5"
scaler_path = folder_path + "lstm_scaler.pkl"
SEQUENCE_LENGTH = 60

# --- 2. 預測函式 ---
def predict_next_day_price(target_date_str):
    try:
        # 載入模型和 scaler
        model = load_model(model_path)
        scaler = joblib.load(scaler_path)
        full_df = load_and_clean_data(all_data_files)
        full_df.set_index('Date', inplace=True)

        target_date = pd.to_datetime(target_date_str)
        
        # 選取預測所需的最後60天數據
        last_60_days = full_df.loc[:target_date].tail(SEQUENCE_LENGTH)

        if len(last_60_days) < SEQUENCE_LENGTH:
            print(f"❌ 錯誤：歷史數據不足（需要 {SEQUENCE_LENGTH} 天）。")
            return

        # 標準化與塑形
        last_60_days_scaled = scaler.transform(last_60_days['Price'].values.reshape(-1, 1))
        input_feature = np.reshape(last_60_days_scaled, (1, SEQUENCE_LENGTH, 1))
        
        # 預測
        predicted_price_scaled = model.predict(input_feature)
        predicted_price = scaler.inverse_transform(predicted_price_scaled)[0][0]

        # 顯示結果
        next_day = target_date + timedelta(days=1)
        print("\n" + "="*40)
        print(f"🔍 查詢基準日期: {target_date.strftime('%Y-%m-%d')}")
        print(f"   當日收盤價: ${full_df.loc[target_date]['Price']:,.2f}")
        print("-"*40)
        print(f"📈 預測目標日期: {next_day.strftime('%Y-%m-%d')}")
        print(f"💰 預測明日金價: ${predicted_price:,.2f}")
        print("="*40)

    except FileNotFoundError:
        print("錯誤：找不到模型或 scaler 檔案。請先執行 'train_lstm_model.py'。")
    except KeyError:
        print(f"\n錯誤：在資料庫中找不到日期 '{target_date_str}'。")
    except Exception as e:
        print(f"\n預測時發生未知錯誤: {e}")

# --- 3. 主程式 ---
if __name__ == "__main__":
    print("黃金價格明日預測工具")
    date_input = input("\n請輸入要預測的基準日期 (格式 YYYY-MM-DD): ")
    predict_next_day_price(date_input)