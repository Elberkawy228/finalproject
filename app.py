import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# 1. تحميل الموديل والقاموس السحري
current_dir = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(current_dir, 'car_price_model.pkl'))
model_columns = joblib.load(os.path.join(current_dir, 'model_columns.pkl'))
mappings = joblib.load(os.path.join(current_dir, 'mappings.pkl')) 

st.title("🚗 مقيم أسعار السيارات الذكي")
st.write("أدخل مواصفات سيارتك بدقة لمعرفة سعرها الحقيقي في السوق!")

# 2. القوائم الديناميكية (بتاخد الخيارات من القاموس مباشرة)
col1, col2 = st.columns(2)

with col1:
    power = st.number_input("قوة الموتور (بالحصان):", min_value=30.0, max_value=600.0, value=100.0)
    engine = st.number_input("سعة الموتور (CC):", min_value=500.0, max_value=6000.0, value=1500.0)
    car_age = st.number_input("عمر السيارة (بالسنوات):", min_value=0, max_value=30, value=5)
    kilometers = st.number_input("الكيلومترات المقطوعة:", min_value=0, max_value=500000, value=50000, step=5000)

with col2:
    # بنعرض للعميل الكلمات الحقيقية (هيونداي، أودي، إلخ) من الداتا بتاعتك
    car_model = st.selectbox("ماركة السيارة:", list(mappings['Car_Model'].keys()))
    location = st.selectbox("المدينة:", list(mappings['Location'].keys()))
    transmission = st.selectbox("نوع الناقل:", list(mappings['Transmission'].keys()))
    fuel = st.selectbox("نوع الوقود:", list(mappings['Fuel_Type'].keys()))
    owner = st.selectbox("المالك:", list(mappings['Owner_Type'].keys()))

# 3. زرار الحساب
if st.button("احسب السعر 💰"):
    # هنا الموقع بياخد اختيارات العميل ويترجمها للأرقام المظبوطة بالمللي من القاموس
    input_data = {
        'Car_Model': mappings['Car_Model'][car_model],
        'Location': mappings['Location'][location],
        'Transmission': mappings['Transmission'][transmission],
        'Fuel_Type': mappings['Fuel_Type'][fuel],
        'Owner_Type': mappings['Owner_Type'][owner],
        'Power': power,
        'Engine': engine,
        'Car_Age': car_age,
        'Kilometers_Driven': kilometers,
        'Seats': 5.0,  # افترضنا 5 كراسي كمتوسط
        'Mileage': 18.0, # افترضنا استهلاك متوسط
        'Power_per_cc': power / engine
    }
    
    input_df = pd.DataFrame([input_data])
    
    # 4. الـ Log Transformation زي كولاب بالظبط
    cols_to_log = ['Engine', 'Power', 'Kilometers_Driven', 'Seats', 'Car_Age']
    for col in cols_to_log:
        input_df[col] = np.log1p(input_df[col]) 

    # 5. الترتيب عشان الموديل ميتلخبطش
    for col in model_columns:
        if col not in input_df.columns:
            input_df[col] = 0
            
    input_df = input_df[model_columns]
    
    # 6. التوقع النهائي
    predicted_log = model.predict(input_df)
    real_price_lakh = np.expm1(predicted_log)[0]
    
    # طباعة السعر
    st.success(f"السعر المتوقع: {real_price_lakh:.2f} Lakh")
    st.info(f"🇺🇸 السعر بالدولار: {(real_price_lakh * 100000) / 92:,.0f} $ تقريباً")
