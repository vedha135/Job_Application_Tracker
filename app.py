import streamlit as st

st.set_page_config(
    page_title="Job Application Tracker",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Job Application Tracker")
st.write("Track your job applications in one place!")

st.success("Welcome! Your Job Tracker is ready.")


st.header("➕ Add New Job Application")

with st.form("job_form"):
    company = st.text_input("Company Name")
    role = st.text_input("Job Role")
    location = st.text_input("Location")

    status = st.selectbox(
        "Application Status",
        ["Applied", "Interview", "Selected", "Rejected"]
    )

    submitted = st.form_submit_button("Save Application")

    if submitted:
        if company and role:
            st.success(f"Application for {role} at {company} added!")
        else:
            st.warning("Please enter Company Name and Job Role.")


        # Create Database
import sqlite3
import pandas as pd

conn = sqlite3.connect("job_applications.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    role TEXT,
    location TEXT,
    status TEXT
)
""")

conn.commit()

# Save Application to Database
if submitted and company and role:
    cursor.execute("""
    INSERT INTO applications (company, role, location, status)
    VALUES (?, ?, ?, ?)
    """, (company, role, location, status))

    conn.commit()

# Display Applications
st.header("📋 My Job Applications")

df = pd.read_sql_query("SELECT * FROM applications", conn)

if not df.empty:
    st.dataframe(df, use_container_width=True)

    st.metric("Total Applications", len(df))
else:
    st.info("No applications added yet.")

# Update Application Status
st.divider()
st.header("🔄 Update Application Status")

if not df.empty:

    application_options = {
        f"{row['company']} - {row['role']} (ID: {row['id']})": row['id']
        for _, row in df.iterrows()
    }

    selected_application = st.selectbox(
        "Select Application",
        list(application_options.keys())
    )

    new_status = st.selectbox(
        "Update Status",
        ["Applied", "Interview", "Selected", "Rejected"]
    )

    if st.button("Update Status"):
        selected_id = application_options[selected_application]

        cursor.execute(
            "UPDATE applications SET status = ? WHERE id = ?",
            (new_status, selected_id)
        )

        conn.commit()

        st.success("Application status updated successfully!")
        st.rerun()

else:
    st.info("Add an application first to update its status.")


# Application Analytics
st.divider()
st.header("📊 Application Analytics")

if not df.empty:
    status_counts = df["status"].value_counts()
    status_counts = status_counts.reindex(
        ["Applied", "Interview", "Selected", "Rejected"],
        fill_value=0
    )

    st.subheader("Applications by Status")
    st.bar_chart(status_counts, height=300)

    col1, col2 = st.columns(2)

    col1.metric("Total Applications", len(df))
    col2.metric(
        "Interviews",
        len(df[df["status"] == "Interview"])
    )

else:
    st.info("Add applications to view analytics")

conn.close()