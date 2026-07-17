import os
import shutil
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDialog, QFormLayout, QComboBox, QMessageBox,
                             QFileDialog, QCheckBox)
from PySide6.QtCore import Qt
import database
from ui.style import apply_shadow

class TemplateDialog(QDialog):
    """Dialog for adding or editing a template profile."""
    def __init__(self, template_data=None, parent=None):
        super().__init__(parent)
        self.template_data = template_data
        self.setWindowTitle("Tambah Template" if not template_data else "Edit Template")
        self.resize(400, 300)
        self.selected_file_path = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # 1. Nama Template
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Contoh: Surat Keterangan Domisili")
        form_layout.addRow(QLabel("Nama Template:"), self.txt_name)

        # 2. Jenis Surat
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Domisili", "SKTM", "Usaha", "Belum Menikah", "Kelahiran", "Kematian", "Lainnya"])
        self.combo_type.setEditable(True)
        form_layout.addRow(QLabel("Jenis Surat:"), self.combo_type)

        # 3. File Template Selector
        file_layout = QHBoxLayout()
        self.lbl_file = QLabel("Belum ada berkas dipilih.")
        self.lbl_file.setStyleSheet("color: #64748b; font-style: italic;")
        
        btn_browse = QPushButton("Pilih DOCX")
        btn_browse.setProperty("class", "SecondaryButton")
        btn_browse.setStyleSheet("padding: 5px 10px;")
        btn_browse.clicked.connect(self.browse_file)
        
        file_layout.addWidget(btn_browse)
        file_layout.addWidget(self.lbl_file, stretch=1)
        form_layout.addRow(QLabel("Berkas Template:"), file_layout)

        # 4. Status Aktif
        self.chk_active = QCheckBox("Aktif")
        self.chk_active.setChecked(True)
        form_layout.addRow(QLabel("Status:"), self.chk_active)

        layout.addLayout(form_layout)

        # Fill fields if editing
        if self.template_data:
            self.txt_name.setText(self.template_data["nama_template"])
            self.combo_type.setCurrentText(self.template_data["jenis_surat"])
            self.lbl_file.setText(self.template_data["file_template"])
            self.chk_active.setChecked(bool(self.template_data["aktif"]))
            btn_browse.setEnabled(False) # lock template file swap from this screen to avoid accidents

        # Buttons
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Batal")
        btn_cancel.setProperty("class", "SecondaryButton")
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton("Simpan")
        btn_save.setProperty("class", "PrimaryButton")
        btn_save.clicked.connect(self.save_data)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih File Template DOCX", "", "Word Documents (*.docx)",
            options=QFileDialog.DontUseNativeDialog
        )
        if file_path:
            self.selected_file_path = file_path
            self.lbl_file.setText(os.path.basename(file_path))

    def save_data(self):
        name = self.txt_name.text().strip()
        jenis = self.combo_type.currentText().strip()
        status = 1 if self.chk_active.isChecked() else 0

        if not name:
            QMessageBox.warning(self, "Validasi Gagal", "Nama template wajib diisi.")
            return
        if not jenis:
            QMessageBox.warning(self, "Validasi Gagal", "Jenis surat wajib diisi.")
            return

        templates_dir = Path("templates/doc")
        templates_dir.mkdir(parents=True, exist_ok=True)

        if self.template_data:
            # Updating Template metadata
            file_name = self.template_data["file_template"]
            success, msg = database.update_template(
                self.template_data["id"], name, jenis, file_name, status
            )
        else:
            # Adding new template (requires copy file)
            if not self.selected_file_path:
                QMessageBox.warning(self, "Validasi Gagal", "Pilih berkas DOCX terlebih dahulu.")
                return
            
            file_name = os.path.basename(self.selected_file_path)
            dest_path = templates_dir / file_name

            # Check if file already exists in templates folder
            if dest_path.exists():
                ans = QMessageBox.question(
                    self, "Berkas Ada",
                    f"Berkas dengan nama '{file_name}' sudah ada di folder templates. Overwrite?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if ans == QMessageBox.No:
                    return

            try:
                shutil.copy(self.selected_file_path, dest_path)
            except Exception as e:
                QMessageBox.critical(self, "Gagal", f"Gagal menyalin berkas template: {str(e)}")
                return

            success, msg = database.add_template(name, jenis, file_name, status)

        if success:
            QMessageBox.information(self, "Sukses", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Gagal", msg)


class TemplatePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Toolbar Row
        toolbar = QHBoxLayout()
        title_lbl = QLabel("Daftar Template Surat")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
        
        btn_add = QPushButton("Tambah Template")
        btn_add.setProperty("class", "SuccessButton")
        btn_add.clicked.connect(self.add_template)

        toolbar.addWidget(title_lbl)
        toolbar.addStretch()
        toolbar.addWidget(btn_add)
        layout.addLayout(toolbar)

        # Templates list table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nama Template", "Jenis Surat", "Nama Berkas", "Status", "Aksi"])
        self.table.setColumnCount(6) # corrected column count
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.refresh_table()

    def refresh_table(self):
        templates = database.get_all_templates()
        self.table.setRowCount(len(templates))

        for idx, row in enumerate(templates):
            self.table.setItem(idx, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(idx, 1, QTableWidgetItem(row["nama_template"]))
            self.table.setItem(idx, 2, QTableWidgetItem(row["jenis_surat"]))
            self.table.setItem(idx, 3, QTableWidgetItem(row["file_template"]))
            
            # Status Active label
            status_text = "Aktif" if row["aktif"] == 1 else "Non-Aktif"
            status_item = QTableWidgetItem(status_text)
            if row["aktif"] == 1:
                status_item.setForeground(Qt.darkGreen)
            else:
                status_item.setForeground(Qt.red)
            self.table.setItem(idx, 4, status_item)

            # Actions Layout
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 2, 4, 2)
            actions_layout.setSpacing(5)

            btn_edit = QPushButton("Edit")
            btn_edit.setProperty("class", "PrimaryButton")
            btn_edit.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            btn_edit.clicked.connect(lambda checked=False, t=row: self.edit_template(t))

            btn_delete = QPushButton("Hapus")
            btn_delete.setProperty("class", "DangerButton")
            btn_delete.setStyleSheet("padding: 4px 8px; font-size: 11px;")
            btn_delete.clicked.connect(lambda checked=False, t=row: self.delete_template(t))

            actions_layout.addWidget(btn_edit)
            actions_layout.addWidget(btn_delete)

            cell_widget = QWidget()
            cell_widget.setLayout(actions_layout)
            self.table.setCellWidget(idx, 5, cell_widget)

    def add_template(self):
        dlg = TemplateDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.refresh_table()

    def edit_template(self, template):
        dlg = TemplateDialog(template_data=template, parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.refresh_table()

    def delete_template(self, template):
        ans = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus template '{template['nama_template']}'?\n"
            f"Berkas asli '{template['file_template']}' akan tetap ada di folder templates.",
            QMessageBox.Yes | QMessageBox.No
        )
        if ans == QMessageBox.Yes:
            database.delete_template(template["id"])
            self.refresh_table()
