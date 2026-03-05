import pandas as pd

# 1. โหลดข้อมูลจาก CSV ทั้งสองไฟล์
df_menu = pd.read_csv('menuu.csv')
df_nutri = pd.read_csv('Nutrition_Ref.csv')

# เปลี่ยน Nutrition_Ref ให้เป็น Dictionary เพื่อการค้นหาที่เร็วขึ้น
nutri_dict = df_nutri.set_index('Ingredient').to_dict('index')

def analyze_health(ingredients_text):
    if pd.isna(ingredients_text): return 0, 0, 0, 0
    
    # แยกรายชื่อวัตถุดิบ
    items = [i.strip() for i in ingredients_text.split(',')]
    
    total_pro = 0
    total_fat = 0
    total_carb = 0
    total_cal = 0
    
    for item in items:
        # ใช้การค้นหาแบบบางส่วน (เช่น 'อกไก่' ใน 'อกไก่ลวก')
        for key in nutri_dict:
            if key in item:
                total_pro += nutri_dict[key]['Protein']
                total_fat += nutri_dict[key]['Fat']
                total_carb += nutri_dict[key]['Carb']
                total_cal += nutri_dict[key]['Calories']
                break
                
    return total_pro, total_fat, total_carb, total_cal

# 2. นำฟังก์ชันไปใช้กับทุกเมนู
df_menu[['Pro', 'Fat', 'Carb', 'Cal']] = df_menu['Ingre'].apply(
    lambda x: pd.Series(analyze_health(x))
)

# 3. แสดงผล 5 เมนูแรกที่คำนวณแล้ว
print(df_menu[['Menu', 'Pro', 'Fat', 'Carb', 'Cal']].head())
