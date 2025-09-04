import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
worksheet = client.open(SHEET_NAME).sheet1  # Make sure this is your sheet

# -----------------------------
# Predefined Items per Store
# -----------------------------
PREDEFINED_ITEMS = {
    "Sedanos": [
        "Limon", "Tomate", "Pepino", "Cebolla morada", "Cebolla amarilla", "Cebolla blanca",
        "Ajo", "Guineo", "Platano macho", "Platano Burro", "Malanga", "Boniato",
        "Sweet potato", "Papas", "Melon", "Manzana", "Papaya", "Uvas"
    ],
    "Martinez": ["Pierna de pollo", "Bistec de Cerdo", "Bistec de res", "Chuleta ahumada"],
    "Farmacia": ["Peptobismol", "Omeprazol", "Vitaminas"]
}

# -----------------------------
# Helper Functions
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    """Fetch all rows from Google Sheets"""
    raw_data = worksheet.get_all_records()
    # normalize keys to lowercase
    return [{k.lower(): v for k, v in row.items()} for row in raw_data]

def save_item(item, qty, unit, tab):
    """Append a new row to Google Sheets"""
    worksheet.append_row([item, qty, unit, tab])
    st.cache_data.clear()  # refresh cache

def delete_item(row_index):
    """Delete a row by index (1-based in Google Sheets)"""
    worksheet.delete_rows(row_index)
    st.cache_data.clear()  # refresh cache

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="🛒 Family Shopping List", layout="wide")
st.title("🛒 Shared Shopping List")

data = load_data()
tabs = st.tabs(["Sedanos", "Martinez", "Farmacia"])

for store, tab in zip(PREDEFINED_ITEMS.keys(), tabs):
    with tab:
        st.subheader(f"{store} List")

        # Filter items for this store
        store_items = [row for row in data if row.get("tab") == store]

        # Display items in a table with delete buttons
        if store_items:
            for i, row in enumerate(store_items, start=2):  # row 1 = headers
                cols = st.columns([4, 1, 1, 1])
                cols[0].write(row.get("item", ""))
                cols[1].write(row.get("qty", ""))
                cols[2].write(row.get("unit", ""))
                if cols[3].button("❌ Delete", key=f"del_{store}_{i}"):
                    delete_item(i)
                    st.rerun()
        else:
            st.info("No items yet.")

        st.markdown("---")

        # Add new item
        st.subheader(f"➕ Add Item to {store}")
        with st.form(key=f"add_{store}"):
            # Predefined items dropdown or free text
            if PREDEFINED_ITEMS[store]:
                item = st.selectbox(
                    "Select product", PREDEFINED_ITEMS[store] + ["Other"]
                )
                if item == "Other":
                    item = st.text_input("Enter product name")
            else:
                item = st.text_input("Enter product name")

            qty = st.number_input("Quantity", min_value=1, value=1)
            unit = st.text_input("Unit (e.g., kg, pack, bottle)", value="")

            submitted = st.form_submit_button("Add")
            if submitted and item:
                save_item(item, qty, unit, store)
                st.success(f"Added {item} ({qty} {unit}) to {store}")
                st.rerun()
