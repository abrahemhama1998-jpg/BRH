import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. الإعدادات والجمالية ---
st.set_page_config(page_title="الحل للتقنية - النظام الذكي", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; direction: rtl; }
    .stMetric { background: #ffffff; border-radius: 10px; padding: 15px; border-right: 5px solid #28a745; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .preview-card { border: 2px solid #333; padding: 15px; border-radius: 10px; background: white; color: black; text-align: center; max-width: 300px; margin: auto; }
    @media print {
        header, footer, .stTabs, button, [data-testid="stHeader"] { display: none !important; }
        .printable { display: block !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إدارة البيانات والصور ---
DB_FILE = "tech_final_master_db.csv"
IMG_DIR = "stored_images"
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

# --- 3. معالجة رابط الباركود (الاستقبال الذكي) ---
# قراءة رقم الجهاز من الرابط إذا وجد (مثلاً: ?id=1001)
query_params = st.query_params
search_id_from_url = query_params.get("id", "")

# تحديد التبويب الافتراضي (إذا كان هناك ID نفتح البحث فوراً)
default_tab = 0
if search_id_from_url:
    default_tab = 1

# --- 4. واجهة المستخدم ---
st.title("🛠️ منظومة الحل للتقنية - الإصدار الاحترافي")
tabs = st.tabs(["📥 استلام جهاز", "🔍 البحث والإدارة", "📊 التقارير والأرباح"])

# --- التبويب الأول: إضافة جهاز ---
with tabs[0]:
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("👤 اسم الزبون")
        phone = c2.text_input("📞 رقم الهاتف")
        model = c3.text_input("📱 الموديل")
        issue = st.text_area("📝 وصف العطل")
        notes = st.text_area("🗒️ ملاحظات فنية")
        c4, c5 = st.columns(2)
        cost = c4.number_input("💵 التكلفة $", min_value=0)
        uploaded_file = c5.file_uploader("📸 صورة الجهاز", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("✅ حفظ الجهاز"):
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
                st.success(f"تم الحفظ برقم: {new_id}")

# --- التبويب الثاني: البحث والإدارة (يدعم الباركود) ---
with tabs[1]:
    # إذا جاء ID من الباركود، يوضع تلقائياً في خانة البحث
    search = st.text_input("🔎 ابحث عن جهاز (اسم، هاتف، أو ID)", value=search_id_from_url)
    
    if search:
        df_view = st.session_state.db.sort_values(by="التاريخ_الكامل", ascending=False)
        res = df_view[df_view['الزبون'].astype(str).str.contains(search) | 
                     df_view['ID'].astype(str).str.contains(search) | 
                     df_view['الهاتف'].astype(str).str.contains(search)]
        
        if res.empty:
            st.warning("لا توجد نتائج مطابقة.")
        
        for idx, row in res.iterrows():
            # إذا كان البحث قادم من الباركود، نفتح الـ expander تلقائياً
            is_expanded = True if search_id_from_url else False
            
            with st.expander(f"⚙️ {row['الزبون']} - ID: {row['ID']} - {row['الحالة']}", expanded=is_expanded):
                col_info, col_img = st.columns([2, 1])
                with col_info:
                    with st.form(f"edit_{idx}"):
                        u_status = st.selectbox("الحالة", ["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم", "لم يتم الإصلاح"], 
                                               index=["تحت الصيانة", "انتظار قطع", "جاهز", "تم التسليم", "لم يتم الإصلاح"].index(row['الحالة']))
                        u_cost = st.number_input("التكلفة $", value=int(row['التكلفة']))
                        u_parts = st.number_input("سعر القطع $", value=int(row['سعر_القطع']))
                        u_notes = st.text_area("الملاحظات", value=str(row['ملاحظات']))
                        if st.form_submit_button("💾 حفظ"):
                            st.session_state.db.at[idx, "الحالة"] = u_status
                            st.session_state.db.at[idx, "التكلفة"] = u_cost
                            st.session_state.db.at[idx, "سعر_القطع"] = u_parts
                            st.session_state.db.at[idx, "ملاحظات"] = u_notes
                            save_db()
                            st.rerun()
                
                with col_img:
                    if row['صورة'] and os.path.exists(str(row['صورة'])):
                        st.image(str(row['صورة']))
                    else: st.write("🚫 لا توجد صورة")

                # إعدادات الباركود والطباعة
                current_url = "https://brh-tech.streamlit.app" # رابط موقعك
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={current_url}/?id={row['ID']}"
                dt = pd.to_datetime(row['التاريخ_الكامل'])
                
                p1, p2 = st.columns(2)
                with p1:
                    receipt_html = f"""<div class='preview-card'><h3>الحل للتقنية</h3>
                        <p style='font-size:11px;'>{dt.strftime('%Y-%m-%d | %I:%M %p')}</p><hr>
                        <p>ID: {row['ID']}</p><p>الزبون: {row['الزبون']}</p>
                        <h4>المبلغ: {row['التكلفة']} $</h4><img src='{qr_url}' width='90'></div>"""
                    st.markdown(receipt_html, unsafe_allow_html=True)
                    if st.button("🖨️ طباعة الوصل", key=f"p_{idx}"): print_action(receipt_html)
                with p2:
                    sticker_html = f"<div class='preview-card' style='width:160px; padding:5px;'><b>{row['الزبون']}</b><br><img src='{qr_url}' width='70'><br>ID: {row['ID']}</div>"
                    st.markdown(sticker_html, unsafe_allow_html=True)
                    if st.button("🏷️ طباعة ستيكر", key=f"s_{idx}"): print_action(sticker_html)

# --- التبويب الثالث: التقارير المالية ---
with tabs[2]:
    st.header("📊 الأرباح والمحاسبة")
    df_fin = st.session_state.db.copy()
    df_fin['التاريخ_الكامل'] = pd.to_datetime(df_fin['التاريخ_الكامل'])
    delivered = df_fin[df_fin['الحالة'] == "تم التسليم"].copy()
    
    # أرباح شهرية
    delivered['الشهر'] = delivered['التاريخ_الكامل'].dt.strftime('%Y-%m')
    monthly = delivered.groupby('الشهر').agg({'التكلفة': 'sum', 'سعر_القطع': 'sum'}).sort_index(ascending=False)
    
    for month, m_data in monthly.iterrows():
        with st.expander(f"📈 شهر: {month} | صافي الربح: {m_data['التكلفة'] - m_data['سعر_القطع']} $"):
            st.metric("الدخل الصافي لهذا الشهر", f"{m_data['التكلفة'] - m_data['سعر_القطع']} $")
            st.table(delivered[delivered['الشهر'] == month][['ID', 'الزبون', 'التكلفة', 'سعر_القطع']])
