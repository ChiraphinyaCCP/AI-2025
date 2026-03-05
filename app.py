import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. โหลดข้อมูล ---
@st.cache_data
def load_data():
    try:
        m_df = pd.read_csv('menuu.csv').dropna(subset=['Menu', 'Ingre'])
        n_df = pd.read_csv('nutrition.csv')
        n_df.columns = [c.strip() for c in n_df.columns]
        n_df = n_df[['Ingredient', 'Protein', 'Fat', 'Carb', 'Fiber', 'Calories']].dropna()
        nutri_map = n_df.set_index('Ingredient').to_dict('index')

        def get_nutri(s):
            p, f, c, fb, cal = 0, 0, 0, 0, 0
            items = [i.strip() for i in str(s).split(',')]
            for it in items:
                for k, v in nutri_map.items():
                    if k in it:
                        p += v['Protein']; f += v['Fat']; c += v['Carb']
                        fb += v['Fiber']; cal += v['Calories']
                        break
            return p, f, c, fb, cal

        m_df[['P', 'F', 'C', 'Fib', 'Cal']] = m_df['Ingre'].apply(lambda x: pd.Series(get_nutri(x)))
        return m_df, list(nutri_map.keys())
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame(), []

df, ingredient_list = load_data()

# --- 2. จัดการสถานะ Navigation ---
if 'selected_recipe' not in st.session_state:
    st.session_state.selected_recipe = None
if 'nav_origin' not in st.session_state:
    st.session_state.nav_origin = None 

