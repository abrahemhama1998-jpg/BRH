import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# --- 1. الإعدادات الأساسية ---
st.set_page_config(page_title="الحل للتقنية - احترافي", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stMetric { background: #f8f9fa; border-radius: 10px; padding: 15px; border: 1px solid #eee; }
    @media print {
        header, footer, .stTabs, button, [data-testid="stHeader"], .no-print { display: none !important; }
        .printable { display: block !important; width: 100% !important; color: black !important; background: white !important; }
    }
    .preview-card { border: 2px solid #333; padding: 20px; border-radius: 10px; background: white; color: black; text-align: center; max-width: 350px; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات والصور ---
DB_FILE = "tech_v3_database.csv"
IMG_DIR = "device_images"
if not os.path.exists(IMG_DIR): os.makedirs(IMG_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        cols = ["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "ملاحظات", "صورة"]
        for col in cols:
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "ملاحظات", "صورة"])

if 'db' not in st.session_state: st.session_state.db = load_data()

def save_db():
    st.session_state.db.to_csv(DB_FILE, index=False)

def print_action(html):
    st.components.v1.html(f"<script>var w=window.open(); w.document.write('{html}'); w.document.close(); setTimeout(function(){{w.print(); w.close();}}, 500);</script>", height=0)

# --- 3. الواجهة الرئيسية ---
st.title("🛠️ منظومة الحل للتقنية المتكاملة")
tabs = st.tabs(["📥 استلام جهاز جديد", "🔍 إدارة وبحث وتعديل", "📊 التقارير المالية"])

# --- التبويب الأول: إضافة جهاز ---
with tabs[0]:
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("اسم الزبون")
        phone = c2.text_input("رقم الهاتف")
        model = c3.text_input("الموديل")
        issue = st.text_area("وصف العطل")
        notes = st.text_area("ملاحظات إضافية")
        cost = st.number_input("التكلفة المتوقعة $", min_value=0)
        uploaded_file = st.file_uploader("إرفاق صورة للجهاز", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("✅ حفظ وجدولة الجهاز"):
            new_id = len(st.session_state.db) + 1001
            img_path = ""
            if uploaded_file:
                img_path = os.path.join(IMG_DIR, f"{new_id}.jpg")
                with open(img_path, "wb") as f: f.write(uploaded_file.getbuffer())
            
            new_row = {
                "ID": new_id, "الزبون": name, "الهاتف": phone, "الموديل": model,
                "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة",
                "التاريخ": datetime.now().strftime("%Y-%m-%d"), "ملاحظات": notes, "صورة": img_path
            }
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
            save_db()
            st.success(f"تم الحفظ برقم: {new_id}")

# --- التبويب الثاني: البحث والإدارة الشاملة ---
with tabs[1]:
    search = st.text_input("🔎 ابحث (اسم، رقم هاتف، أو ID الجهاز)")
    if search:
        df = st.session_state.db
        res = df[df['الزبون'].astype(str).str.contains(search) | df['ID'].astype(str).str.contains(search) | df['الهاتف'].astype(str).str.contains(search)]
        
        for idx, row in res.iterrows():
            with st.expander(f"⚙️ تعديل: {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=True):
                c_edit1, c_edit2 = st.columns([2, 1])
                
                with c_edit1:
                    with st.form(f"f_{idx}"):
                        u_status = st.selectbox("الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=0)
                        u_cost = st.number_input("التكلفة الكلية $", value=int(row['التكلفة']))
                        u_parts = st.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                        u_notes = st.text_area("تعديل الملاحظات", value=row['ملاحظات'])
                        if st.form_submit_button("💾 حفظ التعديلات"):
                            st.session_state.db.loc[idx, ["الحالة", "التكلفة", "سعر_القطع", "ملاحظات"]] = [u_status, u_cost, u_parts, u_notes]
                            save_db()
                            st.rerun()
                
                with c_edit2:
                    if row['صورة'] and os.path.exists(str(row['صورة'])):
                        st.image(str(row['صورة']), caption="صورة الجهاز", use_container_width=True)
                    else:
                        st.info("لا توجد صورة")
                
                # قسم المعاينة والطباعة داخل البحث
                st.markdown("---")
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                
                p_col1, p_col2 = st.columns(2)
                with p_col1:
                    st.markdown("**معاينة الوصل**")
                    receipt_html = f"<div class='preview-card'><h3>الحل للتقنية</h3><hr><p>ID: {row['ID']}</p><p>الزبون: {row['الزبون']}</p><h4>المبلغ: {row['التكلفة']} $</h4><img src='{qr_url}' width='100'></div>"
                    st.markdown(receipt_html, unsafe_allow_html=True)
                    if st.button(f"🖨️ طباعة الوصل", key=f"p_rec_{idx}"):
                        print_action(receipt_html)

                with p_col2:
                    st.markdown("**معاينة الستيكر**")
                    sticker_html = f"<div class='preview-card' style='padding:10px; width:180px;'><b>{row['الزبون']}</b><br><small>{row['الموديل']}</small><br><img src='{qr_url}' width='80'><br>ID: {row['ID']}</div>"
                    st.markdown(sticker_html, unsafe_allow_html=True)
                    if st.button(f"🏷️ طباعة الستيكر", key=f"p_stk_{idx}"):
                        print_action(sticker_html)

# --- التبويب الثالث: التقارير ---
with tabs[2]:
    delivered = st.session_state.db[st.session_state.db['الحالة'] == "تم التسليم"]
    rev = pd.to_numeric(delivered['التكلفة']).sum()
    parts = pd.to_numeric(delivered['سعر_القطع']).sum()
    st.columns(3)[0].metric("صافي الأرباح", f"{rev - parts} $")
    st.dataframe(st.session_state.db, use_container_width=True)
