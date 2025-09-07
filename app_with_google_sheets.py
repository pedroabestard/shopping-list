import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# -----------------------------
# Google Sheets Setup
# -----------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(credentials)

SHEET_NAME = "Shopping List"
worksheet = client.open(SHEET_NAME).sheet1  # 👈 ensure correct sheet

# -----------------------------
# Predefined Items per Store
# -----------------------------
PREDEFINED_ITEMS = {
    "Sedanos": ["Limon", "Tomate", "Pepino", "Cebolla morada", "Cebolla amarilla"],
    "Martinez": ["Pierna de pollo", "Bistec de Cerdo", "Bistec de res", "Chuleta ahumada"],
    "Farmacia": ["Peptobismol", "Omeprazol", "Vitaminas"]
}

# -----------------------------
# Data Functions
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    """Fetch all rows from Google Sheets"""
    return worksheet.get_all_records()

def save_item(item, qty, unit, tab, row_type="item"):
    """Insert or update item/note in Google Sheets"""
    rows = worksheet.get_all_records()
    headers = worksheet.row_values(1)

    # Check if sheet has "type" column
    if "type" not in headers:
        worksheet.update_cell(1, len(headers) + 1, "type")
        headers.append("type")
        # Fill existing rows with "item"
        for i in range(2, len(rows) + 2):
            worksheet.update_cell(i, len(headers), "item")

    # Search for existing
    for i, row in enumerate(rows, start=2):
        if row["tab"] == tab and row["item"].lower() == item.lower() and row.get("type", "item") == row_type:
            # Update existing row
            worksheet.update(f"A{i}:E{i}", [[item, qty, unit, tab, row_type]])
            st.cache_data.clear()
            return

    # If not found → append new
    worksheet.append_row([item, qty, unit, tab, row_type])
    st.cache_data.clear()

def delete_item(row_index):
    """Delete a row by index (Google Sheets is 1-based)"""
    worksheet.delete_rows(row_index)
    st.cache_data.clear()

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🛒 Shared Shopping List")

data = load_data()

tabs = st.tabs(["Sedanos", "Martinez", "Farmacia"])

for store, tab in zip(PREDEFINED_ITEMS.keys(), tabs):
    with tab:
        st.subheader(f"{store} List")

        # -----------------------------
        # Show existing items
        # -----------------------------
        store_items = [
            (i, row) for i, row in enumerate(data, start=2)
            if row["tab"] == store and row.get("type", "item") == "item"
        ]

        if store_items:
            df = pd.DataFrame(
                [{"Item": row["item"], "Qty": row["qty"], "Unit": row["unit"]} for _, row in store_items]
            )
            df["Delete"] = ""

            st.dataframe(df, use_container_width=True, hide_index=True)

            for idx, (i, row) in enumerate(store_items):
                if st.button("❌", key=f"del_item_{store}_{i}"):
                    delete_item(i)
                    st.rerun()
        else:
            st.info("No items yet.")

        st.markdown("---")

        # -----------------------------
        # Showed Notes Section
        # -----------------------------
        st.subheader(f"📝 Notes for {store}")

        store_notes = [
            (i, row) for i, row in enumerate(data, start=2)
            if row["tab"] == store and row.get("type", "item") == "note"
        ]

        if store_notes:
            for i, row in store_notes:
                st.write(f"• {row['item']}")
                if st.button("❌", key=f"del_note_{store}_{i}"):
                    delete_item(i)
                    st.rerun()
        else:
            st.info("No notes yet.")

        # -----------------------------
        # Add new item
        # -----------------------------
        st.subheader(f"➕ Add Item to {store}")
        with st.form(key=f"add_{store}"):
            if PREDEFINED_ITEMS[store]:
                item = st.selectbox("Select product", PREDEFINED_ITEMS[store] + ["Other"])
                if item == "Other":
                    item = st.text_input("Enter product name")
            else:
                item = st.text_input("Enter product name")

            qty = st.number_input("Quantity", min_value=1, value=1)
            unit = st.text_input("Unit (e.g., kg, pack, bottle)", value="")

            submitted = st.form_submit_button("Add")
            if submitted and item:
                save_item(item, qty, unit, store, row_type="item")
                st.success(f"Added {item} ({qty} {unit}) to {store}")
                st.rerun()

        st.markdown("---")

        # -----------------------------
        # Adding Notes Section (bottom)
        # -----------------------------

        with st.form(key=f"note_{store}"):
            note = st.text_input("Add a note (max 100 chars)", max_chars=100)
            submitted_note = st.form_submit_button("Add Note")
            if submitted_note and note:
                save_item(note, "", "", store, row_type="note")
                st.success(f"Added note: {note}")
                st.rerun()
