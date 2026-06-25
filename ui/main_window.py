from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedWidget, QFrame, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon

# Import individual pages
from ui.dashboard import DashboardPage
from ui.penduduk import PendudukPage
from ui.template import TemplatePage
from ui.buat_surat import BuatSuratPage
from ui.riwayat import RiwayatPage
from ui.backup import BackupPage
from ui.pengaturan import PengaturanPage
from ui.tentang import TentangPage
from ui.style import apply_shadow, STYLE_SHEET
import database

class LoginWidget(QWidget):
    """Widget containing the Login screen interface."""
    def __init__(self, on_login_success, parent=None):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignCenter)

        # Login card container
        card = QFrame()
        card.setObjectName("LoginCard")
        card.setStyleSheet("""
            QFrame#LoginCard { 
                background-color: #ffffff; 
                border: 1px solid #e2e8f0; 
                border-radius: 16px; 
            }
        """)
        card.setFixedSize(400, 450)
        apply_shadow(card, radius=20)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(15)

        # Title
        title_lbl = QLabel("DESA KAMPOKKU JAYA")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f172a;")
        title_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_lbl)

        sub_lbl = QLabel("Aplikasi Pelayanan Surat Otomatis")
        sub_lbl.setStyleSheet("font-size: 13px; color: #64748b; margin-bottom: 20px;")
        sub_lbl.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(sub_lbl)

        # Form Inputs
        card_layout.addWidget(QLabel("Username:"))
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Masukkan username")
        self.txt_username.setText("admin") # helper default
        card_layout.addWidget(self.txt_username)

        card_layout.addWidget(QLabel("Password:"))
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Masukkan password")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setText("admin123") # helper default
        self.txt_password.returnPressed.connect(self.run_login)
        card_layout.addWidget(self.txt_password)

        card_layout.addSpacing(10)

        # Buttons
        btn_login = QPushButton("Masuk Sistem")
        btn_login.setProperty("class", "PrimaryButton")
        btn_login.setStyleSheet("padding: 12px; font-size: 14px;")
        btn_login.clicked.connect(self.run_login)
        card_layout.addWidget(btn_login)

        btn_forgot = QPushButton("Lupa Password?")
        btn_forgot.setStyleSheet("color: #3b82f6; border: none; font-size: 12px; text-decoration: underline; margin-top: 10px;")
        btn_forgot.setCursor(Qt.PointingHandCursor)
        btn_forgot.clicked.connect(self.reset_password)
        card_layout.addWidget(btn_forgot)

        main_layout.addWidget(card)

    def run_login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Login Gagal", "Username dan Password wajib diisi.")
            return

        user = database.authenticate_user(username, password)
        if user:
            # Save user session in config
            config = database.load_config()
            config["user_aktif"] = user["username"]
            config["user_role"] = user["role"]
            database.save_config(config)

            self.on_login_success(user)
        else:
            QMessageBox.critical(self, "Gagal Masuk", "Username atau Password salah.")

    def reset_password(self):
        from PySide6.QtWidgets import QInputDialog, QLineEdit
        key, ok = QInputDialog.getText(
            self, "Pemulihan Password", 
            "Masukkan Recovery Key (Kunci Pemulihan):", 
            QLineEdit.Password
        )
        if ok and key:
            if key == "RESET-DESAKU":
                database.change_user_password("admin", "admin123")
                QMessageBox.information(self, "Sukses", "Password akun 'admin' berhasil di-reset menjadi 'admin123'.\nSilakan login kembali.")
            else:
                QMessageBox.critical(self, "Gagal", "Recovery Key tidak valid!")


