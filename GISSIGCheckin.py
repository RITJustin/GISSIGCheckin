import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(layout="wide")

# Folder to store event files
EVENTS_FOLDER = "events"
os.makedirs(EVENTS_FOLDER, exist_ok=True)

st.title("📋 Event Check-in App")

# Step 1: Select existing event file or upload a new one
event_files = [f for f in os.listdir(EVENTS_FOLDER) if f.endswith(".csv")]
selected_event = st.selectbox("Choose an event file", ["-- Upload new --"] + event_files)

df = None
save_path = None

if selected_event != "-- Upload new --":
    save_path = os.path.join(EVENTS_FOLDER, selected_event)
    df = pd.read_csv(save_path)

else:
    uploaded_file = st.file_uploader("Upload Constant Contact CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        event_name = uploaded_file.name.replace(".csv", "")
        save_path = os.path.join(EVENTS_FOLDER, f"{event_name}_checkins.csv")
        df.to_csv(save_path, index=False)  # Save initial copy
        st.success(f"Event file saved as {save_path}")
        selected_event = os.path.basename(save_path)

# Step 2: If we have an event file, show the check-in interface
if df is not None and save_path:
    st.subheader("Attendee Check-in List")

    # Search box
    search_query = st.text_input("🔎 Search by name").lower()

    # Filter attendees by search
    filtered_df = df[
        df["First Name"].str.lower().str.contains(search_query)
        | df["Last Name"].str.lower().str.contains(search_query)
    ] if search_query else df

    # Display check-in checkboxes
    for i, row in filtered_df.iterrows():
        name = f"{row['First Name']} {row['Last Name']}"
        checked_in = row.get("Checked In Time", "") != ""

        # Create checkbox for each attendee
        if st.checkbox(name, value=checked_in, key=f"checkin_{i}"):
            if not checked_in:
                df.at[i, "Checked In Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.to_csv(save_path, index=False)
        else:
            if checked_in:
                df.at[i, "Checked In Time"] = ""
                df.to_csv(save_path, index=False)

    # Step 3: Add a new walk-in attendee
    st.subheader("➕ Add Walk-in Attendee")
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
            df.to_csv(save_path, index=False)
            st.success(f"Added {first} {last}")
