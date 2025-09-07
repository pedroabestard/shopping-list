# 🛒 Shared Shopping List (Streamlit + Google Sheets)

A collaborative shopping list app built with **Streamlit** and **Google Sheets**.  
The app lets family members (or teams) add, update, and delete items in a shared shopping list.  
All data is synced live with Google Sheets, so everyone sees the same list in real-time.

---

## ✨ Features

- 📦 Add items with **name, quantity, and unit**.  
- 🔄 Prevents duplicates — adding the same item **updates instead of duplicating**.  
- ❌ Remove items with a simple button.  
- 📝 Add and manage **notes** for each store.  
- 🗂️ Organized into **store-specific tabs** (`Sedanos`, `Martinez`, `Farmacia`).  
- ☁️ Data persistence via **Google Sheets** (shared with all users).  
- ⚡ Built with **Streamlit**, quick to deploy and easy to share.

---

## 📂 Project Structure

```
.
├── app.py          # Main Streamlit app
├── README.md       # Project documentation
├── ss1.png         # Project screenshot
├── ss2.png         # Project screenshot
├── ss3.png         # Project screenshot
└── requirements.txt # Python dependencies
```

---

## ⚙️ Setup Instructions

1. **Clone this repo**:
   ```bash
   git clone https://github.com/your-username/shopping-list.git
   cd shopping-list
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Sheets**:
   - Create a Google Cloud Project and enable **Google Sheets API** + **Google Drive API**.  
   - Create a **Service Account** and download the JSON credentials.  
   - Add the service account email to your Google Sheet with **Editor** permissions.  
   - Your Google Sheet must have **two worksheets**:
     - `Shopping List` → with headers: `item | qty | unit | tab`
     - `Notes` → with headers: `note | tab`

5. **Add your credentials to Streamlit**:
   - Save your JSON credentials in `.streamlit/secrets.toml`:
     ```toml
     [gcp_service_account]
     type = "service_account"
     project_id = "your-project-id"
     private_key_id = "..."
     private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
     client_email = "your-service-account@project.iam.gserviceaccount.com"
     client_id = "..."
     ```

6. **Run the app locally**:
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Deployment

Easily deploy to **[Streamlit Cloud](https://streamlit.io/cloud)**:

- Push this repo to GitHub.  
- Connect the repo to Streamlit Cloud.  
- Add your **secrets** (same as `.streamlit/secrets.toml`) in Streamlit Cloud settings.  
- Done ✅

---

## 📸 Screenshots

_Add your own screenshots here after running the app._

Example layout:

- Shopping List items aligned in columns.  
- Notes section at the bottom.  

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) – for the web UI  
- [Google Sheets](https://www.google.com/sheets/about/) – as the shared database  
- [gspread](https://github.com/burnash/gspread) – Google Sheets API wrapper  
- [oauth2client](https://github.com/googleapis/oauth2client) – for authentication  

---

## 🤝 Contributing

Pull requests are welcome!  
If you find a bug or have a feature request, please open an [issue](../../issues).

---

## 📄 License

MIT License – feel free to use and modify for your own projects.
