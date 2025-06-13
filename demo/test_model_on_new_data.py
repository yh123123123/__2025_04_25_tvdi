# test_model_on_new_data.py
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error
from utils_lstm import load_and_clean_data, create_lstm_sequences

# --- 1. 設定 ---
folder_path = "./"
historical_files = [folder_path + "investing_gold_2020_2025Feb.csv"]
new_test_file = [folder_path + "Gold_202503.csv"]
model_path = folder_path + "lstm_gold_predictor.h5"
scaler_path = folder_path + "lstm_scaler.pkl"
SEQUENCE_LENGTH = 60

# --- 2. 主程式 ---
if __name__ == "__main__":
    print("--- 開始執行 LSTM 模型測試腳本 ---")

    # 載入模型和 scaler
    try:
        model = load_model(model_path)
        scaler = joblib.load(scaler_path)
    except Exception as e:
        print(f"錯誤：載入模型或 scaler 失敗: {e}")
        exit()
    
    # 載入數據
    df_hist = load_and_clean_data(historical_files)
    df_new_test = load_and_clean_data(new_test_file)

    # 準備測試數據：需要歷史數據的尾部來生成第一個測試序列
    test_input_data = pd.concat([df_hist.tail(SEQUENCE_LENGTH), df_new_test], ignore_index=True)
    
    # 使用已載入的 scaler 進行標準化
    scaled_test_prices = scaler.transform(test_input_data['Price'].values.reshape(-1, 1))

    # 建立測試序列
    X_test, y_test_scaled = create_lstm_sequences(scaled_test_prices, SEQUENCE_LENGTH)
    
    # 預測
    y_pred_scaled = model.predict(X_test)

    # 反標準化
    y_pred = scaler.inverse_transform(y_pred_scaled)
    y_test = scaler.inverse_transform(y_test_scaled.reshape(-1, 1))

    # 評估
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"\n新測試集 (2025年3月) MAE: {mae:.2f}")
    print(f"新測試集 (2025年3月) RMSE: {rmse:.2f}")
    
    # 視覺化
    plt.figure(figsize=(14, 7))
    plt.plot(df_new_test['Date'], y_test, label='真實價格', color='blue', marker='o')
    plt.plot(df_new_test['Date'], y_pred, label='模型預測價格', color='red', linestyle='--', marker='x')
    plt.title("新數據集上的黃金價格預測 vs. 真實價格 (LSTM)")
    plt.xlabel("日期")
    plt.ylabel("價格（美元）")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()