
import matplotlib
matplotlib.use('Agg')  # <-- 關鍵！設定非 GUI 後端，必須在 pyplot import 之前

import os
import joblib
import pandas as pd
import numpy as np
from datetime import timedelta
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import base64
from io import BytesIO

from utils_lstm import load_and_clean_data, create_lstm_sequences

# --- App 初始化與設定 ---
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# 設定上傳資料夾和模型路徑
UPLOAD_FOLDER = 'uploads'
DATA_DIR = os.path.join(UPLOAD_FOLDER, 'data')
TEST_DIR = os.path.join(UPLOAD_FOLDER, 'test')
MODEL_DIR = 'model'
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(TEST_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "lstm_gold_predictor.h5")
SCALER_PATH = os.path.join(MODEL_DIR, "lstm_scaler.pkl")
SEQUENCE_LENGTH = 60

# 在啟動時載入模型、Scaler 和數據
try:
    model = load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    all_data_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    # 如果 data 資料夾是空的，不要報錯，讓使用者可以透過網頁上傳
    if all_data_files:
        full_df = load_and_clean_data(all_data_files).set_index('Date')
    else:
        full_df = pd.DataFrame(columns=['Price']).set_index(pd.to_datetime([])) # 創建一個空的 DataFrame
    print("✅ 模型、Scaler 和歷史數據已成功載入。")
except Exception as e:
    print(f"⚠️ 啟動時載入模型或數據失敗 (可能是首次啟動): {e}")
    model = None
    scaler = None
    full_df = pd.DataFrame(columns=['Price']).set_index(pd.to_datetime([]))

# --- 路由設定 ---
@app.route('/')
def index():
    return redirect(url_for('predict_page'))

# --- 1. 模型訓練功能 ---
@app.route('/train', methods=['GET', 'POST'])
def train_page():
    if request.method == 'POST':
        # 處理檔案上傳
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            flash('錯誤：未選擇任何檔案。', 'danger')
            return redirect(request.url)
        
        # 清空舊的訓練數據
        for f in os.listdir(DATA_DIR):
            os.remove(os.path.join(DATA_DIR, f))
            
        for file in files:
            if file and file.filename.endswith('.csv'):
                filename = secure_filename(file.filename)
                file.save(os.path.join(DATA_DIR, filename))
        
        flash(f'成功上傳 {len(files)} 個檔案。', 'info')

        # 執行訓練
        try:
            train_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR)]
            price_data = load_and_clean_data(train_files)
            
            scaler_instance = MinMaxScaler(feature_range=(0, 1))
            scaled_prices = scaler_instance.fit_transform(price_data['Price'].values.reshape(-1, 1))
            X_train, y_train = create_lstm_sequences(scaled_prices, SEQUENCE_LENGTH)

            model_instance = Sequential([
                LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)),
                Dropout(0.2),
                LSTM(units=50, return_sequences=False),
                Dropout(0.2),
                Dense(units=25),
                Dense(units=1)
            ])
            model_instance.compile(optimizer='adam', loss='mean_squared_error')
            model_instance.fit(X_train, y_train, epochs=25, batch_size=32, verbose=0)
            
            model_instance.save(MODEL_PATH)
            joblib.dump(scaler_instance, SCALER_PATH)
            
            flash('模型訓練成功，並已儲存！', 'success')
        except Exception as e:
            flash(f'模型訓練失敗：{e}', 'danger')

        return redirect(url_for('train_page'))

    return render_template('train.html')

