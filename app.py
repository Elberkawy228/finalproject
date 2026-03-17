import streamlit as st
import pandas as pd
import numpy as np
import joblib

# 1. تحميل الموديل والعواميد
model = joblib.load('car_price_model.pkl')
model_columns = joblib.load('model_columns.pkl')

# 2. تصميم واجهة الموقع
st.title("🚗 مقيم أسعار السيارات الذكي")
st.write("أدخل مواصفات سيارتك لمعرفة سعرها المتوقع في السوق!")

# 3. أسئلة للعميل (أمثلة، تقدر تزود براحتك)
power = st.number_input("قوة الموتور (بالحصان):", min_value=30.0, max_value=500.0, value=100.0)
engine = st.number_input("سعة الموتور (CC):", min_value=500.0, max_value=600.0, value=1500.0)
car_age = st.number_input("عمر السيارة (بالسنوات):", min_value=0, max_value=30, value=5)
transmission = st.selectbox("نوع الناقل:", ["Automatic", "Manual"])

# 4. زرار النتيجة
if st.button("احسب السعر 💰"):
    # تجميع ردود العميل
    trans_val = 1 if transmission == "Automatic" else 0
    power_per_cc = power / engine  # الميزة اللي إحنا اخترعناها
    
    # عمل قاموس مبدئي بردود العميل
    input_data = {
        'Power': power,
        'Engine': engine,
        'Car_Age': car_age,
        'Transmission': trans_val,
        'Power_per_cc': power_per_cc
    }
    
    # تحويله لـ DataFrame من سطر واحد
    input_df = pd.DataFrame([input_data])
    
    # إضافة باقي العواميد بـ 0 عشان الموديل ميزعلش (زي المدن وباقي أنواع الوقود)
    for col in model_columns:
        if col not in input_df.columns:
            input_df[col] = 0
            
    # ترتيب العواميد زي ما الموديل متعود
    input_df = input_df[model_columns]
    
    # التوقع (وفك شفرة اللوجارتم اللي عملناها)
    predicted_log = model.predict(input_df)
    real_price = np.expm1(predicted_log)[0]
    
    st.success(f"السعر المتوقع: {real_price:.2f} Lakh")