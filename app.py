import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# CSS لإصلاح شكل الواجهة ومنع مشاكل الطباعة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    @media print {
        header, footer, .stTabs, button, [data-testid="stHeader"], .no-print { display: none !important; }
        .printable { display: block !important; width: 100% !important; color: black !important; background: white !important; }
    }
    .printable { display: none; }
    .preview-box { border: 1px solid #ddd; padding: 10px; border-radius: 8px; background: #f9f9f9; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "tech_database_v50.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        cols = ["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"]
        for col in cols:
            if col not in df.columns: df[col] = 0 if "سعر" in col or "التكلفة" in col else ""
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# دالة الطباعة السحرية (تطبع فقط ما تطلبه)
def print_content(html):
    js = f"""<script>
    var win = window.open('', '', 'height=500,width=700');
    win.document.write('<html><head><title>Print</title><style>body{{font-family:Cairo; direction:rtl; text-align:center; color:black;}}</style></head><body>');
    win.document.write('{html}');
    win.document.write('</body></html>');
    win.document.close();
    setTimeout(function(){{ win.print(); win.close(); }}, 500);
    </script>"""
    st.components.v1.html(js, height=0)

# ميزة الباركود الذكي: قراءة ID الجهاز من الرابط
params = st.query_params
auto_id = params.get("device_id", "")

st.title("🛠️ منظومة الحل للتقنية")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 الإدارة والبحث", "📊 المالية"])

with tabs[0]:
    with st.form("new_dev", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c1.text_input("رقم الهاتف")
        model = c2.text_input("الموديل")
        cost = c2.number_input("التكلفة $", min_value=0)
        issue = st.text_area("وصف العطل")
        if st.form_submit_button("✅ حفظ"):
            if name:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الهاتف": phone, "الموديل": model, "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_data(st.session_state.db)
                st.success(f"تم الحفظ! رقم الوصل: {new_id}")

with tabs[1]:
    # إذا مسحت الباركود سيظهر الجهاز هنا فوراً
    search = st.text_input("🔎 ابحث بالاسم أو ID الوصل", value=auto_id)
    if search:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search) | st.session_state.db['ID'].astype(str).str.contains(search)]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ إدارة: {row['الزبون']} (ID: {row['ID']})", expanded=True if auto_id else False):
                with st.form(f"edit_{idx}"):
                    c_a, c_b = st.columns(2)
                    u_cost = c_a.number_input("التكلفة الكلية $", value=int(row['التكلفة']))
                    u_parts = c_b.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        st.session_state.db.loc[idx, ['التكلفة', 'سعر_القطع', 'الحالة']] = [u_cost, u_parts, u_status]
                        save_data(st.session_state.db)
                        st.rerun()

                # الباركود يفتح رابط المنظومة مباشرة
                app_url = "https://brhoom-tech.streamlit.app"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={app_url}/?device_id={row['ID']}"

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🖨️ طباعة الوصل", key=f"p1_{idx}"):
                        html = f"<div style='border:2px solid black; padding:15px;'><h2>الحل للتقنية</h2><p>هاتف: 0916206100</p><hr><p>الزبون: {row['الزبون']}</p><p>رقم الجهاز: {row['ID']}</p><h3>المبلغ: {row['التكلفة']}$</h3><img src='{qr_url}'></div>"
                        print_content(html)
                with col2:
                    if st.button(f"🏷️ طباعة الستيكر", key=f"p2_{idx}"):
                        html = f"<div style='border:1px solid black; width:180px; margin:auto; padding:5px;'><b>{row['الزبون']}</b><br>{row['الموديل']}<br><img src='{qr_url}' width='90'><br>ID: {row['ID']}</div>"
                        print_content(html)

with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    income = pd.to_numeric(delivered['التكلفة']).sum()
    parts = pd.to_numeric(delivered['سعر_القطع']).sum()
    st.metric("💰 صافي الربح", f"{income - parts} $")
    st.dataframe(st.session_state.db.drop(columns=['ID']))
