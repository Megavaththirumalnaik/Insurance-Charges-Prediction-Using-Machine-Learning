import pickle
import streamlit as st
import pandas as pd
import locale

# === Setup Indian Currency Formatting ===
locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')  # May work on Linux
try:
    from babel.numbers import format_currency
    def format_inr(value):
        return format_currency(value, 'INR', locale='en_IN')
except:
    def format_inr(value):
        return f"₹{value:,.2f}"

# === Load Trained Model ===
with open(r"C:\Users\megva\Insurance Charges Prediction Using  Machine Learning\model_insurance.pk1", "rb") as f1:
    model = pickle.load(f1)

st.set_page_config(page_title="Insurance Prediction", layout="centered")
st.title("🏥 Insurance Charges Prediction")

# === User Inputs ===
age = st.number_input("Age", min_value=18, max_value=100, step=1)
sex = st.selectbox("Sex", ["Male", "Female"])
bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, format="%.2f")
children = st.number_input("Number of Children", min_value=0, max_value=10, step=1)
smoker = st.selectbox("Do you smoke?", ["Yes", "No"])
region = st.selectbox("Region", ["southeast", "southwest", "northeast", "northwest"])

# === Plan Info Table ===
st.markdown("### 📋 Insurance Plans")
st.markdown("""
| Plan     | Description                             | Typical Annual Income Range (₹) |
|----------|-----------------------------------------|----------------------------------|
| Basic    | Covers essential hospital expenses only | ₹15,000 – ₹40,000               |
| Standard | Includes OPD, diagnostics, maternity    | ₹40,000 – ₹1,00,000             |
| Premium  | Extensive coverage & wellness benefits  | ₹1,20,000 – ₹1,00,00,000+       |
""")

# === Plan Selection & Income ===
plan = st.selectbox("Select your Insurance Plan", ["Basic", "Standard", "Premium"])
income = st.number_input("Enter your Annual Income", min_value=0, max_value=10000000, step=1000)

# === Dynamic Plan Percentage Function ===
def get_plan_percent(plan, income):
    if plan == "Basic":
        if income < 25000:
            return 0.015
        elif income <= 40000:
            return 0.02
        else:
            return 0.025
    elif plan == "Standard":
        if income <= 60000:
            return 0.025
        elif income <= 100000:
            return 0.03
        else:
            return 0.035
    elif plan == "Premium":
        if income <= 150000:
            return 0.04
        else:
            return 0.05
    return 0.03

plan_percent = get_plan_percent(plan, income)

# === Duration Selection ===
duration = st.selectbox("Choose Policy Duration", ["1 Year", "2 Years", "3 Years", "5 Years"])
duration_map = {"1 Year": 1, "2 Years": 2, "3 Years": 3, "5 Years": 5}
selected_years = duration_map[duration]

# === Preprocessing Inputs ===
sex_flag = 0 if sex == "Male" else 1
smoker_flag = 0 if smoker == "Yes" else 1
region_map = {"southeast": 0, "southwest": 1, "northeast": 2, "northwest": 3}
region_code = region_map[region]

input_df = pd.DataFrame([{
    "age": age,
    "sex": sex_flag,
    "bmi": bmi,
    "children": children,
    "smoker": smoker_flag,
    "region": region_code
}])

# === Prediction ===
if st.button("🔍 Predict Insurance Charge"):
    if income < 15000:
        st.error("❌ You are not eligible for any insurance plan with an income below ₹15,000.")
    else:
        predicted_annual_charge = model.predict(input_df)[0]
        predicted_total_charge = predicted_annual_charge * selected_years
        recommended_charge = income * plan_percent * selected_years

        st.success(f"💰 Predicted Annual Charge: {format_inr(predicted_annual_charge)}")
        st.info(f"📆 Policy Duration: {selected_years} year(s)")
        st.success(f"📊 Total Insurance Charge: {format_inr(predicted_total_charge)}")
        st.info(f"🧾 Recommended max for {plan} Plan: {format_inr(recommended_charge)}")

        if predicted_total_charge > recommended_charge:
            st.warning("⚠️ Predicted cost is higher than recommended for your income and selected plan.")
        else:
            st.success("✅ Prediction is within your budget for the selected plan.")

        st.toast("Prediction completed!", icon="✅")

