# train_lstm_model.py
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from utils_lstm import load_and_clean_data, create_lstm_sequences

# --- 1. 設定 ---
folder_path = "./" # 假設檔案在同級目錄
historical_files = [
    folder_path + "investing_gold_2020_2025Feb.csv",
    folder_path + "Gold_202503.csv"
]
model_save_path = folder_path + "lstm_gold_predictor.h5"
scaler_save_path = folder_path + "lstm_scaler.pkl"
SEQUENCE_LENGTH = 60

# --- 2. 主程式 ---
if __name__ == "__main__":
    print("--- 開始執行 LSTM 模型訓練腳本 ---")

    # 載入數據
    price_data = load_and_clean_data(historical_files)
    
    # 分割訓練集與驗證集 (先分割再標準化，防止數據洩漏)
    train_size = int(len(price_data) * 0.8)
    train_data = price_data.iloc[:train_size]
    val_data = price_data.iloc[train_size:]

    # 標準化
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_train_prices = scaler.fit_transform(train_data['Price'].values.reshape(-1, 1))
    
    # 建立訓練序列
    X_train, y_train = create_lstm_sequences(scaled_train_prices, SEQUENCE_LENGTH)

    # 建立模型
    model = Sequential([
        LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
        Dropout(0.2),
        LSTM(units=50, return_sequences=False),
        Dropout(0.2),
        Dense(units=25),
        Dense(units=1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.summary()

    # 訓練模型
    print("\n開始訓練 LSTM 模型...")
    model.fit(X_train, y_train, epochs=25, batch_size=32, verbose=1)
    print("\n模型訓練完成 ✅")

    # 儲存模型和 scaler
    model.save(model_save_path)
    joblib.dump(scaler, scaler_save_path)
    print(f"模型已儲存至: {model_save_path}")
    print(f"Scaler 已儲存至: {scaler_save_path}")