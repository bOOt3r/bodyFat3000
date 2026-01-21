import streamlit as st
import joblib
import pandas as pd
import os

# Paths to your models
MODELS_DIR = 'models'

st.set_page_config(page_title="AI Body Fat Analyzer 3000", page_icon="⚖️")
st.title("⚖️ AI Body Fat Analyzer 3000")
st.write('Enter your private details below to estimate body fat using "AI".')

# 1. Sidebar for Sex and Age
sex = st.radio("Select Sex (Yes please is not an option..)", ["M", "F"])
age = st.number_input("Age", min_value=15, max_value=150, value=40)

# 2. Main Inputs (Metric)
col1, col2 = st.columns(2)
with col1:
    weight_kg = st.number_input("Weight (kg)", value=80.0)
    height_cm = st.number_input("Height (cm)", value=180.0)
with col2:
    abdomen_cm = st.number_input("Abdomen (cm)", value=100.0)

# 3. Optional Precision Inputs
with st.expander("Optional: Precision Measurements (Highly Recommended)"):
    neck_cm = st.number_input("Neck (cm)", value=0.0)
    hip_cm = st.number_input("Hip (cm)", value=0.0)
    wrist_cm = st.number_input("Wrist (cm)", value=0.0)

# 4. Prediction Logic
if st.button("Calculate Body Fat %"):
    height_m = height_cm / 100.0

    # Check if we use Full or Light model
    is_full = all([neck_cm > 0, hip_cm > 0, wrist_cm > 0])

    if sex == 'M':
        model_name = 'bf_male_full.pkl' if is_full else 'bf_male_light.pkl'
    else:
        model_name = 'bf_female_full.pkl' if is_full else 'bf_female_light.pkl'

    model = joblib.load(os.path.join(MODELS_DIR, model_name))

    if is_full:
        data = pd.DataFrame([[age, weight_kg, height_m, abdomen_cm, neck_cm, hip_cm, wrist_cm]],
                            columns=['Age', 'Weight', 'Height', 'Abdomen', 'Neck', 'Hip', 'Wrist'])
    else:
        data = pd.DataFrame([[age, weight_kg, height_m, abdomen_cm]],
                            columns=['Age', 'Weight', 'Height', 'Abdomen'])

    result = model.predict(data)[0]

    st.success(f"Estimated Body Fat: {result:.1f}%")
    st.info(f"Model used: {model_name.upper()}")