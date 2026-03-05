import pandas as pd
import numpy as np

# 1. โหลดข้อมูล (ต้องมีไฟล์ menuu.csv และ Nutrition_Ref.csv อยู่ในโฟลเดอร์เดียวกัน)
try:
    df_menu = pd.read_csv('menuu.csv')
    df_nutri = pd.read_csv('nutrition.csv')
    print("--- โหลดข้อมูลสำเร็จ ---")
except FileNotFoundError:
    print("Error: ไม่พบไฟล์ CSV กรุณาตรวจสอบชื่อไฟล์ให้ถูกต้อง")

# ทำความสะอาดข้อมูลเบื้องต้น (ลบแถวที่ไม่มีชื่อเมนูหรือวัตถุดิบ)
df_menu = df_menu.dropna(subset=['Menu', 'Ingre']).reset_index(drop=True)

# 2. สร้าง Dictionary สำหรับค้นหาข้อมูลโภชนาการได้รวดเร็ว
nutri_dict = df_nutri.set_index('Ingredient').to_dict('index')

# 3. ฟังก์ชันวิเคราะห์สารอาหารรายเมนู
def analyze_menu_nutrition(ingredients_str):
    if pd.isna(ingredients_str):
        return 0, 0, 0, 0, 0
    
    # แยกรายชื่อวัตถุดิบที่คั่นด้วยคอมม่า
    ingredients = [i.strip() for i in str(ingredients_str).split(',')]
    t_pro, t_fat, t_carb, t_fiber, t_cal = 0, 0, 0, 0, 0
    
    for ing in ingredients:
        # ค้นหาวัตถุดิบในฐานข้อมูลอ้างอิง (Keyword Matching)
        for ref_name, values in nutri_dict.items():
            if ref_name in ing:
                t_pro += values['Protein']
                t_fat += values['Fat']
                t_carb += values['Carb']
                t_fiber += values['Fiber']
                t_cal += values['Calories']
                break
    return t_pro, t_fat, t_carb, t_fiber, t_cal

# นำฟังก์ชันไปใช้เพื่อสร้างคอลัมน์สารอาหารใหม่ในตารางเมนู
df_menu[['Protein', 'Fat', 'Carbohydrate', 'Fiber', 'Calories']] = df_menu['Ingre'].apply(
    lambda x: pd.Series(analyze_menu_nutrition(x))
)

# 4. ฟังก์ชันคำนวณคะแนนสุขภาพและการติด Tag อัตโนมัติ
def calculate_health_score(row):
    score = 50 # คะแนนเริ่มต้น
    meth = str(row['Meth'])
    
    # ให้คะแนนตามวิธีการปรุง
    if meth in ['นึ่ง', 'ต้ม', 'ลวก', 'อบ', 'แกง']:
        score += 20
    elif meth in ['ทอด', 'ผัด']:
        score -= 10
        
    # ให้คะแนนตามความหนาแน่นสารอาหาร
    if row['Protein'] > 15: score += 15
    if row['Fiber'] > 2: score += 15
    if row['Fat'] > 20: score -= 10
    
    # ตรวจสอบเงื่อนไขเพื่อติด Tag (ใช้แสดงผลบนหน้าแอป)
    tags = []
    if row['Protein'] > 18: tags.append("High Protein")
    if row['Fiber'] > 2: tags.append("Fiber Rich")
    if row['Carbohydrate'] < 15 and 'ข้าว' not in row['Menu']: tags.append("Low Carb")
    if row['Fat'] < 5: tags.append("Low Fat")
    
    return pd.Series([max(0, min(100, score)), ", ".join(tags) if tags else "General"])

df_menu[['HealthScore', 'Tags']] = df_menu.apply(calculate_health_score, axis=1)

# 5. ระบบแนะนำเมนู (Weight-based Recommendation)
def get_recommendation(weight, meal_type, top_n=5):
    # คำนวณโปรตีนที่ต้องการต่อมื้อ (ประมาณ 1.5g ต่อน้ำหนักตัว / 3 มื้อ)
    target_pro_per_meal = (weight * 1.5) / 3
    
    filtered_df = df_menu.copy()
    
    if meal_type == 'Dinner':
        # กฎสำหรับมื้อเย็น: คาร์บต่ำ, พลังงานไม่เกิน 500 kcal
        filtered_df = filtered_df[
            (filtered_df['Carbohydrate'] < 30) & 
            (filtered_df['Calories'] < 500)
        ]
    elif meal_type in ['Breakfast', 'Lunch']:
        # กฎสำหรับมื้อเช้า/กลางวัน: เน้นโปรตีนและพลังงานเพื่อทำกิจกรรม
        filtered_df = filtered_df[filtered_df['Protein'] >= (target_pro_per_meal * 0.7)]
        
    # เรียงลำดับตามคะแนนสุขภาพและปริมาณโปรตีนจากมากไปน้อย
    return filtered_df.sort_values(by=['HealthScore', 'Protein'], ascending=False).head(top_n)

# --- ตัวอย่างการรันระบบ ---
WEIGHT = 65  # น้ำหนักตัว (กก.)
MEAL = 'Dinner'  # มื้อที่ต้องการ (Breakfast, Lunch, Dinner)

print(f"\n--- เมนูแนะนำสำหรับ {MEAL} (น้ำหนักตัว {WEIGHT} กก.) ---")
results = get_recommendation(WEIGHT, MEAL)
print(results[['Menu', 'Meth', 'Protein', 'Calories', 'HealthScore', 'Tags']])

# บันทึกผลการวิเคราะห์ทั้งหมดลงในไฟล์ใหม่เพื่อนำไปใช้ใน GitHub หรือ Web App
df_menu.to_csv('Final_Menu_Analysis.csv', index=False)
print("\n--- บันทึกผลการวิเคราะห์ลงใน 'Final_Menu_Analysis.csv' เรียบร้อยแล้ว ---")
