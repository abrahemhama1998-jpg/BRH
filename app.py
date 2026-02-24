import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. الإعدادات والتصميم الاحترافي ---
st.set_page_config(page_title="الحل للتقنية - PRO V8", layout="wide")

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
        background: #d4edda; border: 1px solid #c3e6cb;
        padding: 15px; border-radius: 10px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قواعد البيانات ---
DB_FILE = "devices_pro_v8.csv"
INV_FILE = "inventory_pro_v8.csv"
IMG_DIR = "device_images"

if not os.path.exists(IMG_DIR): os.makedirs(IMG_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['التاريخ'] = pd.to_datetime(df['التاريخ'], errors='coerce')
        # تنظيف البيانات فور تحميلها لضمان عمل البحث
        for col in ['الزبون', 'الهاتف', 'الموديل', 'ملاحظات', 'الحالة']:
            df[col] = df[col].fillna('')
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "ملاحظات", "الصورة"])

def load_inv():
    if os.path.exists(INV_FILE): return pd.read_csv(INV_FILE)
    return pd.DataFrame(columns=["القطعة", "السعر", "الكمية"])

# تخزين البيانات في الجلسة
if 'db' not in st.session_state: st.session_state.db = load_data()
if 'inv' not in st.session_state: st.session_state.inv = load_inv()

def save_all():
    st.session_state.db.to_csv(DB_FILE, index=False)
    st.session_state.inv.to_csv(INV_FILE, index=False)

# --- 3. نظام الحماية ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 بوابة الوصول - الحل للتقنية")
    user = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("تسجيل الدخول"):
        if user == "admin" and password == "123":
            st.session_state.auth = True
            st.rerun()
        else: st.error("بيانات غير صحيحة")
    st.stop()

# --- 4. القائمة الجانبية ---
menu = st.sidebar.radio("القائمة الرئيسية", ["🏠 الرئيسية", "📥 استلام الأجهزة", "🔍 البحث والإدارة", "📦 المخزن", "💰 قسم المالية"])

# --- التبويب 1: الرئيسية ---
if menu == "🏠 الرئيسية":
    st.header("📊 ملخص النشاط اليومي")
    df = st.session_state.db
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><h3>📦 الكلي</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card' style='border-top-color:#ffc107;'><h3>🛠️ صيانة</h3><h2>{len(df[df['الحالة']=='تحت الصيانة'])}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-card' style='border-top-color:#28a745;'><h3>✅ جاهز</h3><h2>{len(df[df['الحالة']=='جاهز'])}</h2></div>", unsafe_allow_html=True)
    with c4: 
        profit = pd.to_numeric(df[df['الحالة']=='تم التسليم']['التكلفة']).sum()
        st.markdown(f"<div class='metric-card' style='border-top-color:#17a2b8;'><h3>💰 الدخل</h3><h2>{profit}$</h2></div>", unsafe_allow_html=True)

# --- التبويب 2: استلام الأجهزة ---
elif menu == "📥 استلام الأجهزة":
    st.header("📝 تسجيل جهاز جديد")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c2.text_input("رقم الهاتف")
        model = c1.text_input("موديل الجهاز")
        cost = c2.number_input("تكلفة تقديرية $", min_value=0)
        issue = st.text_area("وصف العطل")
        notes = st.text_area("ملاحظات إضافية (مثل: خدوش بالظهر، بدون شاحن)")
        img = st.file_uploader("تصوير الجهاز", type=['jpg', 'jpeg', 'png'])
        
        if st.form_submit_button("🚀 حفظ في المنظومة"):
            new_id = len(st.session_state.db) + 1001
            path = ""
            if img:
                path = os.path.join(IMG_DIR, f"{new_id}.jpg")
                with open(path, "wb") as f: f.write(img.getbuffer())
            
            new_row = pd.DataFrame([[new_id, name, phone, model, issue, cost, 0, "تحت الصيانة", datetime.now(), notes, path]], columns=st.session_state.db.columns)
            st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
            save_all()
            st.success(f"تم الحفظ بنجاح! ID: {new_id}")