# ==========================================
# ส่วนที่ 1 & 4: หน้าแสดงรายละเอียดสูตรอาหาร (Detail Page)
# ==========================================
if st.session_state.selected_recipe is not None:
    recipe = st.session_state.selected_recipe
    origin = st.session_state.nav_origin
    
    st.button("⬅️ กลับไปหน้าหลัก", on_click=lambda: st.session_state.update({"selected_recipe": None}))
    st.title(f"🍴 {recipe['Menu']}")
    
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.image(recipe['ImURL'] if pd.notna(recipe['ImURL']) else "https://via.placeholder.com/600x400", use_container_width=True)
        st.subheader("🛒 วัตถุดิบ")
        st.write(recipe['Ingre'].replace(',', '\n').replace('|', '\n'))
    
    with c2:
        st.subheader("📊 สัดส่วนสารอาหารมื้อนี้")
        pie_df = pd.DataFrame({"สาร": ["โปรตีน", "ไขมัน", "คาร์บ", "ใยอาหาร"], "กรัม": [recipe['P'], recipe['F'], recipe['C'], recipe['Fib']]})
        fig = px.pie(pie_df[pie_df['กรัม']>0], values='กรัม', names='สาร', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        st.metric("🔥 พลังงานมื้อนี้", f"{recipe['Cal']:.0f} kcal")

    if origin == 'personal':
        t_p = st.session_state.get('target_p', 25)
        t_c = st.session_state.get('target_c', 50)
        meal = st.session_state.get('meal_time')
        
        st.markdown(f"### 💡 คำแนะนำเพื่อความสมบูรณ์สำหรับ {meal}")
        with st.container(border=True):
            a1, a2, a3 = st.columns(3)
            with a1:
                p_diff = recipe['P'] - t_p
                if abs(p_diff) <= 5: st.success(f"✅ โปรตีนพอดี ({recipe['P']:.1f}g)")
                elif p_diff > 5: st.warning("⚠️ โปรตีนสูงเกินมื้อ")
                else: st.error("🥩 โปรตีนไม่ถึงเกณฑ์")
            with a2:
                if recipe['C'] > t_c: st.error(f"⚠️ คาร์บเกินเป้ามื้อ")
                else: st.success("✅ คาร์บเหมาะสม")
            with a3:
                st.info(f"🌿 ใยอาหาร: {recipe['Fib']:.1f}g")

    st.divider()
    st.subheader("🍳 ขั้นตอนการทำ")
    st.write(recipe['Step'].replace(',', '\n').replace('|', '\n') if pd.notna(recipe['Step']) else "ไม่มีข้อมูลขั้นตอน")

# ==========================================
# ส่วนที่ 2 & หน้าหลัก: (Main UI)
# ==========================================
else:
    st.sidebar.title("🍱 Cooking Time!")
    page = st.sidebar.radio("เลือกโหมด:", ["🔍 ค้นหาสูตรทั่วไป", "⚖️ วิเคราะห์ส่วนบุคคล"])

    if page == "🔍 ค้นหาสูตรทั่วไป":
        st.title("🍳 Cooking Time!")
        col_s, col_t = st.columns([2, 1])
        with col_s: selected = st.multiselect("🥕 เลือกวัตถุดิบที่คุณมี:", ingredient_list)
        with col_t: meth = st.multiselect("ประเภทอาหาร:", ["ต้ม", "ผัด", "แกง", "ทอด", "ยำ"])
        
        res = df.copy()
        if selected: res = res[res['Ingre'].apply(lambda x: any(ing in str(x) for ing in selected))]
        if meth: res = res[res['Meth'].isin(meth)]
        
        st.write(f"พบทั้งหมด {len(res)} รายการ")
        cols = st.columns(2)
        for idx, (_, row) in enumerate(res.head(10).iterrows()):
            with cols[idx % 2]:
                with st.container(border=True):
                    st.image(row['ImURL'] if pd.notna(row['ImURL']) else "https://via.placeholder.com/400x250", use_container_width=True)
                    st.subheader(row['Menu'])
                    st.write(f"📍 {row['Meth']} | {row['Cal']:.0f} kcal")
                    if st.button("📖 ดูสูตร", key=f"g_{row['Menu']}"):
                        st.session_state.update({"selected_recipe": row, "nav_origin": "general"})
                        st.rerun()

    elif page == "⚖️ วิเคราะห์ส่วนบุคคล":
        st.title("⚖️ Personalized Nutrition Analysis")
        c1, c2, c3 = st.columns(3)
        weight = c1.number_input("น้ำหนัก (กก.)", 30.0, 150.0, 65.0)
        height = c2.number_input("ส่วนสูง (ซม.)", 100.0, 220.0, 165.0)
        age = c3.number_input("อายุ (ปี)", 5, 100, 25)
        
        c4, c5, c6 = st.columns(3)
        gender = c4.selectbox("เพศ", ["หญิง", "ชาย"])
        activity = c5.selectbox("กิจกรรม", ["น้อย", "ปานกลาง", "มาก"])
        if activity == "น้อย":
            st.info("สำหรับคนทำงานออฟฟิศ นั่งเกือบทั้งวัน หรือแทบไม่ได้ออกกำลังกายเลย")
        elif activity == "ปานกลาง":
            st.info("สำหรับคนที่มีการขยับตัวบ่อย หรือออกกำลังกายสัปดาห์ละ 3-5 วัน")
        elif activity == "มาก":
            st.info("สำหรับคนที่ออกกำลังกายหนัก ออกกำลังกายเกือบทุกวัน หรือทำงานที่ต้องใช้แรงกายมาก")
        meal_time = c6.selectbox("เลือกมื้ออาหาร", ["มื้อเช้า", "มื้อกลางวัน", "มื้อเย็น"])
        
        goal = st.radio("เป้าหมายการกิน:", ["เน้นโปรตีนสมดุล", "คุมน้ำหนัก (Low Carb)", "เน้นไฟเบอร์สูง"], horizontal=True)

        # คำนวณรายมื้อ 30-40-30
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == "ชาย" else -161)
        tdee = bmr * {"น้อย": 1.2, "ปานกลาง": 1.4, "มาก": 1.7}[activity]
        m_dist = {"มื้อเช้า": 0.3, "มื้อกลางวัน": 0.4, "มื้อเย็น": 0.3}
        target_cal = tdee * m_dist[meal_time]
        target_p = (weight * (1.7 if gender == "ชาย" else 1.4)) * m_dist[meal_time]
        target_c = (target_cal * (0.20 if meal_time == "มื้อเย็น" else 0.45)) / 4

        st.session_state.update({"target_p": target_p, "target_c": target_c, "meal_time": meal_time})

        def calc_score(r):
            score = 100
            score -= (abs(r['P'] - target_p) / target_p) * 50
            if r['C'] > target_c: score -= ((r['C'] - target_c) / target_c) * 50
            return int(max(0, score))

        df['Score'] = df.apply(calc_score, axis=1)

        # --- ส่วนที่แก้ไข: เปลี่ยน st.info เป็นรูปแบบ List (แบบรูปที่ 2) ---
        with st.container(border=True):
            st.markdown(f"### 🎯 เป้าหมายสำหรับ {meal_time}:")
            st.write(f"* **พลังงาน:** {m_dist[meal_time]*100:.0f}% ของทั้งวัน ({target_cal:.0f} kcal)")
            st.write(f"* **โปรตีน:** 30% ของทั้งวัน ({target_p:.1f} g)")
            
            # ปรับ % คาร์บตามตัวเลือกเป้าหมาย
            c_pct = 45 if goal != "คุมน้ำหนัก (Low Carb)" else 20
            st.write(f"* **คาร์โบไฮเดรต:** {c_pct}% ของพลังงานมื้อนี้ ({target_c:.1f} g)")
        # ------------------------------------------------------------
        
        recom = df.sort_values(by='Score', ascending=False).head(5)
        for _, row in recom.iterrows():
            with st.container(border=True):
                col_i, col_m = st.columns([1, 2])
                with col_i:
                    st.image(row['ImURL'] if pd.notna(row['ImURL']) else "https://via.placeholder.com/200", use_container_width=True)
                with col_m:
                    st.subheader(f"{row['Menu']} ({row['Score']}%)")
                    st.write(f"🍗 โปรตีน {row['P']:.1f}g | 🥗 คาร์บ {row['C']:.1f}g")
                    if st.button("วิเคราะห์ละเอียด", key=f"rec_{row['Menu']}"):
                        st.session_state.update({"selected_recipe": row, "nav_origin": "personal"})
                        st.rerun()