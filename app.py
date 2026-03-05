import streamlit as st
import pandas as pd

# --- ส่วนของการตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="Thai Healthy Menu AI", layout="wide")
st.title("🥗 AI แนะนำเมนูอาหารไทยสายสุขภาพ")
st.write("คำนวณโภชนาการส่วนบุคคลตามน้ำหนักตัวและมื้ออาหาร")

# --- โหลดฟังก์ชันวิเคราะห์ที่เราทำไว้ (จากขั้นตอนก่อนหน้า) ---
# (สมมติว่าคุณรันโค้ดวิเคราะห์และได้ไฟล์ Final_Menu_Analysis.csv มาแล้ว)
try:
    df = pd.read_csv('Final_Menu_Analysis.csv')
except:
    st.error("ไม่พบไฟล์ข้อมูล กรุณารันโค้ดวิเคราะห์ก่อน")
    st.stop()

# --- Sidebar: รับค่าจากผู้ใช้ ---
st.sidebar.header("ข้อมูลของคุณ")
user_weight = st.sidebar.number_input("น้ำหนักตัว (กก.)", min_value=30, max_value=150, value=65)
meal_type = st.sidebar.selectbox("เลือกมื้ออาหาร", ["Breakfast", "Lunch", "Dinner"])

# --- คำนวณเป้าหมายโปรตีน ---
target_pro = (user_weight * 1.5) / 3
st.info(f"💡 มื้อนี้ร่างกายของคุณต้องการโปรตีนประมาณ: **{target_pro:.1f} กรัม**")

# --- ฟังก์ชันกรองข้อมูล ---
def filter_recommendations(weight, meal):
    filtered = df.copy()
    if meal == 'Dinner':
        filtered = filtered[(filtered['Carbohydrate'] < 30) & (filtered['Calories'] < 500)]
    else:
        filtered = filtered[filtered['Protein'] >= (target_pro * 0.7)]
    return filtered.sort_values(by=['HealthScore', 'Protein'], ascending=False).head(10)

# --- แสดงผลเมนูแนะนำ ---
results = filter_recommendations(user_weight, meal_type)

if not results.empty:
    cols = st.columns(2) # แบ่งเป็น 2 คอลัมน์
    for idx, row in enumerate(results.iterrows()):
        data = row[1]
        with cols[idx % 2]:
            with st.container():
                st.subheader(f"{data['Menu']}")
                # ถ้ามี URL รูปภาพให้แสดง
                if pd.notna(data['ImURL']):
                    st.image(data['ImURL'], use_column_width=True)
                
                # แสดงค่าพลังงานและคะแนน
                st.write(f"🔥 {data['Calories']} kcal | 🍗 โปรตีน {data['Protein']}g")
                st.progress(int(data['HealthScore']))
                st.write(f"🎯 ความเหมาะสม: **{data['HealthScore']}%**")
                st.caption(f"🏷️ Tags: {data['Tags']}")
                st.divider()
else:
    st.warning("ขออภัย ไม่พบเมนูที่ตรงกับเงื่อนไขสุขภาพของคุณในมื้อนี้")