# --- التبويب 3: البحث والإدارة (إصلاح الخطأ هنا) ---
elif menu == "🔍 البحث والإدارة":
    st.header("🔍 محرك البحث الذكي")
    search_id = st.query_params.get("id", "")
    query = st.text_input("ابحث عن جهاز (ID، اسم، أو هاتف)", value=search_id)
    
    if query:
        df = st.session_state.db
        # محرك البحث الآمن
        mask = (
            df['ID'].astype(str).str.contains(query, na=False) |
            df['الزبون'].astype(str).str.lower().str.contains(query.lower(), na=False) |
            df['الهاتف'].astype(str).str.contains(query, na=False)
        )
        results = df[mask]
        
        if results.empty:
            st.warning("لا توجد نتائج مطابقة.")
        else:
            for idx, row in results.iterrows():
                with st.expander(f"⚙️ {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})"):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        new_status = st.selectbox("الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"].index(row['الحالة']) if row['الحالة'] in ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"] else 0, key=f"st_{idx}")
                        
                        # إضافة قطع
                        p_list = ["بدون قطع"] + st.session_state.inv[st.session_state.inv['الكمية'] > 0]['القطعة'].tolist()
                        selected_p = st.selectbox("استخدام قطعة من المخزن", p_list, key=f"p_{idx}")
                        
                        if st.button("تحديث وحفظ", key=f"btn_{idx}"):
                            if selected_p != "بدون قطع":
                                p_data = st.session_state.inv[st.session_state.inv['القطعة'] == selected_p].iloc[0]
                                st.session_state.db.at[idx, 'سعر_القطع'] += p_data['السعر']
                                st.session_state.inv.loc[st.session_state.inv['القطعة'] == selected_p, 'الكمية'] -= 1
                            
                            st.session_state.db.at[idx, 'الحالة'] = new_status
                            save_all()
                            st.rerun()
                    
                    with c2:
                        if row['الصورة'] and os.path.exists(str(row['الصورة'])): st.image(str(row['الصورة']), width=150)
                        qr = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                        if st.button("🏷️ طباعة ستيكر", key=f"stick_{idx}"):
                            html = f"<div style='text-align:center;'><b>{row['الزبون']}</b><br><img src='{qr}'><br>ID: {row['ID']}</div>"
                            st.components.v1.html(f"<script>var w=window.open(); w.document.write(\"{html}\"); w.print(); w.close();</script>")
                        if st.button("📄 طباعة وصل", key=f"rec_{idx}"):
                            html = f"<div style='direction:rtl; text-align:right;'><h2>وصل: {row['الزبون']}</h2><p>الجهاز: {row['الموديل']}</p><h3>المبلغ: {row['التكلفة']}$</h3></div>"
                            st.components.v1.html(f"<script>var w=window.open(); w.document.write(\"{html}\"); w.print(); w.close();</script>")

# --- التبويب 4: المخزن ---
elif menu == "📦 المخزن":
    st.header("📦 إدارة قطع الغيار")
    with st.form("inv_form"):
        c1, c2, c3 = st.columns(3)
        n = c1.text_input("اسم القطعة")
        s = c2.number_input("سعر التكلفة $", min_value=0)
        q = c3.number_input("الكمية", min_value=1)
        if st.form_submit_button("إضافة للمخزن"):
            new_p = pd.DataFrame([[n, s, q]], columns=st.session_state.inv.columns)
            st.session_state.inv = pd.concat([st.session_state.inv, new_p], ignore_index=True)
            save_all()
            st.rerun()
    st.table(st.session_state.inv)

# --- التبويب 5: المالية ---
elif menu == "💰 قسم المالية":
    st.header("📊 التقارير المالية والشهور")
    df_fin = st.session_state.db[st.session_state.db['الحالة'] == 'تم التسليم'].copy()
    if not df_fin.empty:
        df_fin['التاريخ'] = pd.to_datetime(df_fin['التاريخ'])
        df_fin['الشهر'] = df_fin['التاريخ'].dt.strftime('%Y-%m')
        
        for month in sorted(df_fin['الشهر'].unique(), reverse=True):
            m_data = df_fin[df_fin['الشهر'] == month]
            income = m_data['التكلفة'].sum()
            parts = m_data['سعر_القطع'].sum()
            net = income - parts
            
            with st.expander(f"📅 شهر: {month} | صافي الأرباح: {net}$"):
                st.markdown(f"""
                <div class='profit-box'>
                    <h3>💰 صافي ربح الشهر: {net}$</h3>
                    <h4 style='color:#007bff;'>⚖️ حصة الشريك الواحد (50%): {net / 2}$</h4>
                </div>
                """, unsafe_allow_html=True)
                st.write("---")
                st.dataframe(m_data[['ID', 'الزبون', 'الموديل', 'التكلفة', 'سعر_القطع']])
                
                csv = m_data.to_csv(index=False).encode('utf-8-sig')
                st.download_button(f"📥 تحميل تقرير {month}", csv, f"Report_{month}.csv", "text/csv")
    else:
        st.info("لا توجد مبيعات مكتملة بعد.")