class MainAppWidget(QWidget):
    """Widget containing the main app panel with Sidebar and Workspace."""
    def __init__(self, on_logout_callback, parent=None):
        super().__init__(parent)
        self.on_logout_callback = on_logout_callback
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. SIDEBAR FRAME
        sidebar = QFrame()
        sidebar.setObjectName("SidebarFrame")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo and Title
        logo_lbl = QLabel("SI-DESAKU")
        logo_lbl.setObjectName("SidebarTitle")
        logo_lbl.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(logo_lbl)

        sub_logo = QLabel("ADMINISTRASI SURAT DESA")
        sub_logo.setObjectName("SidebarSubtitle")
        sub_logo.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(sub_logo)

        # Menu Buttons (Grouped)
        self.menu_buttons = []
        menus = [
            ("Dashboard", "DASHBOARD"),
            ("Data Penduduk", "DATA PENDUDUK"),
            ("Template Surat", "TEMPLATE SURAT"),
            ("Buat Surat", "BUAT SURAT"),
            ("Riwayat Surat", "RIWAYAT SURAT"),
            ("Backup Data", "BACKUP DATA"),
            ("Pengaturan", "PENGATURAN"),
            ("Tentang Aplikasi", "TENTANG")
        ]

        for idx, (label, name) in enumerate(menus):
            btn = QPushButton(label)
            btn.setProperty("class", "SidebarButton")
            btn.setCheckable(True)
            if idx == 0:
                btn.setChecked(True)
            # connect click
            btn.clicked.connect(lambda checked=False, i=idx: self.switch_page(i))
            self.menu_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Logout Button in Sidebar Bottom
        btn_logout = QPushButton("Keluar (Logout)")
        btn_logout.setProperty("class", "SidebarButton")
        btn_logout.setStyleSheet("color: #ef4444; margin-bottom: 20px; font-weight: bold;")
        btn_logout.clicked.connect(self.on_logout_callback)
        sidebar_layout.addWidget(btn_logout)

        layout.addWidget(sidebar)

        # 2. WORKSPACE AND HEADER (Right Frame)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Header bar
        header = QFrame()
        header.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.lbl_route = QLabel("Dashboard")
        self.lbl_route.setObjectName("HeaderTitle")
        
        self.lbl_user_profile = QLabel("Petugas: Admin (Role: Admin)")
        self.lbl_user_profile.setObjectName("HeaderUser")

        header_layout.addWidget(self.lbl_route)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_user_profile)
        right_layout.addWidget(header)

        # Inner Stacked Widget
        self.inner_stack = QStackedWidget()
        self.inner_stack.setObjectName("WorkspaceFrame")

        # Instantiate pages
        self.page_dashboard = DashboardPage(self)
        self.page_penduduk = PendudukPage(self)
        self.page_template = TemplatePage(self)
        self.page_buat_surat = BuatSuratPage(self)
        self.page_riwayat = RiwayatPage(self)
        self.page_backup = BackupPage(self)
        self.page_pengaturan = PengaturanPage(self)
        self.page_tentang = TentangPage(self)

        # Add to stack
        self.inner_stack.addWidget(self.page_dashboard)  # Index 0
        self.inner_stack.addWidget(self.page_penduduk)   # Index 1
        self.inner_stack.addWidget(self.page_template)   # Index 2
        self.inner_stack.addWidget(self.page_buat_surat)  # Index 3
        self.inner_stack.addWidget(self.page_riwayat)     # Index 4
        self.inner_stack.addWidget(self.page_backup)      # Index 5
        self.inner_stack.addWidget(self.page_pengaturan)  # Index 6
        self.inner_stack.addWidget(self.page_tentang)     # Index 7

        right_layout.addWidget(self.inner_stack)
        layout.addWidget(right_container)

    def switch_page(self, index):
        """Switch current stack view and highlights sidebar selection."""
        # Uncheck other buttons
        for idx, btn in enumerate(self.menu_buttons):
            btn.setChecked(idx == index)

        self.inner_stack.setCurrentIndex(index)
        
        # Set route title
        titles = [
            "Dashboard Utama",
            "Kelola Data Penduduk",
            "Kelola Template Surat Word (DOCX)",
            "Layanan Operasional Buat Surat",
            "Riwayat Penerbitan Surat",
            "Backup dan Restore Data",
            "Pengaturan Profil Desa & Sistem",
            "Tentang Aplikasi Kependudukan"
        ]
        self.lbl_route.setText(titles[index])

        # Page-specific refresh helpers
        if index == 0:
            self.page_dashboard.refresh_data()
        elif index == 1:
            self.page_penduduk.refresh_table()
        elif index == 2:
            self.page_template.refresh_table()
        elif index == 3:
            self.page_buat_surat.load_active_templates()
            self.page_buat_surat.generate_next_number()
        elif index == 4:
            self.page_riwayat.load_data()
        elif index == 6:
            self.page_pengaturan.load_settings()

    def update_user_session(self):
        """Update header info based on the currently logged-in user."""
        config = database.load_config()
        user = config.get("user_aktif", "Admin")
        role = config.get("user_role", "Admin")
        self.lbl_user_profile.setText(f"Petugas: {user} ({role})")


class MainWindow(QMainWindow):
    """Main App Window executing layout logic."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SI-DESAKU - Aplikasi Surat Otomatis Desa")
        self.setMinimumSize(1024, 720)
        self.resize(1150, 750)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet(STYLE_SHEET)
        
        # Initialize DB
        database.init_db()

        self.main_stack = QStackedWidget()
        self.setCentralWidget(self.main_stack)

        # Build structures
        self.login_widget = LoginWidget(on_login_success=self.login_success, parent=self)
        self.app_widget = MainAppWidget(on_logout_callback=self.logout_user, parent=self)

        self.main_stack.addWidget(self.login_widget) # index 0
        self.main_stack.addWidget(self.app_widget)   # index 1

        # Start with Login Page
        self.main_stack.setCurrentIndex(0)

    def login_success(self, user):
        """Executed upon successful validation in LoginWidget."""
        self.app_widget.update_user_session()
        self.app_widget.switch_page(0) # start on dashboard
        self.main_stack.setCurrentIndex(1) # load workspace

    def logout_user(self):
        """Resets inputs and redirects to Login Screen."""
        self.login_widget.txt_password.clear()
        self.main_stack.setCurrentIndex(0)
