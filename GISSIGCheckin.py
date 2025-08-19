import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="wide")

EVENTS_FOLDER = "events"
os.makedirs(EVENTS_FOLDER, exist_ok=True)

# Select existing event file or upload new
event_files = [f for f in os.listdir(EVENTS_FOLDER) if f.endswith(".csv")]
selected_event = st.selectbox("Choose an event file", ["-- Upload new --"] + event_files)

if selected_event != "-- Upload new --":
    df = pd.read_csv(os.path.join(EVENTS_FOLDER, selected_event))
else:
    uploaded_file = st.file_uploader("Upload Constant Contact CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        event_name = uploaded_file.name.replace(".csv", "")
        save_path = os.path.join(EVENTS_FOLDER, f"{event_name}_checkins.csv")
        df.to_csv(save_path, index=False)  # Save initial copy
        st.success(f"Event file saved as {save_path}")
        selected_event = os.path.basename(save_path)

if selected_event != "-- Upload new --":
    save_path = os.path.join(EVENTS_FOLDER, selected_event)

    # Show attendees
    st.subheader("Attendee Check-in List")
    for i, row in df.iterrows():
        name = f"{row['First Name']} {row['Last Name']}"
        checked_in = row.get("Checked In Time", "") != ""

        if st.checkbox(name, value=checked_in, key=f"checkin_{i}"):
            if not checked_in:
                df.at[i, "Checked In Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.to_csv(save_path, index=False)  # Save progress
        else:
            if checked_in:
                df.at[i, "Checked In Time"] = ""
                df.to_csv(save_path, index=False)  # Save progress

    # Add a new attendee
    st.subheader("Add Walk-in Attendee")
    with st.form("add_attendee"):
        first = st.text_input("First Name")
        last = st.text_input("Last Name")
        submitted = st.form_submit_button("Add Attendee")
        if submitted and first and last:
            new_row = {
                "Ticket Name": "Walk-in",
                "Ticket Id": "",
                "First Name": first,
                "Last Name": last,
                "Registration Status": "Walk-in",
                "Payment Status": "",
                "Checked In Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Total Spent": 0,
                "Date Purchased": datetime.now().strftime("%Y-%m-%d"),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(save_path, index=False)  # Save progress
            st.success(f"Added {first} {last}")
