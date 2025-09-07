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
worksheet = client.open(SHEET_NAME).sheet1  # 👈 ensure correct sheet

# -----------------------------
# Predefined Items per Store
# -----------------------------
PREDEFINED_ITEMS = {
    "Sedanos": [
        "Limon", "Tomate", "Pepino", "Cebolla morada", "Cebolla amarilla",
        "Cebolla blanca", "Ajo", "Guineo", "Platano macho", "Platano Burro",
        "Malanga", "Boniato", "Sweet potato", "Papas", "Melon", "Manzana",
        "Papaya", "Uvas", "Pimiento ojo", "Pimiento verde", "Pimiento amarillo",
        "Col", "Ensalada Caesar", "Jamon", "Queso gouda", "Queso parmesano", "Leche",
        "Huevos", "Salchicha", "Chorizo colombiano", "Mantequilla", "Yogurt de sabor",
        "Yogurt plano", "Mayonesa", "Leche condensada", "Ketchup", "Mostaza", "Aceitunas",
        "Mayoracha", "Leche evaporada", "Agua", "Malta Hatuey", "Refresco Piñita",
        "Coca cola zero", "Coca Cola regular", "Cerveza", "Malta bucanero",
        "Pure de tomate", "Cafe", "Adobo Goya", "Lemon-Pepper", "Sal", "Tajin",
        "Salsa Maggie", "Comino", "Miel", "Azucar", "Chocolate", "Palomitas de Maiz",
        "Nutella", "Bizcocho", "Aceite de cocina", "Aceite de Oliva", "Frijoles", "Spaghettis",
        "Arroz", "Chicharos", "Helado de Chocolate", "Helado de Cookies and Cream",
        "Helado de Cafe", "Helado de Mantecado", "Helado de Vainilla", "Galletas saladas",
        "Pan de Hamburgues", "Tortilla de Maiz", "Tortilla de Harina", "Pan de Sandwich",
        "Maruchan", "Chicles", "Crema"
    ],
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
    """Append a new row to Google Sheets"""
    worksheet.append_row([item, qty, unit, tab, row_type])
    st.cache_data.clear()  # refresh cache

def delete_item(row_index):
    """Delete a row by index (Google Sheets is 1-based)"""
    worksheet.delete_rows(row_index)
    st.cache_data.clear()  # refresh cache

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
            row for row in data
            if row["tab"] == store and row.get("type", "item") == "item"
        ]
        if store_items:
            for i, row in enumerate(store_items, start=2):  # row index starts at 2 (1 = header)
                st.write(f"- {row['item']} ({row['qty']} {row['unit']})")
                if st.button(f"❌ Delete {row['item']}", key=f"del_{store}_{i}"):
                    delete_item(i)
                    st.rerun()
        else:
            st.info("No items yet.")

        st.markdown("---")

        # -----------------------------
        # Notes Section
        # -----------------------------
        st.subheader(f"📝 Notes for {store}")

        store_notes = [
            row for row in data
            if row["tab"] == store and row.get("type", "item") == "note"
        ]
        if store_notes:
            for i, row in enumerate(store_notes, start=2):
                st.write(f"• {row['item']}")
                if st.button(f"❌ Delete note", key=f"del_note_{store}_{i}"):
                    delete_item(i)
                    st.rerun()
        else:
            st.info("No notes yet.")

        with st.form(key=f"note_{store}"):
            note = st.text_input("Add a note (max 100 chars)", max_chars=100)
            submitted_note = st.form_submit_button("Add Note")
            if submitted_note and note:
                save_item(note, "", "", store, row_type="note")
                st.success(f"Added note: {note}")
                st.rerun()

        st.markdown("---")

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

