import streamlit as st

# كود اختباري صافي 100%
st.set_page_config(page_title="الحل للتقنية", layout="wide")

st.balloons() # لإظهار احتفال عند النجاح
st.title("🛠️ الحل للتقنية - المنظومة تعمل بنجاح!")
st.success("إبراهيم، إذا رأيت هذه الرسالة، فالسيرفر سليم 100%.")

# خانة تجريبية
name = st.text_input("جرب اكتب اسمك هنا:")
if name:
    st.write(f"أهلاً بك يا {name} في منظومتك الجديدة.")
