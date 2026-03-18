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
engine = st.number_input("سعة الموتور (CC):", min_value=500.0, max_value=6000.0, value=1500.0)
car_age = st.number_input("عمر السيارة (بالسنوات):", min_value=0, max_value=30, value=5)
transmission = st.selectbox("نوع الناقل:", ["Automatic", "Manual"])

# 4. زرار النتيجة
if st.button("احسب السعر 💰"):
    # 1. تجميع ردود العميل (خلي بالك: 1 يعني مانيوال و 0 أوتوماتيك زي ما الداتا كانت متظبطة غالباً)
    trans_val = 1 if transmission == "Manual" else 0
    power_per_cc = power / engine
    
    # 2. عمل قاموس مبدئي بردود العميل (قبل الـ Log)
    input_data = {
        'Power': power,
        'Engine': engine,
        'Car_Age': car_age,
        'Kilometers_Driven': 50000, # حطينا قيم تقريبية للعواميد اللي ناقصة عشان الموديل ميزعلش
        'Seats': 5,
        'Mileage': 18.0,
        'Transmission_Manual': trans_val, # اسم العمود زي ما طلع من الـ get_dummies
        'Power_per_cc': power_per_cc
    }
    
    # 3. تحويله لـ DataFrame من سطر واحد
    input_df = pd.DataFrame([input_data])
    
    # 4. ⚠️ السحر هنا: تطبيق الـ Log Transformation على نفس العواميد اللي عملناها في كولاب
    cols_to_log = ['Engine', 'Power', 'Kilometers_Driven', 'Seats', 'Car_Age']
    for col in cols_to_log:
        # بنضيف 1 عشان لو في صفر (زي عمر 0) الكود ميضربش
        input_df[col] = np.log1p(input_df[col]) 

    # 5. إضافة باقي العواميد بـ 0 عشان الموديل ميزعلش (زي المدن وباقي أنواع الوقود)
    for col in model_columns:
        if col not in input_df.columns:
            input_df[col] = 0
            
    # 6. ترتيب العواميد زي ما الموديل متعود بالظبط
    input_df = input_df[model_columns]
    
    # 7. التوقع وفك التشفير
    predicted_log = model.predict(input_df)
    real_price_lakh = np.expm1(predicted_log)[0]
    
    # حساب الدولار
    price_in_rupees = real_price_lakh * 100000
    price_in_usd = price_in_rupees / 92
    
    # طباعة النتيجة
    st.success(f"السعر المتوقع: {real_price_lakh:.2f} Lakh")
    st.info(f"🇺🇸 السعر بالدولار: {price_in_usd:,.0f} $ تقريباً")
