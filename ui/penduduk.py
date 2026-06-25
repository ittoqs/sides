import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDialog, QFormLayout, QComboBox, QMessageBox,
                             QFileDialog, QTabWidget, QGroupBox, QScrollArea, QTextEdit)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QIcon
import database
from excel_handler import ExcelHandler
from ui.style import apply_shadow

class ResidentDialog(QDialog):
    """Dialog for adding or editing a resident's details."""
    def __init__(self, resident_data=None, parent=None):
        super().__init__(parent)
        self.resident_data = resident_data
        self.setWindowTitle("Tambah Penduduk" if not resident_data else "Edit Penduduk")
        self.resize(550, 650)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Scroll Area for Form since there are many fields
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        form_widget = QWidget()
        self.form_layout = QFormLayout(form_widget)
        self.form_layout.setSpacing(12)
        self.form_layout.setLabelAlignment(Qt.AlignLeft)

        # Fields Definitions
        self.inputs = {}
        
        fields = [
            ("nik", "NIK", "16 Digit Nomor Induk Kependudukan"),
            ("kk", "Nomor KK", "16 Digit Nomor Kartu Keluarga"),
            ("nama", "Nama Lengkap", "Nama sesuai KTP"),
            ("tempat_lahir", "Tempat Lahir", "Kota/Kabupaten Lahir"),
            ("tanggal_lahir", "Tanggal Lahir", "Format: YYYY-MM-DD (Contoh: 1995-12-31)"),
            ("jenis_kelamin", "Jenis Kelamin", ["Laki-laki", "Perempuan"]),
            ("agama", "Agama", ["Islam", "Kristen", "Katolik", "Hindu", "Budha", "Khonghucu", "Lainnya"]),
            ("status_perkawinan", "Status Perkawinan", ["Belum Kawin", "Kawin", "Cerai Hidup", "Cerai Mati"]),
            ("pekerjaan", "Pekerjaan", "Contoh: Karyawan Swasta, Petani, PNS"),
            ("alamat", "Alamat Lengkap", "Nama Jalan, Dusun, Kampung, No. Rumah"),
            ("rt", "RT", "Contoh: 004"),
            ("rw", "RW", "Contoh: 002"),
            ("desa", "Desa / Kelurahan", ""),
            ("kecamatan", "Kecamatan", ""),
            ("kabupaten", "Kabupaten / Kota", ""),
            ("provinsi", "Provinsi", ""),
            ("kewarganegaraan", "Kewarganegaraan", ["WNI", "WNA"])
        ]

        # Get default location settings to prefill Desa, Kec, Kab, Prov
        config = database.load_config()
        instansi = config.get("instansi", {})

        for field_name, label, desc in fields:
            lbl = QLabel(label)
            lbl.setProperty("class", "FormLabel")
            
            if isinstance(desc, list):
                # Combobox field
                combo = QComboBox()
                combo.addItems(desc)
                self.inputs[field_name] = combo
                self.form_layout.addRow(lbl, combo)
            else:
                # Text input field
                txt = QLineEdit()
                txt.setPlaceholderText(desc)
                
                # Auto fill default from config if adding new
                if not self.resident_data:
                    if field_name == "desa":
                        txt.setText(instansi.get("desa", ""))
                    elif field_name == "kecamatan":
                        txt.setText(instansi.get("kecamatan", ""))
                    elif field_name == "kabupaten":
                        txt.setText(instansi.get("kabupaten", ""))
                    elif field_name == "provinsi":
                        txt.setText(instansi.get("provinsi", ""))
                        
                self.inputs[field_name] = txt
                self.form_layout.addRow(lbl, txt)

        scroll.setWidget(form_widget)
        main_layout.addWidget(scroll)

        # Pre-fill data if editing
        if self.resident_data:
            for field_name, widget in self.inputs.items():
                val = self.resident_data.get(field_name, "")
                if isinstance(widget, QComboBox):
                    idx = widget.findText(val)
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
                    else:
                        widget.setCurrentText(val)
                else:
                    widget.setText(str(val))

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_cancel = QPushButton("Batal")
        btn_cancel.setProperty("class", "SecondaryButton")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Simpan")
        btn_save.setProperty("class", "PrimaryButton")
        btn_save.clicked.connect(self.save_data)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        main_layout.addLayout(btn_layout)

    def save_data(self):
        # Gather data
        data = {}
        for field_name, widget in self.inputs.items():
            if isinstance(widget, QComboBox):
                data[field_name] = widget.currentText()
            else:
                data[field_name] = widget.text().strip()

        # Validation
        if not data["nik"] or len(data["nik"]) != 16 or not data["nik"].isdigit():
            QMessageBox.warning(self, "Validasi Gagal", "NIK harus berupa 16 digit angka.")
            return
        if not data["nama"]:
            QMessageBox.warning(self, "Validasi Gagal", "Nama Lengkap wajib diisi.")
            return

        # Save to DB
        if self.resident_data:
            # Edit
            success, msg = database.update_penduduk(self.resident_data["id"], data)
        else:
            # Add
            success, msg = database.add_penduduk(data)

        if success:
            QMessageBox.information(self, "Sukses", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Gagal", msg)


class PendudukPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_page = 0
        self.rows_per_page = 15
        self.selected_excel_path = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #cbd5e1; border-radius: 8px; background: #ffffff; padding: 10px; }
            QTabBar::tab { background: #e2e8f0; color: #475569; padding: 10px 20px; font-weight: bold; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #ffffff; color: #3b82f6; border: 1px solid #cbd5e1; border-bottom: none; }
        """)

        # Tab 1: Database Penduduk
        tab_list = QWidget()
        self.setup_list_tab(tab_list)
        self.tabs.addTab(tab_list, "Daftar Penduduk")

        # Tab 2: Impor Excel
        tab_import = QWidget()
        self.setup_import_tab(tab_import)
        self.tabs.addTab(tab_import, "Import Excel")

        layout.addWidget(self.tabs)
        self.refresh_table()

    def setup_list_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Toolbar Row
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Cari berdasarkan NIK, KK, atau Nama...")
        self.txt_search.textChanged.connect(self.search_data)
        
        btn_add = QPushButton("Tambah Penduduk")
        btn_add.setProperty("class", "SuccessButton")
        btn_add.clicked.connect(self.add_resident)

        toolbar.addWidget(self.txt_search, stretch=1)
        toolbar.addWidget(btn_add)
        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "NIK", "No. KK", "Nama Lengkap", "L/P", "Pekerjaan", "Alamat", "Aksi"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Pagination controls
        pagi_layout = QHBoxLayout()
        self.btn_prev = QPushButton("Sebelumnya")
        self.btn_prev.setProperty("class", "SecondaryButton")
        self.btn_prev.clicked.connect(self.prev_page)
        
        self.lbl_page = QLabel("Halaman 1")
        self.lbl_page.setStyleSheet("font-weight: bold; color: #475569;")
        
        self.btn_next = QPushButton("Selanjutnya")
        self.btn_next.setProperty("class", "SecondaryButton")
        self.btn_next.clicked.connect(self.next_page)
        
        pagi_layout.addWidget(self.btn_prev)
        pagi_layout.addStretch()
        pagi_layout.addWidget(self.lbl_page)
        pagi_layout.addStretch()
        pagi_layout.addWidget(self.btn_next)
        layout.addLayout(pagi_layout)

    def setup_import_tab(self, tab):
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)

        # Step 1: File Picker Group
        picker_group = QGroupBox("1. Pilih File Excel")
        picker_layout = QHBoxLayout(picker_group)
        self.lbl_file_status = QLabel("Belum ada file yang dipilih.")
        self.lbl_file_status.setStyleSheet("color: #64748b; font-style: italic;")
        
        btn_pick = QPushButton("Pilih File (.xlsx)")
        btn_pick.setProperty("class", "PrimaryButton")
        btn_pick.clicked.connect(self.pick_excel)
        
        btn_download_tpl = QPushButton("Unduh Template Excel")
        btn_download_tpl.setProperty("class", "SecondaryButton")
        btn_download_tpl.clicked.connect(self.download_template)
        
        picker_layout.addWidget(btn_pick)
        picker_layout.addWidget(btn_download_tpl)
        picker_layout.addWidget(self.lbl_file_status, stretch=1)
        layout.addWidget(picker_group)

        # Step 2: Mapping and Preview Row
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(15)

        # Column Mapping Box (Left)
        mapping_group = QGroupBox("2. Pemetaan Kolom")
        mapping_group.setMinimumWidth(250)
        mapping_group.setMaximumWidth(300)
        self.mapping_form_layout = QFormLayout(mapping_group)
        self.mapping_form_layout.setSpacing(8)
        self.mapping_form_layout.setContentsMargins(10, 15, 10, 10)
        
        self.map_combos = {}
        db_fields = [
            ("nik", "NIK (*)"),
            ("kk", "No. KK"),
            ("nama", "Nama (*)"),
            ("tempat_lahir", "Tempat Lahir"),
            ("tanggal_lahir", "Tgl Lahir (YYYY-MM-DD)"),
            ("jenis_kelamin", "L/P"),
            ("agama", "Agama"),
            ("status_perkawinan", "Status Kawin"),
            ("pekerjaan", "Pekerjaan"),
            ("alamat", "Alamat"),
            ("rt", "RT"),
            ("rw", "RW"),
            ("desa", "Desa/Kelurahan"),
            ("kecamatan", "Kecamatan"),
            ("kabupaten", "Kabupaten/Kota"),
            ("provinsi", "Provinsi"),
            ("kewarganegaraan", "Kewarganegaraan")
        ]
        
        for field, label in db_fields:
            combo = QComboBox()
            combo.setPlaceholderText("Pilih Kolom...")
            self.map_combos[field] = combo
            self.mapping_form_layout.addRow(QLabel(label), combo)

        middle_layout.addWidget(mapping_group)

        # Sheet Preview Box (Right)
        preview_group = QGroupBox("3. Pratinjau Data (Maks 5 Baris)")
        preview_layout = QVBoxLayout(preview_group)
        self.table_preview = QTableWidget()
        self.table_preview.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_preview.setAlternatingRowColors(True)
        preview_layout.addWidget(self.table_preview)
        
        middle_layout.addWidget(preview_group, stretch=1)
        layout.addLayout(middle_layout)

        # Step 3: Run & Logs Row
        import_btn_layout = QHBoxLayout()
        self.btn_import = QPushButton("Mulai Import Data")
        self.btn_import.setProperty("class", "SuccessButton")
        self.btn_import.clicked.connect(self.run_import)
        self.btn_import.setEnabled(False)
        import_btn_layout.addStretch()
        import_btn_layout.addWidget(self.btn_import)
        layout.addLayout(import_btn_layout)

        # Log Console
        log_group = QGroupBox("Log Aktivitas Import")
        log_layout = QVBoxLayout(log_group)
        self.txt_logs = QTextEdit()
        self.txt_logs.setReadOnly(True)
        self.txt_logs.setStyleSheet("background-color: #0f172a; color: #10b981; font-family: Courier New; font-size: 12px;")
        log_layout.addWidget(self.txt_logs)
        layout.addWidget(log_group, stretch=1)

    # --- PENDUDUK CRUD ACTIONS ---
    def refresh_table(self):
        offset = self.current_page * self.rows_per_page
        query = self.txt_search.text().strip()
        
        if query:
            residents = database.search_penduduk(query, limit=self.rows_per_page)
            total = len(residents) # simplistic pagination for search
            self.btn_prev.setEnabled(False)
            self.btn_next.setEnabled(False)
            self.lbl_page.setText(f"Pencarian: {total} Temuan")
        else:
            residents = database.get_all_penduduk(limit=self.rows_per_page, offset=offset)
            total_db = database.count_penduduk()
            total_pages = max(1, (total_db + self.rows_per_page - 1) // self.rows_per_page)
            
            self.btn_prev.setEnabled(self.current_page > 0)
            self.btn_next.setEnabled(offset + self.rows_per_page < total_db)
            self.lbl_page.setText(f"Halaman {self.current_page + 1} dari {total_pages}")

        self.table.setRowCount(len(residents))
        for idx, row in enumerate(residents):
            self.table.setItem(idx, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(idx, 1, QTableWidgetItem(row["nik"]))
            self.table.setItem(idx, 2, QTableWidgetItem(row["kk"]))
            self.table.setItem(idx, 3, QTableWidgetItem(row["nama"]))
            self.table.setItem(idx, 4, QTableWidgetItem(row["jenis_kelamin"][:1] if row["jenis_kelamin"] else ""))
            self.table.setItem(idx, 5, QTableWidgetItem(row["pekerjaan"]))
            self.table.setItem(idx, 6, QTableWidgetItem(row["alamat"]))

            # Action buttons cell
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(5)

            btn_edit = QPushButton("Edit")
            btn_edit.setProperty("class", "PrimaryButton")
            btn_edit.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            # capture variables using default argument
            btn_edit.clicked.connect(lambda checked=False, r=row: self.edit_resident(r))

            btn_delete = QPushButton("Hapus")
            btn_delete.setProperty("class", "DangerButton")
            btn_delete.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            btn_delete.clicked.connect(lambda checked=False, r=row: self.delete_resident(r))

            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)
            
            cell_widget = QWidget()
            cell_widget.setLayout(actions_layout)
            self.table.setCellWidget(idx, 7, cell_widget)

    def search_data(self):
        self.current_page = 0
        self.refresh_table()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh_table()

    def next_page(self):
        self.current_page += 1
        self.refresh_table()

    def add_resident(self):
        dlg = ResidentDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.refresh_table()

    def edit_resident(self, resident):
        dlg = ResidentDialog(resident_data=resident, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.refresh_table()

    def delete_resident(self, resident):
        ans = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus data {resident['nama']} (NIK: {resident['nik']})?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            database.delete_penduduk(resident["id"])
            self.refresh_table()

    # --- IMPOR EXCEL ACTIONS ---
    def pick_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Excel Penduduk", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.selected_excel_path = file_path
            self.lbl_file_status.setText(os.path.basename(file_path))
            self.btn_import.setEnabled(True)
            self.load_excel_preview()

    def load_excel_preview(self):
        headers = ExcelHandler.read_headers(self.selected_excel_path)
        preview_data = ExcelHandler.preview_data(self.selected_excel_path, limit=5)

        # 1. Update Preview Table
        self.table_preview.setColumnCount(len(headers))
        self.table_preview.setHorizontalHeaderLabels(headers)
        self.table_preview.setRowCount(len(preview_data))
        
        for row_idx, row in enumerate(preview_data):
            for col_idx, cell in enumerate(row):
                self.table_preview.setItem(row_idx, col_idx, QTableWidgetItem(str(cell)))
        
        self.table_preview.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)

        # 2. Update column mapping comboboxes
        for field, combo in self.map_combos.items():
            combo.clear()
            combo.addItem("") # empty select
            combo.addItems(headers)

            # Auto mapping heuristics based on common column names
            matching_idx = 0
            for idx, h in enumerate(headers):
                h_lower = h.lower()
                field_lower = field.lower()
                # Check direct or similar matches
                if field_lower == h_lower:
                    matching_idx = idx + 1
                    break
                elif field_lower == "nik" and ("nik" in h_lower or "nomor induk kependudukan" in h_lower):
                    matching_idx = idx + 1
                    break
                elif field_lower == "kk" and ("kk" in h_lower or "no. kk" in h_lower or "nomor kk" in h_lower or "kartu keluarga" in h_lower):
                    matching_idx = idx + 1
                    break
                elif field_lower == "nama" and ("nama" in h_lower or "nama lengkap" in h_lower):
                    matching_idx = idx + 1
                    break
                elif field_lower == "jenis_kelamin" and ("kelamin" in h_lower or "gender" in h_lower or "sex" in h_lower or "l/p" in h_lower or "lp" in h_lower):
                    matching_idx = idx + 1
                    break
                elif field_lower == "tanggal_lahir" and ("lahir" in h_lower and "tgl" in h_lower or "tanggal" in h_lower):
                    matching_idx = idx + 1
                    break
                elif field_lower == "tempat_lahir" and ("tempat" in h_lower or "tpt" in h_lower):
                    matching_idx = idx + 1
                    break
                    
            combo.setCurrentIndex(matching_idx)

    def run_import(self):
        if not self.selected_excel_path:
            return

        # Build column mapping dictionary
        column_mapping = {}
        for field, combo in self.map_combos.items():
            column_mapping[field] = combo.currentText()

        # Validation on mandatory fields: NIK and NAMA must be mapped
        if not column_mapping.get("nik"):
            QMessageBox.critical(self, "Gagal", "Anda harus memetakan kolom NIK.")
            return
        if not column_mapping.get("nama"):
            QMessageBox.critical(self, "Gagal", "Anda harus memetakan kolom Nama.")
            return

        # Start execution
        self.txt_logs.clear()
        self.txt_logs.append("=== Memulai Proses Import Penduduk ===")
        self.txt_logs.append(f"Membaca file: {os.path.basename(self.selected_excel_path)}")

        success_count, error_count, logs = ExcelHandler.import_excel(
            self.selected_excel_path, column_mapping
        )

        for log in logs:
            self.txt_logs.append(log)

        self.txt_logs.append("\n=== Proses Selesai ===")
        self.txt_logs.append(f"Berhasil: {success_count} data")
        self.txt_logs.append(f"Gagal: {error_count} data")
        
        QMessageBox.information(
            self, "Import Selesai",
            f"Proses import selesai!\nBerhasil: {success_count} data\nGagal/Dilewati: {error_count} data"
        )
        self.refresh_table()

    def download_template(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan Template Penduduk", "Template_Data_Penduduk.xlsx", "Excel Files (*.xlsx)"
        )
        if file_path:
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            success, msg = ExcelHandler.generate_template(file_path)
            if success:
                QMessageBox.information(self, "Sukses", f"Template berhasil disimpan ke:\n{file_path}")
            else:
                QMessageBox.critical(self, "Gagal", msg)
