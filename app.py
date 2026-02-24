import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# --- 1. الإعدادات والتصميم الاحترافي ---
st.set_page_config(page_title="منظومة الحل للتقنية - PRO", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f8f9fa; }
    .stat-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); text-align: center; border-bottom: 4px solid #007bff; }
    .low-stock { background-color: #fff3cd; color: #856404; padding: 5px; border-radius: 5px; font-weight: bold; }
    .out-stock { background-color: #f8d7da; color: #721c24; padding: 5px; border-radius: 5px; font-weight: bold; }
    .good-stock { background-color: #d4edda; color: #155724; padding: 5px; border-radius: 5px; font-weight: bold; }
    @media print { .no-print { display: none !important; } .printable { display: block !important; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قواعد البيانات (أجهزة + مخزن) ---
DB_DEVICES = "devices_v6.csv"
DB_INVENTORY = "inventory_v6.csv"

def init_dbs():
    if not os.path.exists(DB_DEVICES):
        pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "الضمان", "ملاحظات"]).to_csv(DB_DEVICES, index=False)
    if not os.path.exists(DB_INVENTORY):
        pd.DataFrame(columns=["القطعة", "السعر", "الكمية"]).to_csv(DB_INVENTORY, index=False)

init_dbs()

# --- 3. نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 تسجيل الدخول للمنظومة")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if user == "admin" and pw == "123": # يمكنك تغييرها هنا
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("بيانات الدخول خاطئة")

if not st.session_state.logged_in:
    login()
    st.stop()

# --- 4. معالجة الباركود التلقائي ---
query_params = st.query_params
search_id_url = query_params.get("id", "")

# --- 5. محرك المنظومة ---
st.sidebar.title("💎 الحل للتقنية")
menu = st.sidebar.radio("القائمة الرئيسية", ["🏠 لوحة التحكم", "📥 استلام جهاز", "🔍 البحث والإدارة", "📦 المخزن والقطع", "📊 التقارير"])

# تحميل البيانات
df_dev = pd.read_csv(DB_DEVICES)
df_inv = pd.read_csv(DB_INVENTORY)

# --- التبويب الأول: لوحة التحكم ---
if menu == "🏠 لوحة التحكم":
    st.header("📊 نظرة عامة")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("أجهزة قيد الصيانة", len(df_dev[df_dev['الحالة'] == 'تحت الصيانة']))
    c2.metric("أجهزة جاهزة", len(df_dev[df_dev['الحالة'] == 'جاهز']))
    c3.metric("قطع منخفضة المخزون", len(df_inv[df_inv['الكمية'] < 5]))
    total_cash = pd.to_numeric(df_dev[df_dev['الحالة'] == 'تم التسليم']['التكلفة']).sum()
    c4.metric("صندوق المحل (كاش)", f"{total_cash} $")
    
    st.subheader("⚠️ تنبيهات المخزن")
    for _, item in df_inv.iterrows():
        if item['الكمية'] == 0:
            st.error(f"انتهت قطعة: {item['القطعة']}")
        elif item['الكمية'] < 5:
            st.warning(f"قربت تخلص: {item['القطعة']} (المتبقي: {item['الكمية']})")

# --- التبويب الثاني: استلام جهاز ---
elif menu == "📥 استلام جهاز":
    st.header("📝 تسجيل جهاز جديد")
    with st.form("add_device"):
        c1, c2 = st.columns(2)
        name = c1.text_input("اسم الزبون")
        phone = c2.text_input("الهاتف")
        model = c1.text_input("الموديل")
        issue = st.text_area("وصف العطل")
        cost = c2.number_input("التكلفة التقريبية $", min_value=0)
        if st.form_submit_button("حفظ الجهاز"):
            new_id = len(df_dev) + 1001
            new_dev = pd.DataFrame([[new_id, name, phone, model, issue, cost, 0, "تحت الصيانة", datetime.now().date(), datetime.now().date() + timedelta(days=30), ""]], columns=df_dev.columns)
            df_dev = pd.concat([df_dev, new_dev], ignore_index=True)
            df_dev.to_csv(DB_DEVICES, index=False)
            st.success(f"تم الحفظ! ID الجهاز: {new_id}")

# --- التبويب الثالث: البحث والإدارة ---
elif menu == "🔍 البحث والإدارة":
    st.header("🔍 تتبع وصيانة الأجهزة")
    search = st.text_input("ابحث بالاسم أو ID", value=search_id_url)
    if search:
        results = df_dev[df_dev['الزبون'].astype(str).contains(search) | df_dev['ID'].astype(str).fullmatch(search)]
        for idx, row in results.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})", expanded=(search_id_url != "")):
                c1, c2 = st.columns(2)
                with c1:
                    new_status = st.selectbox("تغيير الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"].index(row['الحالة']))
                    
                    # نظام إضافة قطع من المخزن
                    available_parts = ["بدون قطع"] + df_inv[df_inv['الكمية'] > 0]['القطعة'].tolist()
                    selected_part = st.selectbox("إضافة قطعة غيار من المخزن", available_parts)
                    
                    if st.button("تحديث البيانات والقطع"):
                        if selected_part != "بدون قطع":
                            part_info = df_inv[df_inv['القطعة'] == selected_part].iloc[0]
                            # تحديث التكلفة وخصم المخزن
                            df_dev.at[idx, 'سعر_القطع'] += part_info['السعر']
                            df_dev.at[idx, 'التكلفة'] += part_info['السعر']
                            df_inv.loc[df_inv['القطعة'] == selected_part, 'الكمية'] -= 1
                            df_inv.to_csv(DB_INVENTORY, index=False)
                        
                        df_dev.at[idx, 'الحالة'] = new_status
                        df_dev.to_csv(DB_DEVICES, index=False)
                        st.success("تم التحديث")
                        st.rerun()

                with c2:
                    st.write("**الطباعة:**")
                    # الستيكر: اسم + باركود فقط
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                    sticker_html = f"<div style='border:1px solid #000; padding:5px; text-align:center;'><b>{row['الزبون']}</b><br><img src='{qr_url}' width='80'><br>ID: {row['ID']}</div>"
                    if st.button("طباعة الستيكر (اسم + باركود)"):
                        st.components.v1.html(f"<script>var w=window.open(); w.document.write(\"{sticker_html}\"); w.print(); w.close();</script>")
                    
                    # الوصل: معلومات كاملة بدون باركود
                    receipt_html = f"<div style='direction:rtl; text-align:right;'><h2>وصل استلام - الحل للتقنية</h2><hr><p>الزبون: {row['الزبون']}</p><p>الجهاز: {row['الموديل']}</p><p>العطل: {row['العطل']}</p><h3>المبلغ: {row['التكلفة']} $</h3></div>"
                    if st.button("طباعة الوصل (بدون باركود)"):
                        st.components.v1.html(f"<script>var w=window.open(); w.document.write(\"{receipt_html}\"); w.print(); w.close();</script>")

