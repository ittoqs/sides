import os
import sys
import datetime
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QMessageBox, 
                             QFrame, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt
import database
import document_generator
from ui.style import apply_shadow

class BuatSuratPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_resident = None
        self.generated_docx = None
        self.generated_pdf = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Scroll Area for responsive layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        # STEP 1: NIK Search Box
        step1_frame = QFrame()
        step1_frame.setProperty("class", "Card")
        step1_frame.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 10px; }")
        apply_shadow(step1_frame)
        
        step1_layout = QHBoxLayout(step1_frame)
        step1_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_nik = QLabel("Masukkan NIK:")
        lbl_nik.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.txt_search_nik = QLineEdit()
        self.txt_search_nik.setPlaceholderText("Cari 16 Digit NIK...")
        self.txt_search_nik.setMaxLength(16)
        # Trigger search on Enter
        self.txt_search_nik.returnPressed.connect(self.search_resident)
        
        btn_search = QPushButton("Cari NIK")
        btn_search.setProperty("class", "PrimaryButton")
        btn_search.clicked.connect(self.search_resident)

        step1_layout.addWidget(lbl_nik)
        step1_layout.addWidget(self.txt_search_nik, stretch=1)
        step1_layout.addWidget(btn_search)
        layout.addWidget(step1_frame)

        # STEP 2: Resident Profile Display
        self.profile_frame = QFrame()
        self.profile_frame.setProperty("class", "Card")
        self.profile_frame.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 10px; }")
        apply_shadow(self.profile_frame)
        self.profile_frame.setVisible(False)

        profile_layout = QVBoxLayout(self.profile_frame)
        profile_layout.setContentsMargins(15, 15, 15, 15)
        
        profile_title = QLabel("Profil Penduduk")
        profile_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a; margin-bottom: 5px;")
        profile_layout.addWidget(profile_title)

        self.grid_profile = QGridLayout()
        self.grid_profile.setSpacing(10)
        profile_layout.addLayout(self.grid_profile)
        layout.addWidget(self.profile_frame)

        # STEP 3: Letter Generation Options
        self.gen_frame = QFrame()
        self.gen_frame.setProperty("class", "Card")
        self.gen_frame.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 10px; }")
        apply_shadow(self.gen_frame)
        self.gen_frame.setVisible(False)

        gen_layout = QVBoxLayout(self.gen_frame)
        gen_layout.setContentsMargins(15, 15, 15, 15)

        gen_title = QLabel("Detail Format Surat")
        gen_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #0f172a; margin-bottom: 10px;")
        gen_layout.addWidget(gen_title)

        options_layout = QHBoxLayout()
        options_layout.setSpacing(15)

        # Template Selection
        combo_vbox = QVBoxLayout()
        combo_vbox.addWidget(QLabel("Jenis Surat / Template:"))
        self.combo_template = QComboBox()
        self.combo_template.currentIndexChanged.connect(self.template_changed)
        combo_vbox.addWidget(self.combo_template)
        options_layout.addLayout(combo_vbox, stretch=1)

        # Letter Number input
        num_vbox = QVBoxLayout()
        num_vbox.addWidget(QLabel("Nomor Surat (Dihasilkan Otomatis):"))
        self.txt_letter_num = QLineEdit()
        num_vbox.addWidget(self.txt_letter_num)
        options_layout.addLayout(num_vbox, stretch=1)

        gen_layout.addLayout(options_layout)
        gen_layout.addSpacing(2)

        # Generate Buttons
        self.btn_generate = QPushButton("Generate Dokumen (Word & PDF)")
        self.btn_generate.setProperty("class", "SuccessButton")
        self.btn_generate.setStyleSheet("padding: 12px; font-size: 14px;")
        self.btn_generate.clicked.connect(self.generate_letter)
        gen_layout.addWidget(self.btn_generate)

        layout.addWidget(self.gen_frame)

        # STEP 4: Actions (Print / View)
        self.action_frame = QFrame()
        self.action_frame.setProperty("class", "Card")
        self.action_frame.setStyleSheet("QFrame { background-color: #ffffff; border-radius: 10px; border: 1.5px solid #10b981; }")
        apply_shadow(self.action_frame)
        self.action_frame.setVisible(False)

        action_layout = QVBoxLayout(self.action_frame)
        action_layout.setContentsMargins(15, 15, 15, 15)

        action_title = QLabel("Dokumen Berhasil Dibuat!")
        action_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #10b981; margin-bottom: 10px;")
        action_layout.addWidget(action_title)

        self.lbl_output_docx = QLabel("Word: ")
        self.lbl_output_pdf = QLabel("PDF: ")
        self.lbl_output_docx.setStyleSheet("color: #475569; font-size: 12px;")
        self.lbl_output_pdf.setStyleSheet("color: #475569; font-size: 12px;")
        action_layout.addWidget(self.lbl_output_docx)
        action_layout.addWidget(self.lbl_output_pdf)
        action_layout.addSpacing(5)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_open_word = QPushButton("Buka Word")
        self.btn_open_word.setProperty("class", "SecondaryButton")
        self.btn_open_word.clicked.connect(self.open_word)

        self.btn_open_pdf = QPushButton("Buka PDF")
        self.btn_open_pdf.setProperty("class", "SecondaryButton")
        self.btn_open_pdf.clicked.connect(self.open_pdf)

        self.btn_print = QPushButton("Cetak Surat")
        self.btn_print.setProperty("class", "PrimaryButton")
        self.btn_print.clicked.connect(self.print_letter)

        btn_row.addWidget(self.btn_open_word)
        btn_row.addWidget(self.btn_open_pdf)
        btn_row.addWidget(self.btn_print)
        action_layout.addLayout(btn_row)

        layout.addWidget(self.action_frame)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def load_active_templates(self):
        """Populate the templates dropdown list."""
        self.combo_template.clear()
        templates = database.get_active_templates()
        for t in templates:
            # store dict as user data
            self.combo_template.addItem(t["nama_template"], t)

    def search_resident(self):
        nik = self.txt_search_nik.text().strip()
        if not nik:
            QMessageBox.warning(self, "Peringatan", "Mohon masukkan NIK terlebih dahulu.")
            return

        res = database.get_penduduk_by_nik(nik)
        if not res:
            self.profile_frame.setVisible(False)
            self.gen_frame.setVisible(False)
            self.action_frame.setVisible(False)
            self.selected_resident = None
            
            ans = QMessageBox.question(
                self, "Penduduk Tidak Ditemukan",
                f"Data penduduk dengan NIK '{nik}' tidak terdaftar.\nApakah Anda ingin menambahkannya sekarang?",
                QMessageBox.Yes | QMessageBox.No
            )
            if ans == QMessageBox.Yes:
                # Redirect to adding resident
                from ui.penduduk import ResidentDialog
                dlg = ResidentDialog(parent=self)
                dlg.inputs["nik"].setText(nik)
                if dlg.exec() == ResidentDialog.Accepted:
                    self.txt_search_nik.setText(nik)
                    self.search_resident()
            return

        self.selected_resident = res
        self.display_profile()
        self.load_active_templates()
        self.generate_next_number()

        self.profile_frame.setVisible(True)
        self.gen_frame.setVisible(True)
        self.action_frame.setVisible(False)

    def display_profile(self):
        # Clear layout grid
        while self.grid_profile.count():
            item = self.grid_profile.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        fields_to_show = [
            ("Nama Lengkap", self.selected_resident["nama"]),
            ("No. KK", self.selected_resident["kk"]),
            ("NIK", self.selected_resident["nik"]),
            ("Tempat, Tgl Lahir", f"{self.selected_resident['tempat_lahir']}, {self.selected_resident['tanggal_lahir']}"),
            ("Agama", self.selected_resident["agama"]),
            ("Jenis Kelamin", self.selected_resident["jenis_kelamin"]),
            ("Pekerjaan", self.selected_resident["pekerjaan"]),
            ("Alamat", f"{self.selected_resident['alamat']} RT {self.selected_resident['rt']} / RW {self.selected_resident['rw']}")
        ]

        for idx, (label, val) in enumerate(fields_to_show):
            row = idx // 2
            col = (idx % 2) * 2

            lbl_title = QLabel(f"{label}:")
            lbl_title.setStyleSheet("font-weight: bold; color: #475569;")
            
            lbl_val = QLabel(str(val))
            lbl_val.setStyleSheet("color: #0f172a;")

            self.grid_profile.addWidget(lbl_title, row, col)
            self.grid_profile.addWidget(lbl_val, row, col + 1)

    def generate_next_number(self):
        config = database.load_config()
        format_num = config.get("penomoran", {}).get("format", "470/{{NOMOR}}/DS/{{TAHUN}}")
        counter = config.get("penomoran", {}).get("counter", 1)

        padded_counter = str(counter).zfill(3)
        year = str(datetime.date.today().year)
        
        # Replace format tags
        nomor_surat = format_num.replace("{{NOMOR}}", padded_counter).replace("{{TAHUN}}", year)
        self.txt_letter_num.setText(nomor_surat)

    def template_changed(self, idx):
        if idx < 0:
            return
        # Auto-regenerate number format if required or keep simple
        self.generate_next_number()

    def generate_letter(self):
        if not self.selected_resident:
            return

        t_idx = self.combo_template.currentIndex()
        if t_idx < 0:
            QMessageBox.warning(self, "Kesalahan", "Pilih template surat terlebih dahulu.")
            return

        t_data = self.combo_template.itemData(t_idx)
        file_template = t_data["file_template"]
        jenis_surat = t_data["jenis_surat"]
        letter_num = self.txt_letter_num.text().strip()

        if not letter_num:
            QMessageBox.warning(self, "Kesalahan", "Nomor surat tidak boleh kosong.")
            return

        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("Sedang memproses...")

        # 1. Generate DOCX
        docx_path, err = document_generator.generate_document(
            file_template, self.selected_resident, letter_num
        )

        if err:
            QMessageBox.critical(self, "Gagal", err)
            self.btn_generate.setEnabled(True)
            self.btn_generate.setText("Generate Dokumen (Word & PDF)")
            return

        self.generated_docx = docx_path
        self.lbl_output_docx.setText(f"Word: {os.path.basename(docx_path)}")

        # 2. Convert to PDF
        config = database.load_config()
        # check if there's custom libreoffice path in setting
        lo_path = config.get("penyimpanan", {}).get("libreoffice_path", "")
        
        pdf_path, pdf_err = document_generator.convert_to_pdf(docx_path, libreoffice_path=lo_path)
        if pdf_err:
            QMessageBox.warning(
                self, "Konversi PDF Gagal",
                f"Dokumen Word berhasil dibuat, namun konversi PDF gagal:\n{pdf_err}\n\n"
                "Aplikasi akan tetap menampilkan berkas Word saja."
            )
            self.generated_pdf = None
            self.lbl_output_pdf.setText("PDF: Gagal dikonversi.")
            self.btn_open_pdf.setEnabled(False)
        else:
            self.generated_pdf = pdf_path
            self.lbl_output_pdf.setText(f"PDF: {os.path.basename(pdf_path)}")
            self.btn_open_pdf.setEnabled(True)

        # 3. Log History to Database
        petugas_aktif = config.get("user_aktif", "Admin")
        database.add_riwayat(
            letter_num,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.selected_resident["nik"],
            self.selected_resident["nama"],
            jenis_surat,
            str(self.generated_docx),
            str(self.generated_pdf) if self.generated_pdf else "",
            petugas_aktif
        )

        # 4. Increment and save counter in settings
        counter = config.get("penomoran", {}).get("counter", 1)
        config["penomoran"]["counter"] = counter + 1
        database.save_config(config)

        # Enable actions
        self.action_frame.setVisible(True)
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("Generate Dokumen (Word & PDF)")

    def open_word(self):
        if not self.generated_docx or not Path(self.generated_docx).exists():
            return
        
        try:
            if sys.platform == "win32":
                os.startfile(str(self.generated_docx))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(self.generated_docx)])
            else:
                subprocess.run(["xdg-open", str(self.generated_docx)])
        except Exception as e:
            QMessageBox.critical(self, "Gagal membuka berkas", str(e))

    def open_pdf(self):
        if not self.generated_pdf or not Path(self.generated_pdf).exists():
            return
        
        try:
            if sys.platform == "win32":
                os.startfile(str(self.generated_pdf))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(self.generated_pdf)])
            else:
                subprocess.run(["xdg-open", str(self.generated_pdf)])
        except Exception as e:
            QMessageBox.critical(self, "Gagal membuka berkas", str(e))

    def print_letter(self):
        # Prefer PDF for printing, fallback to DOCX
        file_to_print = self.generated_pdf if self.generated_pdf else self.generated_docx
        if not file_to_print:
            return

        config = database.load_config()
        printer_name = config.get("printer", {}).get("default", "")

        ok, err = document_generator.print_document(file_to_print, printer_name)
        if ok:
            QMessageBox.information(self, "Mencetak", "Perintah cetak berhasil dikirim ke printer.")
        else:
            QMessageBox.critical(self, "Mencetak Gagal", f"Gagal mengirim perintah cetak:\n{err}")
