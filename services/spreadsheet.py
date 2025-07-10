import os
import re
import datetime
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# ══════════════ ENV SETUP ══════════════
load_dotenv()
SINGLE_SSID = os.getenv("SINGLE_SSID")
CREDS_PATH = os.getenv("SERVICE_ACCOUNT_PATH")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
CREDS = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
SPREADSHEET_CLIENT = gspread.authorize(CREDS)
CLIENT = SPREADSHEET_CLIENT

# ══════════════ UTILITIES ══════════════
def _norm(val):
    return re.sub(r"\s+", " ", str(val)).strip().casefold()

def _next_id(ws) -> str:
    ids = ws.col_values(1)[1:]
    return str(int(ids[-1]) + 1) if ids else "1"

def _ensure_header(ws):
    default_header = [
        "No", "User ID", "Timestamp", "Kategori",
        "Nama Sales", "Telda", "STO",
        "POI Name", "Alamat", "Ekosistem", "Visit ke",
        "Nama PIC", "Jabatan PIC", "HP",
        "Provider", "Provider Detail", "Abonemen", "Kegiatan",
        "Feedback", "Feedback Detail", "Informasi Detail", "Photo URL"
    ]

    if ws.title.strip().lower() == "follow up":
        header = default_header + ["Hasil FU"]
    else:
        header = default_header

    existing_header = ws.row_values(1)
    if existing_header != header:
        if ws.row_count > 0:
            ws.delete_rows(1)
        ws.insert_row(header, 1)

def _get_sheet_by_kategori(kategori: str):
    sheet_name = "Visit Baru" if kategori == "Visit Baru" else "Follow Up"
    return CLIENT.open_by_key(SINGLE_SSID).worksheet(sheet_name)

# ══════════════ SIMPAN DATA BERDASARKAN KATEGORI ══════════════
def save_data(data: dict) -> str:
    kategori = data.get("kategori", "Visit Baru")
    ws = _get_sheet_by_kategori(kategori)
    _ensure_header(ws)

    now_wib = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

    # Buat key unik lokasi (tanpa alamat)
    key = (
        _norm(data.get("telda")),
        _norm(data.get("sto")),
        _norm(data.get("poi_name")),
    )

    # Ambil semua entri dari kedua sheet
    sh = SPREADSHEET_CLIENT.open_by_key(SINGLE_SSID)
    all_rows = []
    for sheetname in ["Visit Baru", "Follow Up"]:
        try:
            rows = sh.worksheet(sheetname).get_all_records()
            for row in rows:
                row_key = (
                    _norm(row.get("Telda")),
                    _norm(row.get("STO")),
                    _norm(row.get("POI Name")),
                )
                if row_key == key:
                    all_rows.append(row)
        except Exception:
            continue

    visit_ke = len(all_rows) + 1

    row_vals = [
        _next_id(ws),
        data.get("user_id"),
        now_wib,
        kategori,
        data.get("nama_sales"),
        data.get("telda"),
        data.get("sto"),
        data.get("poi_name"),
        data.get("address"),
        data.get("ekosistem"),
        str(visit_ke),
        data.get("contact_name"),
        data.get("contact_position"),
        data.get("contact_phone"),
        data.get("provider"),
        data.get("provider_detail"),
        data.get("cost"),
        data.get("kegiatan"),
        data.get("feedback"),
        data.get("feedback_detail"),
        data.get("detail_info"),
    ]

    # Tambahkan hasil_fu jika Follow Up
    if kategori == "Follow Up":
        row_vals.append(data.get("hasil_fu", "-"))
    
    row_vals.append(data.get("photo_url"))

    ws.append_row(row_vals, value_input_option="USER_ENTERED")
    return f"➕ Data berhasil ditambahkan ke {kategori} (Visit ke-{visit_ke})"

# ══════════════ AMBIL DATA 30 HARI TERAKHIR DARI SEMUA SHEET ══════════════
def get_last_30_days_data():
    data_all = []
    for sheet_name in ["Visit Baru", "Follow Up"]:
        try:
            ws = CLIENT.open_by_key(SINGLE_SSID).worksheet(sheet_name)
            _ensure_header(ws)

            now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
            since = now - datetime.timedelta(days=30)

            for r in ws.get_all_records():
                try:
                    ts = datetime.datetime.strptime(r["Timestamp"], "%Y-%m-%d %H:%M:%S")
                    if ts >= since:
                        r["timestamp"] = ts
                        data_all.append(r)
                except ValueError:
                    continue
        except Exception:
            continue

    return sorted(data_all, key=lambda x: x["timestamp"], reverse=True)