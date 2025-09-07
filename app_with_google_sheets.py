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
sheet_items = client.open(SHEET_NAME).worksheet("Shopping List")  # items
sheet_notes = client.open(SHEET_NAME).worksheet("Notes")          # notes

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
def load_items():
    return sheet_items.get_all_records()

@st.cache_data(ttl=60)
def load_notes():
    return sheet_notes.get_all_records()

def save_item(item, qty, unit, tab):
    """Insert or update an item in Shopping List sheet"""
    rows = sheet_items.get_all_records()
    for i, row in enumerate(rows, start=2):
        if row["tab"] == tab and row["item"].lower() == item.lower():
            # Update existing
            sheet_items.update(f"A{i}:D{i}", [[item, qty, unit, tab]])
            st.cache_data.clear()
            return
    # If not found, append
    sheet_items.append_row([item, qty, unit, tab])
    st.cache_data.clear()

def delete_item(row_index):
    sheet_items.delete_rows(row_index)
    st.cache_data.clear()

def save_note(note, tab):
    """Insert note in Notes sheet (no duplicates)"""
    rows = sheet_notes.get_all_records()
    for i, row in enumerate(rows, start=2):
        if row["tab"] == tab and row["note"].lower() == note.lower():
            return  # prevent duplicates
    sheet_notes.append_row([note, tab])
    st.cache_data.clear()

def delete_note(row_index):
    sheet_notes.delete_rows(row_index)
    st.cache_data.clear()

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🛒 Shared Shopping List")

items_data = load_items()
notes_data = load_notes()

tabs = st.tabs(["Sedanos", "Martinez", "Farmacia"])

for store, tab in zip(PREDEFINED_ITEMS.keys(), tabs):
    with tab:
        st.subheader(f"{store} List")

        # -----------------------------
        # Show existing items aligned
        # -----------------------------
        store_items = [
            (i, row) for i, row in enumerate(items_data, start=2)
            if row["tab"] == store
        ]

        if store_items:
            header = st.columns([4, 1, 2, 1])
            header[0].markdown("**Item**")
            header[1].markdown("**Qty**")
            header[2].markdown("**Unit**")
            header[3].markdown("**Delete**")

            for row_index, row in store_items:
                cols = st.columns([4, 1, 2, 1])
                cols[0].write(row["item"])
                cols[1].write(row["qty"])
                cols[2].write(row["unit"])
                if cols[3].button("❌", key=f"del_item_{store}_{row_index}"):
                    delete_item(row_index)
                    st.rerun()
        else:
            st.info("No items yet.")

        st.markdown("---")

        # -----------------------------
        # Notes Section
        # -----------------------------
        st.subheader(f"📝 Notes for {store}")

        store_notes = [
            (i, row) for i, row in enumerate(notes_data, start=2)
            if row["tab"] == store
        ]

        if store_notes:
            for row_index, row in store_notes:
                cols = st.columns([8, 1])
                cols[0].write(f"• {row['note']}")
                if cols[1].button("❌", key=f"del_note_{store}_{row_index}"):
                    delete_note(row_index)
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
                save_item(item, qty, unit, store)
                st.success(f"Added {item} ({qty} {unit}) to {store}")
                st.rerun()

        st.markdown("---")

        # -----------------------------
        # Add Notes Section (bottom)
        # -----------------------------

        with st.form(key=f"note_{store}"):
            note = st.text_input("Add a note (max 100 chars)", max_chars=100)
            submitted_note = st.form_submit_button("Add Note")
            if submitted_note and note:
                save_note(note, store)
                st.success(f"Added note: {note}")
                st.rerun()