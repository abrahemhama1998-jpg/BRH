import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. التصميم الإداري الاحترافي (Corporate UI) ---
st.set_page_config(page_title="ProSystem | الحل للتقنية", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;700&display=swap');
    
    :root {
        --primary-color: #1e3a8a; /* الأزرق الملكي */
        --bg-color: #f1f5f9;
        --card-bg: #ffffff;
    }

    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    .stApp { background-color: var(--bg-color); }
    
    /* تنسيق كروت الإحصائيات */
    .corporate-card {
        background: var(--card-bg);
        padding: 25px;
        border-radius: 12px;
        border-right: 8px solid var(--primary-color);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s;
    }
    .corporate-card:hover { transform: translateY(-5px); }
    
    /* القائمة الجانبية */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; /* لون كحلي غامق رسمي */
        color: white;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* العناوين */
    h1, h2, h3 { color: var(--primary-color); font-weight: 700; }
    
    /* تنسيق المالية */
    .profit-section {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات (ثابت كما هو لضمان الأمان) ---
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

# --- 3. محرك الطباعة المستقر (بدون تغيير) ---
def print_service(content_html):
    js_code = f"""
    <div id="print-area" style="display:none;">{content_html}</div>
    <script>
        var content = document.getElementById('print-area').innerHTML;
        var win = window.open('', '', 'height=700,width=700');
        win.document.write('<html><head><title>Print System</title>');
        win.document.write('<style>@import url("https://fonts.googleapis.com/css2?family=Cairo&display=swap"); body {{ font-family: "Cairo", sans-serif; direction: rtl; text-align: center; }} .box {{ border: 2px solid #000; padding: 15px; border-radius: 10px; display: inline-block; min-width: 280px; }} table {{ width: 100%; margin-top: 10px; }} td {{ text-align: right; padding: 5px; border-bottom: 1px solid #eee; }}</style>');
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
    st.markdown("<h1 style='text-align:center;'>🔐 نظام الحل للتقنية - تسجيل الدخول</h1>", unsafe_allow_html=True)
    u, p = st.text_input("اسم المستخدم"), st.text_input("كلمة المرور", type="password")
    if st.button("دخول للنظام الآمن"):
        if u == "admin" and p == "123":
            st.session_state.auth = True
            st.rerun()
        else: st.error("بيانات غير مصرح بها")
    st.stop()

# --- 5. الهوية الجانبية الاحترافية ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3067/3067451.png", width=100)
st.sidebar.title("إدارة الحل للتقنية")
menu = st.sidebar.selectbox("📂 الانتقال السريع:", ["📊 لوحة التحكم", "📥 قسم الاستلام", "🔍 إدارة الأجهزة", "📦 المستودع", "💰 التقارير المالية"])

# --- التبويب 1: لوحة التحكم (الرسمية) ---
if menu == "📊 لوحة التحكم":
    st.header("🏢 المركز الرئيسي للمعلومات")
    df = st.session_state.db
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='corporate-card'><h3>📦 إجمالي الطلبات</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='corporate-card' style='border-right-color:#eab308;'><h3>🛠️ تحت الإجراء</h3><h2>{len(df[df['الحالة']=='تحت الصيانة'])}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='corporate-card' style='border-right-color:#22c55e;'><h3>✅ مكتملة وجاهزة</h3><h2>{len(df[df['الحالة']=='جاهز'])}</h2></div>", unsafe_allow_html=True)
    cash = pd.to_numeric(df[df['الحالة']=='تم التسليم']['التكلفة']).sum()
    with c4: st.markdown(f"<div class='corporate-card' style='border-right-color:#0ea5e9;'><h3>💰 الإيرادات</h3><h2>{cash}$</h2></div>", unsafe_allow_html=True)

# --- التبويب 2: قسم الاستلام ---
elif menu == "📥 قسم الاستلام":
    st.header("📋 تسجيل أصول صيانة جديدة")
    with st.form("corporate_add"):
        c1, c2 = st.columns(2)
        name = c1.text_input("👤 اسم العميل بالكامل")
        phone = c2.text_input("📱 هاتف العميل")
        model = c1.text_input("📱 نوع وموديل الجهاز")
        cost = c2.number_input("💵 ميزانية الصيانة المتوقعة $", min_value=0)
        issue = st.text_area("🔧 تفاصيل العطل الفني")
        notes = st.text_area("📝 ملاحظات حالة الاستلام (خدوش، ملحقات)")
        img = st.file_uploader("📸 توثيق صورة الجهاز", type=['jpg','png'])
        if st.form_submit_button("إرسال البيانات للنظام"):
            new_id = len(st.session_state.db) + 1001
            path = os.path.join(IMG_DIR, f"{new_id}.jpg") if img else ""
            if img:
                with open(path, "wb") as f: f.write(img.getbuffer())
            st.session_state.db.loc[len(st.session_state.db)] = [new_id, name, phone, model, issue, cost, 0, "تحت الصيانة", datetime.now(), notes, path]
            save_all(); st.success(f"تم تسجيل المعاملة بنجاح - رقم المرجع: {new_id}")

# --- التبويب 3: إدارة الأجهزة (البحث والطباعة) ---
elif menu == "🔍 إدارة الأجهزة":
    st.header("🔍 وحدة المتابعة والتحكم")
    search_q = st.text_input("ادخل اسم العميل، رقم الهاتف، أو معرف الجهاز (ID)")
    if search_q:
        df = st.session_state.db
        mask = df['ID'].astype(str).str.contains(search_q) | df['الزبون'].astype(str).str.contains(search_q) | df['الهاتف'].astype(str).str.contains(search_q)
        results = df[mask]
        for idx, row in results.iterrows():
            with st.expander(f"📁 سجل العملية: {row['الزبون']} | ID: {row['ID']}"):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    new_status = st.selectbox("تعديل الحالة التشغيلية", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"].index(row['الحالة']), key=f"st_{idx}")
                    p_list = ["بدون قطع غيار"] + st.session_state.inv[st.session_state.inv['الكمية'] > 0]['القطعة'].tolist()
                    sel_p = st.selectbox("ربط قطعة من المستودع", p_list, key=f"p_{idx}")
                    if st.button("تأكيد التحديثات", key=f"sv_{idx}"):
                        if sel_p != "بدون قطع غيار":
                            p_info = st.session_state.inv[st.session_state.inv['القطعة'] == sel_p].iloc[0]
                            st.session_state.db.at[idx, 'سعر_القطع'] += p_info['السعر']
                            st.session_state.inv.loc[st.session_state.inv['القطعة'] == sel_p, 'الكمية'] -= 1
                        st.session_state.db.at[idx, 'الحالة'] = new_status
                        save_all(); st.rerun()
                with col_b:
                    if row['الصورة']: st.image(row['الصورة'], width=120)
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                    if st.button("🏷️ طباعة ستيكر المرجع", key=f"stk_{idx}"):
                        print_service(f"<h3>الحل للتقنية</h3><b>{row['الزبون']}</b><br><img src='{qr_url}' width='110'><br>REF: {row['ID']}")
                    if st.button("📄 إصدار وصل رسمي", key=f"rec_{idx}"):
                        rec_html = f"<h3>فاتورة صيانة رسمية</h3><hr><table><tr><td><b>رقم الجهاز:</b></td><td>{row['ID']}</td></tr><tr><td><b>العميل:</b></td><td>{row['الزبون']}</td></tr><tr><td><b>الموديل:</b></td><td>{row['الموديل']}</td></tr><tr><td><b>العطل:</b></td><td>{row['العطل']}</td></tr><tr><td><b>المبلغ:</b></td><td>{row['التكلفة']}$</td></tr></table><p>تاريخ: {str(row['التاريخ'])[:16]}</p>"
                        print_service(rec_html)

# --- التبويب 4: المستودع ---
elif menu == "📦 المستودع":
    st.header("📦 إدارة الأصول وقطع الغيار")
    with st.form("inv_corporate"):
        c1, c2, c3 = st.columns(3)
        n, s, q = c1.text_input("اسم الصنف"), c2.number_input("سعر الوحدة $"), c3.number_input("الكمية المضافة", min_value=1)
        if st.form_submit_button("إضافة للمخزون الرسمي"):
            st.session_state.inv.loc[len(st.session_state.inv)] = [n, s, q]
            save_all(); st.rerun()
    st.dataframe(st.session_state.inv, use_container_width=True)

# --- التبويب 5: المالية ---
elif menu == "💰 التقارير المالية":
    st.header("💰 الإدارة المالية وتحليل الأرباح")
    df_f = st.session_state.db[st.session_state.db['الحالة']=='تم التسليم'].copy()
    if not df_f.empty:
        df_f['الشهر'] = pd.to_datetime(df_f['التاريخ']).dt.strftime('%Y-%m')
        for m in sorted(df_f['الشهر'].unique(), reverse=True):
            m_data = df_f[df_f['الشهر']==m]
            profit = m_data['التكلفة'].sum() - m_data['سعر_القطع'].sum()
            with st.expander(f"📊 كشف مالي لشهر: {m}"):
                st.markdown(f"<div class='profit-section'><h3>صافي ربح المركز: {profit}$</h3><h3>نصيب الشركاء (50% لكل شريك): {profit/2}$</h3></div>", unsafe_allow_html=True)
                st.dataframe(m_data[['ID','الزبون','الموديل','التكلفة']], use_container_width=True)
