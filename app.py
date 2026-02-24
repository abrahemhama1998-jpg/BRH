import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. إعدادات الصفحة والتنسيق ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; text-align: right; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stMetric { background: #f0f2f6; padding: 10px; border-radius: 10px; }
    
    /* تنسيق الطباعة */
    @media print {
        .no-print, header, footer, [data-testid="stHeader"], .stTabs, button { display: none !important; }
        .printable { display: block !important; border: 2px solid black; padding: 20px; text-align: center; }
    }
    .printable { display: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. قاعدة البيانات ---
DB_FILE = "tech_database_final.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_db():
    st.session_state.db.to_csv(DB_FILE, index=False)

# --- 3. الواجهة الرئيسية ---
st.title("🛠️ منظومة الحل للتقنية للصيانة")
tabs = st.tabs(["📥 استلام جهاز", "🔍 الإدارة والبحث", "📊 التحليلات الممالية"])

# --- التبويب الأول: إضافة جهاز ---
with tabs[0]:
    with st.form("new_dev_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        model = c2.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = st.text_area("وصف العطل")
        if st.form_submit_button("✅ حفظ الجهاز"):
            if name:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_db()
                st.session_state.last_id = new_id
                st.success(f"تم الحفظ! رقم الجهاز: {new_id}")

    # معاينة الطباعة (تظهر بعد الحفظ)
    if 'last_id' in st.session_state:
        row = st.session_state.db[st.session_state.db['ID'] == st.session_state.last_id].iloc[0]
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
        
        st.markdown("### 🖨️ معاينة الوصل")
        # هذا الجزء سيظهر في المتصفح وسيظهر عند الطباعة
        receipt_html = f"""
        <div class="printable">
            <h2>الحل للتقنية للصيانة</h2>
            <hr>
            <p>رقم الجهاز: {row['ID']}</p>
            <p>الزبون: {row['الزبون']}</p>
            <p>الموديل: {row['الموديل']}</p>
            <h3>المبلغ: {row['التكلفة']} $</h3>
            <img src="{qr_url}" width="120">
        </div>
        """
        st.markdown(receipt_html, unsafe_allow_html=True)
        
        if st.button("اضغط هنا للطباعة (Ctrl + P)"):
            st.warning("بعد الضغط، استخدم Ctrl + P من الكيبورد للطباعة")
        
        if st.button("إنهاء ومعاملة جديدة"):
            del st.session_state.last_id
            st.rerun()

# --- التبويب الثاني: الإدارة والبحث ---
with tabs[1]:
    search = st.text_input("🔎 ابحث بالاسم أو ID")
    if search:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search) | df['ID'].astype(str).str.contains(search)]
        
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})"):
                with st.form(f"edit_{idx}"):
                    c1, c2, c3 = st.columns(3)
                    u_cost = c1.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = c2.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = c3.selectbox("الحالة", ["تحت الصيانة", "جاهز للتسليم", "تم التسليم"], index=0)
                    if st.form_submit_button("💾 تحديث"):
                        st.session_state.db.loc[idx, ["التكلفة", "سعر_القطع", "الحالة"]] = [u_cost, u_parts, u_status]
                        save_db()
                        st.rerun()

# --- التبويب الثالث: التحليلات والمالية ---
with tabs[2]:
    st.header("📊 ملخص المبيعات والأرباح")
    df = st.session_state.db
    # تحويل القيم لأرقام لضمان الحساب الصحيح
    df['التكلفة'] = pd.to_numeric(df['التكلفة'], errors='coerce').fillna(0)
    df['سعر_القطع'] = pd.to_numeric(df['سعر_القطع'], errors='coerce').fillna(0)
    
    delivered = df[df['الحالة'] == "تم التسليم"]
    
    total_revenue = delivered['التكلفة'].sum()
    total_parts = delivered['سعر_القطع'].sum()
    net_profit = total_revenue - total_parts
    
    m1, m2, m3 = st.columns(3)
    m1.metric("إجمالي المقبوضات", f"{total_revenue} $")
    m2.metric("تكلفة قطع الغيار", f"{total_parts} $")
    m3.metric("صافي الربح", f"{net_profit} $")
    
    st.write("### السجل الكامل للعمليات")
    st.dataframe(df, use_container_width=True)
