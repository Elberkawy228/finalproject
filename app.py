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
    power_per_cc = power / engine
    
    # 1. الداتا الأساسية
    input_data = {
        'Power': power,
        'Engine': engine,
        'Car_Age': car_age,
        'Kilometers_Driven': 100000, # زودنا الكيلومترات عشان تبان مستعملة جامد
        'Seats': 5,
        'Mileage': 18.0,
        'Power_per_cc': power_per_cc
    }
    
    input_df = pd.DataFrame([input_data])
    
    # 2. السحر: تطبيق الـ Log
    cols_to_log = ['Engine', 'Power', 'Kilometers_Driven', 'Seats', 'Car_Age']
    for col in cols_to_log:
        input_df[col] = np.log1p(input_df[col]) 

    # 3. نحط باقي العواميد بـ صفر
   # 5. إضافة باقي العواميد وتحديد قيم "متوسطة" بدل الصفر عشان منلبسش في عربية فارهة!
    for col in model_columns:
        if col not in input_df.columns:
            if col == 'Car_Model':
                input_df[col] = 18  # رقم بيمثل عربية اقتصادية متوسطة
            elif col == 'Location':
                input_df[col] = 5   # مدينة عادية
            elif col == 'Fuel_Type':
                input_df[col] = 1   # بنزين عادي
            elif col == 'Owner_Type':
                input_df[col] = 2   # مالك تاني أو تالت (عشان تبان متهالكة)
            else:
                input_df[col] = 0
            
    # 4. 🚨 الإصلاح الحقيقي: نديها هوية اقتصادية عشان متتسعرش كأنها بورش!
    for col in input_df.columns:
        # لو في عمود للبنزين، نخليه 1
        if 'Petrol' in col:
            input_df[col] = 1
        # نختار ماركة شعبية (ماروتي، هيونداي، أو تاتا) ونخليها 1
        if any(brand in col for brand in ['Maruti', 'Hyundai', 'Tata', 'Chevrolet']):
            input_df[col] = 1
            break # نختار ماركة واحدة بس
            
    # 5. تظبيط الناقل بناءً على اسم العمود الحقيقي في الداتا بتاعتك
    if 'Transmission_Manual' in input_df.columns:
        input_df['Transmission_Manual'] = 1 if transmission == "Manual" else 0
    elif 'Transmission' in input_df.columns:
        # لو العمود اسمه Transmission بس (غالباً 1 مانيوال و 0 أوتوماتيك)
        input_df['Transmission'] = 1 if transmission == "Manual" else 0
            
    # 6. الترتيب والتوقع
    input_df = input_df[model_columns]
    
    # السطر ده هيعرض الجدول على الموقع عشان نشوف الموديل بيستلم إيه بالظبط
    st.write("🔍 الداتا اللي الموديل شايفها فعلاً:", input_df)
    
    predicted_log = model.predict(input_df)
    real_price_lakh = np.expm1(predicted_log)[0]
    
    price_in_rupees = real_price_lakh * 100000
    price_in_usd = price_in_rupees / 92
    
    st.success(f"السعر المتوقع: {real_price_lakh:.2f} Lakh")
    st.info(f"🇺🇸 السعر بالدولار: {price_in_usd:,.0f} $ تقريباً")
