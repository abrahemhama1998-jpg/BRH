import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. الإعدادات والتصميم (نفس النمط الاحترافي) ---
st.set_page_config(page_title="الحل للتقنية | Enterprise", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    :root { --corporate-blue: #1e3a8a; --corporate-light: #f8fafc; --border-color: #e2e8f0; }
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: var(--corporate-light); }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    .system-header {
        background-color: white; padding: 20px 30px; border-radius: 8px;
        border-bottom: 4px solid var(--corporate-blue); box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;
    }
    div.row-widget.stRadio > div {
        display: flex; flex-direction: row; justify-content: center;
        background: white; padding: 10px; border-radius: 8px; gap: 15px;
    }
    .stButton > button { background-color: var(--corporate-blue); color: white; border-radius: 6px; font-weight: bold; width: 100%; }
    .last-received-label { background: #e0f2fe; padding: 5px 15px; border-radius: 5px; color: #0369a1; font-weight: bold; margin-bottom: 10px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات ---
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

def print_service(content_html):
    js_code = f"""
    <div id="print-area" style="display:none;">{content_html}</div>
    <script>
        var content = document.getElementById('print-area').innerHTML;
        var win = window.open('', '', 'height=700,width=700');
        win.document.write('<html><head><title>Print System</title>');
        win.document.write('<style>@import url("https://fonts.googleapis.com/css2?family=Cairo&display=swap"); body {{ font-family: "Cairo", sans-serif; direction: rtl; text-align: center; margin: 0; padding: 10px; }} .box {{ border: 2px solid #000; padding: 15px; border-radius: 10px; display: inline-block; min-width: 250px; }} table {{ width: 100%; margin-top: 10px; border-collapse: collapse; }} td {{ text-align: right; padding: 5px; border-bottom: 1px solid #eee; }} img {{ margin: 10px 0; }}</style>');
        win.document.write('</head><body><div class="box">');
        win.document.write(content);
        win.document.write('</div></body></html>');
        win.document.close();
        win.onload = function() {{ setTimeout(function() {{ win.print(); win.close(); }}, 1000); }};
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 4. حماية النظام ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<div class='system-header' style='justify-content:center;'><h1>🛡️ نظام الإدارة المركزي - الحل للتقنية</h1></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container(border=True):
            u, p = st.text_input("معرف الموظف"), st.text_input("رمز المرور", type="password")
            if st.button("تسجيل الدخول"):
                if u == "admin" and p == "123": st.session_state.auth = True; st.rerun()
    st.stop()

# --- 5. الواجهة الرئيسية ---
st.markdown("<div class='system-header'><h1>المركز الرئيسي | الحل للتقنية</h1><span style='color:gray;'>نظام إدارة الأصول ERP</span></div>", unsafe_allow_html=True)
menu = st.radio("القائمة:", ["📊 لوحة المعلومات", "📥 تسجيل الأجهزة", "🔍 المتابعة والعمليات", "📦 المستودع العام", "💰 الإدارة المالية"], horizontal=True, label_visibility="collapsed")
st.write("---")

# --- لوحة المعلومات ---
if menu == "📊 لوحة المعلومات":
    df = st.session_state.db
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='pro-card'><h3>إجمالي المعاملات</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='pro-card'><h3>تحت الصيانة</h3><h2>{len(df[df['الحالة']=='تحت الصيانة'])}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='pro-card'><h3>جاهز للتسليم</h3><h2>{len(df[df['الحالة']=='جاهز'])}</h2></div>", unsafe_allow_html=True)
    cash = pd.to_numeric(df[df['الحالة']=='تم التسليم']['التكلفة']).sum()
    with c4: st.markdown(f"<div class='pro-card'><h3>الإيرادات</h3><h2>{cash}$</h2></div>", unsafe_allow_html=True)

# --- تسجيل الأجهزة ---
elif menu == "📥 تسجيل الأجهزة":
    st.subheader("إدراج أصل جديد")
    with st.container(border=True):
        with st.form("pro_add"):
            c1, c2 = st.columns(2)
            name, phone = c1.text_input("الزبون"), c2.text_input("الهاتف")
            model, cost = c1.text_input("الموديل"), c2.number_input("التكلفة $", min_value=0)
            issue, notes = st.text_area("العطل"), st.text_area("ملاحظات")
            img = st.file_uploader("الصورة", type=['jpg','png'])
            if st.form_submit_button("إعتماد"):
                new_id = len(st.session_state.db) + 1001
                path = os.path.join(IMG_DIR, f"{new_id}.jpg") if img else ""
                if img:
                    with open(path, "wb") as f: f.write(img.getbuffer())
                st.session_state.db.loc[len(st.session_state.db)] = [new_id, name, phone, model, issue, cost, 0, "تحت الصيانة", datetime.now(), notes, path]
                save_all(); st.success(f"تم التسجيل: {new_id}")

# --- المتابعة والعمليات (التعديل المطلوب هنا) ---
elif menu == "🔍 المتابعة والعمليات":
    st.subheader("🔍 البحث والمتابعة")
    q = st.text_input("ابحث بالاسم، الهاتف، أو ID...")
    
    # تحديد البيانات التي ستعرض (إما نتائج البحث أو آخر 10 مستلمات)
    df_all = st.session_state.db
    if q:
        mask = df_all['ID'].astype(str).str.contains(q) | df_all['الزبون'].astype(str).str.contains(q) | df_all['الهاتف'].astype(str).str.contains(q)
        display_df = df_all[mask]
        st.write(f"🔍 نتائج البحث عن: {q}")
    else:
        st.markdown("<div class='last-received-label'>🕒 آخر 10 أجهزة تم استلامها</div>", unsafe_allow_html=True)
        # جلب آخر 10 صفوف وعكس الترتيب ليظهر الأحدث أولاً
        display_df = df_all.tail(10).iloc[::-1]

    # عرض الأجهزة في شكل بطاقات منسدلة
    if not display_df.empty:
        for idx, row in display_df.iterrows():
            with st.expander(f"📱 {row['الزبون']} | {row['الموديل']} | ID: {row['ID']}"):
                ca, cb = st.columns([2, 1])
                with ca:
                    # ميزات التعديل
                    new_st = st.selectbox("الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], 
                                         index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"].index(row['الحالة']), key=f"s_{idx}")
                    p_list = ["بدون قطع"] + st.session_state.inv[st.session_state.inv['الكمية'] > 0]['القطعة'].tolist()
                    sel_p = st.selectbox("صرف قطعة", p_list, key=f"p_{idx}")
                    
                    if st.button("تحديث السجل", key=f"b_{idx}"):
                        if sel_p != "بدون قطع":
                            p_info = st.session_state.inv[st.session_state.inv['القطعة'] == sel_p].iloc[0]
                            st.session_state.db.at[idx, 'سعر_القطع'] += p_info['السعر']
                            st.session_state.inv.loc[st.session_state.inv['القطعة'] == sel_p, 'الكمية'] -= 1
                        st.session_state.db.at[idx, 'الحالة'] = new_st
                        save_all(); st.rerun()
                with cb:
                    qr_link = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=ID:{row['ID']}"
                    if st.button("🏷️ طباعة ستيكر", key=f"qr_{idx}"):
                        print_service(f"<h2>{row['الزبون']}</h2><img src='{qr_link}' width='120'><br>ID: {row['ID']}")
                    if st.button("📄 طباعة إيصال", key=f"pr_{idx}"):
                        receipt = f"<h1>الحل للتقنية</h1><h4>0916206100</h4><hr><h3>بيانات الجهاز</h3><table><tr><td>ID:</td><td>{row['ID']}</td></tr><tr><td>العميل:</td><td>{row['الزبون']}</td></tr><tr><td>الجهاز:</td><td>{row['الموديل']}</td></tr><tr><td>العطل:</td><td>{row['العطل']}</td></tr></table><hr><p style='color:red; font-weight:bold;'>نحن غير مسؤولين عن الجهاز بعد 90 يوماً.</p>"
                        print_service(receipt)
    else:
        st.warning("لا توجد بيانات لعرضها.")

# --- الأقسام الأخرى ---
elif menu == "📦 المستودع العام":
    st.subheader("إدارة المخزن")
    with st.form("inv"):
        c1, c2, c3 = st.columns(3)
        n, s, q = c1.text_input("القطعة"), c2.number_input("السعر $"), c3.number_input("الكمية", min_value=1)
        if st.form_submit_button("إضافة"):
            st.session_state.inv.loc[len(st.session_state.inv)] = [n, s, q]
            save_all(); st.rerun()
    st.dataframe(st.session_state.inv, use_container_width=True)

elif menu == "💰 الإدارة المالية":
    st.subheader("الأرباح والتقارير")
    df_f = st.session_state.db[st.session_state.db['الحالة']=='تم التسليم'].copy()
    if not df_f.empty:
        df_f['الشهر'] = pd.to_datetime(df_f['التاريخ']).dt.strftime('%Y-%m')
        for m in sorted(df_f['الشهر'].unique(), reverse=True):
            m_data = df_f[df_f['الشهر']==m]
            profit = m_data['التكلفة'].sum() - m_data['سعر_القطع'].sum()
            with st.expander(f"كشف شهر {m}"):
                st.info(f"الربح: {profit}$ | الشريك: {profit/2}$")
                st.dataframe(m_data[['ID','الزبون','التكلفة']], use_container_width=True)
