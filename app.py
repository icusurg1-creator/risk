import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# การตั้งค่าหน้าเว็บ
st.set_page_config(page_title="ICU Risk & KPI Management", page_icon="🏥", layout="wide")

# รายชื่อหอผู้ป่วย 15 แห่ง
WARDS = [
    "SICU1", "SICU2", "POICU1", "POICU2", "NeuroICU", 
    "CVTICU", "CCU", "MICU1", "MICU2", "CICU", 
    "IICU", "ICUสงฆ์", "PICU", "NICU1", "NICU2"
]

# รหัสความเสี่ยงเบื้องต้น (สามารถเพิ่มได้)
RISK_CODES = [
    "CPL101 (ท่อช่วยหายใจเลื่อนหลุด)",
    "CPL102 (สายเครื่องมือแพทย์หลุด)",
    "CAUTI (การติดเชื้อทางเดินปัสสาวะ)",
    "VAP (ปอดอักเสบจากการใช้เครื่องช่วยหายใจ)",
    "CLABSI (การติดเชื้อในกระแสเลือด)",
    "CPM101 (แพ้ยาซ้ำ)",
    "CPP405 (พลัดตกหกล้ม)",
    "อื่นๆ"
]

# สร้างเมนูด้านซ้าย (Sidebar)
st.sidebar.title("🏥 เมนูหลัก")
menu = st.sidebar.radio("เลือกหน้าต่างการทำงาน:", ["📝 ลงบันทึกความเสี่ยง", "📊 แดชบอร์ดสรุปผล"])

# -----------------------------------------
# หน้าที่ 1: ฟอร์มลงบันทึกความเสี่ยง
# -----------------------------------------
if menu == "📝 ลงบันทึกความเสี่ยง":
    st.title("📝 ลงบันทึกอุบัติการณ์ความเสี่ยง (Risk Log)")
    st.markdown("กรุณากรอกข้อมูลให้ครบถ้วนเพื่อบันทึกลงในฐานข้อมูลกลาง")

    # สร้างฟอร์ม
    with st.form("risk_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("วันที่เกิดเหตุ", datetime.date.today())
            ward = st.selectbox("หอผู้ป่วย", ["-- เลือกหอผู้ป่วย --"] + WARDS)
            severity = st.selectbox("ระดับความรุนแรง", ["-- เลือกระดับ --", "A", "B", "C", "D", "E", "F", "G", "H", "I"])
        
        with col2:
            time = st.time_input("เวลาที่เกิดเหตุ (โดยประมาณ)")
            risk_code = st.selectbox("รหัสความเสี่ยง", ["-- เลือกรหัสความเสี่ยง --"] + RISK_CODES)
            reporter = st.text_input("ชื่อผู้รายงาน (ตัวเลือก)")

        details = st.text_area("รายละเอียด / การแก้ไขเบื้องต้น")
        
        # ปุ่มกดบันทึก
        submitted = st.form_submit_button("💾 บันทึกข้อมูล")

        if submitted:
            if ward == "-- เลือกหอผู้ป่วย --" or risk_code == "-- เลือกรหัสความเสี่ยง --" or severity == "-- เลือกระดับ --":
                st.warning("⚠️ กรุณาเลือก หอผู้ป่วย, รหัสความเสี่ยง และระดับความรุนแรงให้ครบถ้วน")
            else:
                # ส่วนนี้คือจุดที่จะเขียนโค้ดเชื่อมกับ Google Sheets ในอนาคต
                # ตัวอย่าง: sheet.append_row([str(date), str(time), ward, risk_code, severity, details, reporter])
                st.success(f"✅ บันทึกข้อมูลความเสี่ยงของ {ward} สำเร็จแล้ว!")
                st.info(f"ข้อมูลที่บันทึก: {risk_code} ระดับ {severity} วันที่ {date}")

# -----------------------------------------
# หน้าที่ 2: แดชบอร์ด (Dashboard)
# -----------------------------------------
elif menu == "📊 แดชบอร์ดสรุปผล":
    st.title("📊 แดชบอร์ดตัวชี้วัด กลุ่มงานการพยาบาลผู้ป่วยหนัก")
    
    # เมนูตัวกรอง (Filter)
    st.sidebar.markdown("---")
    st.sidebar.subheader("ตัวกรองข้อมูล")
    selected_year = st.sidebar.selectbox("ปีงบประมาณ", ["2567", "2568", "2569"])
    selected_ward = st.sidebar.multiselect("เลือกหอผู้ป่วย (ค่าเริ่มต้นคือดูภาพรวมทั้งหมด)", WARDS)

    # สร้างข้อมูลจำลอง (Mock Data) เพื่อให้เห็นภาพ Dashboard
    # ในการใช้งานจริง จะดึงข้อมูลนี้มาจาก Google Sheets
    mock_data = {
        "หอผู้ป่วย": WARDS,
        "VAP Rate": [8.8, 0, 12.2, 5.2, 17.1, 6.9, 0, 0, 11.6, 0, 0, 0, 6.9, 0, 0],
        "จำนวนครั้งที่เกิด Medication Error": [2, 0, 1, 0, 3, 5, 0, 1, 0, 2, 0, 0, 0, 1, 0]
    }
    df = pd.DataFrame(mock_data)

    if selected_ward:
        df = df[df["หอผู้ป่วย"].isin(selected_ward)]

    # แบ่งหน้าจอแสดง KPI แบบสรุปตัวเลข (Metric)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ผู้ป่วยเสียชีวิตสะสม", "396", "+12 เดือนนี้")
    col2.metric("VAP เฉลี่ยกลุ่มงาน", "6.96", "-1.2% จากปีที่แล้ว")
    col3.metric("CLABSI เฉลี่ยกลุ่มงาน", "3.36", "+0.5% จากปีที่แล้ว")
    col4.metric("Medication Error รวม", "28", "ระดับ E-I: 2 ครั้ง")

    st.markdown("---")

    # กราฟเปรียบเทียบระหว่างหอผู้ป่วย
    st.subheader("📈 เปรียบเทียบอัตราการเกิด VAP ระหว่างหอผู้ป่วย")
    fig_vap = px.bar(df, x="หอผู้ป่วย", y="VAP Rate", color="หอผู้ป่วย", text_auto=True)
    st.plotly_chart(fig_vap, use_container_width=True)

    st.subheader("💊 จำนวนครั้งที่เกิด Medication Error แยกตามหอ")
    fig_med = px.line(df, x="หอผู้ป่วย", y="จำนวนครั้งที่เกิด Medication Error", markers=True)
    st.plotly_chart(fig_med, use_container_width=True)

    # แสดงตารางข้อมูลดิบ
    with st.expander("ดูตารางข้อมูลรายละเอียด"):
        st.dataframe(df, use_container_width=True)
