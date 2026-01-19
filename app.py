from __future__ import annotations

from typing import Dict, List

import streamlit as st

from agent_logic import PayrollOrchestrator
from chat_engine import PayrollChatbot
from models import PayrollRecord, UserProfile


st.set_page_config(page_title="AI Payroll Orchestrator", layout="wide")

st.title("AI Payroll Orchestrator")
st.caption(
    "Secure, explainable payroll automation for the modern workforce."
)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
orchestrator = PayrollOrchestrator()
chatbot = PayrollChatbot()
with st.sidebar:
    st.header("Controls")
    use_sample = st.toggle("Use sample timesheet", value=True)
    sample_text = st.text_area(
        "Sample timesheet",
        value="Weekly report with overtime logged for project Alpha.",
        disabled=not use_sample,
    )
    uploaded_file = st.file_uploader("Upload Timesheet", type=["txt"])
    st.divider()
    st.subheader("Employee Details")
    employee_name = st.text_input("Name", value="Employee")
    employee_role = st.text_input("Role", value="Contractor")
    hourly_rate = st.number_input("Hourly rate", min_value=1.0, value=50.0, step=1.0)
    st.subheader("Employee Chat")
    chat_query = st.text_input("Ask a payroll question")
    send_chat = st.button("Send")
    st.divider()
    approve_payout = st.checkbox("HR Approval granted")

pipeline_result = None

if uploaded_file is not None or use_sample:
    file_content = (
        uploaded_file.read().decode("utf-8") if uploaded_file is not None else sample_text
    )
    with st.status("Processing timesheet", expanded=True) as status:
        st.write("Scanning...")
        timesheet_result = orchestrator.extract_data(file_content)
        st.write("Scrubbing PII...")
        st.write("Calculating...")
        payroll_record = orchestrator.calculate_pay(timesheet_result, user_rate=hourly_rate)
        st.write("Auditing...")
        payroll_record = orchestrator.audit_transaction(payroll_record)
        status.update(label="Pipeline complete", state="complete")

    pipeline_result = {
        "timesheet": timesheet_result.model_dump(),
        "payroll_record": payroll_record.model_dump(),
        "audit": {
            "flag": payroll_record.audit_flag,
            "reason": payroll_record.audit_reason,
        },
        "user": UserProfile(
            id="1",
            name=employee_name,
            role=employee_role,
            hourly_rate=hourly_rate,
        ),
    }

if pipeline_result:
    payroll_record_data = pipeline_result.get("payroll_record", {})
    payroll_record = PayrollRecord(**payroll_record_data)
    timesheet_data = pipeline_result.get("timesheet", {})

    metrics = st.columns(4)
    metrics[0].metric("Hours Claimed", f"{timesheet_data.get('hours_claimed', 0):.1f}")
    metrics[1].metric("Gross Pay", f"${payroll_record.gross_pay:,.2f}")
    metrics[2].metric("Tax", f"${payroll_record.tax:,.2f}")
    metrics[3].metric("Net Pay", f"${payroll_record.net_pay:,.2f}")

    st.subheader("Pay Slip")
    slip_cols = st.columns([2, 1])
    with slip_cols[0]:
        with st.container(border=True):
            st.markdown(
                f"""
                **Employee:** {employee_name}  
                **Role:** {employee_role}  
                **Gross Pay:** ${payroll_record.gross_pay:,.2f}  
                **Tax (10%):** ${payroll_record.tax:,.2f}  
                **Net Pay:** ${payroll_record.net_pay:,.2f}  
                **Status:** {payroll_record.status}
                """
            )
    with slip_cols[1]:
        st.success("Payout summary ready", icon="✅")
        st.write("Processed file:")
        st.code(timesheet_data.get("file_name", "ingested.txt"))

        payslip_text = (
            f"Employee: {employee_name}\n"
            f"Role: {employee_role}\n"
            f"Hours Claimed: {timesheet_data.get('hours_claimed', 0):.1f}\n"
            f"Gross Pay: ${payroll_record.gross_pay:,.2f}\n"
            f"Tax: ${payroll_record.tax:,.2f}\n"
            f"Net Pay: ${payroll_record.net_pay:,.2f}\n"
            f"Status: {payroll_record.status}\n"
        )
        st.download_button(
            "Download Pay Slip",
            data=payslip_text,
            file_name="payslip.txt",
            mime="text/plain",
        )

    if payroll_record.audit_flag:
        st.error(
            f"⚠️ Transaction Flagged by AI Auditor: {payroll_record.audit_reason}",
            icon="🚨",
        )
    elif approve_payout:
        st.success("✅ HR approval recorded. Ready for payout.")
    elif not payroll_record.audit_flag:
        st.info("Awaiting HR approval before final payout.")

    with st.expander("Audit Trail", expanded=False):
        st.write("- Timesheet scanned")
        st.write("- PII scrubbed")
        st.write("- Payroll calculated")
        if payroll_record.audit_flag:
            st.write("- AI audit flagged overtime")
        else:
            st.write("- AI audit passed")
        if approve_payout:
            st.write("- HR approval granted")

    if send_chat and chat_query:
        response = chatbot.get_response(chat_query, pipeline_result)
        st.session_state.chat_history.append({"role": "user", "content": chat_query})
        st.session_state.chat_history.append({"role": "assistant", "content": response})

if st.session_state.chat_history:
    st.subheader("Employee Chat")
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
else:
    st.info("Upload a timesheet or enable the sample data to start the pipeline.")

