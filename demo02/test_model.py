
import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error
from utils_lstm import load_and_clean_data, create_lstm_sequences
import sys

# --- 1. 設定 ---
folder_path = "./"
MODEL_DIR = "model"
DATA_DIR = "data"
TEST_DIR = "test"
MODEL_PATH = os.path.join(MODEL_DIR, "lstm_gold_predictor.h5")
SCALER_PATH = os.path.join(MODEL_DIR, "lstm_scaler.pkl")
SEQUENCE_LENGTH = 60

# --- 2. 主程式 ---
def test_model(test_filename):
    """
    載入已訓練的模型，並在指定的新測試檔案上進行評估。
    """
    print(f"\n--- 使用新資料 '{test_filename}' 進行模型測試 ---")
    
    test_filepath = os.path.join(TEST_DIR, test_filename)
    if not os.path.exists(test_filepath):
        print(f"❌ 錯誤：找不到測試檔案 '{test_filename}' 於 '{TEST_DIR}' 資料夾中。")
        return

    # 載入模型和 scaler
    try:
        model = load_model(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print(f"已從 {MODEL_PATH} 和 {SCALER_PATH} 載入模型與 Scaler。")
    except Exception as e:
        print(f"❌ 錯誤：載入模型或 scaler 失敗: {e}")
        return

    # 載入所有歷史數據和新的測試數據
    historical_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    df_hist = load_and_clean_data(historical_files)
    df_new_test = load_and_clean_data([test_filepath])
    print(f"已載入 {len(df_new_test)} 筆新測試資料。")

    # 準備測試數據
    test_input_data = pd.concat([df_hist.tail(SEQUENCE_LENGTH), df_new_test], ignore_index=True)
    scaled_test_prices = scaler.transform(test_input_data['Price'].values.reshape(-1, 1))
    
    # 建立測試序列
    X_test, y_test_scaled = create_lstm_sequences(scaled_test_prices, SEQUENCE_LENGTH)

    # #############  START: 新增的錯誤檢查 #############
    if len(X_test) == 0:
        print(f"\n❌ 錯誤：測試檔案 '{test_filename}' 的數據筆數太少，無法生成任何一個完整的測試序列。")
        print(f"   需要至少 {SEQUENCE_LENGTH + 1} 筆數據才能生成一個序列點進行測試。")
        return
    # #############  END: 新增的錯誤檢查 #############
    
    # 預測
    y_pred_scaled = model.predict(X_test)
    y_pred = scaler.inverse_transform(y_pred_scaled)
    y_test = scaler.inverse_transform(y_test_scaled.reshape(-1, 1))

    # 評估
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    print(f"\n新測試集 ({test_filename}) MAE: {mae:.2f}")
    print(f"新測試集 ({test_filename}) RMSE: {rmse:.2f}")
    
    # 視覺化
    plt.figure(figsize=(14, 7))
    plt.plot(df_new_test['Date'], y_test, 'b-o', label='真實價格', markersize=4)
    plt.plot(df_new_test['Date'], y_pred, 'r--x', label='模型預測價格', markersize=4)
    plt.title(f"新數據集 '{test_filename}' 上的價格預測 (LSTM)")
    plt.xlabel("日期")
    plt.ylabel("價格（美元）")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    test_filename = "Gold_202504_test.csv" # 預設測試檔案
    if len(sys.argv) > 1:
        test_filename = sys.argv[1]

    test_model(test_filename)