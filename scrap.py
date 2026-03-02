import requests
from bs4 import BeautifulSoup
import re
import csv
import time

# -----------------------------------------------------------------------------
# 1. ตั้งเงื่อนไขกรองข้อมูล

BAN = ["สำเร็จรูป", "เอโร่", "โลโบ", "พาสต้าซอส", "ซอสกะเพรา"]
Seasoning = ["ซอส", "น้ำปลา", "น้ำตาล", "เกลือ", "พริกไทย", "ซีอิ๊ว", "ผง", "น้ำมัน", "กะทิ", "มะนาว", "ผงชูรส", "ซีอิ้ว", "เต้าเจี้ยว"]
Topp = ["ไข่ดาว", "ไข่เจียว", "ไข่ต้ม"]
Qunti = r'[0-9๐-๙\./]+|\s*(กรัม|กิโลกรัม|ช้อนโต๊ะ|ช้อนชา|ถ้วย|มล\.|ซีซี|ถ้วยตวง|ขีด|กิโล|ฟอง|ต้น|หัว|กลีบ|ซีก|ชิ้น|แว่น|ใบ)\s*'

BoxMenu = set()

# -----------------------------------------------------------------------------
# 2. ฟังก์ชันทำความสะอาดข้อมูล

def clean(Fname):
    # เงื่อนไข 1: ข้ามถ้ามีภาษาอังกฤษหรืออักขระพิเศษ
    if not Fname or re.search(r'[a-zA-Z]', Fname):
        return "ชื่อไม่เหมาะสม/มีอังกฤษ", True

    # เงื่อนไข 2: ตัดคำที่ไม่ใช่ชื่อเมนู
    Nname = re.split(r'วิธีทำ|สูตร|แป้ง|สำหรับ|ง่ายๆ|ทำเอง', Fname)[0].strip()

    # เงื่อนไข 3: ลบ Topping เพื่อเช็คความซ้ำซ้อน (เช่น กะเพราไข่ดาว -> กะเพรา)
    for Top in Topp:
        Nname = Nname.replace(Top, "").strip()

    # เงื่อนไข 4: ตรวจสอบเมนูซ้ำ
    if Nname in BoxMenu:
        return Nname, True
    else:
        BoxMenu.add(Nname)
        return Nname, False

# -----------------------------------------------------------------------------
# 3. ฟังก์ชันแยกวัตถุดิบกับเครื่องปรุง

def sort_ingredients(ingredient_list):
    ingre = []
    seas = []

    for cate in ingredient_list:
        no_val = re.sub(Qunti, '', cate).strip()
        no_val = re.sub(r'\(.*?\)', '', no_val).strip()
        
        if not no_val: continue

        if any(word in no_val for word in BAN):
            return "พบสูตรสำเร็จรูป", [], []
            
        if any(Seword in no_val for Seword in Seasoning):
            seas.append(no_val)
        else:
            ingre.append(no_val)
            
    return "ผ่าน", ingre, seas

# -----------------------------------------------------------------------------
# 4. ฟังก์ชันการดึงข้อมูล

def mainLINK(Alink):
    setting = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(Alink, headers=setting)
        soup = BeautifulSoup(res.content, 'html.parser')
        
        All_Link = []
        for a in soup.find_all('a', href=True):
            link = a['href']
            # กรองเอาเฉพาะสูตรที่เป็นทางการ (Official)
            if '/recipes/' in link and not any(x in link for x in ['/tags/', '/collections/', '/ugc/']):
                Fulink = "https://www.wongnai.com" + link if link.startswith('/') else link
                if Fulink not in All_Link:
                    All_Link.append(Fulink)
        return All_Link
    except:
        return []

def Recipe(menu_link):
    try:
        settingM = {'User-Agent': 'Mozilla/5.0'}
        resM = requests.get(menu_link, headers=settingM, timeout=10)
        soupM = BeautifulSoup(resM.content, 'html.parser')

        # แก้ไขจุดนี้: เปลี่ยนจาก ซุป เป็น soupM
        Fname = soupM.find('h1').text.strip() if soupM.find('h1') else ""
        nameM, is_duplicate = clean(Fname)
        
        if is_duplicate:
            return None

        ingredient_tags = [i.text.strip() for i in soupM.find_all('div', class_=re.compile('ingredient-item|css-'))]
        if not ingredient_tags: return None
        
        status, ingre, seas = sort_ingredients(ingredient_tags)
        if status == "พบสูตรสำเร็จรูป": 
            print(f"  [ข้าม] {nameM} -> ใช้ซอสสำเร็จรูป")
            return None

        steps = [s.text.strip() for s in soupM.find_all('div', class_=re.compile('step-description|css-'))]

        return {
            'Menu': nameM,
            'Main Ingredients': ", ".join(ingre),
            'Seasonings': ", ".join(seas),
            'Step': " | ".join(steps)
        }
    except Exception as e:
        return None

# -----------------------------------------------------------------------------
# 5. ส่วนสั่งรันและบันทึกข้อมูล

if __name__ == "__main__":
    openLink = "https://www.wongnai.com/recipes/tags/main-dish-recipes"
    print("กำลังค้นหาลิงก์...")
    mallink = mainLINK(openLink)
    
    final_results = []
    print(f"พบทั้งหมด {len(mallink)} ลิงก์ เริ่มดึงข้อมูล...")

    for i, link in enumerate(mallink):
        data = Recipe(link)
        if data:
            final_results.append(data)
            print(f"[{i+1}] บันทึกแล้ว: {data['Menu']}")
        time.sleep(1) # ป้องกันการโดนบล็อก

    # บันทึกเป็น CSV
    with open('wongnai_clean_data.csv', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Menu', 'Main Ingredients', 'Seasonings', 'Step'])
        writer.writeheader()
        writer.writerows(final_results)

    print("\n✅ เสร็จสิ้น! บันทึกข้อมูลลงไฟล์ wongnai_clean_data.csv เรียบร้อยแล้ว")
