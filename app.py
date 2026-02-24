import streamlit as st
import pandas as pd
import os

# إعداد الصفحة الأساسي
st.set_page_config(page_title="الحل للتقنية", layout="wide")

st.title("🛠️ منظومة الحل للتقنية - تعمل الآن!")

# إنشاء قاعدة بيانات بسيطة إذا لم تكن موجودة
DB_FILE = "data.csv"
if 'db' not in st.session_state:
    if os.path.exists(DB_FILE):
        st.session_state.db = pd.read_csv(DB_FILE)
    else:
        st.session_state.db = pd.DataFrame(columns=["الاسم", "الموديل", "التكلفة"])

# واجهة بسيطة للتأكد من العمل
tab1, tab2 = st.tabs(["إضافة جهاز", "عرض السجل"])

with tab1:
    with st.form("my_form"):
        name = st.text_input("اسم الزبون")
        model = st.text_input("الموديل")
        cost = st.number_input("التكلفة $", min_value=0)
        submit = st.form_submit_button("حفظ")
        if submit:
            new_data = pd.DataFrame([[name, model, cost]], columns=["الاسم", "الموديل", "التكلفة"])
            st.session_state.db = pd.concat([st.session_state.db, new_data], ignore_index=True)
            st.session_state.db.to_csv(DB_FILE, index=False)
            st.success("تم الحفظ بنجاح!")

with tab2:
    st.write("بيانات الأجهزة المسجلة:")
    st.dataframe(st.session_state.db)

st.info("إذا ظهرت لك هذه الصفحة، فالمنظومة اشتغلت! الآن يمكننا إضافة أزرار الطباعة والباركود.")
