import streamlit as st
import joblib
import pandas as pd
import os
from datetime import datetime
import io

MODELS_DIR = 'models'

st.set_page_config(page_title="AI Body Fat Analyzer 3000", page_icon="⚖️")
st.title("⚖️ AI Body Fat Analyzer 3000")
st.write('Enter your private details below to estimate body fat using "AI".')

# 1. Sidebar for Sex and Age
sex = st.radio('Select Sex, "Yes please" is not an option..', ["M", "F"])
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

    # Load and Predict
    model = joblib.load(os.path.join(MODELS_DIR, model_name))

    if is_full:
        data = pd.DataFrame([[age, weight_kg, height_m, abdomen_cm, neck_cm, hip_cm, wrist_cm]],
                            columns=['Age', 'Weight', 'Height', 'Abdomen', 'Neck', 'Hip', 'Wrist'])
    else:
        data = pd.DataFrame([[age, weight_kg, height_m, abdomen_cm]],
                            columns=['Age', 'Weight', 'Height', 'Abdomen'])

    # The AI Result
    body_fat_perc = model.predict(data)[0]

    # Standard BMI Result
    bmi = weight_kg / (height_m ** 2)

    # Lean Mass and FFMI Result
    lean_mass = weight_kg * (1 - (body_fat_perc / 100))
    ffmi = lean_mass / (height_m ** 2)

    # Display the Results
    st.divider()
    st.header(f"Your Result: {body_fat_perc:.1f}% Body Fat")

    # Display Standard BMI and Muscle Index (FFMI) side by side
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Standard BMI", f"{bmi:.1f}")
    with col_b:
        st.metric("Muscle Index (FFMI)", f"{ffmi:.1f}")

    # Interpret the Results
    if bmi > 25 and body_fat_perc < 15:
        st.success("Your BMI is high, but your body fat is low. You likely have high muscle mass!")
    elif bmi < 25 and body_fat_perc > 25 and sex == 'M':
        st.warning("You have a normal BMI but high body fat. This is sometimes called 'Skinny Fat'.")
    elif body_fat_perc > 30:
        st.error("Body fat levels are a tad on the high side.")
    else:
        st.info("Your metrics appear to be in a healthy range.")

    # Provide Interpretation Guidance
    st.info("**How to Read the Results:**\n"
            "- **Body Fat %**: Indicates the percentage of your body weight that is fat. "
            "Lower values are generally better for health, but extremely low values can be harmful.\n"
            "- **BMI**: A general indicator of weight relative to height. "
            "Values between 18.5 and 24.9 are considered normal.\n"
            "- **FFMI**: A measure of muscle mass. Values above 20 for men and 18 for women are considered muscular.")

    # Generate the current date and time
    now = datetime.now()
    date_str = now.strftime("%d/%m/%y")
    time_str = now.strftime("%H:%M:%S")

    # Create the CSV content
    csv_content = f"Body\nDate,Time,Weight,BMI,Fat\n{date_str},{time_str},{weight_kg:.2f},{bmi:.2f},{body_fat_perc:.2f}"

    # Create a BytesIO object for the CSV
    csv_bytes = io.BytesIO(csv_content.encode('utf-8'))

    # Add a download button for the CSV
    st.download_button(
        label="Download Results as CSV",
        data=csv_bytes,
        file_name="body_fat_results.csv",
        mime="text/csv"
    )

    # Garmin Connect Link
    st.markdown(
        "[Import to Garmin Connect](https://connect.garmin.com/modern/import-data)",
        unsafe_allow_html=True
    )
