'''
import os
import re
import datetime
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# ══════════════ ENV ══════════════
load_dotenv()
SINGLE_SSID = os.getenv("SINGLE_SSID")                # Spreadsheet ID
CREDS_PATH  = os.getenv("SERVICE_ACCOUNT_PATH")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
CREDS  = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)

# ══════════════ UTILITIES ══════════════
def _sheet():
    return CLIENT.open_by_key(SINGLE_SSID).sheet1

def _ensure_header(ws):
    header = [
        "No", "User ID", "Timestamp", "Kategori",
        "Nama Sales", "Telda", "STO",
        "POI Name", "Alamat", "Ekosistem", "Visit ke",
        "Nama PIC", "Jabatan PIC", "HP",
        "Provider", "Provider Detail", "Abonemen", "Kegiatan",
        "Feedback", "Feedback Detail", "Info Tambahan", "Photo URL",
    ]
    if ws.row_count < 1 or ws.cell(1, 1).value != "No":
        ws.resize(1, len(header))
        ws.update("A1", [header])
    return header

def _next_id(ws) -> str:
    ids = ws.col_values(1)[1:]  # skip header
    return str(int(ids[-1]) + 1) if ids else "1"

def _norm(val):
    return re.sub(r"\s+", " ", str(val)).strip().casefold()

# ══════════════ SAVE SELALU TAMBAH BARU DENGAN VISIT KE ══════════════
def save_data(data: dict) -> str:
    """
    Selalu simpan sebagai baris baru.
    Hitung "Visit ke" berdasarkan kombinasi Telda + STO + POI Name + Alamat.
    """
    ws = _sheet()
    _ensure_header(ws)

    now_wib = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

    # Kunci unik untuk hitung "Visit ke"
    key = (
        _norm(data.get("telda")),
        _norm(data.get("sto")),
        _norm(data.get("poi_name")),
        _norm(data.get("address")),
    )

    all_rows = ws.get_all_records()
    visit_ke = 1
    for row in all_rows:
        row_key = (
            _norm(row.get("Telda")),
            _norm(row.get("STO")),
            _norm(row.get("POI Name")),
            _norm(row.get("Alamat")),
        )
        if row_key == key:
            visit_ke += 1

    row_vals = [
        _next_id(ws),
        data.get("user_id"),
        now_wib,
        data.get("kategori"),
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
        data.get("photo_url"),
    ]

    ws.append_row(row_vals, value_input_option="USER_ENTERED")
    return f"➕ Data berhasil ditambahkan (Visit ke-{visit_ke})."

# ══════════════ AMBIL DATA 30 HARI TERAKHIR ══════════════
def get_last_30_days_data():
    ws = _sheet()
    _ensure_header(ws)

    now = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    since = now - datetime.timedelta(days=30)

    result = []
    for r in ws.get_all_records():
        try:
            ts = datetime.datetime.strptime(r["Timestamp"], "%Y-%m-%d %H:%M:%S")
            if ts >= since:
                r["timestamp"] = ts
                result.append(r)
        except ValueError:
            continue

    return sorted(result, key=lambda x: x["timestamp"], reverse=True)
'''

import os
import re
import datetime
import gspread
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# ══════════════ ENV ══════════════
load_dotenv()
SINGLE_SSID = os.getenv("SINGLE_SSID")
CREDS_PATH = os.getenv("SERVICE_ACCOUNT_PATH")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
CREDS = Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)

# ══════════════ UTILITIES ══════════════
def _get_sheet_by_kategori(kategori: str):
    sheet_name = "Visit Baru" if kategori == "Visit Baru" else "Follow Up"
    return CLIENT.open_by_key(SINGLE_SSID).worksheet(sheet_name)

def _ensure_header(ws):
    header = [
        "No", "User ID", "Timestamp", "Kategori",
        "Nama Sales", "Telda", "STO",
        "POI Name", "Alamat", "Ekosistem", "Visit ke",
        "Nama PIC", "Jabatan PIC", "HP",
        "Provider", "Provider Detail", "Abonemen", "Kegiatan",
        "Feedback", "Feedback Detail", "Info Tambahan", "Photo URL",
    ]
    if ws.row_count < 1 or ws.cell(1, 1).value != "No":
        ws.resize(1, len(header))
        ws.update("A1", [header])
    return header

def _next_id(ws) -> str:
    ids = ws.col_values(1)[1:]
    return str(int(ids[-1]) + 1) if ids else "1"

def _norm(val):
    return re.sub(r"\s+", " ", str(val)).strip().casefold()

# ══════════════ SIMPAN DATA BERDASARKAN KATEGORI ══════════════
def save_data(data: dict) -> str:
    kategori = data.get("kategori", "Visit Baru")
    ws = _get_sheet_by_kategori(kategori)
    _ensure_header(ws)

    now_wib = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")

    # Buat kunci unik kunjungan
    key = (
        _norm(data.get("telda")),
        _norm(data.get("sto")),
        _norm(data.get("poi_name")),
        _norm(data.get("address")),
    )

    all_rows = ws.get_all_records()
    visit_ke = 1
    for row in all_rows:
        row_key = (
            _norm(row.get("Telda")),
            _norm(row.get("STO")),
            _norm(row.get("POI Name")),
            _norm(row.get("Alamat")),
        )
        if row_key == key:
            visit_ke += 1

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
        data.get("photo_url"),
    ]

    ws.append_row(row_vals, value_input_option="USER_ENTERED")
    return f"➕ Data berhasil ditambahkan ke *{kategori}* (Visit ke-{visit_ke})."

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