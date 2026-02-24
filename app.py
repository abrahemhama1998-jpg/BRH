import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. التصميم الإداري العالمي (Modern Corporate UI) ---
st.set_page_config(page_title="Al-Hall Tech | ERP System", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    :root {
        --primary-blue: #2563eb;
        --sidebar-bg: #1e293b;
        --card-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.05);
    }

    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f1f5f9; }
    
    /* تنسيق الكروت العلوية */
    .metric-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: var(--card-shadow);
        border-top: 5px solid var(--primary-blue);
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-container h3 { color: #64748b; font-size: 1rem; margin-bottom: 8px; }
    .metric-container h2 { color: #1e293b; font-size: 2.2rem; font-weight: 700; }

    /* تحسين القائمة الجانبية */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-left: 1px solid #334155;
    }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    .st-emotion-cache-16q9ru2 { font-weight: 600; }

    /* تنسيق النماذج والأزرار */
    .stButton button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white; border: none; border-radius: 10px;
        padding: 10px 24px; font-weight: 600; transition: all 0.3s;
    }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3); }

    /* تنسيق بادجات الحالة */
    .status-badge {
        padding: 5px 15px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات (نفس منطق كودك تماماً لضمان الأمان) ---
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

# --- 3. محرك الطباعة (مستقر وآمن) ---
def print_service(content_html):
    js_code = f"""
    <div id="print-area" style="display:none;">{content_html}</div>
    <script>
        var content = document.getElementById('print-area').innerHTML;
        var win = window.open('', '', 'height=700,width=700');
        win.document.write('<html><head><title>Print System</title>');
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
    st.markdown("<h2 style='text-align:center; color:#1e293b;'>🏛️ الدخول للمنظومة الإدارية</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("تسجيل الدخول الآمن"):
            if u == "admin" and p == "123":
                st.session_state.auth = True; st.rerun()
            else: st.error("بيانات الدخول خاطئة!")
    st.stop()

# --- 5. التنقل والأقسام ---
st.sidebar.markdown("<h1 style='text-align:center; color:white;'>AL-HALL</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border-color:#475569'>", unsafe_allow_html=True)
menu = st.sidebar.radio("📋 الانتقال إلى:", ["📊 لوحة المعلومات", "📥 قسم الاستلام", "🔍 إدارة الأجهزة", "📦 المستودع", "💰 التقارير المالية"])

# --- التبويب 1: لوحة المعلومات ---
if menu == "📊 لوحة المعلومات":
    st.header("🏢 المركز الرئيسي للمعلومات")
    df = st.session_state.db
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-container'><h3>إجمالي الأجهزة</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-container'><h3>تحت الصيانة</h3><h2 style='color:#f59e0b;'>{len(df[df['الحالة']=='تحت الصيانة'])}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-container'><h3>جاهز للتسليم</h3><h2 style='color:#10b981;'>{len(df[df['الحالة']=='جاهز'])}</h2></div>", unsafe_allow_html=True)
    cash = pd.to_numeric(df[df['الحالة']=='تم التسليم']['التكلفة']).sum()
    with c4: st.markdown(f"<div class='metric-container'><h3>صافي الإيرادات</h3><h2 style='color:#2563eb;'>{cash}$</h2></div>", unsafe_allow_html=True)

# --- التبويب 2: قسم الاستلام ---
elif menu == "📥 قسم الاستلام":
    st.header("📋 تسجيل معاملة جديدة")
    with st.form("modern_add"):
        c1, c2 = st.columns(2)
        name, phone = c1.text_input("👤 اسم العميل"), c2.text_input("📱 رقم الهاتف")
        model, cost = c1.text_input("📱 موديل الجهاز"), c2.number_input("💵 التكلفة المقدرة $", min_value=0)
        issue = st.text_area("🔧 تفاصيل العطل الفني")
        notes = st.text_area("📝 ملاحظات الحالة العامة")
        img = st.file_uploader("📸 توثيق صورة الجهاز", type=['jpg','png'])
        if st.form_submit_button("إرسال البيانات للنظام"):
            new_id = len(st.session_state.db) + 1001
            path = os.path.join(IMG_DIR, f"{new_id}.jpg") if img else ""
            if img:
                with open(path, "wb") as f: f.write(img.getbuffer())
            st.session_state.db.loc[len(st.session_state.db)] = [new_id, name, phone, model, issue, cost, 0, "تحت الصيانة", datetime.now(), notes, path]
            save_all(); st.success(f"تم التسجيل بنجاح - رقم المرجع الرسمي: {new_id}")

# --- التبويب 3: إدارة الأجهزة ---
elif menu == "🔍 إدارة الأجهزة":
    st.header("🔍 وحدة التحكم والمتابعة")
    search_q = st.text_input("ابحث عن (اسم، هاتف، أو رقم المرجع)")
    if search_q:
        df = st.session_state.db
        mask = df['ID'].astype(str).str.contains(search_q) | df['الزبون'].astype(str).str.contains(search_q) | df['الهاتف'].astype(str).str.contains(search_q)
        results = df[mask]
        for idx, row in results.iterrows():
            with st.expander(f"📁 سجل العملية: {row['ID']} - {row['الزبون']}"):
                ca, cb = st.columns([2, 1])
                with ca:
                    new_st = st.selectbox("تحديث حالة العمل", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=0, key=f"st_{idx}")
                    p_list = ["بدون قطع غيار"] + st.session_state.inv[st.session_state.inv['الكمية'] > 0]['القطعة'].tolist()
                    sel_p = st.selectbox("ربط قطع غيار من المخزن", p_list, key=f"p_{idx}")
                    if st.button("تأكيد التحديثات", key=f"sv_{idx}"):
                        if sel_p != "بدون قطع غيار":
                            p_info = st.session_state.inv[st.session_state.inv['القطعة'] == sel_p].iloc[0]
                            st.session_state.db.at[idx, 'سعر_القطع'] += p_info['السعر']
                            st.session_state.inv.loc[st.session_state.inv['القطعة'] == sel_p, 'الكمية'] -= 1
                        st.session_state.db.at[idx, 'الحالة'] = new_st
                        save_all(); st.rerun()
                with cb:
                    if row['الصورة']: st.image(row['الصورة'], width=120)
                    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={row['ID']}"
                    if st.button("🏷️ طباعة ستيكر", key=f"stk_{idx}"):
                        print_service(f"<h3>الحل للتقنية</h3><b>{row['الزبون']}</b><br><img src='{qr}' width='110'><br>ID: {row['ID']}")
                    if st.button("📄 طباعة الفاتورة", key=f"rec_{idx}"):
                        rec = f"<h3>فاتورة صيانة</h3><hr><table><tr><td>المرجع:</td><td>{row['ID']}</td></tr><tr><td>العميل:</td><td>{row['الزبون']}</td></tr><tr><td>الجهاز:</td><td>{row['الموديل']}</td></tr><tr><td>المبلغ:</td><td>{row['التكلفة']}$</td></tr></table>"
                        print_service(rec)

# --- التبويب 4: المستودع ---
elif menu == "📦 المستودع":
    st.header("📦 إدارة أصول المخزون")
    with st.form("inv_mod"):
        c1, c2, c3 = st.columns(3)
        n, s, q = c1.text_input("اسم الصنف"), c2.number_input("السعر $"), c3.number_input("الكمية المتاحة", min_value=1)
        if st.form_submit_button("إضافة للمخزون"):
            st.session_state.inv.loc[len(st.session_state.inv)] = [n, s, q]
            save_all(); st.rerun()
    st.dataframe(st.session_state.inv, use_container_width=True)

# --- التبويب 5: التقارير المالية ---
elif menu == "💰 التقارير المالية":
    st.header("💰 تحليل الإيرادات")
    df_f = st.session_state.db[st.session_state.db['الحالة']=='تم التسليم'].copy()
    if not df_f.empty:
        df_f['الشهر'] = pd.to_datetime(df_f['التاريخ']).dt.strftime('%Y-%m')
        for m in sorted(df_f['الشهر'].unique(), reverse=True):
            m_data = df_f[df_f['الشهر']==m]
            profit = m_data['التكلفة'].sum() - m_data['سعر_القطع'].sum()
            with st.expander(f"📊 كشف مالي لشهر {m}"):
                st.markdown(f"<div style='background:white; padding:20px; border-radius:10px; border-right:6px solid #2563eb;'><h3>صافي الربح الإجمالي: {profit}$</h3><h4>نصيب الفرد: {profit/2}$</h4></div>", unsafe_allow_html=True)
                st.dataframe(m_data[['ID','الزبون','الموديل','التكلفة']], use_container_width=True)
