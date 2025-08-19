import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

uploaded_file = st.file_uploader("Upload Constant Contact CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Add a simple boolean column for check-in status
    if "Checked In" not in df.columns:
        df["Checked In"] = False

    # Filter option
    show_only_not_checked = st.checkbox("🔲 Show only people not checked in", value=True)

    # Search bar
    search = st.text_input("🔍 Search by Name")

    # Apply filter
    filtered_df = df
    if show_only_not_checked:
        filtered_df = filtered_df[filtered_df["Checked In"] == False]

    if search:
        results = filtered_df[filtered_df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]
    else:
        results = filtered_df

    if results.empty:
        st.warning("No matches found.")
    else:
        for i, row in results.iterrows():
            col1, col2 = st.columns([3,1])

            with col1:
                name = f"{row['First Name']} {row['Last Name']}"
                ticket = row.get("Ticket Name", "")
                st.markdown(f"**{name}**  \n🎟 {ticket}")

                if row["Checked In"]:
                    st.success(f"✅ Checked in at {row['Checked In Time']}")

            with col2:
                if not row["Checked In"]:
                    if st.button("Check In", key=i):
                        df.at[i, "Checked In"] = True
                        df.at[i, "Checked In Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Summary
    st.subheader("📋 Attendee List")
    st.write(f"Total: {len(df)} | Checked In: {df['Checked In'].sum()} | Not Checked In: {len(df) - df['Checked In'].sum()}")
    st.dataframe(df)

    # Save
    st.download_button("⬇️ Download Updated CSV", df.to_csv(index=False), "checkins.csv")