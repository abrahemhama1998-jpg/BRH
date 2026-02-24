import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. تصميم الواجهة العلوية الاحترافية (Horizontal Navigation UI) ---
st.set_page_config(page_title="Al-Hall Tech | Pro V15", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    :root {
        --primary: #2563eb;
        --bg: #f8fafc;
        --text: #1e293b;
    }

    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: var(--bg); }
    
    /* إخفاء القائمة الجانبية تماماً */
    [data-testid="stSidebar"] { display: none; }
    
    /* تنسيق الحاويات العلوية */
    .header-bar {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        text-align: center;
        border-bottom: 3px solid var(--primary);
    }

    /* كروت الإحصائيات */
    .metric-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center; border-bottom: 4px solid var(--primary);
    }
    .metric-card h2 { color: var(--primary); margin: 0; font-size: 2rem; }
    
    /* تنسيق الأزرار */
    .stButton button {
        width: 100%; border-radius: 10px; 
        background-color: var(--primary); color: white;
        font-weight: 600; transition: 0.3s;
    }
    .stButton button:hover { transform: translateY(-2px); opacity: 0.9; }

    /* جعل الراديو يبدو كقائمة علوية */
    div[data-testid="stHorizontalBlock"] {
        background: white;
        padding: 10px;
        border-radius: 50px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات (ثابت وأمن) ---
DB_FILE = "master_db_v10.csv"
INV_FILE = "inventory_db_v10.csv"
IMG_DIR = "device_vault"

if not os.path.exists(IMG_DIR): os.makedirs(IMG_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['التاريخ'] = pd.to_datetime(df['التاريخ'], errors='coerce')
        for col in ['الزبون', 'الهاتف', 'الموديل', 'ملاحظات', 'الحالة', 'العطل']:
            df[col] = df[col].fillna('')
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "ملاحظات", "الصورة"])

def load_inv():
    if os.path.exists(INV_FILE): return pd.read_csv(INV_FILE)
    return pd.DataFrame(columns=["القطعة", "السعر", "الكمية"])

if 'db' not in st.session_state: st.session_state.db = load_data()
if 'inv' not in st.session_state: st.session_state.inv = load_inv()

def save_all():
    st.session_state.db.to_csv(DB_FILE, index=False)
    st.session_state.inv.to_csv(INV_FILE, index=False)

