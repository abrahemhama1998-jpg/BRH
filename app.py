import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. الإعدادات والتصميم الاحترافي ---
st.set_page_config(page_title="الحل للتقنية - الإصدار النهائي", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f4f7f9; }
    .metric-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #007bff;
        text-align: center;
    }
    .profit-box {
        background: #e8f5e9; border: 1px solid #c3e6cb;
        padding: 15px; border-radius: 10px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قواعد البيانات ---
DB_FILE = "devices_master_v9.csv"
INV_FILE = "inventory_master_v9.csv"
IMG_DIR = "device_images"

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

# --- 3. محرك الطباعة الذكي (Smart Print Engine) ---
def smart_print(html_content):
    # كود جافا سكريبت متطور ينتظر تحميل الصور قبل الطباعة
    js_code = f"""
    <script>
    var printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>طباعة - الحل للتقنية</title>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
                    body {{ font-family: 'Cairo', sans-serif; direction: rtl; text-align: center; padding: 20px; }}
                    .container {{ border: 2px solid #000; padding: 15px; border-radius: 10px; display: inline-block; min-width: 250px; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                    td {{ padding: 5px; border-bottom: 1px solid #eee; text-align: right; }}
                    .header {{ font-weight: bold; font-size: 1.2em; border-bottom: 2px solid #000; padding-bottom: 5px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    {html_content}
                </div>
                <script>
                    window.onload = function() {{
                        setTimeout(function() {{
                            window.print();
                            window.close();
                        }}, 500);
                    }};
                </script>
            </body>
        </html>
    `);
    printWindow.document.close();
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 4. نظام الحماية ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 تسجيل دخول المنظومة")
    u, p = st.text_input("اسم المستخدم"), st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "123":
            st.session_state.auth = True
            st.rerun()
        else: st.error("خطأ!")
    st.stop()

# --- 5. القائمة الجانبية ---
menu = st.sidebar.radio("القائمة", ["🏠 الرئيسية", "📥 استلام الأجهزة", "🔍 البحث والإدارة", "📦 المخزن", "💰 المالية"])

# --- التبويب: الرئيسية ---
if menu == "🏠 الرئيسية":
    st.header("📈 لوحة التحكم")
    df = st.session_state.db
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي الأجهزة", len(df))
    c2.metric("قيد الصيانة", len(df[df['الحالة']=='تحت الصيانة']))
    c3.metric("جاهز", len(df[df['الحالة']=='جاهز']))
    profit = pd.to_numeric(df[df['الحالة']=='تم التسليم']['التكلفة']).sum()
    c4.metric("إجمالي الدخل", f"{profit}$")

# --- التبويب: استلام الأجهزة ---
elif menu == "📥 استلام الأجهزة":
    st.header("📝 تسجيل استلام")
    with st.form("add", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name, phone = col1.text_input("الزبون"), col2.text_input("الهاتف")
        model, cost = col1.text_input("الموديل"), col2.number_input("التكلفة $", min_value=0)
        issue = st.text_area("وصف العطل")
        notes = st.text_area("ملاحظات")
        img = st.file_uploader("صورة الجهاز", type=['jpg','png'])
        if st.form_submit_button("حفظ الجهاز"):
            new_id = len(st.session_state.db) + 1001
            path = os.path.join(IMG_DIR, f"{new_id}.jpg") if img else ""
            if img:
                with open(path, "wb") as f: f.write(img.getbuffer())
            new_row = [new_id, name, phone, model, issue, cost, 0, "تحت الصيانة", datetime.now(), notes, path]
            st.session_state.db.loc[len(st.session_state.db)] = new_row
            save_all()
            st.success(f"تم الحفظ ID: {new_id}")

# --- التبويب: البحث والإدارة ---
elif menu == "🔍 البحث والإدارة":
    search_id = st.query_params.get("id", "")
    q = st.text_input("🔎 ابحث (اسم، ID، هاتف)", value=search_id)
    if q:
        df = st.session_state.db
        mask = df['ID'].astype(str).str.contains(q) | df['الزبون'].astype(str).str.contains(q) | df['الهاتف'].astype(str).str.contains(q)
        results = df[mask]
        for idx, row in results.iterrows():
            with st.expander(f"📱 {row['الزبون']} - ID: {row['ID']}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    new_st = st.selectbox("الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"].index(row['الحالة']), key=f"s_{idx}")
                    p_list = ["بدون قطع"] + st.session_state.inv[st.session_state.inv['الكمية'] > 0]['القطعة'].tolist()
                    sel_p = st.selectbox("إضافة قطعة", p_list, key=f"p_{idx}")
                    if st.button("حفظ التعديلات", key=f"b_{idx}"):
                        if sel_p != "بدون قطع":
                            p_data = st.session_state.inv[st.session_state.inv['القطعة'] == sel_p].iloc[0]
                            st.session_state.db.at[idx, 'سعر_القطع'] += p_data['السعر']
                            st.session_state.inv.loc[st.session_state.inv['القطعة'] == sel_p, 'الكمية'] -= 1
                        st.session_state.db.at[idx, 'الحالة'] = new_st
                        save_all(); st.rerun()
                
                with c2:
                    if row['الصورة']: st.image(row['الصورة'], width=100)
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                    
                    # طباعة الستيكر (اسم + باركود فقط)
                    if st.button("🏷️ طباعة ستيكر", key=f"stk_{idx}"):
                        stk_html = f"<div class='header'>الحل للتقنية</div><br><b>{row['الزبون']}</b><br><br><img src='{qr_url}' width='120'><br><br>ID: {row['ID']}"
                        smart_print(stk_html)
                    
                    # طباعة الوصل (معلومات كاملة بدون باركود)
                    if st.button("📄 طباعة الوصل", key=f"rec_{idx}"):
                        rec_html = f"""
                        <div class='header'>وصل استلام جهاز</div>
                        <table>
                            <tr><td>رقم الجهاز:</td><td>{row['ID']}</td></tr>
                            <tr><td>الزبون:</td><td>{row['الزبون']}</td></tr>
                            <tr><td>الموديل:</td><td>{row['الموديل']}</td></tr>
                            <tr><td>العطل:</td><td>{row['العطل']}</td></tr>
                            <tr><td>التاريخ:</td><td>{str(row['التاريخ'])[:10]}</td></tr>
                            <tr><td style='font-weight:bold;'>المبلغ:</td><td style='font-weight:bold;'>{row['التكلفة']} $</td></tr>
                        </table>
                        <p style='font-size:12px; margin-top:15px;'>شكراً لثقتكم بمحل الحل للتقنية</p>
                        """
                        smart_print(rec_html)

# --- التبويب: المخزن ---
elif menu == "📦 المخزن":
    st.header("📦 إدارة القطع")
    with st.form("inv"):
        c1, c2, c3 = st.columns(3)
        n, s, q = c1.text_input("القطعة"), c2.number_input("السعر $"), c3.number_input("الكمية", min_value=1)
        if st.form_submit_button("إضافة"):
            st.session_state.inv.loc[len(st.session_state.inv)] = [n, s, q]
            save_all(); st.rerun()
    
    # عرض المخزن بألوان ذكية
    for idx, item in st.session_state.inv.iterrows():
        c1, c2, c3 = st.columns([2,1,1])
        c1.write(f"**{item['القطعة']}**")
        c2.write(f"{item['السعر']} $")
        color = "green" if item['الكمية'] > 10 else "orange" if item['الكمية'] > 0 else "red"
        c3.markdown(f"<span style='color:{color}; font-weight:bold;'>الكمية: {item['الكمية']}</span>", unsafe_allow_html=True)

# --- التبويب: المالية ---
elif menu == "💰 المالية":
    st.header("💰 تقرير الأرباح")
    df_f = st.session_state.db[st.session_state.db['الحالة']=='تم التسليم'].copy()
    if not df_f.empty:
        df_f['الشهر'] = df_f['التاريخ'].dt.strftime('%Y-%m')
        for m in df_f['الشهر'].unique():
            m_data = df_f[df_f['الشهر']==m]
            net = m_data['التكلفة'].sum() - m_data['سعر_القطع'].sum()
            with st.expander(f"📅 شهر: {m} (الربح: {net}$)"):
                st.markdown(f"<div class='profit-box'><h4>صافي ربح الشهر: {net}$</h4><h5>حصة الشريك (50%): {net/2}$</h5></div>", unsafe_allow_html=True)
                st.dataframe(m_data[['ID','الزبون','التكلفة','سعر_القطع']])
