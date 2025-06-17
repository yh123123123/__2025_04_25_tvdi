# utils_lstm.py
import pandas as pd
import numpy as np

def load_and_clean_data(file_paths):
    """
    從多個 CSV 檔案路徑載入、合併並清理資料。
    """
    try:
        dfs = [pd.read_csv(file) for file in file_paths]
    except FileNotFoundError as e:
        print(f"❌ 錯誤：找不到檔案 {e.filename}。請確認路徑是否正確。")
        return None

    df = pd.concat(dfs, ignore_index=True)
    
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Price'] = df['Price'].astype(str).replace(',', '', regex=True).astype(float)
    df = df.dropna(subset=['Date', 'Price'])
    df = df.sort_values('Date').reset_index(drop=True)
    df = df[~df['Date'].duplicated(keep='first')]
    
    return df[['Date', 'Price']]

def create_lstm_sequences(data, sequence_length):
    """
    將數據轉換為 LSTM 適用的序列格式 (samples, time steps, features)。
    """
    X, y = [], []
    for i in range(sequence_length, len(data)):
        X.append(data[i-sequence_length:i, 0])
        y.append(data[i, 0])
    
    X, y = np.array(X), np.array(y)
    X = np.reshape(X, (X.shape[0], X.shape[1], 1))
    return X, y