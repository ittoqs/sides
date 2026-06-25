import os
import zipfile
import datetime
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QMessageBox, QFileDialog, QFrame, 
                             QCheckBox, QGroupBox, QTextEdit)
from PySide6.QtCore import Qt
import database
from ui.style import apply_shadow

class BackupPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_restore_zip = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title_lbl = QLabel("Manajemen Backup & Restore")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a;")
        layout.addWidget(title_lbl)

        # Columns Row
        cols_layout = QHBoxLayout()
        cols_layout.setSpacing(20)

        # 1. Left Card: Backup
        backup_card = QFrame()
        backup_card.setObjectName("BackupCard")
        backup_card.setProperty("class", "Card")
        backup_card.setStyleSheet("QFrame#BackupCard { background-color: #ffffff; border-radius: 12px; }")
        apply_shadow(backup_card)
        
        backup_layout = QVBoxLayout(backup_card)
        backup_layout.setContentsMargins(20, 20, 20, 20)
        backup_layout.setSpacing(15)

        lbl_b_title = QLabel("Cadangkan Data (Backup)")
        lbl_b_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #0f172a;")
        backup_layout.addWidget(lbl_b_title)

        backup_layout.addWidget(QLabel("Pilih item yang ingin dicadangkan:"))
        
        self.chk_db = QCheckBox("Database Penduduk & Riwayat (.db)")
        self.chk_db.setChecked(True)
        self.chk_tpl = QCheckBox("Template Surat Word (.docx)")
        self.chk_tpl.setChecked(True)
        self.chk_out = QCheckBox("Surat Hasil Penerbitan (DOCX & PDF)")
        self.chk_out.setChecked(True)

        backup_layout.addWidget(self.chk_db)
        backup_layout.addWidget(self.chk_tpl)
        backup_layout.addWidget(self.chk_out)

        btn_run_backup = QPushButton("Cadangkan Sekarang")
        btn_run_backup.setProperty("class", "PrimaryButton")
        btn_run_backup.clicked.connect(self.run_backup)
        backup_layout.addWidget(btn_run_backup)
        backup_layout.addStretch()

        cols_layout.addWidget(backup_card, stretch=1)

        # 2. Right Card: Restore
        restore_card = QFrame()
        restore_card.setObjectName("RestoreCard")
        restore_card.setProperty("class", "Card")
        restore_card.setStyleSheet("QFrame#RestoreCard { background-color: #ffffff; border-radius: 12px; }")
        apply_shadow(restore_card)

        restore_layout = QVBoxLayout(restore_card)
        restore_layout.setContentsMargins(20, 20, 20, 20)
        restore_layout.setSpacing(15)

        lbl_r_title = QLabel("Kembalikan Data (Restore)")
        lbl_r_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #0f172a;")
        restore_layout.addWidget(lbl_r_title)

        restore_layout.addWidget(QLabel("Pilih berkas cadangan zip untuk di-restore:"))
        
        self.lbl_zip_path = QLabel("Belum ada berkas backup dipilih.")
        self.lbl_zip_path.setStyleSheet("color: #64748b; font-style: italic;")
        
        btn_pick_zip = QPushButton("Pilih Berkas Backup (.zip)")
        btn_pick_zip.setProperty("class", "SecondaryButton")
        btn_pick_zip.clicked.connect(self.pick_zip)

        self.btn_run_restore = QPushButton("Restore Data Sekarang")
        self.btn_run_restore.setProperty("class", "DangerButton")
        self.btn_run_restore.setEnabled(False)
        self.btn_run_restore.clicked.connect(self.run_restore)

        restore_layout.addWidget(btn_pick_zip)
        restore_layout.addWidget(self.lbl_zip_path)
        restore_layout.addWidget(self.btn_run_restore)
        restore_layout.addStretch()

        cols_layout.addWidget(restore_card, stretch=1)
        layout.addLayout(cols_layout)

        # Console Logs at the bottom
        log_group = QGroupBox("Log Backup / Restore")
        log_layout = QVBoxLayout(log_group)
        self.txt_logs = QTextEdit()
        self.txt_logs.setReadOnly(True)
        self.txt_logs.setStyleSheet("background-color: #0f172a; color: #3b82f6; font-family: Courier New; font-size: 12px;")
        self.txt_logs.setMinimumHeight(150)
        log_layout.addWidget(self.txt_logs)
        
        layout.addWidget(log_group, stretch=1)

    def run_backup(self):
        # Determine items to zip
        backup_db = self.chk_db.isChecked()
        backup_tpl = self.chk_tpl.isChecked()
        backup_out = self.chk_out.isChecked()

        if not (backup_db or backup_tpl or backup_out):
            QMessageBox.warning(self, "Peringatan", "Pilih minimal satu item untuk dicadangkan.")
            return

        # Request file path to save zip
        default_filename = f"backup_{datetime.date.today().strftime('%Y%m%d')}.zip"
        
        backup_dir = Path("backup")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        save_path, _ = QFileDialog.getSaveFileName(
            self, "Simpan Backup Zip", str(backup_dir / default_filename), "Backup Zip File (*.zip)"
        )

        if not save_path:
            return

        self.txt_logs.clear()
        self.txt_logs.append("=== Memulai Proses Pencadangan ===")
        self.txt_logs.append(f"Output berkas: {save_path}")

        try:
            with zipfile.ZipFile(save_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # 1. Config file
                if Path("config.json").exists():
                    zip_file.write("config.json")
                    self.txt_logs.append("Menulis konfigurasi: config.json")

                # 2. Database
                if backup_db:
                    db_path = Path("database/surat.db")
                    if db_path.exists():
                        # Close connection first to write cleanly
                        zip_file.write(str(db_path))
                        self.txt_logs.append(f"Menulis database: {db_path}")

                # 3. Templates
                if backup_tpl:
                    tpl_dir = Path("templates")
                    if tpl_dir.exists():
                        for root, _, files in os.walk(tpl_dir):
                            for file in files:
                                f_path = Path(root) / file
                                zip_file.write(str(f_path))
                        self.txt_logs.append("Menulis folder template dokumen...")

                # 4. Outputs
                if backup_out:
                    out_dir = Path("output")
                    if out_dir.exists():
                        count_files = 0
                        for root, _, files in os.walk(out_dir):
                            for file in files:
                                f_path = Path(root) / file
                                zip_file.write(str(f_path))
                                count_files += 1
                        self.txt_logs.append(f"Menulis {count_files} berkas riwayat surat kependudukan...")

            self.txt_logs.append("\n=== Backup Berhasil Disimpan ===")
            QMessageBox.information(self, "Backup Sukses", "Pencadangan data desa berhasil diselesaikan.")
            
        except Exception as e:
            self.txt_logs.append(f"\n[EROR] Kegagalan backup: {str(e)}")
            QMessageBox.critical(self, "Backup Gagal", f"Proses backup gagal:\n{str(e)}")

    def pick_zip(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Berkas Backup Zip", str(Path("backup")), "Zip Files (*.zip)"
        )
        if file_path:
            self.selected_restore_zip = file_path
            self.lbl_zip_path.setText(os.path.basename(file_path))
            self.btn_run_restore.setEnabled(True)

    def run_restore(self):
        if not self.selected_restore_zip:
            return

        # Double warning
        ans1 = QMessageBox.warning(
            self, "Konfirmasi Restore",
            "PENTING! Proses restore akan menimpa data penduduk, template, riwayat, dan konfigurasi aktif saat ini.\n"
            "Apakah Anda yakin ingin melanjutkan?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ans1 != QMessageBox.Yes:
            return

        ans2 = QMessageBox.critical(
            self, "Peringatan Terakhir",
            "Tindakan ini tidak dapat dibatalkan secara otomatis. Disarankan untuk mencadangkan data saat ini terlebih dahulu.\n"
            "Apakah Anda benar-benar yakin ingin menimpa database saat ini?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ans2 != QMessageBox.Yes:
            return

        self.txt_logs.clear()
        self.txt_logs.append("=== Memulai Pemulihan Data (Restore) ===")
        self.txt_logs.append(f"Membuka berkas cadangan: {self.selected_restore_zip}")

        try:
            with zipfile.ZipFile(self.selected_restore_zip, "r") as zip_file:
                # Extract all files overwriting local ones
                # To prevent write lock, close database connection helper
                # Actually SQLite allows overwriting the file if no connection handles are open.
                
                # Check files inside zip
                namelist = zip_file.namelist()
                self.txt_logs.append(f"Daftar berkas dalam zip: {len(namelist)} item.")

                for item in namelist:
                    zip_file.extract(item)
                    self.txt_logs.append(f"Mengembalikan: {item}")

            self.txt_logs.append("\n=== Pemulihan Data Selesai ===")
            QMessageBox.information(
                self, "Restore Sukses",
                "Data desa berhasil dipulihkan dari cadangan!\nSilakan segarkan atau restart aplikasi."
            )
            
        except Exception as e:
            self.txt_logs.append(f"\n[EROR] Kegagalan restore: {str(e)}")
            QMessageBox.critical(self, "Restore Gagal", f"Proses restore gagal:\n{str(e)}")
