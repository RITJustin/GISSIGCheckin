import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

uploaded_file = st.file_uploader("Upload Constant Contact CSV", type="csv")

# --- Load CSV into session state ---
if uploaded_file and "df" not in st.session_state:
    st.session_state.df = pd.read_csv(uploaded_file)

# Only run app if data is loaded
if "df" in st.session_state:
    df = st.session_state.df

    # Add check-in columns if not present
    if "Checked In" not in df.columns:
        df["Checked In"] = False
    if "Checked In Time" not in df.columns:
        df["Checked In Time"] = ""

    # --- Add Walk-In Form ---
    st.subheader("➕ Add Walk-In / Not Registered")
    with st.form("add_attendee"):
        col1, col2, col3 = st.columns(3)
        with col1:
            new_first = st.text_input("First Name")
        with col2:
            new_last = st.text_input("Last Name")
        with col3:
            new_ticket = st.text_input("Ticket Name (Optional)")
        add_btn = st.form_submit_button("Add & Check In")

        if add_btn and new_first.strip() and new_last.strip():
            new_entry = {
                "Ticket Name": new_ticket if new_ticket else "Walk-In",
                "Ticket Id": "NA",
                "First Name": new_first,
                "Last Name": new_last,
                "Registration Status": "Added On-Site",
                "Payment Status": "Unpaid",
                "Checked In Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Total Spent": 0,
                "Date Purchased": datetime.now().strftime("%Y-%m-%d"),
                "Checked In": True,
            }
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            st.session_state.df = df  # persist change
            st.success(f"✅ Added and checked in {new_first} {new_last}")

    # --- Filters ---
    show_only_not_checked = st.checkbox("🔲 Show only people not checked in", value=True)

    # --- Search bar ---
    search = st.text_input("🔍 Search by Name")

    # Apply filters
    filtered_df = df
    if show_only_not_checked:
        filtered_df = filtered_df[filtered_df["Checked In"] == False]

    if search:
        results = filtered_df[filtered_df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]
    else:
        results = filtered_df

    # --- Display Results ---
    if results.empty:
        st.warning("No matches found.")
    else:
        for i, row in results.iterrows():
            col1, col2, col3 = st.columns([3,1,1])

            with col1:
                name = f"{row['First Name']} {row['Last Name']}"
                ticket = row.get("Ticket Name", "")
                st.markdown(f"**{name}**  \n🎟 {ticket}")

                if row["Checked In"]:
                    st.success(f"✅ Checked in at {row['Checked In Time']}")

            with col2:
                if not row["Checked In"]:
                    if st.button("Check In", key=f"in_{i}"):
                        df.at[i, "Checked In"] = True
                        df.at[i, "Checked In Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.df = df  # persist change

            with col3:
                if row["Checked In"]:
                    if st.button("Reset", key=f"reset_{i}"):
                        df.at[i, "Checked In"] = False
                        df.at[i, "Checked In Time"] = ""
                        st.session_state.df = df  # persist change

    # --- Summary ---
    st.subheader("📋 Attendee List")
    st.write(f"Total: {len(df)} | Checked In: {df['Checked In'].sum()} | Not Checked In: {len(df) - df['Checked In'].sum()}")
    st.dataframe(df)

    # --- Save ---
    st.download_button("⬇️ Download Updated CSV", df.to_csv(index=False), "checkins.csv")
