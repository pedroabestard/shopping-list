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
worksheet = client.open(SHEET_NAME).sheet1  # Make sure this is the correct sheet

# -----------------------------
# Predefined Items per Store
# -----------------------------
PREDEFINED_ITEMS = {
    "Sedanos": [
        "Limon", "Tomate", "Pepino", "Cebolla morada", "Cebolla amarilla", "Cebolla blanca",
        "Ajo", "Guineo", "Platano macho", "Platano Burro", "Malanga", "Boniato",
        "Sweet potato", "Papas", "Melon", "Manzana", "Papaya", "Uvas",
        "Pimiento rojo", "Pimiento verde", "Pimiento amarillo", "Col", "Ensalada Caesar",
        "Jamon", "Queso gouda", "Queso parmesano", "Leche", "Huevos",
        "Salchicha", "Chorizo colombiano", "Mantequilla", "Yogurt de sabor", "Yogurt plano",
        "Mayonesa", "Leche condensada", "Ketchup", "Mostaza", "Aceitunas",
        "Mayoracha", "Leche evaporada", "Agua", "Malta Hatuey", "Refresco Piñita",
        "Coca cola zero", "Coca Cola regular", "Cerveza", "Malta bucanero",
        "Pure de tomate", "Cafe", "Adobo Goya", "Lemon-Pepper", "Sal",
        "Tajin", "Salsa Maggie", "Comino", "Miel", "Azucar",
        "Chocolate", "Palomitas de Maiz", "Nutella", "Bizcocho",
        "Aceite de cocina", "Aceite de Oliva", "Frijoles", "Spaghettis",
        "Arroz", "Chicharos", "Helado de Chocolate", "Helado de Cookies and Cream",
        "Helado de Cafe", "Helado de Mantecado", "Helado de Vainilla",
        "Galletas saladas", "Pan de Hamburgues", "Tortilla de Maiz",
        "Tortilla de Harina", "Pan de Sandwich", "Maruchan", "Chicles"
    ],
    "Martinez": ["Pierna de pollo", "Bistec de Cerdo", "Bistec de res", "Chuleta ahumada"],
    "Farmacia": ["Peptobismol", "Omeprazol", "Vitaminas"]
}

# -----------------------------
# Helper Functions
# -----------------------------
@st.cache_data(ttl=60)
def load_data():
    """Fetch all rows from Google Sheets and normalize keys to lowercase"""
    raw_data = worksheet.get_all_records()
    return [{k.lower(): v for k, v in row.items()} for row in raw_data]

def save_item(item, qty, unit, tab, comments):
    """Append or overwrite a row in Google Sheets"""
    data = load_data()
    row_index = None
    for i, row in enumerate(data, start=2):
        if row.get("tab") == tab and row.get("item").strip().lower() == item.strip().lower():
            row_index = i
            break

    if row_index:
        worksheet.update(f"A{row_index}:E{row_index}", [[item, qty, unit, comments, tab]])
    else:
        worksheet.append_row([item, qty, unit, comments, tab])

    st.cache_data.clear()

def delete_item(row_index):
    """Delete a row by index"""
    worksheet.delete_rows(row_index)
    st.cache_data.clear()

def update_comment(row_index, comment):
    """Update comment only"""
    worksheet.update(f"D{row_index}", [[comment]])  # D = 4th column (comments)
    st.cache_data.clear()

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

        # Headers
        header_cols = st.columns([2,1,1,4,1])
        header_cols[0].markdown("**Item**")
        header_cols[1].markdown("**Qty**")
        header_cols[2].markdown("**Unit**")
        header_cols[3].markdown("**Comment**")
        header_cols[4].markdown("**Action**")

        store_items = [row for row in data if row.get("tab") == store]

        # Display rows
        for i, row in enumerate(store_items, start=2):
            c1, c2, c3, c4, c5 = st.columns([2,1,1,4,1])
            c1.write(row.get("item", ""))
            c2.write(row.get("qty", ""))
            c3.write(row.get("unit", ""))

            # Editable comment
            comment_key = f"comment_{store}_{i}"
            comment_value = st.text_input("", value=row.get("comments", ""), key=comment_key)

            # Save comment button
            if c4.button("💾", key=f"save_comment_{store}_{i}"):
                update_comment(i, comment_value)
                st.success("Comment updated!")
                st.rerun()

            # Delete item button
            if c5.button("❌ Delete", key=f"del_{store}_{i}"):
                delete_item(i)
                st.rerun()

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

            # Optional quantity
            qty_input = st.text_input("Quantity (optional)", value="")
            qty = qty_input if qty_input.strip() != "" else ""

            # Optional unit
            unit = st.text_input("Unit (optional)", value="")

            # Optional comment
            comments = st.text_input("Comment (optional)", value="")

            submitted = st.form_submit_button("Add")
            if submitted and item:
                save_item(item, qty, unit, store, comments)
                msg = f"Added {item}"
                if qty or unit or comments:
                    msg += f" ({qty} {unit}" if qty or unit else ""
                    if comments:
                        msg += f", Comment: {comments}"
                    msg += ")"
                msg += f" to {store}"
                st.success(msg)
                st.rerun()