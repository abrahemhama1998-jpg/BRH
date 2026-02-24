import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الصفحة ---
st.set_page_config(page_title="الحل للتقنية", layout="wide")

# تصميم خاص للطباعة والواجهة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    @media print {
        header, footer, .stTabs, button, [data-testid="stHeader"], .no-print {
            display: none !important;
        }
        .printable { display: block !important; width: 100% !important; color: black !important; }
    }
    .preview-box { border: 1px solid #ddd; padding: 10px; border-radius: 8px; background: #f9f9f9; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# قاعدة البيانات
DB_FILE = "tech_database.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "الزبون", "الموديل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# دالة الطباعة (تفتح نافذة مستقلة للوصل فقط)
def print_content(html):
    js = f"""<script>
    var win = window.open('', '', 'height=500,width=700');
    win.document.write('<html><head><title>Print</title><style>body{{font-family:Cairo; direction:rtl; text-align:center; color:black;}} .box{{border:2px solid black; padding:20px;}}</style></head><body><div class="box">');
    win.document.write('{html}');
    win.document.write('</div></body></html>');
    win.document.close();
    setTimeout(function(){{ win.print(); win.close(); }}, 500);
    </script>"""
    st.components.v1.html(js, height=0)

# ميزة الباركود: استقبال رقم الجهاز من الرابط
params = st.query_params
auto_id = params.get("id", "")

st.title("🛠️ منظومة الحل للتقنية للصيانة")

tabs = st.tabs(["➕ إضافة جهاز", "🔍 البحث والإدارة", "📊 المالية"])

# 1. إضافة جهاز جديد
with tabs[0]:
    with st.form("new_device", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        model = c2.text_input("موديل الجهاز")
        cost = c1.number_input("التكلفة المتفق عليها $", min_value=0)
        if st.form_submit_button("✅ حفظ الجهاز"):
            if name and model:
                new_id = len(st.session_state.db) + 1001
                new_row = {"ID": new_id, "الزبون": name, "الموديل": model, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة", "التاريخ": datetime.now().strftime("%Y-%m-%d")}
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.db.to_csv(DB_FILE, index=False)
                st.success(f"تم الحفظ! رقم الجهاز: {new_id}")

# 2. البحث والتعديل والطباعة
with tabs[1]:
    search = st.text_input("🔎 ابحث بالاسم أو برقم ID الجهاز", value=auto_id)
    if search:
        results = st.session_state.db[st.session_state.db['الزبون'].astype(str).str.contains(search) | st.session_state.db['ID'].astype(str).str.contains(search)]
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - ID: {row['ID']}", expanded=True if auto_id else False):
                with st.form(f"edit_{idx}"):
                    c_a, c_b = st.columns(2)
                    u_cost = c_a.number_input("التكلفة $", value=int(row['التكلفة']))
                    u_parts = c_b.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                    u_status = st.selectbox("الحالة", ["تحت الصيانة", "تم التسليم"], index=0 if row['الحالة']=="تحت الصيانة" else 1)
                    if st.form_submit_button("💾 حفظ التعديلات"):
                        st.session_state.db.loc[idx, ['التكلفة', 'سعر_القطع', 'الحالة']] = [u_cost, u_parts, u_status]
                        st.session_state.db.to_csv(DB_FILE, index=False)
                        st.rerun()

                # الباركود: يفتح المنظومة ويبحث عن الـ ID تلقائياً
                # ملاحظة: تم استخدام رابط تطبيقك الفعلي
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    if st.button(f"🖨️ طباعة وصل الزبون", key=f"print_rec_{idx}"):
                        html = f"<h2>الحل للتقنية</h2><p>رقم الجهاز: {row['ID']}</p><p>الزبون: {row['الزبون']}</p><p>الموديل: {row['الموديل']}</p><h3>المطلوب: {row['التكلفة']}$</h3><img src='{qr_url}' width='130'>"
                        print_content(html)
                with col_p2:
                    if st.button(f"🏷️ طباعة ستيكر الجهاز", key=f"print_stk_{idx}"):
                        html = f"<b>{row['الزبون']}</b><br>{row['الموديل']}<br><img src='{qr_url}' width='100'><br>ID: {row['ID']}"
                        print_content(html)

# 3. المالية
with tabs[2]:
    st.write("### سجل الحسابات")
    st.dataframe(st.session_state.db)
