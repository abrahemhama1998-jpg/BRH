import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# --- 1. الإعدادات والتنسيق الجمالي الاحترافي ---
st.set_page_config(page_title="منظومة الحل للتقنية - الإصدار الذهبي", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stApp { background-color: #f0f2f6; }
    
    /* تنسيق الكروت المالية */
    .metric-container {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-right: 6px solid #007bff; text-align: center;
    }
    .profit-split {
        background: #e3f2fd; border: 1px dashed #007bff;
        padding: 10px; border-radius: 10px; margin-top: 10px;
    }
    
    /* تنسيق الجداول */
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    
    /* إخفاء عناصر الاستريم ليت للطباعة */
    @media print {
        .no-print, .stSidebar, button, header { display: none !important; }
        .printable { display: block !important; width: 100% !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة قواعد البيانات ---
DB_DEVICES = "devices_final_v7.csv"
DB_INVENTORY = "inventory_final_v7.csv"
IMG_DIR = "stored_images"

if not os.path.exists(IMG_DIR): os.makedirs(IMG_DIR)

def init_dbs():
    if not os.path.exists(DB_DEVICES):
        pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ", "ملاحظات", "الصورة"]).to_csv(DB_DEVICES, index=False)
    if not os.path.exists(DB_INVENTORY):
        pd.DataFrame(columns=["القطعة", "السعر", "الكمية"]).to_csv(DB_INVENTORY, index=False)

init_dbs()

# --- 3. نظام الحماية ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🛡️ تسجيل الدخول - الحل للتقنية")
    with st.container():
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول للنظام"):
            if u == "admin" and p == "123": 
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("خطأ في البيانات")
    st.stop()

# --- 4. قراءة البيانات ---
df_dev = pd.read_csv(DB_DEVICES)
df_inv = pd.read_csv(DB_INVENTORY)
df_dev['التاريخ'] = pd.to_datetime(df_dev['التاريخ'], errors='coerce')

# --- 5. القائمة الجانبية ---
st.sidebar.markdown("<h1 style='text-align:center;'>💎 الحل للتقنية</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("الانتقال إلى:", ["🏠 الرئيسية", "📥 استلام الأجهزة", "🔍 البحث والإدارة", "📦 المخزن", "📊 قسم المالية"])

# --- التبويب 1: الرئيسية (Dashboard) ---
if menu == "🏠 الرئيسية":
    st.header("📈 ملخص النشاط")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='metric-container'><h3>🛠️ قيد التصليح</h3><h2>{len(df_dev[df_dev['الحالة']=='تحت الصيانة'])}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-container' style='border-right-color:#28a745;'><h3>✅ جاهز للتسليم</h3><h2>{len(df_dev[df_dev['الحالة']=='جاهز'])}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-container' style='border-right-color:#ffc107;'><h3>⚠️ قطع منتهية</h3><h2>{len(df_inv[df_inv['الكمية']==0])}</h2></div>", unsafe_allow_html=True)

# --- التبويب 2: استلام الأجهزة (مع الصور والملاحظات) ---
elif menu == "📥 استلام الأجهزة":
    st.header("📝 تسجيل دخول جهاز")
    with st.form("new_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        f_name = col1.text_input("👤 اسم الزبون")
        f_phone = col2.text_input("📞 رقم الهاتف")
        f_model = col1.text_input("📱 موديل الجهاز")
        f_cost = col2.number_input("💵 التكلفة التقريبية $", min_value=0)
        f_issue = st.text_area("📝 وصف العطل")
        f_notes = st.text_area("🗒️ ملاحظات إضافية (خدوش، إضافات)")
        f_img = st.file_uploader("📸 رفع صورة الجهاز عند الاستلام", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("🚀 تسجيل وحفظ الجهاز"):
            new_id = len(df_dev) + 1001
            img_path = ""
            if f_img:
                img_path = os.path.join(IMG_DIR, f"{new_id}.jpg")
                with open(img_path, "wb") as f: f.write(f_img.getbuffer())
            
            new_row = [new_id, f_name, f_phone, f_model, f_issue, f_cost, 0, "تحت الصيانة", datetime.now().date(), f_notes, img_path]
            df_dev.loc[len(df_dev)] = new_row
            df_dev.to_csv(DB_DEVICES, index=False)
            st.success(f"✅ تم التسجيل بنجاح! رقم الجهاز: {new_id}")

# --- التبويب 3: البحث والإدارة (ستيكر ووصل) ---
elif menu == "🔍 البحث والإدارة":
    search_id = st.query_params.get("id", "")
    q = st.text_input("🔎 ابحث عن جهاز (ID أو اسم)", value=search_id)
    if q:
        results = df_dev[df_dev['الزبون'].astype(str).contains(q) | df_dev['ID'].astype(str).fullmatch(q)]
        for idx, row in results.iterrows():
            with st.expander(f"📱 {row['الزبون']} - {row['الموديل']} (ID: {row['ID']})"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    new_st = st.selectbox("تحديث الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"], index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم"].index(row['الحالة']))
                    available_parts = ["بدون قطع"] + df_inv[df_inv['الكمية']>0]['القطعة'].tolist()
                    p_sel = st.selectbox("إضافة قطعة من المخزن", available_parts)
                    if st.button(f"حفظ التعديلات {row['ID']}"):
                        if p_sel != "بدون قطع":
                            p_info = df_inv[df_inv['القطعة']==p_sel].iloc[0]
                            df_dev.at[idx, 'سعر_القطع'] += p_info['السعر']
                            df_inv.loc[df_inv['القطعة']==p_sel, 'الكمية'] -= 1
                            df_inv.to_csv(DB_INVENTORY, index=False)
                        df_dev.at[idx, 'الحالة'] = new_st
                        df_dev.to_csv(DB_DEVICES, index=False)
                        st.rerun()
                with c2:
                    if row['الصورة'] and os.path.exists(str(row['الصورة'])): st.image(str(row['الصورة']), width=150)
                    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                    # الستيكر (بباركود)
                    if st.button("🏷️ طباعة ستيكر الباركود"):
                        html = f"<div style='text-align:center; font-family:Cairo;'><b>{row['الزبون']}</b><br><img src='{qr}' width='100'><br>ID: {row['ID']}</div>"
                        st.components.v1.html(f"<script>var w=window.open(); w.document.write(\"{html}\"); w.print(); w.close();</script>")
                    # الوصل (بدون باركود)
                    if st.button("📄 طباعة وصل الزبون"):
                        html = f"<div style='direction:rtl; font-family:Cairo;'><h2>وصل صيانة - الحل للتقنية</h2><hr><p>الزبون: {row['الزبون']}</p><p>الجهاز: {row['الموديل']}</p><h3>المبلغ: {row['التكلفة']}$</h3></div>"
                        st.components.v1.html(f"<script>var w=window.open(); w.document.write(\"{html}\"); w.print(); w.close();</script>")

# --- التبويب 4: المخزن ---
elif menu == "📦 المخزن":
    st.header("📦 إدارة قطع الغيار")
    with st.form("add_inv"):
        c1, c2, c3 = st.columns(3)
        n = c1.text_input("اسم القطعة")
        p = c2.number_input("السعر $", min_value=0)
        q = c3.number_input("الكمية", min_value=0)
        if st.form_submit_button("إضافة للمخزن"):
            df_inv.loc[len(df_inv)] = [n, p, q]
            df_inv.to_csv(DB_INVENTORY, index=False)
            st.rerun()
    st.table(df_inv)

# --- التبويب 5: قسم المالية (الاحترافي المطور) ---
elif menu == "📊 قسم المالية":
    st.header("💹 التقارير المالية والأرباح")
    
    # تحويل التاريخ ومعالجة البيانات
    df_fin = df_dev[df_dev['الحالة'] == 'تم التسليم'].copy()
    df_fin['الشهر'] = df_fin['التاريخ'].dt.strftime('%Y-%m')
    df_fin['اليوم'] = df_fin['التاريخ'].dt.strftime('%Y-%m-%d')
    
    months = df_fin['الشهر'].unique()
    
    for month in sorted(months, reverse=True):
        m_data = df_fin[df_fin['الشهر'] == month]
        total_income = m_data['التكلفة'].sum()
        total_parts = m_data['سعر_القطع'].sum()
        net_profit = total_income - total_parts
        
        with st.expander(f"📅 تقرير شهر: {month} (صافي الربح: {net_profit}$)", expanded=True):
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("إجمالي الدخل", f"{total_income} $")
            col_m2.metric("تكلفة القطع", f"{total_parts} $")
            col_m3.metric("صافي الربح الكلي", f"{net_profit} $")
            
            # ميزة تقسيم الأرباح على 2
            st.markdown(f"""
            <div class='profit-split'>
                <b>⚖️ تقسيم الأرباح (الشراكة):</b><br>
                حصة الشخص الواحد لهذا الشهر: <span style='color:green; font-size:20px;'>{net_profit / 2} $</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("---")
            st.write("**تفاصيل العمليات اليومية لهذا الشهر:**")
            st.dataframe(m_data[['اليوم', 'ID', 'الزبون', 'الموديل', 'التكلفة', 'سعر_القطع']])
            
            # ميزة تحميل نسخة لكل شهر
            csv_month = m_data.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label=f"📥 تحميل نسخة احتياطية لشهر {month}",
                data=csv_month,
                file_name=f"Report_{month}.csv",
                mime='text/csv',
            )
