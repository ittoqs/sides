from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
import database
from ui.style import apply_shadow

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 1. Cards Layout (Top Row)
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # Total Penduduk Card
        self.card_penduduk = self.create_stat_card("TOTAL PENDUDUK", "0", "#3b82f6")
        # Surat Hari Ini Card
        self.card_today = self.create_stat_card("SURAT HARI INI", "0", "#10b981")
        # Surat Bulan Ini Card
        self.card_month = self.create_stat_card("SURAT BULAN INI", "0", "#f59e0b")
        # Template Aktif Card
        self.card_templates = self.create_stat_card("TEMPLATE AKTIF", "0", "#8b5cf6")

        cards_layout.addWidget(self.card_penduduk)
        cards_layout.addWidget(self.card_today)
        cards_layout.addWidget(self.card_month)
        cards_layout.addWidget(self.card_templates)
        layout.addLayout(cards_layout)

        # 2. Main Content Row (Splits into Recent Letters and Document Stats)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Left Column: Recent Letters Table
        left_frame = QFrame()
        left_frame.setObjectName("MainCard")
        left_frame.setProperty("class", "Card")
        left_frame.setStyleSheet("QFrame#MainCard { background-color: #ffffff; border-radius: 12px; }")
        apply_shadow(left_frame)
        
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(15, 15, 15, 15)
        
        table_title = QLabel("Surat Terbaru")
        table_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #0f172a; margin-bottom: 5px;")
        left_layout.addWidget(table_title)

        self.table_recent = QTableWidget()
        self.table_recent.setColumnCount(5)
        self.table_recent.setHorizontalHeaderLabels(["No. Surat", "Tanggal", "NIK", "Nama Penerima", "Jenis Surat"])
        self.table_recent.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_recent.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table_recent.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_recent.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_recent.setAlternatingRowColors(True)
        self.table_recent.setStyleSheet("QTableWidget { border: none; }")
        
        left_layout.addWidget(self.table_recent)
        content_layout.addWidget(left_frame, stretch=3)

        # Right Column: Letter Statistics Chart
        right_frame = QFrame()
        right_frame.setObjectName("ChartCard")
        right_frame.setProperty("class", "Card")
        right_frame.setStyleSheet("QFrame#ChartCard { background-color: #ffffff; border-radius: 12px; }")
        apply_shadow(right_frame)

        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(15, 15, 15, 15)

        chart_title = QLabel("Distribusi Surat")
        chart_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #0f172a; margin-bottom: 10px;")
        right_layout.addWidget(chart_title)

        # Container for custom chart bars
        self.chart_container = QWidget()
        self.chart_container_layout = QVBoxLayout(self.chart_container)
        self.chart_container_layout.setContentsMargins(0, 0, 0, 0)
        self.chart_container_layout.setSpacing(15)
        right_layout.addWidget(self.chart_container)
        right_layout.addStretch()

        content_layout.addWidget(right_frame, stretch=2)
        layout.addLayout(content_layout)

        # Load data initially
        self.refresh_data()

    def create_stat_card(self, title, val, color):
        card = QFrame()
        card.setObjectName("StatCard")
        card.setProperty("class", "StatCard")
        card.setStyleSheet("QFrame#StatCard { background-color: #ffffff; border-left: 5px solid " + color + "; border-radius: 10px; }")
        apply_shadow(card)

        lyt = QVBoxLayout(card)
        lyt.setContentsMargins(20, 15, 20, 15)
        
        lbl_title = QLabel(title)
        lbl_title.setObjectName("StatLabel")
        
        lbl_val = QLabel(val)
        lbl_val.setObjectName("StatVal")

        lyt.addWidget(lbl_title)
        lyt.addWidget(lbl_val)
        return card

    def set_card_value(self, card, value):
        lbl_val = card.findChild(QLabel, "StatVal")
        if lbl_val:
            lbl_val.setText(str(value))

    def refresh_data(self):
        """Fetch current stats and populate widgets."""
        # 1. Total Penduduk
        total_p = database.count_penduduk()
        self.set_card_value(self.card_penduduk, total_p)

        # 2. Surat Hari Ini
        today_s = database.count_surat_today()
        self.set_card_value(self.card_today, today_s)

        # 3. Surat Bulan Ini
        month_s = database.count_surat_this_month()
        self.set_card_value(self.card_month, month_s)

        # 4. Template Aktif
        active_t = len(database.get_active_templates())
        self.set_card_value(self.card_templates, active_t)

        # 5. Populate Recent Letters
        recent_letters = database.get_all_riwayat(filter_time="all", query="")[:10]
        self.table_recent.setRowCount(len(recent_letters))
        for idx, row in enumerate(recent_letters):
            self.table_recent.setItem(idx, 0, QTableWidgetItem(row["nomor_surat"]))
            self.table_recent.setItem(idx, 1, QTableWidgetItem(row["tanggal"][:10]))
            self.table_recent.setItem(idx, 2, QTableWidgetItem(row["nik"]))
            self.table_recent.setItem(idx, 3, QTableWidgetItem(row["nama"]))
            self.table_recent.setItem(idx, 4, QTableWidgetItem(row["jenis_surat"]))

        # 6. Populate Distribution Bars
        # Clear container first
        while self.chart_container_layout.count():
            item = self.chart_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        stat_data = database.get_stat_surat()
        max_count = max([item["jumlah"] for item in stat_data]) if stat_data else 1
        if max_count == 0:
            max_count = 1

        if not stat_data:
            empty_lbl = QLabel("Belum ada data pembuatan surat.")
            empty_lbl.setStyleSheet("color: #64748b; font-style: italic; font-size: 13px;")
            self.chart_container_layout.addWidget(empty_lbl)
        else:
            for item in stat_data:
                name = item["jenis_surat"]
                count = item["jumlah"]
                percentage = int((count / max_count) * 100)

                bar_widget = QWidget()
                bar_layout = QVBoxLayout(bar_widget)
                bar_layout.setContentsMargins(0, 0, 0, 0)
                bar_layout.setSpacing(4)

                info_layout = QHBoxLayout()
                lbl_name = QLabel(name)
                lbl_name.setStyleSheet("font-weight: 500; font-size: 13px; color: #334155;")
                lbl_count = QLabel(f"{count} Surat")
                lbl_count.setStyleSheet("font-weight: bold; font-size: 13px; color: #0f172a;")
                info_layout.addWidget(lbl_name)
                info_layout.addStretch()
                info_layout.addWidget(lbl_count)
                bar_layout.addLayout(info_layout)

                # Visual Bar
                outer_bar = QFrame()
                outer_bar.setStyleSheet("background-color: #f1f5f9; border-radius: 4px; min-height: 8px; max-height: 8px;")
                outer_layout = QHBoxLayout(outer_bar)
                outer_layout.setContentsMargins(0, 0, 0, 0)

                inner_bar = QFrame()
                inner_bar.setStyleSheet("background-color: #3b82f6; border-radius: 4px; min-height: 8px; max-height: 8px;")
                
                outer_layout.addWidget(inner_bar, stretch=percentage)
                outer_layout.addStretch(stretch=(100 - percentage))
                
                bar_layout.addWidget(outer_bar)
                self.chart_container_layout.addWidget(bar_widget)