# --- 3. محرك الطباعة ---
def print_service(content_html):
    js_code = f"""
    <div id="print-area" style="display:none;">{content_html}</div>
    <script>
        var content = document.getElementById('print-area').innerHTML;
        var win = window.open('', '', 'height=700,width=700');
        win.document.write('<html><head><title>Print</title>');
        win.document.write('<style>@import url("https://fonts.googleapis.com/css2?family=Cairo&display=swap"); body {{ font-family: "Cairo", sans-serif; direction: rtl; text-align: center; }} .box {{ border: 2px solid #000; padding: 20px; border-radius: 10px; display: inline-block; min-width: 280px; }} table {{ width: 100%; margin-top: 15px; }} td {{ text-align: right; padding: 5px; border-bottom: 1px solid #eee; }}</style>');
        win.document.write('</head><body><div class="box">');
        win.document.write(content);
        win.document.write('</div></body></html>');
        win.document.close();
        win.onload = function() {{ setTimeout(function() {{ win.print(); win.close(); }}, 800); }};
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 4. حماية النظام ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center; color:#2563eb;'>🔒 الحل للتقنية - الدخول</h2>", unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "123":
            st.session_state.auth = True; st.rerun()
    st.stop()

# --- 5. القائمة العلوية الأفقية (The Header) ---
st.markdown("<div class='header-bar'><h1>💎 منظومة الحل للتقنية الإدارية</h1></div>", unsafe_allow_html=True)

# إنشاء أزرار التنقل بشكل أفقي في الأعلى
menu = st.select_slider(
    "انتقل بين الأقسام من هنا:",
    options=["📊 الرئيسية", "📥 الاستلام", "🔍 البحث والإدارة", "📦 المخزن", "💰 المالية"],
    value="📊 الرئيسية"
)

st.markdown("<hr>", unsafe_allow_html=True)

# --- التبويب 1: الرئيسية ---
if menu == "📊 الرئيسية":
    df = st.session_state.db
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><h3>📦 الكلي</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><h3>🛠️ صيانة</h3><h2 style='color:#f59e0b;'>{len(df[df['الحالة']=='تحت الصيانة'])}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card'><h3>✅ جاهز</h3><h2 style='color:#10b981;'>{len(df[df['الحالة']=='جاهز'])}</h2></div>", unsafe_allow_html=True)
    cash = pd.to_numeric(df[df['الحالة']=='تم التسليم']['التكلفة']).sum()
    with c4: st.markdown(f"<div class='metric-card'><h3>💰 دخل</h3><h2>{cash}$</h2></div>", unsafe_allow_html=True)

# --- التبويب 2: الاستلام ---
elif menu == "📥 الاستلام":
    st.header("📥 تسجيل جهاز جديد")
    with st.form("add_form"):
        c1, c2 = st.columns(2)
        name, phone = c1.text_input("👤 اسم الزبون"), c2.text_input("📱 رقم الهاتف")
        model, cost = c1.text_input("📱 موديل الجهاز"), c2.number_input("💵 التكلفة المقدرة $", min_value=0)
        issue = st.text_area("🔧 وصف العطل")
        notes = st.text_area("📝 ملاحظات إضافية")
        img = st.file_uploader("📸 صورة الجهاز", type=['jpg','png'])
        if st.form_submit_button("حفظ البيانات"):
            new_id = len(st.session_state.db) + 1001
            path = os.path.join(IMG_DIR, f"{new_id}.jpg") if img else ""
            if img:
                with open(path, "wb") as f: f.write(img.getbuffer())
            st.session_state.db.loc[len(st.session_state.db)] = [new_id, name, phone, model, issue, cost, 0, "تحت الصيانة", datetime.now(), notes, path]
            save_all(); st.success(f"تم التسجيل بنجاح! رقم المرجع: {new_id}")

# --- التبويب 3: البحث والإدارة ---
elif menu == "🔍 البحث والإدارة":
    st.header("🔍 متابعة الأجهزة والطباعة")
    q = st.text_input("ابحث باسم الزبون أو رقم الهاتف أو ID")
    if q:
        df = st.session_state.db
        mask = df['ID'].astype(str).str.contains(q) | df['الزبون'].astype(str).str.contains(q) | df['الهاتف'].astype(str).str.contains(q)
        res = df[mask]
        for idx, row in res.iterrows():
            with st.expander(f"📱 {row['الزبون']} - ID: {row['ID']}"):
                ca, cb = st.columns([2, 1])
                with ca:
                    new_st = st.selectbox("تحديث الحالة", ["تحت الصيانة", "جاهز", "تم التسليم"], key=f"s_{idx}")
                    p_list = ["بدون قطع"] + st.session_state.inv[st.session_state.inv['الكمية'] > 0]['القطعة'].tolist()
                    sel_p = st.selectbox("إضافة قطع غيار", p_list, key=f"p_{idx}")
                    if st.button("تحديث الحفظ", key=f"b_{idx}"):
                        if sel_p != "بدون قطع":
                            p_info = st.session_state.inv[st.session_state.inv['القطعة'] == sel_p].iloc[0]
                            st.session_state.db.at[idx, 'سعر_القطع'] += p_info['السعر']
                            st.session_state.inv.loc[st.session_state.inv['القطعة'] == sel_p, 'الكمية'] -= 1
                        st.session_state.db.at[idx, 'الحالة'] = new_st
                        save_all(); st.rerun()
                with cb:
                    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={row['ID']}"
                    if st.button("🏷️ طباعة باركود", key=f"qr_{idx}"):
                        print_service(f"<h3>الحل للتقنية</h3><b>{row['الزبون']}</b><br><img src='{qr}' width='110'><br>ID: {row['ID']}")
                    if st.button("📄 طباعة وصل", key=f"pr_{idx}"):
                        print_service(f"<h3>وصل استلام</h3><hr>ID: {row['ID']}<br>الزبون: {row['الزبون']}<br>الموديل: {row['الموديل']}<br>التكلفة: {row['التكلفة']}$")

# --- التبويب 4: المخزن ---
elif menu == "📦 المخزن":
    st.header("📦 إدارة قطع الغيار")
    with st.form("inv_form"):
        c1, c2, c3 = st.columns(3)
        n, s, q = c1.text_input("اسم القطعة"), c2.number_input("السعر $"), c3.number_input("الكمية", min_value=1)
        if st.form_submit_button("إضافة للمخزن"):
            st.session_state.inv.loc[len(st.session_state.inv)] = [n, s, q]
            save_all(); st.rerun()
    st.dataframe(st.session_state.inv, use_container_width=True)

# --- التبويب 5: المالية ---
elif menu == "💰 المالية":
    st.header("💰 تقارير الأرباح")
    df_f = st.session_state.db[st.session_state.db['الحالة']=='تم التسليم'].copy()
    if not df_f.empty:
        df_f['الشهر'] = pd.to_datetime(df_f['التاريخ']).dt.strftime('%Y-%m')
        for m in sorted(df_f['الشهر'].unique(), reverse=True):
            m_data = df_f[df_f['الشهر']==m]
            profit = m_data['التكلفة'].sum() - m_data['سعر_القطع'].sum()
            with st.expander(f"📅 كشف شهر {m}"):
                st.info(f"صافي الربح: {profit}$ | حصة الشريك: {profit/2}$")
                st.dataframe(m_data[['ID','الزبون','التكلفة']], use_container_width=True)
