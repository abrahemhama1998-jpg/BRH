import streamlit as st
import pandas as pd
import os
import urllib.parse
from datetime import datetime

# --- 1. إعدادات الصفحة والروابط ---
st.set_page_config(page_title="الحل للتقنية | Smart System", layout="wide", initial_sidebar_state="collapsed")

# الحصول على عنوان الموقع الحالي (عشان الرابط يشتغل صح في المتصفح)
# ملاحظة: إذا كنت تستخدمه محلياً سيعود بـ localhost
query_params = st.query_params

# --- 2. التصميم CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    .system-header {
        background-color: white; padding: 20px; border-radius: 8px;
        border-bottom: 4px solid #1e3a8a; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;
    }
    .stButton > button { background-color: #1e3a8a; color: white; font-weight: bold; width: 100%; border-radius: 8px; }
    .edit-box { background-color: #fff4e5; padding: 20px; border-radius: 10px; border: 1px solid #ffa94d; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. محرك البيانات ---
DB_FILE = "master_db_v10.csv"
if 'db' not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.db = pd.read_csv(DB_FILE).fillna('')
    else:
        st.session_state.db = pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "ملاحظات", "الصورة"])

def save_all():
    st.session_state.db.to_csv(DB_FILE, index=False)

def print_service(content_html):
    js_code = f"""
    <div id="print-area" style="display:none;">{content_html}</div>
    <script>
        var win = window.open('', '', 'height=700,width=700');
        win.document.write('<html><head><title>Print</title><style>body{{font-family:Cairo;direction:rtl;text-align:center;}} .box{{border:2px solid #000;padding:10px;display:inline-block;}}</style></head><body>');
        win.document.write('<div class="box">' + document.getElementById('print-area').innerHTML + '</div>');
        win.document.write('</body></html>');
        win.document.close();
        setTimeout(function(){{ win.print(); win.close(); }}, 1500);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 4. واجهة النظام ---
st.markdown("<div class='system-header'><h1>الحل للتقنية - الربط الذكي</h1></div>", unsafe_allow_html=True)

# التحقق إذا كان هناك ID في الرابط (جاي من الباركود)
device_from_url = query_params.get("device_id")

if device_from_url:
    # --- وضع التعديل السريع (يفتح عند مسح الباركود) ---
    st.markdown(f"<div class='edit-box'><h3>🛠️ تعديل سريع للجهاز رقم: {device_from_url}</h3>", unsafe_allow_html=True)
    target_id = int(device_from_url)
    df = st.session_state.db
    row_idx = df.index[df['ID'] == target_id]
    
    if not row_idx.empty:
        idx = row_idx[0]
        with st.form("quick_edit"):
            c1, c2 = st.columns(2)
            new_name = c1.text_input("الزبون", value=df.at[idx, 'الزبون'])
            new_phone = c2.text_input("الهاتف", value=df.at[idx, 'الهاتف'])
            new_model = c1.text_input("الموديل", value=df.at[idx, 'الموديل'])
            new_status = c2.selectbox("الحالة", ["تحت الصيانة", "جاهز", "تم التسليم"], index=["تحت الصيانة", "جاهز", "تم التسليم"].index(df.at[idx, 'الحالة']))
            new_issue = st.text_area("العطل", value=df.at[idx, 'العطل'])
            
            if st.form_submit_button("حفظ التعديلات"):
                st.session_state.db.at[idx, 'الزبون'] = new_name
                st.session_state.db.at[idx, 'الهاتف'] = new_phone
                st.session_state.db.at[idx, 'الموديل'] = new_model
                st.session_state.db.at[idx, 'الحالة'] = new_status
                st.session_state.db.at[idx, 'العطل'] = new_issue
                save_all()
                st.success("تم التعديل بنجاح!")
                # العودة للرئيسية بعد الحفظ
                if st.button("العودة للقائمة الرئيسية"):
                    st.query_params.clear()
                    st.rerun()
    else:
        st.error("الجهاز غير موجود")
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("إلغاء والعودة"):
        st.query_params.clear()
        st.rerun()
    st.stop()

# --- القائمة العادية ---
menu = st.radio("القائمة:", ["📊 الإحصائيات", "📥 الاستلام", "🔍 المتابعة"], horizontal=True, label_visibility="collapsed")
st.write("---")

if menu == "🔍 المتابعة":
    q = st.text_input("ابحث هنا...")
    df_all = st.session_state.db
    display_df = df_all[df_all['الزبون'].str.contains(q)] if q else df_all.tail(10).iloc[::-1]

    for idx, row in display_df.iterrows():
        with st.expander(f"📱 {row['الزبون']} (ID: {row['ID']})"):
            c1, c2 = st.columns([2, 1])
            with c1:
                st.write(f"العطل: {row['العطل']}")
                st.write(f"الحالة: {row['الحالة']}")
            with c2:
                # توليد رابط الباركود ليفتح صفحة التعديل
                # ملاحظة: استبدل الرابط أدناه برابط موقعك الحقيقي عند رفعه أونلاين
                base_url = "http://localhost:8501" # الرابط الافتراضي للـ Streamlit
                full_link = f"{base_url}/?device_id={row['ID']}"
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={urllib.parse.quote(full_link)}"
                
                if st.button("🏷️ طباعة ستيكر الذكي", key=f"qr_{idx}"):
                    sticker = f"<h2>{row['الزبون']}</h2><img src='{qr_url}' width='140'><br><b>ID: {row['ID']}</b>"
                    print_service(sticker)

# بقية الأقسام (الاستلام والإحصائيات) تبقى كما هي...
