import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. التصميم العصري الجديد (Modern Clean UI) ---
st.set_page_config(page_title="الحل للتقنية | Pro System", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    :root {
        --primary: #009688; /* لون تيل عصري */
        --secondary: #64748b; /* رمادي احترافي */
        --bg-light: #f8fafc;
        --white: #ffffff;
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: var(--bg-light); }
    
    /* تنسيق القائمة الجانبية الجديد */
    [data-testid="stSidebar"] {
        background-color: var(--white) !important;
        border-left: 1px solid #e2e8f0;
    }
    .sidebar-content { color: var(--secondary); }
    
    /* تنسيق كروت الإحصائيات العصرية */
    .modern-card {
        background: var(--white);
        padding: 20px;
        border-radius: 16px;
        box-shadow: var(--shadow);
        text-align: center;
        transition: transform 0.2s;
    }
    .modern-card:hover { transform: translateY(-3px); }
    .modern-card h3 { color: var(--secondary); font-size: 1rem; font-weight: 600; }
    .modern-card h2 { color: var(--primary); font-size: 2.5rem; font-weight: 700; margin: 10px 0; }
    
    /* تنسيق العناوين والأزرار */
    h1, h2 { color: #1e293b; }
    .stButton button {
        background: linear-gradient(to right, var(--primary), #0d9488);
        color: white; border: none; border-radius: 8px; font-weight: bold;
    }
    .stButton button:hover { opacity: 0.9; }
    
    /* تنسيق قسم المالية */
    .profit-highlight {
        background: #ecfdf5; border: 1px solid #a7f3d0;
        padding: 20px; border-radius: 12px; text-align: center;
        color: #065f46;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات (لم يتم لمسه) ---
DB_FILE = "master_db_v11.csv" # تحديث اسم الملف لضمان النسخة الجديدة
INV_FILE = "inventory_db_v11.csv"
IMG_DIR = "device_vault_v11"

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

# --- 3. محرك الطباعة الفولاذي (لم يتم لمسه) ---
def print_service(content_html):
    # هذا الكود هو الأضمن لعمل الطباعة بدون مشاكل
    js_code = f"""
    <div id="print-area" style="display:none;">{content_html}</div>
    <script>
        var content = document.getElementById('print-area').innerHTML;
        var win = window.open('', '', 'height=700,width=700');
        win.document.write('<html><head><title>Print Job</title>');
        win.document.write('<style>@import url("https://fonts.googleapis.com/css2?family=Cairo&display=swap"); body {{ font-family: "Cairo", sans-serif; direction: rtl; text-align: center; background: #fff; }} .box {{ border: 2px solid #000; padding: 20px; border-radius: 10px; display: inline-block; min-width: 300px; }} table {{ width: 100%; margin-top: 15px; border-collapse: collapse; }} td {{ text-align: right; padding: 8px; border-bottom: 1px solid #eee; }}</style>');
        win.document.write('</head><body><div class="box">');
        win.document.write(content);
        win.document.write('</div></body></html>');
        win.document.close();
        // انتظار إضافي لضمان تحميل الباركود
        win.onload = function() {{ setTimeout(function() {{ win.print(); win.close(); }}, 800); }};
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 4. نظام الحماية ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center; color:var(--primary);'>🔐 تسجيل الدخول - الحل للتقنية</h2>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول للنظام"):
            if u == "admin" and p == "123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("بيانات الدخول غير صحيحة")
    st.stop()

# --- 5. القائمة الجانبية العصرية ---
st.sidebar.markdown("<h2 style='text-align:center; color:#009688;'>💎 الحل للتقنية</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("تنقل بين الأقسام:", ["🏠 الرئيسية", "📥 استلام جهاز", "🔍 البحث والإدارة", "📦 المخزن", "💰 المالية"], label_visibility="collapsed")

# --- التبويب 1: الرئيسية ---
if menu == "🏠 الرئيسية":
    st.header("📊 نظرة عامة على النشاط")
    df = st.session_state.db
    c1, c2, c3, c4 = st.columns(4)
    
    # كروت عصرية جديدة
    with c1: st.markdown(f"<div class='modern-card'><h3>📦 إجمالي الأجهزة</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='modern-card'><h3>🛠️ قيد الصيانة</h3><h2 style='color:#f59e0b;'>{len(df[df['الحالة']=='تحت الصيانة'])}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='modern-card'><h3>✅ جاهز للتسليم</h3><h2 style='color:#10b981;'>{len(df[df['الحالة']=='جاهز'])}</h2></div>", unsafe_allow_html=True)
    cash = pd.to_numeric(df[df['الحالة']=='تم التسليم']['التكلفة']).sum()
    with c4: st.markdown(f"<div class='modern-card'><h3>💰 إجمالي الدخل</h3><h2 style='color:#3b82f6;'>{cash}$</h2></div>", unsafe_allow_html=True)

# --- التبويب 2: استلام جهاز ---
elif menu == "📥 استلام جهاز":
    st.header("📝 تسجيل جهاز جديد")
    st.info("قم بتعبئة بيانات الجهاز والزبون بدقة.")
    with st.form("new_entry_modern"):
        c1, c2 = st.columns(2)
        name = c1.text_input("👤 اسم الزبون")
        phone = c2.text_input("📞 رقم الهاتف")
        model = c1.text_input("📱 موديل الجهاز")
        cost = c2.number_input("💵 التكلفة المتوقعة $", min_value=0)
        issue = st.text_area("🔧 وصف العطل")
        notes = st.text_area("🗒️ ملاحظات الاستلام")
        img = st.file_uploader("📸 صورة الجهاز", type=['jpg','png'])
        if st.form_submit_button("تسجيل وحفظ"):
            new_id = len(st.session_state.db) + 1001
            path = os.path.join(IMG_DIR, f"{new_id}.jpg") if img else ""
            if img: with open(path, "wb") as f: f.write(img.getbuffer())
            st.session_state.db.loc[len(st.session_state.db)] = [new_id, name, phone, model, issue, cost, 0, "تحت الصيانة", datetime.now(), notes, path]
            save_all(); st.success(f"تم التسجيل بنجاح! ID: {new_id}")

# --- التبويب 3: البحث والإدارة ---
elif menu == "🔍 البحث والإدارة":
    st.header("🔍 إدارة الصيانة")
    search_id = st.query_params.get("id", "")
    q = st.text_input("ابحث عن: اسم، هاتف، أو ID", value=search_id)
    if q:
        df = st.session_state.db
        mask = df['ID'].astype(str).str.contains(q) | df['الزبون'].astype(str).str.contains(q) | df['الهاتف'].astype(str).str.contains(q)
        results = df[mask]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ معالجة: {row['الزبون']} | ID: {row['ID']}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown("### تحديث البيانات")
                    new_st = st.selectbox("حالة الجهاز", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"].index(row['الحالة']), key=f"s_{idx}")
                    p_list = ["بدون قطع"] + st.session_state.inv[st.session_state.inv['الكمية'] > 0]['القطعة'].tolist()
                    sel_p = st.selectbox("صرف قطعة من المخزن", p_list, key=f"p_{idx}")
                    if st.button("حفظ التغييرات", key=f"b_{idx}"):
                        if sel_p != "بدون قطع":
                            p_data = st.session_state.inv[st.session_state.inv['القطعة'] == sel_p].iloc[0]
                            st.session_state.db.at[idx, 'سعر_القطع'] += p_data['السعر']
                            st.session_state.inv.loc[st.session_state.inv['القطعة'] == sel_p, 'الكمية'] -= 1
                        st.session_state.db.at[idx, 'الحالة'] = new_st
                        save_all(); st.rerun()
                with c2:
                    st.markdown("### الطباعة والتوثيق")
                    if row['الصورة']: st.image(row['الصورة'], width=150)
                    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                    if st.button("🏷️ طباعة ستيكر (باركود)", key=f"stk_{idx}"):
                        print_service(f"<h3>الحل للتقنية</h3><b>{row['الزبون']}</b><br><img src='{qr}' width='110'><br>ID: {row['ID']}")
                    if st.button("📄 طباعة وصل (تفصيلي)", key=f"rec_{idx}"):
                        rec_html = f"<h2>وصل استلام</h2><hr><table><tr><td><b>المرجع:</b></td><td>{row['ID']}</td></tr><tr><td><b>العميل:</b></td><td>{row['الزبون']}</td></tr><tr><td><b>الجهاز:</b></td><td>{row['الموديل']}</td></tr><tr><td><b>العطل:</b></td><td>{row['العطل']}</td></tr><tr><td><b>التكلفة:</b></td><td>{row['التكلفة']}$</td></tr></table><p style='font-size:12px; margin-top:15px;'>تاريخ: {str(row['التاريخ'])[:16]}</p>"
                        print_service(rec_html)

# --- التبويب 4: المخزن ---
elif menu == "📦 المخزن":
    st.header("📦 مخزون قطع الغيار")
    with st.form("inv_mod"):
        c1, c2, c3 = st.columns(3)
        n, s, q = c1.text_input("القطعة"), c2.number_input("السعر $"), c3.number_input("الكمية", min_value=1)
        if st.form_submit_button("إضافة للمخزن"):
            st.session_state.inv.loc[len(st.session_state.inv)] = [n, s, q]
            save_all(); st.rerun()
    st.dataframe(st.session_state.inv, use_container_width=True)

# --- التبويب 5: المالية ---
elif menu == "💰 المالية":
    st.header("💹 التقارير المالية")
    df_f = st.session_state.db[st.session_state.db['الحالة']=='تم التسليم'].copy()
    if not df_f.empty:
        df_f['الشهر'] = pd.to_datetime(df_f['التاريخ']).dt.strftime('%Y-%m')
        for m in sorted(df_f['الشهر'].unique(), reverse=True):
            m_data = df_f[df_f['الشهر']==m]
            profit = m_data['التكلفة'].sum() - m_data['سعر_القطع'].sum()
            with st.expander(f"📅 تقرير شهر: {m}"):
                st.markdown(f"""
                <div class='profit-highlight'>
                    <h3>إجمالي صافي الربح: {profit}$</h3>
                    <h4>حصة الشريك الواحد (50%): {profit/2}$</h4>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(m_data[['ID','الزبون','التكلفة','سعر_القطع']], use_container_width=True)
