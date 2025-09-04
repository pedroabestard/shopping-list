import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -----------------------------
# Google Sheets Setup
# -----------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(credentials)

SHEET_NAME = "ShoppingList"
try:
    sheet = client.open(SHEET_NAME).sheet1
except gspread.SpreadsheetNotFound:
    st.error(f"Google Sheet '{SHEET_NAME}' not found. Create it and share with service account.")
    st.stop()

# -----------------------------
# Default Users and Items
# -----------------------------
default_items = [
    "Limon", "Tomate", "Pepino", "Cebolla morada", "Cebolla amarilla", "Cebolla blanca",
    "Ajo", "Guineo", "Platano macho", "Platano Burro", "Malanga", "Boniato", "Sweet potato",
    "Papas", "Melon", "Manzana", "Papaya", "Uvas", "Pimiento ojo", "Pimiento verde",
    "Pimiento amarillo", "Col", "Ensalada Caesar", "Jamon", "Queso gouda", "Queso parmesano",
    "Leche", "Huevos", "Salchicha", "Chorizo colombiano", "Mantequilla", "Yogurt de sabor",
    "Yogurt plano", "Mayonesa", "Leche condensada", "Ketchup", "Mostaza", "Aceitunas",
    "Mayoracha", "Leche evaporada", "Agua", "Malta Hatuey", "Refresco Piñita",
    "Coca cola zero", "Coca Cola regular", "Cerveza", "Malta bucanero", "Pure de tomate",
    "Cafe", "Adobo Goya", "Lemon-Pepper", "Sal", "Tajin", "Salsa Maggie", "Comino", "Miel",
    "Azucar", "Chocolate", "Palomitas de Maiz", "Nutella", "Bizcocho", "Aceite de cocina",
    "Aceite de Oliva", "Frijoles", "Spaghettis", "Arroz", "Chicharos", "Helado de Chocolate",
    "Helado de Cookies and Cream", "Helado de Cafe", "Helado de Mantecado", "Helado de Vainilla",
    "Galletas saladas", "Pan de Hamburgues", "Tortilla de Maiz", "Tortilla de Harina",
    "Pan de Sandwich", "Maruchan", "Chicles"
]

units = ["", "pounds", "units", "kg", "liters", "bottles", "packs"]
tabs = ["Sedanos", "Martinez", "Farmacia"]

# -----------------------------
# Helper Functions
# -----------------------------
def load_data():
    data = sheet.get_all_records()
    return data

def save_item(item, qty, unit, tab):
    sheet.append_row([item, qty, unit, tab])

def delete_item(row_index):
    sheet.delete_rows(row_index)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🛒 Family Shopping List")

# Filter by tab
selected_tab = st.selectbox("🛍️ Select Store", options=tabs)

# Header
cols = st.columns([3, 1, 1, 1])
cols[0].markdown("**Item**")
cols[1].markdown("**Qty**")
cols[2].markdown("**Unit**")
cols[3].markdown("**Action**")

# Load and filter data
data = load_data()
filtered_data = [row for row in data if row.get("tab") == selected_tab]

# Display items
for i, row in enumerate(filtered_data, start=2):  # start=2 because row 1 is headers
    if row.get("tab") != selected_tab:
        continue
    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
    c1.write(row["item"])
    c2.write(row["qty"])
    c3.write(row["unit"])
    if c4.button("❌ Delete", key=f"del_{i}"):
        delete_item(i)
        st.rerun()

st.divider()

# Add new item
st.subheader("➕ Add New Item")
with st.form("add_item_form"):
    item = st.selectbox("Item", options=[""] + default_items)
    qty = st.number_input("Quantity", min_value=0, step=1)
    unit = st.selectbox("Unit", options=units)
    tab = st.selectbox("Store Tab", options=tabs)
    submitted = st.form_submit_button("Add")
    if submitted and item:
        save_item(item, qty, unit, tab)
        st.success(f"Added {item} ({qty} {unit}) to {tab}")
        st.experimental_rerun()