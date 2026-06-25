import os
import sys
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QComboBox, QMessageBox)
from PySide6.QtCore import Qt
import database
import document_generator
from ui.style import apply_shadow

class RiwayatPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Toolbar Row
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Search box
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Cari berdasarkan NIK, Nama, atau No. Surat...")
        self.txt_search.textChanged.connect(self.load_data)

        # Time filter
        self.combo_filter = QComboBox()
        self.combo_filter.addItem("Semua Riwayat", "all")
        self.combo_filter.addItem("Hari Ini", "today")
        self.combo_filter.addItem("Bulan Ini", "month")
        self.combo_filter.addItem("Tahun Ini", "year")
        self.combo_filter.currentIndexChanged.connect(self.load_data)

        btn_refresh = QPushButton("Segarkan")
        btn_refresh.setProperty("class", "PrimaryButton")
        btn_refresh.clicked.connect(self.load_data)

        toolbar.addWidget(self.txt_search, stretch=1)
        toolbar.addWidget(self.combo_filter)
        toolbar.addWidget(btn_refresh)
        layout.addLayout(toolbar)

        # Table Grid
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "No. Surat", "Tanggal", "NIK", "Nama Penerima", "Jenis Surat", "Petugas", "Aksi"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.load_data()

    def load_data(self):
        filter_time = self.combo_filter.currentData()
        query = self.txt_search.text().strip()

        records = database.get_all_riwayat(filter_time, query)
        self.table.setRowCount(len(records))

        for idx, row in enumerate(records):
            self.table.setItem(idx, 0, QTableWidgetItem(row["nomor_surat"]))
            self.table.setItem(idx, 1, QTableWidgetItem(row["tanggal"]))
            self.table.setItem(idx, 2, QTableWidgetItem(row["nik"]))
            self.table.setItem(idx, 3, QTableWidgetItem(row["nama"]))
            self.table.setItem(idx, 4, QTableWidgetItem(row["jenis_surat"]))
            self.table.setItem(idx, 5, QTableWidgetItem(row["petugas"]))

            # Action Buttons cell
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(5)

            # Open Word Button
            btn_word = QPushButton("Word")
            btn_word.setProperty("class", "SecondaryButton")
            btn_word.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            docx_path = row["file_docx"]
            btn_word.clicked.connect(lambda checked=False, p=docx_path: self.open_file(p))
            actions_layout.addWidget(btn_word)

            # Open PDF Button
            btn_pdf = QPushButton("PDF")
            btn_pdf.setProperty("class", "SecondaryButton")
            btn_pdf.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            pdf_path = row["file_pdf"]
            if pdf_path and Path(pdf_path).exists():
                btn_pdf.clicked.connect(lambda checked=False, p=pdf_path: self.open_file(p))
            else:
                btn_pdf.setEnabled(False)
            actions_layout.addWidget(btn_pdf)

            # Print Button
            btn_print = QPushButton("Cetak")
            btn_print.setProperty("class", "PrimaryButton")
            btn_print.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            file_to_print = pdf_path if (pdf_path and Path(pdf_path).exists()) else docx_path
            btn_print.clicked.connect(lambda checked=False, p=file_to_print: self.print_file(p))
            actions_layout.addWidget(btn_print)

            cell_widget = QWidget()
            cell_widget.setLayout(actions_layout)
            self.table.setCellWidget(idx, 6, cell_widget)

    def open_file(self, file_path):
        if not file_path or not Path(file_path).exists():
            QMessageBox.warning(self, "Berkas Hilang", "Berkas dokumen tidak ditemukan di media penyimpanan.")
            return

        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path])
            else:
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            QMessageBox.critical(self, "Gagal membuka berkas", str(e))

    def print_file(self, file_path):
        if not file_path or not Path(file_path).exists():
            QMessageBox.warning(self, "Berkas Hilang", "Berkas dokumen tidak ditemukan di media penyimpanan.")
            return

        config = database.load_config()
        printer_name = config.get("printer", {}).get("default", "")

        ok, err = document_generator.print_document(file_path, printer_name)
        if ok:
            QMessageBox.information(self, "Mencetak", "Perintah cetak berhasil dikirim ke printer.")
        else:
            QMessageBox.critical(self, "Mencetak Gagal", f"Gagal mengirim perintah cetak:\n{err}")
