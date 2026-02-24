import streamlit as st
import pandas as pd
import os
from datetime import datetime

# إعداد الصفحة
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# تصميم لمنع طباعة عناصر الموقع والتركيز على الوصل
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    @media print {
        header, footer, .stTabs, button, [data-testid="stHeader"] { display: none !important; }
        .printable { display: block !important; }
    }
    </style>
    """, unsafe_allow_html=True)

DB_FILE = "tech_database.csv"

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "الزبون", "الموديل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

if 'db' not in st.session_state: st.session_state.db = load_data()

def trigger_print(html):
    js = f"""<script>
    var win = window.open('', '', 'height=500,width=700');
    win.document.write('<html><head><title>Print</title><style>body{{font-family:Cairo; direction:rtl; text-align:center; padding:20px;}} .box{{border:2px solid #000; padding:20px;}}</style></head><body><div class="box">');
    win.document.write('{html}');
    win.document.write('</div></body></html>');
    win.document.close();
    setTimeout(function(){{ win.print(); win.close(); }}, 500);
    </script>"""
    st.components.v1.html(js, height=0)

# استقبال رقم الجهاز من الباركود
params = st.query_params
auto_id = params.get("id", "")

st.title("🛠️ منظومة الحل للتقنية")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 البحث والإدارة", "📊 المالية"])

with tabs[0]:
    with st.form("new_dev", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        model = c2.text_input("الموديل")
        cost = c1.number_input("التكلفة الكلية $", min_value=0)
        if st.form_submit_button("✅ حفظ"):
            new_id = len(st.session_state.db) + 1001
            new_row = {"ID": new_id, "الزبون": name, "الموديل": model, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.db.to_csv(DB_FILE, index=False)
            st.success(f"تم الحفظ! رقم الجهاز: {new_id}")

with tabs[1]:
    search = st.text_input("🔎 ابحث بالاسم أو ID", value=auto_id)
    if search:
        res = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search) | st.session_state.db['ID'].astype(str).str.contains(search)]
        for idx, row in res.iterrows():
            with st.expander(f"📋 {row['الزبون']} - ID: {row['ID']}", expanded=True if auto_id else False):
                # الباركود الذكي (رابط خارجي سريع)
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={st.query_params.get('app_url', 'https://brh-tech.streamlit.app')}/?id={row['ID']}"
                
                c_1, c_2 = st.columns(2)
                with c_1:
                    if st.button(f"🖨️ طباعة الوصل", key=f"p1_{idx}"):
                        html = f"<h2>الحل للتقنية</h2><hr><p>الزبون: {row['الزبون']}</p><p>رقم الجهاز: {row['ID']}</p><h3>المبلغ: {row['التكلفة']}$</h3><img src='{qr_url}' width='130'>"
                        trigger_print(html)
                with c_2:
                    if st.button(f"🏷️ طباعة الستيكر", key=f"p2_{idx}"):
                        html = f"<b>{row['الزبون']}</b><br>{row['الموديل']}<br><img src='{qr_url}' width='100'><br>ID: {row['ID']}"
                        trigger_print(html)

with tabs[2]:
    st.dataframe(st.session_state.db)
