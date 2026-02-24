import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. الإعدادات المتقدمة للهوية البصرية ---
st.set_page_config(page_title="الحل للتقنية | Management System", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* خلفية وتنسيق عام */
    .main { background-color: #f4f7f6; }
    .stApp { background: #f4f7f6; }
    
    /* تصميم الكروت الإحصائية */
    .stat-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 5px solid #007bff;
        text-align: center; transition: 0.3s;
    }
    .stat-card:hover { transform: translateY(-5px); }
    
    /* تنسيق الوصل للطباعة */
    @media print {
        header, footer, .stTabs, button, [data-testid="stHeader"], .no-print { display: none !important; }
        .printable { display: block !important; width: 100% !important; color: black !important; background: white !important; }
    }
    
    /* أيقونات وحالات */
    .status-ready { color: #28a745; font-weight: bold; }
    .status-repair { color: #ffc107; font-weight: bold; }
    .status-urgent { color: #dc3545; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات والصور ---
DB_FILE = "tech_v4_pro_database.csv"
IMG_DIR = "device_vault"
if not os.path.exists(IMG_DIR): os.makedirs(IMG_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['التاريخ_الكامل'] = pd.to_datetime(df['التاريخ_الكامل'], errors='coerce')
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ_الكامل", "ملاحظات", "صورة"])

if 'db' not in st.session_state: st.session_state.db = load_data()

def save_db():
    st.session_state.db.to_csv(DB_FILE, index=False)

def print_action(html):
    st.components.v1.html(f"<script>var w=window.open(); w.document.write('{html}'); w.document.close(); setTimeout(function(){{w.print(); w.close();}}, 500);</script>", height=0)

# --- 3. معالجة الباركود التلقائي ---
search_id_from_url = st.query_params.get("id", "")

# --- 4. الواجهة الرئيسية ---
st.title("🛡️ منظومة الحل للتقنية - الإصدار الشامل")
st.markdown("---")

# --- لوحة الإحصائيات (Dashboard) ---
df_all = st.session_state.db
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='stat-card'><h3>📦 الكلي</h3><h2>{len(df_all)}</h2></div>", unsafe_allow_html=True)
with col2:
    repairing = len(df_all[df_all['الحالة'] == "تحت الصيانة"])
    st.markdown(f"<div class='stat-card' style='border-top-color: #ffc107;'><h3>🛠️ صيانة</h3><h2>{repairing}</h2></div>", unsafe_allow_html=True)
with col3:
    ready = len(df_all[df_all['الحالة'] == "جاهز"])
    st.markdown(f"<div class='stat-card' style='border-top-color: #28a745;'><h3>✅ جاهز</h3><h2>{ready}</h2></div>", unsafe_allow_html=True)
with col4:
    total_rev = pd.to_numeric(df_all[df_all['الحالة'] == "تم التسليم"]['التكلفة']).sum()
    st.markdown(f"<div class='stat-card' style='border-top-color: #17a2b8;'><h3>💰 أرباح</h3><h2>{total_rev}$</h2></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# التبويبات
tabs = st.tabs(["📋 لوحة التحكم والإدارة", "📥 تسجيل استلام", "📊 المحاسبة العميقة"])

# --- التبويب الأول: البحث والإدارة (المحرك الرئيسي) ---
with tabs[0]:
    search_q = st.text_input("🔎 ابحث عن زبون أو جهاز (أو امسح الباركود الآن)", value=search_id_from_url, placeholder="اكتب هنا للبحث...")
    
    if search_q:
        results = df_all[df_all['الزبون'].astype(str).str.contains(search_q) | 
                        df_all['ID'].astype(str) == str(search_q) | 
                        df_all['الهاتف'].astype(str).str.contains(search_q)]
        
        for idx, row in results.sort_values(by="التاريخ_الكامل", ascending=False).iterrows():
            is_open = True if search_id_from_url == str(row['ID']) else False
            with st.expander(f"📱 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=is_open):
                c_a, c_b, c_c = st.columns([2, 1, 1])
                
                with c_a:
                    with st.form(f"update_{idx}"):
                        st.write("🔧 **تحديث فني**")
                        u_status = st.selectbox("حالة الجهاز", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم", "لم يتم الإصلاح"], 
                                               index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم", "لم يتم الإصلاح"].index(row['الحالة']))
                        u_cost = st.number_input("المبلغ المطلوب $", value=int(row['التكلفة']))
                        u_parts = st.number_input("تكلفة القطع $", value=int(row['سعر_القطع']))
                        u_notes = st.text_area("تقرير فني داخلي", value=str(row['ملاحظات']))
                        if st.form_submit_button("💾 تحديث البيانات"):
                            st.session_state.db.at[idx, "الحالة"] = u_status
                            st.session_state.db.at[idx, "التكلفة"] = u_cost
                            st.session_state.db.at[idx, "سعر_القطع"] = u_parts
                            st.session_state.db.at[idx, "ملاحظات"] = u_notes
                            save_db()
                            st.rerun()
                
                with c_b:
                    if row['صورة'] and os.path.exists(str(row['صورة'])):
                        st.image(str(row['صورة']), caption="حالة الجهاز عند الاستلام")
                    else:
                        st.info("لا توجد صورة مرفقة")
                
                with c_c:
                    st.write("🧾 **الطباعة والباركود**")
                    current_url = "https://brh-tech.streamlit.app"
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={current_url}/?id={row['ID']}"
                    dt = pd.to_datetime(row['التاريخ_الكامل'])
                    
                    receipt_html = f"""<div style="border:2px solid black; padding:10px; text-align:center; font-family:Cairo; background:white; color:black;">
                        <h2 style="margin:0;">الحل للتقنية</h2>
                        <p style="font-size:10px;">{dt.strftime('%Y-%m-%d | %I:%M %p')}</p>
                        <hr>
                        <p>ID: <b>{row['ID']}</b></p>
                        <p>الزبون: {row['الزبون']}</p>
                        <p>الجهاز: {row['الموديل']}</p>
                        <h3>المبلـغ: {row['التكلفة']}$</h3>
                        <img src="{qr_url}" width="80">
                        </div>"""
                    
                    if st.button("🖨️ طباعة الوصل", key=f"p_{idx}"): print_action(receipt_html)
                    if st.button("🏷️ طباعة ستيكر", key=f"s_{idx}"):
                        stk_html = f"<div style='text-align:center; font-family:Cairo; color:black;'><b>{row['الزبون']}</b><br><img src='{qr_url}' width='70'><br>ID: {row['ID']}</div>"
                        print_action(stk_html)

# --- التبويب الثاني: استلام جهاز جديد ---
with tabs[1]:
    with st.container():
        st.subheader("📝 نموذج استلام جهاز جديد")
        with st.form("main_add_form", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            f_name = col_f1.text_input("👤 اسم الزبون الكامل")
            f_phone = col_f2.text_input("📞 رقم الهاتف للواتساب")
            f_model = col_f1.text_input("📱 نوع وموديل الجهاز")
            f_cost = col_f2.number_input("💵 المبلغ المتفق عليه $", min_value=0)
            f_issue = st.text_area("📝 وصف العطل")
            f_file = st.file_uploader("📸 تصوير حالة الجهاز", type=["jpg", "png", "jpeg"])
            
            if st.form_submit_button("🚀 تسجيل في المنظومة وإصدار ID"):
                if f_name and f_model:
                    new_id = len(st.session_state.db) + 1001
                    img_path = ""
                    if f_file:
                        img_path = os.path.join(IMG_DIR, f"{new_id}.jpg")
                        with open(img_path, "wb") as f: f.write(f_file.getbuffer())
                    
                    new_row = {
                        "ID": str(new_id), "الزبون": f_name, "الهاتف": f_phone, "الموديل": f_model,
                        "العطل": f_issue, "التكلفة": f_cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة",
                        "التاريخ_الكامل": datetime.now(), "ملاحظات": "", "صورة": img_path
                    }
                    st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                    save_db()
                    st.success(f"✅ تم التسجيل! رقم الجهاز: {new_id}")

# --- التبويب الثالث: المحاسبة الاحترافية ---
with tabs[2]:
    st.subheader("💹 التقارير المالية والربحية")
    df_fin = st.session_state.db.copy()
    df_fin['التاريخ_الكامل'] = pd.to_datetime(df_fin['التاريخ_الكامل'])
    
    # فلترة الشهور
    df_fin['الشهر'] = df_fin['التاريخ_الكامل'].dt.strftime('%Y-%m')
    months = df_fin['الشهر'].unique()
    
    for m in sorted(months, reverse=True):
        m_data = df_fin[(df_fin['الشهر'] == m) & (df_fin['الحالة'] == "تم التسليم")]
        if not m_data.empty:
            income = m_data['التكلفة'].sum()
            outgo = m_data['سعر_القطع'].sum()
            with st.expander(f"📅 تقرير شهر: {m} | الأرباح: {income - outgo} $"):
                st.write(f"إجمالي المقبوضات: {income}$ | إجمالي القطع: {outgo}$")
                st.table(m_data[['ID', 'الزبون', 'الموديل', 'التكلفة']])
