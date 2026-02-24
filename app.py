import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. إعدادات الهوية والتنسيق ---
st.set_page_config(page_title="الحل للتقنية | منظومة الصيانة", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    
    .stMetric { background: #f8f9fa; border-radius: 10px; padding: 15px; border: 1px solid #eee; }
    
    /* تنسيق خاص للوصل ليظهر بشكل مرتب */
    .ticket-container {
        border: 2px solid #000;
        padding: 20px;
        border-radius: 10px;
        background: white;
        color: black;
        text-align: center;
        width: 300px;
        margin: auto;
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

# --- 3. دالة الطباعة الجديدة (حل مشكلة عدم الاستجابة) ---
def print_service(html_content):
    # نستخدم مكون Streamlit HTML لعرض الزر والسكربت بداخله مباشرة
    full_html = f"""
    <div id="print_area">
        {html_content}
    </div>
    <script>
        function doPrint() {{
            var printContents = document.getElementById('print_area').innerHTML;
            var originalContents = document.body.innerHTML;
            var printWindow = window.open('', '', 'height=600,width=800');
            printWindow.document.write('<html><head><title>طباعة</title>');
            printWindow.document.write('<style>body{{font-family:Cairo; direction:rtl; text-align:center; padding:20px; color:black;}}</style>');
            printWindow.document.write('</head><body>');
            printWindow.document.write(printContents);
            printWindow.document.write('</body></html>');
            printWindow.document.close();
            printWindow.focus();
            setTimeout(function() {{ printWindow.print(); printWindow.close(); }}, 500);
        }}
        doPrint();
    </script>
    """
    components.html(full_html, height=400)

# استقبال الباركود
params = st.query_params
auto_id = params.get("id", "")

st.title("🛠️ منظومة الحل للتقنية")
st.markdown("---")

tabs = st.tabs(["📥 استلام جهاز", "🔍 الإدارة والبحث", "💰 التقارير المالية"])

# --- التبويب الأول: إضافة جهاز ---
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

    if 'last_added' in st.session_state:
        row = st.session_state.last_added
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
        
        st.info("معاينة الوصل قبل الطباعة")
        
        # كود الوصل
        receipt_html = f"""
        <div style="border:2px solid #000; padding:15px; text-align:center; width:280px; margin:auto; background:white; color:black;">
            <h2 style="margin:0;">الحل للتقنية</h2>
            <hr>
            <p style="margin:5px;"><b>رقم الوصل:</b> {row['ID']}</p>
            <p style="margin:5px;"><b>الزبون:</b> {row['الزبون']}</p>
            <p style="margin:5px;"><b>الجهاز:</b> {row['الموديل']}</p>
            <h3 style="margin:10px;">المبلغ: {row['التكلفة']} $</h3>
            <img src="{qr_url}" width="120">
            <p style="font-size:10px; margin-top:10px;">يرجى الاحتفاظ بالوصل للاستلام</p>
        </div>
        """
        
        if st.button("🖨️ تأكيد وأمر الطباعة"):
            print_service(receipt_html)
            
        if st.button("❌ إنهاء العملية"):
            del st.session_state.last_added
            st.rerun()

# (بقية التبويبات تظل كما هي في الكود السابق)
with tabs[1]:
    # ... كود البحث يظل كما هو ...
    st.write("استخدم تبويب البحث للإدارة")