# --- التبويب الرابع: المخزن ---
elif menu == "📦 المخزن والقطع":
    st.header("📦 إدارة مخزن قطع الغيار")
    with st.form("add_part"):
        c1, c2, c3 = st.columns(3)
        p_name = c1.text_input("اسم القطعة (مثلاً: شاشة آيفون 11)")
        p_price = c2.number_input("سعر التكلفة $", min_value=0)
        p_qty = c3.number_input("الكمية المتوفرة", min_value=0)
        if st.form_submit_button("إضافة للمخزن"):
            new_p = pd.DataFrame([[p_name, p_price, p_qty]], columns=df_inv.columns)
            df_inv = pd.concat([df_inv, new_p], ignore_index=True)
            df_inv.to_csv(DB_INVENTORY, index=False)
            st.rerun()
    
    st.subheader("قائمة المخزون الحالي")
    for idx, item in df_inv.iterrows():
        c1, c2, c3, c4 = st.columns([2,1,1,1])
        c1.write(f"**{item['القطعة']}**")
        c2.write(f"{item['السعر']} $")
        
        # تلوين الكميات
        if item['الكمية'] > 10:
            c3.markdown(f"<span class='good-stock'>{item['الكمية']} متوفر</span>", unsafe_allow_html=True)
        elif item['الكمية'] > 0:
            c3.markdown(f"<span class='low-stock'>{item['الكمية']} منخفض</span>", unsafe_allow_html=True)
        else:
            c3.markdown(f"<span class='out-stock'>منتهي</span>", unsafe_allow_html=True)
        
        if c4.button("حذف", key=f"del_{idx}"):
            df_inv = df_inv.drop(idx)
            df_inv.to_csv(DB_INVENTORY, index=False)
            st.rerun()

# --- التبويب الخامس: التقارير ---
elif menu == "📊 التقارير":
    st.header("📈 التقارير المالية")
    delivered = df_dev[df_dev['الحالة'] == 'تم التسليم']
    st.write(f"إجمالي المبيعات: {pd.to_numeric(delivered['التكلفة']).sum()} $")
    st.write(f"إجمالي تكلفة القطع: {pd.to_numeric(delivered['سعر_القطع']).sum()} $")
    st.success(f"صافي الربح: {pd.to_numeric(delivered['التكلفة']).sum() - pd.to_numeric(delivered['سعر_القطع']).sum()} $")
    st.dataframe(delivered)
