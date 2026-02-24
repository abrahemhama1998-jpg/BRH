import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. الإعدادات الأساسية والهوية ---
st.set_page_config(page_title="الحل للتقنية - النظام المتكامل", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stMetric { background: #ffffff; border-radius: 10px; padding: 15px; border-right: 5px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .preview-card { border: 2px solid #333; padding: 15px; border-radius: 10px; background: white; color: black; text-align: center; max-width: 300px; margin: auto; }
    .status-badge { padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات والصور ---
DB_FILE = "tech_master_db.csv"
IMG_DIR = "stored_images"
if not os.path.exists(IMG_DIR): os.makedirs(IMG_DIR)

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['التاريخ_الكامل'] = pd.to_datetime(df['التاريخ_الكامل'], errors='coerce')
        for col in ["ملاحظات", "صورة"]:
            if col not in df.columns: df[col] = ""
        return df
    return pd.DataFrame(columns=["ID", "الزبون", "الهاتف", "الموديل", "العطل", "التكلفة", "سعر_القطع", "الحالة", "التاريخ_الكامل", "ملاحظات", "صورة"])

if 'db' not in st.session_state: st.session_state.db = load_data()

def save_db():
    st.session_state.db.to_csv(DB_FILE, index=False)

def print_action(html):
    st.components.v1.html(f"<script>var w=window.open(); w.document.write('{html}'); w.document.close(); setTimeout(function(){{w.print(); w.close();}}, 500);</script>", height=0)

# --- 3. الواجهة الرئيسية ---
st.title("🛠️ منظومة الحل للتقنية - الإدارة المحاسبية والفنية")
tabs = st.tabs(["📥 استلام جهاز", "🔍 البحث والإدارة", "📊 التقارير والأرباح"])

# --- التبويب الأول: إضافة جهاز ---
with tabs[0]:
    with st.form("add_device_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("👤 اسم الزبون")
        phone = c2.text_input("📞 رقم الهاتف")
        model = c3.text_input("📱 الموديل")
        
        issue = st.text_area("📝 وصف العطل")
        notes = st.text_area("🗒️ ملاحظات فنية (داخلية)")
        
        c4, c5 = st.columns(2)
        cost = c4.number_input("💵 التكلفة المتفق عليها $", min_value=0)
        uploaded_file = c5.file_uploader("📸 إرفاق صورة للجهاز/العطل", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("✅ حفظ البيانات"):
            if name and model:
                new_id = len(st.session_state.db) + 1001
                now = datetime.now()
                img_path = ""
                if uploaded_file:
                    img_path = os.path.join(IMG_DIR, f"{new_id}.jpg")
                    with open(img_path, "wb") as f: f.write(uploaded_file.getbuffer())
                
                new_row = {
                    "ID": new_id, "الزبون": name, "الهاتف": phone, "الموديل": model,
                    "العطل": issue, "التكلفة": cost, "سعر_القطع": 0, "الحالة": "تحت الصيانة",
                    "التاريخ_الكامل": now, "ملاحظات": notes, "صورة": img_path
                }
                st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
                save_db()
                st.success(f"تم تسجيل الجهاز بنجاح برقم: {new_id}")

# --- التبويب الثاني: البحث والإدارة الشاملة ---
with tabs[1]:
    search = st.text_input("🔎 ابحث عن جهاز (اسم، هاتف، أو ID)")
    if search:
        df_view = st.session_state.db.sort_values(by="التاريخ_الكامل", ascending=False)
        res = df_view[df_view['الزبون'].astype(str).str.contains(search) | df_view['ID'].astype(str).str.contains(search) | df_view['الهاتف'].astype(str).str.contains(search)]
        
        for idx, row in res.iterrows():
            with st.expander(f"⚙️ {row['الزبون']} - {row['الموديل']} (ID: {row['ID']}) - {row['الحالة']}"):
                col_info, col_img = st.columns([2, 1])
                
                with col_info:
                    with st.form(f"edit_{idx}"):
                        u_status = st.selectbox("الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم", "لم يتم الإصلاح"], index=0)
                        u_cost = st.number_input("التكلفة $", value=int(row['التكلفة']))
                        u_parts = st.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                        u_notes = st.text_area("تعديل الملاحظات", value=str(row['ملاحظات']))
                        if st.form_submit_button("💾 حفظ التعديلات"):
                            st.session_state.db.at[idx, "الحالة"] = u_status
                            st.session_state.db.at[idx, "التكلفة"] = u_cost
                            st.session_state.db.at[idx, "سعر_القطع"] = u_parts
                            st.session_state.db.at[idx, "ملاحظات"] = u_notes
                            save_db()
                            st.rerun()
                
                with col_img:
                    if row['صورة'] and os.path.exists(str(row['صورة'])):
                        st.image(str(row['صورة']), caption="صورة الجهاز المعني")
                    else: st.write("🚫 لا توجد صورة")

                # الطباعة والمعاينة
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://brh-tech.streamlit.app/?id={row['ID']}"
                dt = pd.to_datetime(row['التاريخ_الكامل'])
                
                p1, p2 = st.columns(2)
                with p1:
                    receipt_html = f"""<div class='preview-card'><h3>الحل للتقنية</h3>
                        <p style='font-size:11px;'>{dt.strftime('%Y-%m-%d | %I:%M %p')}</p><hr>
                        <p>ID: {row['ID']}</p><p>الزبون: {row['الزبون']}</p>
                        <h4>المبلغ: {row['التكلفة']} $</h4><img src='{qr_url}' width='90'></div>"""
                    st.markdown(receipt_html, unsafe_allow_html=True)
                    if st.button("🖨️ طباعة الوصل", key=f"btn_p_{idx}"): print_action(receipt_html)
                with p2:
                    sticker_html = f"<div class='preview-card' style='width:160px; padding:5px;'><b>{row['الزبون']}</b><br><img src='{qr_url}' width='70'><br>ID: {row['ID']}</div>"
                    st.markdown(sticker_html, unsafe_allow_html=True)
                    if st.button("🏷️ طباعة ستيكر", key=f"btn_s_{idx}"): print_action(sticker_html)

# --- التبويب الثالث: المحاسبة الاحترافية (يومي وشهري) ---
with tabs[2]:
    st.header("📊 التقارير المالية التفصيلية")
    full_df = st.session_state.db.copy()
    full_df['التاريخ_الكامل'] = pd.to_datetime(full_df['التاريخ_الكامل'])
    
    # فلترة المسلم فقط للحسابات
    delivered = full_df[full_df['الحالة'] == "تم التسليم"].copy()
    
    # --- الملخص الشهري ---
    st.subheader("📅 الأرباح الشهرية")
    delivered['الشهر'] = delivered['التاريخ_الكامل'].dt.strftime('%Y - %m')
    monthly = delivered.groupby('الشهر').agg({'التكلفة': 'sum', 'سعر_القطع': 'sum'}).sort_index(ascending=False)
    
    for month, m_data in monthly.iterrows():
        with st.expander(f"📈 شهر: {month} | صافي الربح: {m_data['التكلفة'] - m_data['سعر_القطع']} $"):
            c_m1, c_m2, c_m3 = st.columns(3)
            c_m1.metric("إجمالي الدخل", f"{m_data['التكلفة']} $")
            c_m2.metric("تكلفة القطع", f"{m_data['سعر_القطع']} $")
            c_m3.metric("صافي الربح", f"{m_data['التكلفة'] - m_data['سعر_القطع']} $")
            st.write("أجهزة هذا الشهر:")
            st.table(delivered[delivered['الشهر'] == month][['ID', 'الزبون', 'التكلفة', 'سعر_القطع']])

    # --- الملخص اليومي ---
    st.markdown("---")
    st.subheader("📆 الأرباح اليومية (آخر 30 يوم)")
    delivered['اليوم'] = delivered['التاريخ_الكامل'].dt.date
    daily = delivered.groupby('اليوم').agg({'التكلفة': 'sum', 'سعر_القطع': 'sum'}).sort_index(ascending=False).head(30)
    daily['الربح الصافي'] = daily['التكلفة'] - daily['سعر_القطع']
    st.dataframe(daily, use_container_width=True)
