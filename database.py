import os
import sys
import sqlite3
import hashlib
import json
import shutil
from pathlib import Path

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

DB_DIR = Path("database")
DB_PATH = DB_DIR / "surat.db"
CONFIG_PATH = Path("config.json")

def load_config():
    """Load configuration from config.json. If missing, copy from bundle or create default."""
    if not CONFIG_PATH.exists():
        bundled_config_path = get_resource_path("config.json")
        if os.path.exists(bundled_config_path) and os.path.abspath(bundled_config_path) != os.path.abspath(str(CONFIG_PATH)):
            try:
                shutil.copy(bundled_config_path, str(CONFIG_PATH))
            except Exception as e:
                print(f"Failed to copy bundled config: {e}")

        if not CONFIG_PATH.exists():
            default_config = {
                "instansi": {
                    "desa": "Kampokku Jaya",
                    "kecamatan": "Pakkampong",
                    "kabupaten": "Limpo",
                    "provinsi": "Limpo Toddang",
                    "alamat": "Jl. Raya Kampong No. 01, Desa Kampokku Jaya",
                    "telepon": "(0123) 456789"
                },
                "penomoran": {
                    "format": "470/{{NOMOR}}/DS/{{TAHUN}}",
                    "counter": 1
                },
                "penandatangan": {
                    "nama": "H. Baco Tang, S.IP",
                    "nip": "",
                    "jabatan": "Kepala Desa"
                },
                "penyimpanan": {
                    "folder_docx": "output/docx",
                    "folder_pdf": "output/pdf"
                },
                "printer": {
                    "default": ""
                }
            }
            save_config(default_config)
            return default_config

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def save_config(config):
    """Save configuration to config.json."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

DB_DIR = Path("database")
DB_PATH = DB_DIR / "surat.db"

def get_connection():
    """Create a database connection and return it."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    """Initialize database tables and default data."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Penduduk Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS penduduk (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nik TEXT UNIQUE NOT NULL,
        kk TEXT NOT NULL,
        nama TEXT NOT NULL,
        tempat_lahir TEXT,
        tanggal_lahir TEXT,
        jenis_kelamin TEXT,
        agama TEXT,
        status_perkawinan TEXT,
        pekerjaan TEXT,
        alamat TEXT,
        rt TEXT,
        rw TEXT,
        desa TEXT,
        kecamatan TEXT,
        kabupaten TEXT,
        provinsi TEXT,
        kewarganegaraan TEXT DEFAULT 'WNI'
    )
    """)

    # 2. Template Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS template (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama_template TEXT NOT NULL,
        jenis_surat TEXT NOT NULL,
        file_template TEXT NOT NULL UNIQUE,
        aktif INTEGER DEFAULT 1
    )
    """)

    # 3. Riwayat Surat Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS riwayat_surat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nomor_surat TEXT NOT NULL,
        tanggal TEXT NOT NULL,
        nik TEXT NOT NULL,
        nama TEXT NOT NULL,
        jenis_surat TEXT NOT NULL,
        file_docx TEXT NOT NULL,
        file_pdf TEXT,
        petugas TEXT NOT NULL
    )
    """)

    # 4. User Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # Insert default admin user if table is empty
    cursor.execute("SELECT COUNT(*) FROM user")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), "Admin")
        )
        cursor.execute(
            "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)",
            ("petugas", hash_password("petugas123"), "Petugas")
        )

    # Insert default templates if empty
    cursor.execute("SELECT COUNT(*) FROM template")
    if cursor.fetchone()[0] == 0:
        default_templates = [
            ("Surat Keterangan Domisili", "Domisili", "Domisili.docx", 1),
            ("Surat Keterangan Tidak Mampu", "SKTM", "SKTM.docx", 1),
            ("Surat Keterangan Usaha", "Usaha", "Usaha.docx", 1),
            ("Surat Keterangan Belum Menikah", "Belum Menikah", "BelumMenikah.docx", 1)
        ]
        cursor.executemany(
            "INSERT INTO template (nama_template, jenis_surat, file_template, aktif) VALUES (?, ?, ?, ?)",
            default_templates
        )

    conn.commit()
    conn.close()

# --- USER MANAGEMENT ---
def authenticate_user(username, password):
    """Authenticate user credentials."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, role FROM user WHERE username = ? AND password_hash = ?",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def change_user_password(username, new_password):
    """Change a user's password."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user SET password_hash = ? WHERE username = ?",
        (hash_password(new_password), username)
    )
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0

# --- PENDUDUK (RESIDENT) CRUD ---
def get_all_penduduk(limit=100, offset=0):
    """Fetch all residents with pagination."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM penduduk ORDER BY nama ASC LIMIT ? OFFSET ?", (limit, offset))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def count_penduduk():
    """Get total number of residents."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM penduduk")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_penduduk_by_nik(nik):
    """Get a single resident by NIK."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM penduduk WHERE nik = ?", (nik,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_penduduk(data):
    """Add a new resident."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO penduduk (
            nik, kk, nama, tempat_lahir, tanggal_lahir, jenis_kelamin, agama,
            status_perkawinan, pekerjaan, alamat, rt, rw, desa, kecamatan,
            kabupaten, provinsi, kewarganegaraan
        ) VALUES (
            :nik, :kk, :nama, :tempat_lahir, :tanggal_lahir, :jenis_kelamin, :agama,
            :status_perkawinan, :pekerjaan, :alamat, :rt, :rw, :desa, :kecamatan,
            :kabupaten, :provinsi, :kewarganegaraan
        )
        """, data)
        conn.commit()
        return True, "Data penduduk berhasil ditambahkan."
    except sqlite3.IntegrityError:
        return False, f"NIK '{data.get('nik')}' sudah terdaftar dalam sistem."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_penduduk(resident_id, data):
    """Update resident data."""
    conn = get_connection()
    cursor = conn.cursor()
    data['id'] = resident_id
    try:
        cursor.execute("""
        UPDATE penduduk SET
            nik = :nik, kk = :kk, nama = :nama, tempat_lahir = :tempat_lahir,
            tanggal_lahir = :tanggal_lahir, jenis_kelamin = :jenis_kelamin, agama = :agama,
            status_perkawinan = :status_perkawinan, pekerjaan = :pekerjaan, alamat = :alamat,
            rt = :rt, rw = :rw, desa = :desa, kecamatan = :kecamatan,
            kabupaten = :kabupaten, provinsi = :provinsi, kewarganegaraan = :kewarganegaraan
        WHERE id = :id
        """, data)
        conn.commit()
        return True, "Data penduduk berhasil diperbarui."
    except sqlite3.IntegrityError:
        return False, f"NIK '{data.get('nik')}' sudah digunakan oleh penduduk lain."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_penduduk(resident_id):
    """Delete a resident."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM penduduk WHERE id = ?", (resident_id,))
    conn.commit()
    conn.close()

def search_penduduk(query, limit=100):
    """Search resident by NIK, KK, or Nama."""
    conn = get_connection()
    cursor = conn.cursor()
    search_str = f"%{query}%"
    cursor.execute("""
    SELECT * FROM penduduk
    WHERE nik LIKE ? OR kk LIKE ? OR nama LIKE ?
    ORDER BY nama ASC LIMIT ?
    """, (search_str, search_str, search_str, limit))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

# --- TEMPLATE CRUD ---
def get_all_templates():
    """Fetch all document templates."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM template ORDER BY nama_template ASC")
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def get_active_templates():
    """Fetch active templates."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM template WHERE aktif = 1 ORDER BY nama_template ASC")
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def add_template(nama_template, jenis_surat, file_template, aktif=1):
    """Add a new template."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO template (nama_template, jenis_surat, file_template, aktif) VALUES (?, ?, ?, ?)",
            (nama_template, jenis_surat, file_template, aktif)
        )
        conn.commit()
        return True, "Template berhasil ditambahkan."
    except sqlite3.IntegrityError:
        return False, f"File template '{file_template}' sudah ada."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_template(template_id, nama_template, jenis_surat, file_template, aktif):
    """Update template info."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        UPDATE template SET
            nama_template = ?, jenis_surat = ?, file_template = ?, aktif = ?
        WHERE id = ?
        """, (nama_template, jenis_surat, file_template, aktif, template_id))
        conn.commit()
        return True, "Template berhasil diperbarui."
    except sqlite3.IntegrityError:
        return False, f"File template '{file_template}' sudah digunakan."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_template(template_id):
    """Delete a template."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM template WHERE id = ?", (template_id,))
    conn.commit()
    conn.close()

# --- RIWAYAT SURAT ---
def add_riwayat(nomor_surat, tanggal, nik, nama, jenis_surat, file_docx, file_pdf, petugas):
    """Log generated letter details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO riwayat_surat (
        nomor_surat, tanggal, nik, nama, jenis_surat, file_docx, file_pdf, petugas
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nomor_surat, tanggal, nik, nama, jenis_surat, file_docx, file_pdf, petugas))
    conn.commit()
    conn.close()

