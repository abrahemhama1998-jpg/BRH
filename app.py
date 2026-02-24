import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. الإعدادات والجمالية ---
st.set_page_config(page_title="الحل للتقنية - PRO V10", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f8f9fa; }
    .metric-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-right: 5px solid #007bff;
        text-align: center; margin-bottom: 20px;
    }
    .profit-box {
        background: #e3f2fd; border: 1px solid #90caf9;
        padding: 15px; border-radius: 10px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات ---
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

# --- 3. محرك الطباعة المطور (لا يفتح نافذة منبثقة - يطبع فوراً) ---
def print_service(content_html):
    # كود جافا سكريبت يضمن الطباعة بعد تحميل الصور
    js_code = f"""
    <div id="print-area" style="display:none;">{content_html}</div>
    <script>
        var content = document.getElementById('print-area').innerHTML;
        var win = window.open('', '', 'height=700,width=700');
        win.document.write('<html><head><title>طباعة</title>');
        win.document.write('<style>@import url("https://fonts.googleapis.com/css2?family=Cairo&display=swap"); body {{ font-family: "Cairo", sans-serif; direction: rtl; text-align: center; }} .box {{ border: 2px solid #000; padding: 15px; border-radius: 10px; display: inline-block; min-width: 250px; }} table {{ width: 100%; margin-top: 10px; }} td {{ text-align: right; padding: 5px; border-bottom: 1px solid #eee; }}</style>');
        win.document.write('</head><body><div class="box">');
        win.document.write(content);
        win.document.write('</div></body></html>');
        win.document.close();
        win.onload = function() {{
            setTimeout(function() {{ win.print(); win.close(); }}, 700);
        }};
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 4. نظام الحماية ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🛡️ الحل للتقنية - تسجيل دخول")
    u, p = st.text_input("المستخدم"), st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "123":
            st.session_state.auth = True
            st.rerun()
        else: st.error("بيانات خاطئة!")
    st.stop()

# --- 5. القائمة ---
menu = st.sidebar.radio("القائمة الرئيسية", ["🏠 الرئيسية", "📥 استلام جديد", "🔍 البحث والإدارة", "📦 المخزن", "💰 المالية"])

# --- الرئيسية ---
if menu == "🏠 الرئيسية":
    st.header("📈 لوحة التحكم")
    df = st.session_state.db
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='metric-card'><h3>📦 الأجهزة</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card' style='border-right-color:#ffc107;'><h3>🛠️ صيانة</h3><h2>{len(df[df['الحالة']=='تحت الصيانة'])}</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card' style='border-right-color:#28a745;'><h3>✅ جاهز</h3><h2>{len(df[df['الحالة']=='جاهز'])}</h2></div>", unsafe_allow_html=True)
    cash = pd.to_numeric(df[df['الحالة']=='تم التسليم']['التكلفة']).sum()
    c4.markdown(f"<div class='metric-card' style='border-right-color:#17a2b8;'><h3>💰 الدخل</h3><h2>{cash}$</h2></div>", unsafe_allow_html=True)

# --- استلام جديد ---
elif menu == "📥 استلام جديد":
    st.header("📝 تسجيل استلام")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name, phone = c1.text_input("الزبون"), c2.text_input("الهاتف")
        model, cost = c1.text_input("الموديل"), c2.number_input("التكلفة $", min_value=0)
        issue = st.text_area("وصف العطل")
        notes = st.text_area("ملاحظات (خدوش أو غيرها)")
        img = st.file_uploader("صورة الجهاز", type=['jpg','png'])
        if st.form_submit_button("حفظ الجهاز"):
            new_id = len(st.session_state.db) + 1001
            path = os.path.join(IMG_DIR, f"{new_id}.jpg") if img else ""
            if img:
                with open(path, "wb") as f: f.write(img.getbuffer())
            new_row = [new_id, name, phone, model, issue, cost, 0, "تحت الصيانة", datetime.now(), notes, path]
            st.session_state.db.loc[len(st.session_state.db)] = new_row
            save_all(); st.success(f"تم الحفظ ID: {new_id}")

# --- البحث والإدارة ---
elif menu == "🔍 البحث والإدارة":
    search_id = st.query_params.get("id", "")
    q = st.text_input("🔎 ابحث (اسم، هاتف، ID)", value=search_id)
    if q:
        df = st.session_state.db
        mask = df['ID'].astype(str).str.contains(q) | df['الزبون'].astype(str).str.contains(q) | df['الهاتف'].astype(str).str.contains(q)
        results = df[mask]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - ID: {row['ID']}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    new_st = st.selectbox("الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"].index(row['الحالة']), key=f"st_{idx}")
                    p_list = ["بدون قطع"] + st.session_state.inv[st.session_state.inv['الكمية'] > 0]['القطعة'].tolist()
                    sel_p = st.selectbox("إضافة قطعة", p_list, key=f"p_{idx}")
                    if st.button("حفظ التعديلات", key=f"save_{idx}"):
                        if sel_p != "بدون قطع":
                            p_info = st.session_state.inv[st.session_state.inv['القطعة'] == sel_p].iloc[0]
                            st.session_state.db.at[idx, 'سعر_القطع'] += p_info['السعر']
                            st.session_state.inv.loc[st.session_state.inv['القطعة'] == sel_p, 'الكمية'] -= 1
                        st.session_state.db.at[idx, 'الحالة'] = new_st
                        save_all(); st.rerun()
                with c2:
                    if row['الصورة']: st.image(row['الصورة'], width=100)
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                    
                    if st.button("🏷️ طباعة ستيكر", key=f"stk_{idx}"):
                        stk_html = f"<h3>الحل للتقنية</h3><b>{row['الزبون']}</b><br><br><img src='{qr_url}' width='120'><br><br>ID: {row['ID']}"
                        print_service(stk_html)
                    
                    if st.button("📄 طباعة وصل", key=f"rec_{idx}"):
                        rec_html = f"""
                        <h2 style='border-bottom:2px solid #000;'>وصل استلام صيانة</h2>
                        <table>
                            <tr><td><b>رقم الجهاز:</b></td><td>{row['ID']}</td></tr>
                            <tr><td><b>الزبون:</b></td><td>{row['الزبون']}</td></tr>
                            <tr><td><b>الجهاز:</b></td><td>{row['الموديل']}</td></tr>
                            <tr><td><b>العطل:</b></td><td>{row['العطل']}</td></tr>
                            <tr><td><b>التكلفة:</b></td><td>{row['التكلفة']}$</td></tr>
                            <tr><td><b>ملاحظات:</b></td><td>{row['ملاحظات']}</td></tr>
                        </table>
                        <p style='margin-top:20px; font-size:12px;'>التاريخ: {str(row['التاريخ'])[:16]}</p>
                        """
                        print_service(rec_html)

# --- المخزن ---
elif menu == "📦 المخزن":
    st.header("📦 إدارة المخزن")
    with st.form("inv"):
        c1, c2, c3 = st.columns(3)
        n, s, q = c1.text_input("القطعة"), c2.number_input("السعر $"), c3.number_input("الكمية", min_value=1)
        if st.form_submit_button("إضافة"):
            new_p = pd.DataFrame([[n, s, q]], columns=st.session_state.inv.columns)
            st.session_state.inv = pd.concat([st.session_state.inv, new_p], ignore_index=True)
            save_all(); st.rerun()
    
    for idx, item in st.session_state.inv.iterrows():
        c1, c2, c3 = st.columns([2,1,1])
        c1.write(f"**{item['القطعة']}**")
        color = "green" if item['الكمية'] > 5 else "red"
        c3.markdown(f"<span style='color:{color};'>الكمية: {item['الكمية']}</span>", unsafe_allow_html=True)

# --- المالية ---
elif menu == "💰 المالية":
    st.header("💰 تقارير الأرباح والشراكة")
    df_f = st.session_state.db[st.session_state.db['الحالة']=='تم التسليم'].copy()
    if not df_f.empty:
        df_f['الشهر'] = pd.to_datetime(df_f['التاريخ']).dt.strftime('%Y-%m')
        for m in sorted(df_f['الشهر'].unique(), reverse=True):
            m_data = df_f[df_f['الشهر']==m]
            profit = m_data['التكلفة'].sum() - m_data['سعر_القطع'].sum()
            with st.expander(f"📅 شهر {m} (الربح: {profit}$)", expanded=True):
                st.markdown(f"<div class='profit-box'><h3>صافي الربح: {profit}$</h3><h4>حصة الشريك الواحد: {profit/2}$</h4></div>", unsafe_allow_html=True)
                st.dataframe(m_data[['ID','الزبون','الموديل','التكلفة']])
