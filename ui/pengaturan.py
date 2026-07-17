import os
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFrame, 
                             QFormLayout, QComboBox, QGroupBox, QFileDialog, QScrollArea)
from PySide6.QtCore import Qt
import database
import document_generator
from ui.style import apply_shadow

class PengaturanPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)

        # 1. Profil Desa / Kelurahan
        g_desa = QGroupBox("1. Profil Instansi (Desa/Kelurahan)")
        f_desa = QFormLayout(g_desa)
        f_desa.setSpacing(10)
        
        self.txt_desa = QLineEdit()
        self.txt_kec = QLineEdit()
        self.txt_kab = QLineEdit()
        self.txt_prov = QLineEdit()
        self.txt_alamat = QLineEdit()
        self.txt_telp = QLineEdit()

        f_desa.addRow(QLabel("Nama Desa:"), self.txt_desa)
        f_desa.addRow(QLabel("Kecamatan:"), self.txt_kec)
        f_desa.addRow(QLabel("Kabupaten / Kota:"), self.txt_kab)
        f_desa.addRow(QLabel("Provinsi:"), self.txt_prov)
        f_desa.addRow(QLabel("Alamat Kantor:"), self.txt_alamat)
        f_desa.addRow(QLabel("Telepon Kantor:"), self.txt_telp)
        container_layout.addWidget(g_desa)

        # 2. Penandatangan (Kepala Desa)
        g_kades = QGroupBox("2. Penandatangan Dokumen")
        f_kades = QFormLayout(g_kades)
        f_kades.setSpacing(10)
        
        self.txt_kades_nama = QLineEdit()
        self.txt_kades_nip = QLineEdit()
        self.txt_kades_jabatan = QLineEdit()

        f_kades.addRow(QLabel("Nama Pejabat:"), self.txt_kades_nama)
        f_kades.addRow(QLabel("NIP Pejabat:"), self.txt_kades_nip)
        f_kades.addRow(QLabel("Jabatan Pejabat:"), self.txt_kades_jabatan)
        container_layout.addWidget(g_kades)

        # 3. Format Penomoran
        g_format = QGroupBox("3. Penomoran Surat Otomatis")
        f_format = QFormLayout(g_format)
        f_format.setSpacing(10)
        
        self.txt_format_num = QLineEdit()
        self.txt_counter = QLineEdit()
        
        f_format.addRow(QLabel("Format Nomor Surat:"), self.txt_format_num)
        f_format.addRow(QLabel("Counter Nomor Selanjutnya:"), self.txt_counter)
        
        lbl_hint = QLabel("Gunakan {{NOMOR}} untuk nomor urut dan {{TAHUN}} untuk tahun aktif.\nContoh: 470/{{NOMOR}}/DS/{{TAHUN}}")
        lbl_hint.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        f_format.addRow(QLabel(""), lbl_hint)
        container_layout.addWidget(g_format)

        # 4. Lokasi Penyimpanan & PDF Engine
        g_store = QGroupBox("4. Folder Penyimpanan & Konverter PDF")
        f_store = QFormLayout(g_store)
        f_store.setSpacing(10)
        
        self.txt_dir_docx = QLineEdit()
        self.txt_dir_pdf = QLineEdit()
        self.txt_libreoffice_path = QLineEdit()

        # Docx path row
        layout_docx = QHBoxLayout()
        layout_docx.addWidget(self.txt_dir_docx)
        btn_dir_docx = QPushButton("Pilih Folder")
        btn_dir_docx.setProperty("class", "SecondaryButton")
        btn_dir_docx.setStyleSheet("padding: 5px 10px;")
        btn_dir_docx.clicked.connect(lambda: self.browse_dir(self.txt_dir_docx))
        layout_docx.addWidget(btn_dir_docx)
        f_store.addRow(QLabel("Penyimpanan Word (DOCX):"), layout_docx)

        # PDF path row
        layout_pdf = QHBoxLayout()
        layout_pdf.addWidget(self.txt_dir_pdf)
        btn_dir_pdf = QPushButton("Pilih Folder")
        btn_dir_pdf.setProperty("class", "SecondaryButton")
        btn_dir_pdf.setStyleSheet("padding: 5px 10px;")
        btn_dir_pdf.clicked.connect(lambda: self.browse_dir(self.txt_dir_pdf))
        layout_pdf.addWidget(btn_dir_pdf)
        f_store.addRow(QLabel("Penyimpanan PDF:"), layout_pdf)

        # Custom LibreOffice executable path (for bundling LibreOffice portable)
        layout_lo = QHBoxLayout()
        layout_lo.addWidget(self.txt_libreoffice_path)
        btn_lo = QPushButton("Pilih Berkas")
        btn_lo.setProperty("class", "SecondaryButton")
        btn_lo.setStyleSheet("padding: 5px 10px;")
        btn_lo.clicked.connect(self.browse_lo_exec)
        layout_lo.addWidget(btn_lo)
        f_store.addRow(QLabel("Jalur LibreOffice (Optional):"), layout_lo)
        
        lbl_lo_hint = QLabel("Jalur langsung ke executable 'soffice.exe' atau 'libreoffice'. Kosongkan untuk deteksi otomatis.")
        lbl_lo_hint.setStyleSheet("color: #64748b; font-size: 11px; font-style: italic;")
        f_store.addRow(QLabel(""), lbl_lo_hint)

        container_layout.addWidget(g_store)

        # 5. Printer Default
        g_print = QGroupBox("5. Printer Default")
        f_print = QFormLayout(g_print)
        f_print.setSpacing(10)
        
        self.combo_printer = QComboBox()
        self.combo_printer.addItem("Default Sistem", "")
        f_print.addRow(QLabel("Pilih Printer:"), self.combo_printer)
        container_layout.addWidget(g_print)

        # 6. Keamanan (Ganti Password)
        g_sec = QGroupBox("6. Keamanan Akun")
        f_sec = QFormLayout(g_sec)
        f_sec.setSpacing(10)
        
        self.txt_pass_baru = QLineEdit()
        self.txt_pass_baru.setEchoMode(QLineEdit.Password)
        self.txt_pass_baru.setPlaceholderText("Kosongkan jika tidak ingin mengubah password")
        
        self.txt_pass_konfirm = QLineEdit()
        self.txt_pass_konfirm.setEchoMode(QLineEdit.Password)
        self.txt_pass_konfirm.setPlaceholderText("Ketik ulang password baru")
        
        f_sec.addRow(QLabel("Password Baru:"), self.txt_pass_baru)
        f_sec.addRow(QLabel("Konfirmasi Password:"), self.txt_pass_konfirm)
        container_layout.addWidget(g_sec)

        # 7. Save Button Frame
        save_layout = QHBoxLayout()
        btn_save = QPushButton("Simpan Pengaturan")
        btn_save.setProperty("class", "PrimaryButton")
        btn_save.setStyleSheet("padding: 12px 24px; font-size: 14px;")
        btn_save.clicked.connect(self.save_settings)
        save_layout.addStretch()
        save_layout.addWidget(btn_save)
        container_layout.addLayout(save_layout)

        container_layout.addStretch(1)  # Push everything up to prevent cutoff

        # Set Scroll Area Policies
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        # Load values
        self.load_settings()
        self.load_printers()

    def browse_dir(self, line_edit):
        folder = QFileDialog.getExistingDirectory(
            self, "Pilih Folder Penyimpanan",
            options=QFileDialog.DontUseNativeDialog
        )
        if folder:
            line_edit.setText(folder)

    def browse_lo_exec(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Berkas LibreOffice Executable", "", 
            "Executables (soffice soffice.exe libreoffice)",
            options=QFileDialog.DontUseNativeDialog
        )
        if file_path:
            self.txt_libreoffice_path.setText(file_path)

    def load_settings(self):
        config = database.load_config()

        instansi = config.get("instansi", {})
        self.txt_desa.setText(instansi.get("desa", ""))
        self.txt_kec.setText(instansi.get("kecamatan", ""))
        self.txt_kab.setText(instansi.get("kabupaten", ""))
        self.txt_prov.setText(instansi.get("provinsi", ""))
        self.txt_alamat.setText(instansi.get("alamat", ""))
        self.txt_telp.setText(instansi.get("telepon", ""))

        signatory = config.get("penandatangan", {})
        self.txt_kades_nama.setText(signatory.get("nama", ""))
        self.txt_kades_nip.setText(signatory.get("nip", ""))
        self.txt_kades_jabatan.setText(signatory.get("jabatan", ""))

        penomoran = config.get("penomoran", {})
        self.txt_format_num.setText(penomoran.get("format", ""))
        self.txt_counter.setText(str(penomoran.get("counter", 1)))

        storage = config.get("penyimpanan", {})
        self.txt_dir_docx.setText(storage.get("folder_docx", "output/docx"))
        self.txt_dir_pdf.setText(storage.get("folder_pdf", "output/pdf"))
        self.txt_libreoffice_path.setText(storage.get("libreoffice_path", ""))

    def load_printers(self):
        config = database.load_config()
        saved_printer = config.get("printer", {}).get("default", "")

        printers = document_generator.get_available_printers()
        for p in printers:
            self.combo_printer.addItem(p, p)

        idx = self.combo_printer.findData(saved_printer)
        if idx >= 0:
            self.combo_printer.setCurrentIndex(idx)

    def save_settings(self):
        # Validate counter
        counter_str = self.txt_counter.text().strip()
        if not counter_str.isdigit():
            QMessageBox.warning(self, "Validasi Gagal", "Counter nomor surat harus berupa angka bulat.")
            return

        # Validate password if changed
        pass_baru = self.txt_pass_baru.text().strip()
        pass_konfirm = self.txt_pass_konfirm.text().strip()
        if pass_baru or pass_konfirm:
            if pass_baru != pass_konfirm:
                QMessageBox.warning(self, "Validasi Gagal", "Konfirmasi password tidak cocok.")
                return
            if len(pass_baru) < 6:
                QMessageBox.warning(self, "Validasi Gagal", "Password minimal 6 karakter.")
                return
            
            # Apply password change for current active user
            cfg = database.load_config()
            active_user = cfg.get("user_aktif", "admin")
            database.change_user_password(active_user, pass_baru)
            self.txt_pass_baru.clear()
            self.txt_pass_konfirm.clear()
            QMessageBox.information(self, "Keamanan", "Password berhasil diubah.")

        # Prepare new config object
        config = {
            "instansi": {
                "desa": self.txt_desa.text().strip(),
                "kecamatan": self.txt_kec.text().strip(),
                "kabupaten": self.txt_kab.text().strip(),
                "provinsi": self.txt_prov.text().strip(),
                "alamat": self.txt_alamat.text().strip(),
                "telepon": self.txt_telp.text().strip()
            },
            "penandatangan": {
                "nama": self.txt_kades_nama.text().strip(),
                "nip": self.txt_kades_nip.text().strip(),
                "jabatan": self.txt_kades_jabatan.text().strip()
            },
            "penomoran": {
                "format": self.txt_format_num.text().strip(),
                "counter": int(counter_str)
            },
            "penyimpanan": {
                "folder_docx": self.txt_dir_docx.text().strip(),
                "folder_pdf": self.txt_dir_pdf.text().strip(),
                "libreoffice_path": self.txt_libreoffice_path.text().strip()
            },
            "printer": {
                "default": self.combo_printer.currentData()
            }
        }

        # Write to disk
        database.save_config(config)
        QMessageBox.information(self, "Sukses", "Pengaturan instansi berhasil disimpan.")
        
        # Verify output dirs exist or create them
        Path(config["penyimpanan"]["folder_docx"]).mkdir(parents=True, exist_ok=True)
        Path(config["penyimpanan"]["folder_pdf"]).mkdir(parents=True, exist_ok=True)
