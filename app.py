import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# --- 1. الإعدادات والجمالية ---
st.set_page_config(page_title="الحل للتقنية | منظومة ذكية", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stat-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #007bff;
        text-align: center;
    }
    .urgent-task { background-color: #ffe5e5; border-right: 5px solid #ff4b4b; padding: 10px; border-radius: 5px; margin-bottom: 5px;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات ---
DB_FILE = "tech_v5_pro_database.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['التاريخ_الكامل'] = pd.to_datetime(df['التاريخ_الكامل'], errors='coerce')
        df['الزبون'] = df['الزبون'].fillna('')
        df['الهاتف'] = df['الهاتف'].fillna('')
        df['ID'] = df['ID'].fillna(0).astype(int)
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ_الكامل", "ملاحظات"])

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_db():
    st.session_state.db.to_csv(DB_FILE, index=False)

# --- 3. لوحة التحكم والإحصائيات ---
st.title("🛡️ منظومة الحل للتقنية - الإصدار الذهبي")

df_stats = st.session_state.db
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f"<div class='stat-card'><h3>📦 إجمالي الأجهزة</h3><h2>{len(df_stats)}</h2></div>", unsafe_allow_html=True)
with c2: 
    delayed = len(df_stats[(df_stats['الحالة'] == 'تحت الصيانة') & (df_stats['التاريخ_الكامل'] < datetime.now() - timedelta(days=3))])
    st.markdown(f"<div class='stat-card' style='border-top-color: #ff4b4b;'><h3>⚠️ متأخر (+3 أيام)</h3><h2>{delayed}</h2></div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='stat-card' style='border-top-color: #28a745;'><h3>✅ جاهز للتسليم</h3><h2>{len(df_stats[df_stats['الحالة'] == 'جاهز'])}</h2></div>", unsafe_allow_html=True)
with c4: 
    rev = pd.to_numeric(df_stats[df_stats['الحالة'] == 'تم التسليم']['التكلفة']).sum()
    st.markdown(f"<div class='stat-card' style='border-top-color: #17a2b8;'><h3>💰 إجمالي الدخل</h3><h2>{rev}$</h2></div>", unsafe_allow_html=True)

tabs = st.tabs(["🔍 البحث والإدارة", "📥 إضافة جهاز", "📊 التقارير المالية"])

# --- التبويب الأول: البحث والإدارة (مع زر واتساب) ---
with tabs[0]:
    search_id_from_url = st.query_params.get("id", "")
    search_q = st.text_input("🔎 ابحث بالاسم، الهاتف، أو ID", value=search_id_from_url)
    
    if search_q:
        df_search = st.session_state.db.copy()
        query = str(search_q).lower()
        mask = (df_search['الزبون'].astype(str).str.lower().str.contains(query) | 
                df_search['الهاتف'].astype(str).str.contains(query) | 
                df_search['ID'].astype(str).str.fullmatch(query))
        
        results = df_search[mask]
        
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=(search_id_from_url != "")):
                col1, col2 = st.columns([2, 1])
                with col1:
                    with st.form(f"form_{idx}"):
                        u_status = st.selectbox("الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"].index(row['الحالة']) if row['الحالة'] in ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"] else 0)
                        u_cost = st.number_input("التكلفة $", value=int(row['التكلفة']))
                        u_parts = st.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                        if st.form_submit_button("حفظ التعديلات"):
                            st.session_state.db.at[idx, "الحالة"] = u_status
                            st.session_state.db.at[idx, "التكلفة"] = u_cost
                            st.session_state.db.at[idx, "سعر_القطع"] = u_parts
                            save_db()
                            st.rerun()
                
                with col2:
                    # ميزة الواتساب التلقائي
                    msg = f"مرحباً سيد {row['الزبون']}، جهازك ({row['الموديل']}) حالته الآن: {row['الحالة']}. التكلفة: {row['التكلفة']}$."
                    wa_link = f"https://wa.me/{row['الهاتف']}?text={msg}"
                    st.link_button("💬 مراسلة الزبون واتساب", wa_link)
                    
                    # الباركود
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                    st.image(qr_url, caption="باركود الجهاز")

# --- التبويب الثاني: إضافة جهاز ---
with tabs[1]:
    with st.form("new_dev"):
        c_a, c_b = st.columns(2)
        f_name = c_a.text_input("اسم الزبون")
        f_phone = c_b.text_input("رقم الهاتف (مع رمز الدولة)")
        f_model = c_a.text_input("نوع الجهاز")
        f_cost = c_b.number_input("التكلفة المتفق عليها $", min_value=0)
        f_issue = st.text_area("وصف العطل")
        if st.form_submit_button("إضافة الجهاز للنظام"):
            new_id = len(st.session_state.db) + 1001
            new_row = {"ID": new_id, "الزبون": f_name, "الهاتف": f_phone, "الموديل": f_model, "الحالة": "تحت الصيانة", "التكلفة": f_cost, "سعر_القطع": 0, "التاريخ_الكامل": datetime.now(), "العطل": f_issue}
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
            save_db()
            st.success(f"تم تسجيل الجهاز برقم {new_id}")

# --- التبويب الثالث: التقارير المالية وتصدير البيانات ---
with tabs[2]:
    st.subheader("📊 الأداء المالي")
    df_fin = st.session_state.db.copy()
    csv = df_fin.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 تحميل كل البيانات (Excel/CSV)", csv, "inventory_report.csv", "text/csv")
    
    # عرض جدول الأرباح
    st.dataframe(df_fin[df_fin['الحالة'] == 'تم التسليم'][['ID', 'الزبون', 'التكلفة', 'سعر_القطع']])
