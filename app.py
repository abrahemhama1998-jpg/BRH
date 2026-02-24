import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. الإعدادات الأساسية ---
st.set_page_config(page_title="الحل للتقنية - المحاسب الذكي", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stMetric { background: #f8f9fa; border-radius: 10px; padding: 15px; border: 1px solid #eee; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .preview-card { border: 2px solid #333; padding: 15px; border-radius: 10px; background: white; color: black; text-align: center; max-width: 320px; margin: auto; line-height: 1.6; }
    .report-box { border-right: 5px solid #007bff; padding-right: 15px; background: #f0f2f6; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات ---
DB_FILE = "tech_pro_database.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # التأكد من تحويل التاريخ لنوع تاريخ حقيقي للفرز
        df['التاريخ_الكامل'] = pd.to_datetime(df['التاريخ_الكامل'], errors='coerce')
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ_الكامل", "ملاحظات"])

if 'db' not in st.session_state: st.session_state.db = load_data()

def save_db():
    st.session_state.db.to_csv(DB_FILE, index=False)

def print_action(html):
    st.components.v1.html(f"<script>var w=window.open(); w.document.write('{html}'); w.document.close(); setTimeout(function(){{w.print(); w.close();}}, 500);</script>", height=0)

# --- 3. الواجهة الرئيسية ---
st.title("🛠️ منظومة الحل للتقنية - الإدارة والمحاسبة")
tabs = st.tabs(["📥 استلام جهاز", "🔍 إدارة وبحث وتعديل", "📊 التقارير المالية والأرباح"])

# --- التبويب الأول: إضافة جهاز ---
with tabs[0]:
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("اسم الزبون")
        phone = c2.text_input("رقم الهاتف")
        model = c3.text_input("الموديل")
        issue = st.text_area("وصف العطل")
        cost = st.number_input("التكلفة المتوقعة $", min_value=0)
        
        if st.form_submit_button("✅ حفظ وجدولة الجهاز"):
            if name and model:
                new_id = len(st.session_state.db) + 1001
                now = datetime.now()
                new_row = {
                    "ID": new_id, "الزبون": name, "الهاتف": phone, "الموديل": model,
                    "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة",
                    "التاريخ_الكامل": now, "ملاحظات": ""
                }
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_db()
                st.success(f"تم الحفظ برقم: {new_id} في تمام الساعة {now.strftime('%H:%M')}")

# --- التبويب الثاني: البحث والإدارة الشاملة ---
with tabs[1]:
    search = st.text_input("🔎 ابحث (اسم، رقم هاتف، أو ID الجهاز)")
    if search:
        df = st.session_state.db.sort_values(by="التاريخ_الكامل", ascending=False)
        res = df[df['الزبون'].astype(str).str.contains(search) | df['ID'].astype(str).str.contains(search) | df['الهاتف'].astype(str).str.contains(search)]
        
        for idx, row in res.iterrows():
            with st.expander(f"⚙️ تعديل: {row['الزبون']} - ID: {row['ID']} ({row['الحالة']})"):
                c_edit1, c_edit2 = st.columns([1, 1])
                with c_edit1:
                    with st.form(f"f_{idx}"):
                        u_status = st.selectbox("الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم", "لم يتم الإصلاح"], index=0)
                        u_cost = st.number_input("التكلفة الكلية $", value=int(row['التكلفة']))
                        u_parts = st.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                        if st.form_submit_button("💾 حفظ التعديلات"):
                            st.session_state.db.loc[idx, ["الحالة", "التكلفة", "سعر_القطع"]] = [u_status, u_cost, u_parts]
                            save_db()
                            st.rerun()
                
                # التاريخ والوقت المنسق للوصل
                date_str = pd.to_datetime(row['التاريخ_الكامل']).strftime('%Y-%m-%d')
                time_str = pd.to_datetime(row['التاريخ_الكامل']).strftime('%I:%M %p')
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"

                with c_edit2:
                    st.markdown("**معاينة الوصل**")
                    receipt_html = f"""<div class='preview-card'>
                        <h3>الحل للتقنية</h3>
                        <p style='font-size:12px;'>التاريخ: {date_str} | الوقت: {time_str}</p>
                        <hr><p>ID: {row['ID']}</p><p>الزبون: {row['الزبون']}</p>
                        <h4>المطلوب: {row['التكلفة']} $</h4>
                        <img src='{qr_url}' width='90'><br>
                        <small>شكراً لثقتكم بنا</small></div>"""
                    st.markdown(receipt_html, unsafe_allow_html=True)
                    if st.button(f"🖨️ طباعة الوصل", key=f"p_rec_{idx}"): print_action(receipt_html)

# --- التبويب الثالث: التقارير المالية المنظمة ---
with tabs[2]:
    st.header("📊 التقارير المالية الذكية")
    df = st.session_state.db.copy()
    df['التاريخ_الكامل'] = pd.to_datetime(df['التاريخ_الكامل'])
    
    # فلترة الأجهزة التي تم تسليمها فقط للحساب المالي
    delivered_df = df[df['الحالة'] == "تم التسليم"].copy()
    
    # 1. إحصائيات عامة
    st.subheader("📌 الملخص العام")
    c_m1, c_m2, c_m3 = st.columns(3)
    total_rev = delivered_df['التكلفة'].sum()
    total_parts = delivered_df['سعر_القطع'].sum()
    c_m1.metric("إجمالي الدخل التاريخي", f"{total_rev} $")
    c_m2.metric("إجمالي سعر القطع", f"{total_parts} $")
    c_m3.metric("صافي الربح الكلي", f"{total_rev - total_parts} $")

    # 2. تقرير حسب الشهور
    st.markdown("---")
    st.subheader("📅 الأرباح الشهرية (لهذا العام)")
    delivered_df['الشهر'] = delivered_df['التاريخ_الكامل'].dt.strftime('%Y-%m')
    monthly_stats = delivered_df.groupby('الشهر').agg({'التكلفة': 'sum', 'سعر_القطع': 'sum'}).sort_index(ascending=False)
    
    for month, m_row in monthly_stats.iterrows():
        with st.container():
            st.markdown(f"<div class='report-box'><b>الشهر: {month}</b> | الدخل: {m_row['التكلفة']}$ | القطع: {m_row['سعر_القطع']}$ | <b>الربح: {m_row['التكلفة'] - m_row['سعر_القطع']}$</b></div>", unsafe_allow_html=True)

    # 3. تقرير حسب الأيام
    st.markdown("---")
    st.subheader("📆 الأرباح اليومية (آخر 30 يوم)")
    delivered_df['اليوم'] = delivered_df['التاريخ_الكامل'].dt.date
    daily_stats = delivered_df.groupby('اليوم').agg({'التكلفة': 'sum', 'سعر_القطع': 'sum'}).sort_index(ascending=False)
    
    st.table(daily_stats.head(30).assign(الربح=lambda x: x['التكلفة'] - x['سعر_القطع']))
