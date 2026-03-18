import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# 1. تحميل الموديل
current_dir = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(current_dir, 'car_price_model.pkl'))
model_columns = joblib.load(os.path.join(current_dir, 'model_columns.pkl'))

st.title("🚗 مقيم أسعار السيارات الذكي")
st.write("أدخل مواصفات سيارتك لمعرفة سعرها المتوقع في السوق!")

# 2. الأسئلة (كبرنا القايمة عشان الموديل يفهم صح)
col1, col2 = st.columns(2) # بنقسم الشاشة نصين عشان الشكل يبقى شيك

with col1:
    power = st.number_input("قوة الموتور (بالحصان):", min_value=30.0, max_value=600.0, value=100.0)
    engine = st.number_input("سعة الموتور (CC):", min_value=500.0, max_value=6000.0, value=1500.0)
    car_age = st.number_input("عمر السيارة (بالسنوات):", min_value=0, max_value=30, value=5)
    kilometers = st.number_input("الكيلومترات المقطوعة:", min_value=0, max_value=500000, value=50000, step=5000)

with col2:
    transmission = st.selectbox("نوع الناقل:", ["Manual", "Automatic"])
    fuel = st.selectbox("نوع الوقود:", ["Petrol", "Diesel", "CNG"])
    owner = st.selectbox("المالك:", ["First", "Second", "Third or More"])
    # افترضنا إننا عملنا لستة مبسطة للماركات (ممكن نطورها بعدين)
    car_brand_tier = st.selectbox("فئة السيارة:", ["اقتصادية (مثال: هيونداي، ماروتي)", "متوسطة (مثال: هوندا، تويوتا)", "فارهة (مثال: أودي، مرسيدس)"])

# 3. زرار الحساب
if st.button("احسب السعر 💰"):
    # ترجمة كلام العميل لأرقام يفهمها الموديل
    fuel_val = 1 if fuel == "Petrol" else (0 if fuel == "Diesel" else 2)
    owner_val = 0 if owner == "First" else (2 if owner == "Second" else 3)
    
    brand_val = 18 # افتراضي (اقتصادية)
    if car_brand_tier == "متوسطة (مثال: هوندا، تويوتا)": brand_val = 10
    elif car_brand_tier == "فارهة (مثال: أودي، مرسيدس)": brand_val = 2
    
    input_data = {
        'Power': power,
        'Engine': engine,
        'Car_Age': car_age,
        'Kilometers_Driven': kilometers,
        'Seats': 5,
        'Mileage': 18.0,
        'Fuel_Type': fuel_val,
        'Owner_Type': owner_val,
        'Car_Model': brand_val,
        'Power_per_cc': power / engine
    }
    
    input_df = pd.DataFrame([input_data])
    
    # تطبيق اللوجارتم
    cols_to_log = ['Engine', 'Power', 'Kilometers_Driven', 'Seats', 'Car_Age']
    for col in cols_to_log:
        input_df[col] = np.log1p(input_df[col]) 

    # تظبيط العواميد
    for col in model_columns:
        if col not in input_df.columns:
            input_df[col] = 0
            
    if 'Transmission_Manual' in input_df.columns:
        input_df['Transmission_Manual'] = 1 if transmission == "Manual" else 0
    elif 'Transmission' in input_df.columns:
        input_df['Transmission'] = 1 if transmission == "Manual" else 0
            
    input_df = input_df[model_columns]
    
    # التوقع
    predicted_log = model.predict(input_df)
    real_price_lakh = np.expm1(predicted_log)[0]
    
    st.success(f"السعر المتوقع: {real_price_lakh:.2f} Lakh")
    st.info(f"🇺🇸 السعر بالدولار: {(real_price_lakh * 100000) / 92:,.0f} $ تقريباً")
