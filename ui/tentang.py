import os
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt
import database
from ui.style import apply_shadow

class TentangPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        self.tabs = __import__('PySide6.QtWidgets', fromlist=['QTabWidget']).QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #cbd5e1; border-radius: 8px; background: #ffffff; padding: 10px; }
            QTabBar::tab { background: #e2e8f0; color: #475569; padding: 10px 20px; font-weight: bold; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #ffffff; color: #3b82f6; border: 1px solid #cbd5e1; border-bottom: none; }
        """)

        # Tab 1: Tentang Aplikasi
        tab_tentang = QWidget()
        self.setup_tentang_tab(tab_tentang)
        self.tabs.addTab(tab_tentang, "Tentang Aplikasi")

        # Tab 2: Panduan Penggunaan
        tab_panduan = QWidget()
        self.setup_panduan_tab(tab_panduan)
        self.tabs.addTab(tab_panduan, "Panduan Penggunaan")

        layout.addWidget(self.tabs)

    def setup_tentang_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setObjectName("AboutCard")
        card.setProperty("class", "Card")
        card.setMinimumWidth(500)
        card.setMaximumWidth(600)
        card.setStyleSheet("QFrame#AboutCard { background-color: #ffffff; border-radius: 12px; }")
        apply_shadow(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)

        app_title = QLabel("Aplikasi Surat Otomatis Desa")
        app_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a365d; text-align: center;")
        app_title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(app_title)

        app_version = QLabel("Versi Desktop 1.0.0 (Offline Edition)")
        app_version.setStyleSheet("font-size: 13px; color: #64748b;")
        app_version.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(app_version)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #e2e8f0;")
        card_layout.addWidget(line)

        app_desc = QLabel(
            "Sistem Informasi pelayanan surat menyurat administrasi desa secara mandiri. "
            "Dirancang khusus untuk dapat beroperasi 100% tanpa jaringan internet, "
            "menggunakan database SQLite lokal dan pengolah kata Microsoft Word / LibreOffice."
        )
        app_desc.setStyleSheet("font-size: 13px; color: #475569; line-height: 1.4;")
        app_desc.setWordWrap(True)
        app_desc.setAlignment(Qt.AlignJustify)
        card_layout.addWidget(app_desc)

        card_layout.addSpacing(10)

        db_path = Path("database/surat.db").resolve()
        backup_path = Path("backup").resolve()

        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        info_layout.addWidget(self.create_info_row("Lokasi Database:", str(db_path)))
        info_layout.addWidget(self.create_info_row("Lokasi Backup:", str(backup_path)))
        info_layout.addWidget(self.create_info_row("Pengembang:", "Tau ri Attang Salo"))
        info_layout.addWidget(self.create_info_row("Lisensi:", "MIT License"))

        card_layout.addLayout(info_layout)
        layout.addWidget(card)

    def setup_panduan_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        from PySide6.QtWidgets import QTextEdit
        txt_panduan = QTextEdit()
        txt_panduan.setReadOnly(True)
        txt_panduan.setStyleSheet("background-color: #f8fafc; border: 1px solid #e2e8f0; padding: 15px; font-size: 13px; color: #334155; line-height: 1.6;")
        
        panduan_html = """
        <h2>Buku Panduan Penggunaan SI-DESAKU</h2>
        
        <h3>1. Login dan Akun Default</h3>
        <ul>
            <li><b>Username:</b> admin</li>
            <li><b>Password:</b> admin123</li>
            <li>Jika lupa password, klik tulisan <b>Lupa Password?</b> di halaman login lalu masukkan Recovery Key: <b>RESET-DESAKU</b> untuk mereset sandi admin kembali ke default.</li>
        </ul>
        
        <h3>2. Mengelola Data Penduduk</h3>
        <ul>
            <li>Pilih menu <b>Data Penduduk</b>. Di sini Anda bisa menambah, mengedit, atau menghapus data warga secara manual.</li>
            <li><b>Import Excel:</b> Untuk memasukkan data jumlah besar, klik tab <i>Import Excel</i>, klik <b>Unduh Template Excel</b>, isi data sesuai format, lalu unggah (Import) kembali.</li>
        </ul>
        
        <h3>3. Mencetak Surat (Buat Surat)</h3>
        <ul>
            <li>Pastikan data pemohon (NIK/Nama) sudah ada di menu Data Penduduk.</li>
            <li>Pilih menu <b>Buat Surat</b>. Cari penduduk berdasarkan nama atau NIK.</li>
            <li>Pilih jenis surat (misal: Surat Domisili, SKTM, dll).</li>
            <li>Klik <b>Generate Dokumen</b>. Aplikasi akan otomatis membuatkan file Word (.docx) dan PDF.</li>
        </ul>
        
        <h3>4. Pengaturan Sistem</h3>
        <ul>
            <li>Di menu <b>Pengaturan</b>, Anda wajib mengisi data instansi (Nama Desa, Kecamatan, Nama Kepala Desa, dsb).</li>
            <li>Atur juga <b>Counter Surat</b> jika Anda ingin melanjutkan nomor registrasi surat lama.</li>
            <li>Anda juga dapat mengubah <b>Password Akun</b> Anda di menu Pengaturan ini demi keamanan.</li>
        </ul>
        """
        txt_panduan.setHtml(panduan_html)
        layout.addWidget(txt_panduan)

    def create_info_row(self, label, value):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        lbl = QLabel(label)
        lbl.setStyleSheet("font-weight: bold; color: #475569; min-width: 130px;")
        
        val = QLabel(value)
        val.setStyleSheet("color: #1e293b;")
        val.setWordWrap(True)
        val.setTextInteractionFlags(Qt.TextSelectableByMouse)

        row_layout.addWidget(lbl)
        row_layout.addWidget(val, stretch=1)
        return row
