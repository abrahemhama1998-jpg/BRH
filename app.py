import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. إعدادات الهوية والتنسيق ---
st.set_page_config(page_title="الحل للتقنية | منظومة الصيانة", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    /* تنسيق كروت العرض */
    .stMetric { background: #f8f9fa; border-radius: 10px; padding: 15px; border: 1px solid #eee; }
    
    /* إعدادات الطباعة الاحترافية */
    @media print {
        header, footer, .stTabs, button, [data-testid="stHeader"], .no-print { display: none !important; }
        .printable { display: block !important; width: 100% !important; color: black !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قاعدة البيانات ---
DB_FILE = "tech_solution_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for col in ["سعر_القطع", "التكلفة"]:
            if col not in df.columns: df[col] = 0
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ"])

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def save_db():
    st.session_state.db.to_csv(DB_FILE, index=False)

# --- 3. دوال المساعدة (طباعة وباركود) ---
def print_service(html):
    js = f"""<script>
    var win = window.open('', '', 'height=500,width=700');
    win.document.write('<html><head><title>طباعة</title><style>body{{font-family:Cairo; direction:rtl; text-align:center; padding:30px;}} .ticket{{border:2px solid #000; padding:20px; border-radius:15px;}}</style></head><body><div class="ticket">');
    win.document.write('{html}');
    win.document.write('</div></body></html>');
    win.document.close();
    setTimeout(function(){{ win.print(); win.close(); }}, 500);
    </script>"""
    st.components.v1.html(js, height=0)

# استقبال الباركود
params = st.query_params
auto_id = params.get("id", "")

# --- 4. واجهة المستخدم الرئيسية ---
st.title("🛠️ منظومة الحل للتقنية")
st.markdown("---")

tabs = st.tabs(["📥 استلام جهاز", "🔍 الإدارة والبحث", "💰 التقارير المالية"])

# --- التبويب الأول: إضافة جهاز (مع الطباعة الفورية) ---
with tabs[0]:
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("👤 اسم الزبون")
        phone = c2.text_input("📞 رقم الهاتف")
        model = c3.text_input("📱 نوع الجهاز وموديله")
        issue = st.text_area("📝 وصف العطل")
        
        c4, c5 = st.columns(2)
        initial_cost = c4.number_input("💵 التكلفة التقريبية ($)", min_value=0)
        status = c5.selectbox("🚦 الحالة الأولية", ["تحت الصيانة", "انتظار قطع", "مستعجل"])
        
        submitted = st.form_submit_button("✅ حفظ الجهاز")
        
        if submitted:
            if name and model:
                new_id = len(st.session_state.db) + 1001
                new_row = {
                    "ID": new_id, "الزبون": name, "الهاتف": phone, "الموديل": model, 
                    "العطل": issue, "التكلفة": initial_cost, "سعر_القطع": 0, 
                    "الحالة": status, "التاريخ": datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_db()
                st.session_state.last_added = new_row
                st.success(f"تم الحفظ بنجاح! رقم الجهاز: {new_id}")

    # إظهار أزرار الطباعة فوراً بعد الحفظ خارج الفورم
    if 'last_added' in st.session_state:
        row = st.session_state.last_added
        st.info(f"إجراءات سريعة للجهاز رقم: {row['ID']}")
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
        
        cp1, cp2 = st.columns(2)
        with cp1:
            if st.button("🖨️ طباعة وصل الزبون الآن"):
                html_code = f"<h2>وصل استلام - الحل للتقنية</h2><hr><p>ID: {row['ID']}</p><p>الزبون: {row['الزبون']}</p><h3>المطلوب: {row['التكلفة']} $</h3><img src='{qr_url}' width='120'>"
                print_service(html_code)
        with cp2:
            if st.button("🏷️ طباعة ستيكر الجهاز الآن"):
                html_code = f"<b>{row['الزبون']}</b><br><img src='{qr_url}' width='100'><br>ID: {row['ID']}"
                print_service(html_code)
        if st.button("❌ إنهاء العملية"):
            del st.session_state.last_added
            st.rerun()

# --- التبويب الثاني: البحث والإدارة ---
with tabs[1]:
    search_query = st.text_input("🔎 ابحث عن جهاز (اسم، هاتف، أو رقم ID)", value=auto_id)
    if search_query:
        df = st.session_state.db
        results = df[df['الزبون'].astype(str).str.contains(search_query) | 
                     df['ID'].astype(str).str.contains(search_query) | 
                     df['الهاتف'].astype(str).str.contains(search_query)]
        
        for idx, row in results.iterrows():
            with st.expander(f"📋 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=True if auto_id else False):
                with st.form(f"update_{idx}"):
                    col1, col2, col3 = st.columns(3)
                    u_cost = col1.number_input("المبلغ ($)", value=int(row['التكلفة']))
                    u_parts = col2.number_input("قطع الغيار ($)", value=int(row['سعر_القطع']))
                    u_status = col3.selectbox("الحالة", ["تحت الصيانة", "جاهز للتسليم", "تم التسليم"], index=0)
                    if st.form_submit_button("💾 تحديث"):
                        st.session_state.db.loc[idx, ["التكلفة", "سعر_القطع", "الحالة"]] = [u_cost, u_parts, u_status]
                        save_db()
                        st.rerun()

# --- التبويب الثالث: التقارير المالية ---
with tabs[2]:
    st.header("📊 ملخص الأداء المالي")
    df_finance = st.session_state.db
    total_revenue = df_finance[df_finance['الحالة'] == "تم التسليم"]['التكلفة'].sum()
    total_parts = df_finance[df_finance['الحالة'] == "تم التسليم"]['سعر_القطع'].sum()
    m1, m2, m3 = st.columns(3)
    m1.metric("إجمالي الدخل", f"{total_revenue} $")
    m2.metric("تكلفة القطع", f"{total_parts} $")
    m3.metric("صافي الربح", f"{total_revenue - total_parts} $")
    st.dataframe(df_finance)