def get_all_riwayat(filter_time="all", query=""):
    """Fetch history logs with time filters and search terms."""
    conn = get_connection()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM riwayat_surat WHERE 1=1"
    params = []
    
    # 1. Apply Date Filter
    if filter_time == "today":
        sql += " AND tanggal LIKE ?"
        import datetime
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        params.append(f"{today_str}%")
    elif filter_time == "month":
        sql += " AND tanggal LIKE ?"
        import datetime
        month_str = datetime.date.today().strftime("%Y-%m-")
        params.append(f"{month_str}%")
    elif filter_time == "year":
        sql += " AND tanggal LIKE ?"
        import datetime
        year_str = datetime.date.today().strftime("%Y-")
        params.append(f"{year_str}%")

    # 2. Apply Query Filter
    if query:
        sql += " AND (nik LIKE ? OR nama LIKE ? OR nomor_surat LIKE ?)"
        q_str = f"%{query}%"
        params.extend([q_str, q_str, q_str])

    sql += " ORDER BY id DESC"
    cursor.execute(sql, params)
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def count_surat_today():
    """Get letters printed today."""
    import datetime
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM riwayat_surat WHERE tanggal LIKE ?", (f"{today_str}%",))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def count_surat_this_month():
    """Get letters printed this month."""
    import datetime
    month_str = datetime.date.today().strftime("%Y-%m-")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM riwayat_surat WHERE tanggal LIKE ?", (f"{month_str}%",))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_stat_surat():
    """Get statistics grouped by type and date for dashboard charts."""
    conn = get_connection()
    cursor = conn.cursor()
    # Let's return count of letters generated grouped by jenis_surat
    cursor.execute("SELECT jenis_surat, COUNT(*) as jumlah FROM riwayat_surat GROUP BY jenis_surat")
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return data
