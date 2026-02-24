import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. تصميم الواجهة الاحترافية العليا (Premium Horizontal UI) ---
st.set_page_config(page_title="الحل للتقنية | Enterprise", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    :root {
        --corporate-blue: #1e3a8a;
        --corporate-light: #f8fafc;
        --border-color: #e2e8f0;
    }

    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: var(--corporate-light); }
    
    /* إخفاء الشريط الجانبي وزر الفتح نهائياً */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    
    /* ترويسة النظام (الهيدر) */
    .system-header {
        background-color: white;
        padding: 20px 30px;
        border-radius: 8px;
        border-bottom: 4px solid var(--corporate-blue);
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .system-header h1 { margin: 0; color: var(--corporate-blue); font-size: 1.8rem; font-weight: 700; }
    
    /* تنسيق أزرار التنقل الأفقية (الراديو) لتبدو كشريط احترافي */
    div.row-widget.stRadio > div {
        display: flex;
        flex-direction: row;
        justify-content: center;
        background: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        gap: 15px;
    }
    div.row-widget.stRadio > div > label {
        background-color: var(--corporate-light);
        padding: 10px 25px;
        border-radius: 6px;
        border: 1px solid var(--border-color);
        cursor: pointer;
        transition: all 0.2s ease;
    }
    div.row-widget.stRadio > div > label:hover {
        background-color: #eff6ff;
        border-color: #bfdbfe;
    }
    
    /* كروت البيانات والإحصائيات */
    .pro-card {
        background: white;
        padding: 25px;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        border-right: 5px solid var(--corporate-blue);
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        text-align: center;
    }
    .pro-card h3 { color: #64748b; font-size: 1rem; margin-bottom: 10px; font-weight: 600; }
    .pro-card h2 { color: #0f172a; font-size: 2.5rem; font-weight: 700; margin: 0; }
    
    /* الأزرار العامة */
    .stButton > button {
        background-color: var(--corporate-blue);
        color: white; border-radius: 6px; border: none; font-weight: bold; width: 100%;
    }
    .stButton > button:hover { opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات (مستقر وآمن 100%) ---
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

# --- 3. محرك الطباعة (تم الحفاظ عليه كما هو) ---
def print_service(content_html):
    js_code = f"""
    <div id="print-area" style="display:none;">{content_html}</div>
    <script>
        var content = document.getElementById('print-area').innerHTML;
        var win = window.open('', '', 'height=700,width=700');
        win.document.write('<html><head><title>Print System</title>');
        win.document.write('<style>@import url("https://fonts.googleapis.com/css2?family=Cairo&display=swap"); body {{ font-family: "Cairo", sans-serif; direction: rtl; text-align: center; }} .box {{ border: 2px solid #000; padding: 20px; border-radius: 10px; display: inline-block; min-width: 280px; }} table {{ width: 100%; margin-top: 15px; border-collapse: collapse; }} td {{ text-align: right; padding: 8px; border-bottom: 1px solid #eee; }}</style>');
        win.document.write('</head><body><div class="box">');
        win.document.write(content);
        win.document.write('</div></body></html>');
        win.document.close();
        win.onload = function() {{ setTimeout(function() {{ win.print(); win.close(); }}, 800); }};
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 4. حماية النظام (تسجيل الدخول) ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<div class='system-header' style='justify-content:center;'><h1>🛡️ نظام الإدارة المركزي - الحل للتقنية</h1></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container(border=True):
            u = st.text_input("معرف الموظف")
            p = st.text_input("رمز المرور", type="password")
            if st.button("تسجيل الدخول"):
                if u == "admin" and p == "123":
                    st.session_state.auth = True; st.rerun()
                else: st.error("بيانات غير صحيحة")
    st.stop()

# --- 5. الترويسة وشريط التنقل الأفقي ---
st.markdown("<div class='system-header'><h1>المركز الرئيسي | الحل للتقنية</h1><span style='color:gray;'>نظام إدارة الأصول ERP</span></div>", unsafe_allow_html=True)

menu = st.radio(
    "القائمة الإدارية:",
    ["📊 لوحة المعلومات", "📥 تسجيل الأجهزة", "🔍 المتابعة والعمليات", "📦 المستودع العام", "💰 الإدارة المالية"],
    horizontal=True,
    label_visibility="collapsed"
)

st.write("---")

# --- التبويب 1: لوحة المعلومات ---
if menu == "📊 لوحة المعلومات":
    df = st.session_state.db
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='pro-card'><h3>إجمالي المعاملات</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='pro-card' style='border-right-color:#eab308;'><h3>قيد المعالجة</h3><h2>{len(df[df['الحالة']=='تحت الصيانة'])}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='pro-card' style='border-right-color:#22c55e;'><h3>مكتمل وجاهز</h3><h2>{len(df[df['الحالة']=='جاهز'])}</h2></div>", unsafe_allow_html=True)
    cash = pd.to_numeric(df[df['الحالة']=='تم التسليم']['التكلفة']).sum()
    with c4: st.markdown(f"<div class='pro-card' style='border-right-color:#3b82f6;'><h3>الإيرادات المحققة</h3><h2>{cash}$</h2></div>", unsafe_allow_html=True)

# --- التبويب 2: الاستلام ---
elif menu == "📥 تسجيل الأجهزة":
    st.subheader("إدراج أصل جديد في النظام")
    with st.container(border=True):
        with st.form("professional_add"):
            c1, c2 = st.columns(2)
            name = c1.text_input("الاسم الرباعي للعميل")
            phone = c2.text_input("رقم التواصل")
            model = c1.text_input("نوع وموديل الجهاز")
            cost = c2.number_input("التكلفة التقديرية (دولار)", min_value=0)
            issue = st.text_area("التشخيص الفني للعطل")
            notes = st.text_area("ملاحظات إضافية (حالة الهيكل، الملحقات)")
            img = st.file_uploader("إرفاق صورة فوتوغرافية", type=['jpg','png'])
            
            if st.form_submit_button("إعتماد وتسجيل البيانات"):
                new_id = len(st.session_state.db) + 1001
                path = os.path.join(IMG_DIR, f"{new_id}.jpg") if img else ""
                if img:
                    with open(path, "wb") as f: f.write(img.getbuffer())
                st.session_state.db.loc[len(st.session_state.db)] = [new_id, name, phone, model, issue, cost, 0, "تحت الصيانة", datetime.now(), notes, path]
                save_all(); st.success(f"تم إنشاء السجل بنجاح. رقم المرجع: {new_id}")

# --- التبويب 3: البحث ---
elif menu == "🔍 المتابعة والعمليات":
    st.subheader("محرك البحث المتقدم والإدارة")
    q = st.text_input("أدخل معرف الجهاز (ID) أو رقم الهاتف أو اسم العميل للبحث...")
    if q:
        df = st.session_state.db
        mask = df['ID'].astype(str).str.contains(q) | df['الزبون'].astype(str).str.contains(q) | df['الهاتف'].astype(str).str.contains(q)
        res = df[mask]
        for idx, row in res.iterrows():
            with st.expander(f"ملف العميل: {row['الزبون']} | المرجع: {row['ID']}"):
                ca, cb = st.columns([2, 1])
                with ca:
                    new_st = st.selectbox("الحالة التشغيلية", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"].index(row['الحالة']), key=f"s_{idx}")
                    p_list = ["بدون قطع غيار"] + st.session_state.inv[st.session_state.inv['الكمية'] > 0]['القطعة'].tolist()
                    sel_p = st.selectbox("صرف قطعة من المستودع", p_list, key=f"p_{idx}")
                    if st.button("حفظ الإجراءات", key=f"b_{idx}"):
                        if sel_p != "بدون قطع غيار":
                            p_info = st.session_state.inv[st.session_state.inv['القطعة'] == sel_p].iloc[0]
                            st.session_state.db.at[idx, 'سعر_القطع'] += p_info['السعر']
                            st.session_state.inv.loc[st.session_state.inv['القطعة'] == sel_p, 'الكمية'] -= 1
                        st.session_state.db.at[idx, 'الحالة'] = new_st
                        save_all(); st.rerun()
                with cb:
                    if row['الصورة']: st.image(row['الصورة'], width=120)
                    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={row['ID']}"
                    if st.button("🏷️ طباعة الباركود", key=f"qr_{idx}"):
                        print_service(f"<h3>الحل للتقنية</h3><b>{row['الزبون']}</b><br><img src='{qr}' width='110'><br>REF: {row['ID']}")
                    if st.button("📄 طباعة إيصال", key=f"pr_{idx}"):
                        print_service(f"<h2>إيصال استلام</h2><hr>رقم المرجع: <b>{row['ID']}</b><br>العميل: {row['الزبون']}<br>النوع: {row['الموديل']}<br>التكلفة: {row['التكلفة']}$")

# --- التبويب 4: المخزن ---
elif menu == "📦 المستودع العام":
    st.subheader("إدارة مخزون قطع الغيار")
    with st.container(border=True):
        with st.form("inv_form"):
            c1, c2, c3 = st.columns(3)
            n = c1.text_input("اسم الصنف")
            s = c2.number_input("تكلفة الوحدة (دولار)", min_value=0.0)
            q = c3.number_input("الكمية الواردة", min_value=1)
            if st.form_submit_button("إضافة إلى العهدة"):
                st.session_state.inv.loc[len(st.session_state.inv)] = [n, s, q]
                save_all(); st.rerun()
    st.dataframe(st.session_state.inv, use_container_width=True)

# --- التبويب 5: المالية ---
elif menu == "💰 الإدارة المالية":
    st.subheader("التقارير والكشوفات المالية")
    df_f = st.session_state.db[st.session_state.db['الحالة']=='تم التسليم'].copy()
    if not df_f.empty:
        df_f['الشهر'] = pd.to_datetime(df_f['التاريخ']).dt.strftime('%Y-%m')
        for m in sorted(df_f['الشهر'].unique(), reverse=True):
            m_data = df_f[df_f['الشهر']==m]
            profit = m_data['التكلفة'].sum() - m_data['سعر_القطع'].sum()
            with st.expander(f"التقرير المالي لشهر: {m}"):
                st.markdown(f"""
                <div style='background: white; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 15px;'>
                    <h3 style='color: #1e3a8a; margin:0;'>إجمالي صافي الأرباح: {profit}$</h3>
                    <h4 style='color: #64748b; margin-top:5px;'>استحقاق الشريك (50%): {profit/2}$</h4>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(m_data[['ID','الزبون','التكلفة', 'سعر_القطع']], use_container_width=True)