# --- 2. 模型測試功能 ---
@app.route('/test', methods=['GET', 'POST'])
def test_page():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('錯誤：未選擇測試檔案。', 'danger')
            return redirect(request.url)

        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            test_filepath = os.path.join(TEST_DIR, filename)
            file.save(test_filepath)
            
            try:
                model_test = load_model(MODEL_PATH)
                scaler_test = joblib.load(SCALER_PATH)
                
                train_files = [os.path.join(DATA_DIR, f) for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
                df_hist = load_and_clean_data(train_files)
                df_new_test = load_and_clean_data([test_filepath])
                
                # 準備測試數據
                test_input_data = pd.concat([df_hist.tail(SEQUENCE_LENGTH), df_new_test], ignore_index=True)
                scaled_test_prices = scaler_test.transform(test_input_data['Price'].values.reshape(-1, 1))
                
                # 建立測試序列
                X_test, y_test_scaled = create_lstm_sequences(scaled_test_prices, SEQUENCE_LENGTH)
                
                # #############  START: 新增的錯誤檢查 #############
                if len(X_test) == 0:
                    flash(f"錯誤：測試檔案 '{filename}' 的數據筆數太少，無法生成任何一個完整的測試序列（需要 > {SEQUENCE_LENGTH} 筆數據）。", 'danger')
                    return render_template('test.html', result=None)
                # #############  END: 新增的錯誤檢查 #############

                # 進行預測
                y_pred_scaled = model_test.predict(X_test)
                y_pred = scaler_test.inverse_transform(y_pred_scaled)
                y_test = scaler_test.inverse_transform(y_test_scaled.reshape(-1, 1))
                
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))

                # 生成圖表
                fig = plt.figure(figsize=(10, 5))
                plt.plot(df_new_test['Date'], y_test, 'b-o', label='真實價格')
                plt.plot(df_new_test['Date'], y_pred, 'r--x', label='預測價格')
                plt.title(f"'{filename}' 測試結果")
                plt.legend()
                plt.grid(True)
                
                buf = BytesIO()
                fig.savefig(buf, format="png")
                plot_data = base64.b64encode(buf.getbuffer()).decode("ascii")
                plt.close(fig)

                return render_template('test.html', result={'mae': f'{mae:.2f}', 'rmse': f'{rmse:.2f}', 'plot': plot_data})

            except Exception as e:
                flash(f'模型測試失敗：{e}', 'danger')

    return render_template('test.html')

# --- 3. 預測明日價格功能 ---
@app.route('/predict', methods=['GET', 'POST'])
def predict_page():
    if model is None:
        flash('模型尚未訓練，請先前往「訓練模型」頁面進行訓練。', 'warning')
        return render_template('predict.html', error="模型未載入")
        
    latest_date = full_df.index.max().strftime('%Y-%m-%d') if not full_df.empty else ""

    if request.method == 'POST':
        target_date_str = request.form.get('date')
        if not target_date_str:
            flash('請選擇一個基準日期。', 'warning')
            return render_template('predict.html', latest_date=latest_date)

        try:
            target_date = pd.to_datetime(target_date_str)
            
            last_60_days = full_df.loc[:target_date].tail(SEQUENCE_LENGTH)

            if len(last_60_days) < SEQUENCE_LENGTH:
                flash(f"歷史數據不足（需要 {SEQUENCE_LENGTH} 天）。", "warning")
                return render_template('predict.html', latest_date=latest_date)

            today_price = full_df.loc[target_date]['Price']
            
            last_60_days_scaled = scaler.transform(last_60_days['Price'].values.reshape(-1, 1))
            input_feature = np.reshape(last_60_days_scaled, (1, SEQUENCE_LENGTH, 1))
            
            predicted_price_scaled = model.predict(input_feature)
            predicted_price = scaler.inverse_transform(predicted_price_scaled)[0][0]
            
            result = {
                'target_date': target_date.strftime('%Y-%m-%d'),
                'today_price': f"${today_price:,.2f}",
                'next_day': (target_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                'predicted_price': f"${predicted_price:,.2f}"
            }
            return render_template('predict.html', result=result, latest_date=latest_date)

        except KeyError:
            flash(f"資料庫中找不到日期 '{target_date_str}' 的價格。", 'danger')
        except Exception as e:
            flash(f'預測時發生錯誤: {e}', 'danger')

    return render_template('predict.html', latest_date=latest_date)

if __name__ == '__main__':
    app.run(debug=True)