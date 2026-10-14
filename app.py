
import sys
import math
import sqlite3
from datetime import datetime
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QFrame,
    QDoubleSpinBox,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QMessageBox,
)


class RubberFarmApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Rubber Farm Manager")
        self.resize(1180, 760)
        self.setMinimumSize(900, 600)
        self.db_path = (
            Path(__file__).resolve().parent
            / "rubber_farm.db"
        )
        self.init_db()
        self.init_production_db()

        # พื้นที่หลักของแอป
        central = QWidget()
        central.setObjectName("centralRoot")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(20)

        # ส่วนหัว
        header = QHBoxLayout()

        brand = QLabel("Plook Khum")
        brand.setObjectName("brand")
        header.addWidget(brand)

        header.addStretch()

        subtitle = QLabel("ระบบจัดการสวนยางพารา")
        subtitle.setObjectName("tagline")
        header.addWidget(subtitle)

        main_layout.addLayout(header)

        # เมนูด้านบน
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)

        self.nav_buttons = []
        self.page_stack = QStackedWidget()

        pages = [
            (
                "ภาพรวม",
                "ภาพรวมสวน",
                "ดูข้อมูลสำคัญและสถานะของสวนยางพารา",
            ),
            (
                "คำนวณน้ำ",
                "คำนวณปริมาณน้ำ",
                "คำนวณปริมาณน้ำที่ต้องใช้ในพื้นที่สวน",
            ),
            (
                "คำนวณปุ๋ย",
                "คำนวณปริมาณปุ๋ย",
                "คำนวณปริมาณปุ๋ย จำนวนกระสอบ และต้นทุน",
            ),
            (
                "ความคุ้มค่า",
                "วิเคราะห์ความคุ้มค่า",
                "ตรวจสอบรายรับ ต้นทุน และกำไรสุทธิ",
            ),
            (
                "ประวัติ",
                "ประวัติการคำนวณ",
                "ดูประวัติการคำนวณน้ำ ปุ๋ย และความคุ้มค่า",
             ),
            (
                "ข้อมูลสวน",
                "ข้อมูลประจำสวน",
                "จัดการข้อมูลพื้นฐานสำหรับคำนวณและคาดการณ์ผลผลิต",
            ),
            (
                "ผลผลิต",
                "บันทึกผลผลิตยางพารา",
                "บันทึกข้อมูลผลผลิตรายเดือนและเตรียมวิเคราะห์แนวโน้ม",
            ),
            ("คาดการณ์",
             "คาดการณ์ผลผลิตยางพารา",
             "ประมาณผลผลิตเดือนถัดไปจากข้อมูลย้อนหลัง",
             ),
             ("กราฟผลผลิต",
              "กราฟวิเคราะห์ผลผลิตยางพารา",
              "เปรียบเทียบผลผลิตย้อนหลังและแนวโน้มที่คาดการณ์",
              ),

        ]

        for index, (menu, title, description) in enumerate(pages):
            button = QPushButton(menu)
            button.setObjectName("navButton")
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked=False, i=index: self.show_page(i)
            )

            nav_layout.addWidget(button)
            self.nav_buttons.append(button)

            if menu == "ภาพรวม":
                page = self.create_dashboard(title, description)
            elif menu == "คำนวณน้ำ":
                page = self.create_water_calculator(title, description)
            elif menu == "คำนวณปุ๋ย":
                page = self.create_fertilizer_calculator(title, description)  
            elif menu == "ความคุ้มค่า":
                page = self.create_profit_calculator(title, description) 
            elif menu == "ประวัติ":
                page = self.create_history_page(title, description) 
            elif menu == "ข้อมูลสวน":
                self.init_farm_db()
                page = self.create_farm_page(title, description)        
            elif menu == "ผลผลิต":
                page = self.create_production_page(title, description)
            elif menu == "คาดการณ์":
                page = self.create_forecast_page(title, description)
            elif menu == "กราฟผลผลิต":
                page = self.create_production_chart_page(title, description)
            else:
                page = self.create_placeholder(title, description)

            self.page_stack.addWidget(page)

        nav_layout.addStretch()

        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.page_stack, 1)

        # รูปแบบหน้าตา
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F4F7F1;
            }

            QWidget#centralRoot {
                background-color: #F4F7F1;
            }

            QLabel#brand {
                font-size: 24px;
                font-weight: 700;
                color: #1B4332;
            }

            QLabel#tagline {
                font-size: 13px;
                color: #68786B;
            }

            QPushButton#navButton {
                background-color: #E5ECE3;
                color: #385343;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#navButton:hover {
                background-color: #D8E5D7;
            }

            QPushButton#navButton:checked {
                background-color: #2F6B47;
                color: white;
            }

            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
                color: #1D3325;
            }

            QLabel#description {
                font-size: 14px;
                color: #69776D;
            }

            QFrame#statCard, QFrame#infoCard {
                background-color: white;
                border: 1px solid #E0E8E0;
                border-radius: 14px;
            }

            QLabel#statName {
                font-size: 13px;
                color: #69776D;
            }

            QLabel#statValue {
                font-size: 25px;
                font-weight: 700;
                color: #2D6A4F;
            }

            QLabel#statHint, QLabel#infoDescription {
                font-size: 12px;
                color: #89948B;
            }

            QLabel#infoTitle {
                font-size: 17px;
                font-weight: 600;
                color: #2D4B37;
            }
        """)

        self.show_page(0)

    def create_dashboard(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        desc = QLabel(description)
        desc.setObjectName("description")
        layout.addWidget(desc)

        layout.addSpacing(12)

        # การ์ดข้อมูลภาพรวม
        cards = QHBoxLayout()
        cards.setSpacing(14)

        cards.addWidget(
            self.create_stat_card(
                "พื้นที่สวน", "0 ไร่", "รอเพิ่มข้อมูลสวน"
            )
        )
        cards.addWidget(
            self.create_stat_card(
                "จำนวนต้นยาง", "0 ต้น", "รอเพิ่มจำนวนต้น"
            )
        )
        cards.addWidget(
            self.create_stat_card(
                "รายรับเดือนนี้", "฿0", "รอบันทึกรายรับ"
            )
        )
        cards.addWidget(
            self.create_stat_card(
                "ต้นทุนเดือนนี้", "฿0", "รอบันทึกต้นทุน"
            )
        )

        layout.addLayout(cards)

        note = QLabel(
            "เริ่มต้นด้วยการเพิ่มข้อมูลสวน "
            "จากนั้นเราจะเชื่อมข้อมูลเข้ากับระบบคำนวณ"
        )
        note.setObjectName("description")
        note.setWordWrap(True)
        layout.addSpacing(8)
        layout.addWidget(note)

        layout.addStretch()
        return page

    def create_stat_card(self, name, value, hint):
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(135)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        name_label = QLabel(name)
        name_label.setObjectName("statName")
        layout.addWidget(name_label)

        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        layout.addWidget(value_label)

        hint_label = QLabel(hint)
        hint_label.setObjectName("statHint")
        layout.addWidget(hint_label)

        layout.addStretch()
        return card

    def create_water_calculator(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        # หัวข้อหน้า
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        desc = QLabel(description)
        desc.setObjectName("description")
        layout.addWidget(desc)

        layout.addSpacing(12)

        # กล่องรับข้อมูล
        card = QFrame()
        card.setObjectName("infoCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(16)

        form = QFormLayout()
        form.setVerticalSpacing(14)

        # ช่องพื้นที่สวน
        self.water_area = QDoubleSpinBox()
        self.water_area.setRange(0.01, 1000000)
        self.water_area.setDecimals(2)
        self.water_area.setValue(10)

        # ช่องปริมาณน้ำสุทธิที่ต้องการ
        self.water_depth = QDoubleSpinBox()
        self.water_depth.setRange(0, 1000)
        self.water_depth.setDecimals(1)
        self.water_depth.setValue(5)

        # ประสิทธิภาพระบบให้น้ำ
        self.water_efficiency = QDoubleSpinBox()
        self.water_efficiency.setRange(1, 100)
        self.water_efficiency.setDecimals(0)
        self.water_efficiency.setValue(80)
        self.water_efficiency.setSuffix(" %")

        form.addRow("พื้นที่สวน (ไร่)", self.water_area)
        form.addRow(
            "ปริมาณน้ำสุทธิที่ต้องการ (มม.)",
            self.water_depth
        )
        form.addRow(
            "ประสิทธิภาพระบบให้น้ำ",
            self.water_efficiency
        )

        card_layout.addLayout(form)

        # ปุ่มคำนวณ
        calculate_button = QPushButton("คำนวณปริมาณน้ำ")
        calculate_button.setMinimumHeight(44)
        calculate_button.setStyleSheet("""
            QPushButton {
                background-color: #2F6B47;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #245738;
            }
        """)
        calculate_button.clicked.connect(self.calculate_water)
        card_layout.addWidget(calculate_button)

        # พื้นที่แสดงผลลัพธ์
        self.water_result = QLabel(
            "กรอกข้อมูล แล้วกดปุ่มคำนวณปริมาณน้ำ"
        )
        self.water_result.setWordWrap(True)
        self.water_result.setStyleSheet("""
            QLabel {
                color: #1D3325;
                font-size: 15px;
                padding: 8px 0;
            }
        """)
        card_layout.addWidget(self.water_result)

        layout.addWidget(card)

        # คำอธิบายสูตร
        note = QLabel(
            "หมายเหตุ: ค่าน้ำที่คำนวณเป็นค่าประมาณ "
            "ตามปริมาณน้ำและประสิทธิภาพที่กรอก"
        )
        note.setObjectName("description")
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addStretch()
        return page

    def calculate_water(self):
        # อ่านค่าจากช่องกรอก
        area = self.water_area.value()
        depth = self.water_depth.value()
        efficiency = self.water_efficiency.value() / 100

        # น้ำสุทธิที่ต้องการ: 1 ไร่ ต่อความลึก 1 มม.
        # เท่ากับน้ำ 1,600 ลิตร
        net_liters = area * depth * 1600

        # คำนึงถึงการสูญเสียตามประสิทธิภาพระบบ
        total_liters = net_liters / efficiency

        # แปลงลิตรเป็นลูกบาศก์เมตร
        total_cubic_meters = total_liters / 1000

        self.water_result.setText(
            f"ปริมาณน้ำสุทธิที่ต้องการ: "
            f"{net_liters:,.0f} ลิตร\n\n"
            f"ปริมาณน้ำที่ต้องจ่ายโดยประมาณ: "
            f"{total_liters:,.0f} ลิตร\n\n"
            f"เทียบเท่า: {total_cubic_meters:,.2f} "
            f"ลูกบาศก์เมตร"
        )

        self.save_history(
    "น้ำ",
    (
        f"พื้นที่ {area:,.2f} ไร่; "
        f"น้ำสุทธิ {depth:,.1f} มม.; "
        f"ประสิทธิภาพ {efficiency * 100:.0f}%"
    ),
    (
        f"น้ำสุทธิ {net_liters:,.0f} ลิตร; "
        f"น้ำที่ต้องจ่าย {total_liters:,.0f} ลิตร; "
        f"{total_cubic_meters:,.2f} ลบ.ม."
    ),
)

    def create_fertilizer_calculator(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        # หัวข้อหน้า
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        desc = QLabel(description)
        desc.setObjectName("description")
        layout.addWidget(desc)

        layout.addSpacing(12)

        # กล่องกรอกข้อมูล
        card = QFrame()
        card.setObjectName("infoCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(16)

        form = QFormLayout()
        form.setVerticalSpacing(14)

        # 1. พื้นที่สวน
        self.fertilizer_area = QDoubleSpinBox()
        self.fertilizer_area.setRange(0.01, 1000000)
        self.fertilizer_area.setDecimals(2)
        self.fertilizer_area.setValue(10)

        # 2. อัตราปุ๋ยที่ต้องใช้ต่อไร่
        self.fertilizer_rate = QDoubleSpinBox()
        self.fertilizer_rate.setRange(0, 1000)
        self.fertilizer_rate.setDecimals(2)
        self.fertilizer_rate.setValue(25)

        # 3. น้ำหนักปุ๋ยต่อกระสอบ
        self.fertilizer_bag_weight = QDoubleSpinBox()
        self.fertilizer_bag_weight.setRange(1, 1000)
        self.fertilizer_bag_weight.setDecimals(2)
        self.fertilizer_bag_weight.setValue(50)

        # 4. ราคาปุ๋ยต่อกระสอบ
        self.fertilizer_bag_price = QDoubleSpinBox()
        self.fertilizer_bag_price.setRange(0, 1000000)
        self.fertilizer_bag_price.setDecimals(2)
        self.fertilizer_bag_price.setValue(900)

        form.addRow("พื้นที่สวน (ไร่)", self.fertilizer_area)
        form.addRow(
            "อัตราปุ๋ย (กก./ไร่)",
            self.fertilizer_rate
        )
        form.addRow(
            "น้ำหนักต่อกระสอบ (กก.)",
            self.fertilizer_bag_weight
        )
        form.addRow(
            "ราคาต่อกระสอบ (บาท)",
            self.fertilizer_bag_price
        )

        card_layout.addLayout(form)

        # ปุ่มคำนวณ
        calculate_button = QPushButton("คำนวณปริมาณปุ๋ย")
        calculate_button.setMinimumHeight(44)
        calculate_button.setStyleSheet("""
            QPushButton {
                background-color: #2F6B47;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #245738;
            }
        """)

        calculate_button.clicked.connect(
            self.calculate_fertilizer
        )
        card_layout.addWidget(calculate_button)

        # พื้นที่แสดงผล
        self.fertilizer_result = QLabel(
            "กรอกข้อมูล แล้วกดปุ่มคำนวณปริมาณปุ๋ย"
        )
        self.fertilizer_result.setWordWrap(True)
        self.fertilizer_result.setStyleSheet("""
            QLabel {
                color: #1D3325;
                font-size: 15px;
                padding: 8px 0;
            }
        """)
        card_layout.addWidget(self.fertilizer_result)

        layout.addWidget(card)

        note = QLabel(
            "หมายเหตุ: ตัวเลขเริ่มต้นเป็นข้อมูลตัวอย่าง "
            "ควรใช้อัตราปุ๋ยที่เหมาะสมกับอายุยาง "
            "สภาพดิน และคำแนะนำทางวิชาการ"
        )
        note.setObjectName("description")
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addStretch()
        return page

    def calculate_fertilizer(self):
        # อ่านข้อมูลจากช่องกรอก
        area = self.fertilizer_area.value()
        rate = self.fertilizer_rate.value()
        bag_weight = self.fertilizer_bag_weight.value()
        bag_price = self.fertilizer_bag_price.value()

        # คำนวณปริมาณปุ๋ยที่ต้องใช้
        total_kg = area * rate

        # ปัดจำนวนกระสอบขึ้นเป็นจำนวนเต็ม
        if total_kg > 0:
            total_bags = math.ceil(total_kg / bag_weight)
        else:
            total_bags = 0

        # เงินที่ต้องจ่ายเพื่อซื้อปุ๋ยเป็นกระสอบเต็ม
        purchase_cost = total_bags * bag_price

        # มูลค่าปุ๋ยตามปริมาณที่ใช้จริง
        used_cost = (total_kg / bag_weight) * bag_price

        # แสดงผล
        self.fertilizer_result.setText(
            f"ปริมาณปุ๋ยที่ต้องใช้: "
            f"{total_kg:,.2f} กิโลกรัม\n\n"
            f"จำนวนกระสอบที่ต้องซื้อ: "
            f"{total_bags:,} กระสอบ\n\n"
            f"เงินที่ต้องจ่ายเพื่อซื้อปุ๋ย: "
            f"{purchase_cost:,.2f} บาท\n\n"
            f"มูลค่าปุ๋ยตามปริมาณที่ใช้จริง: "
            f"{used_cost:,.2f} บาท"
        )

        self.save_history(
    "ปุ๋ย",
    (
        f"พื้นที่ {area:,.2f} ไร่; "
        f"อัตราปุ๋ย {rate:,.2f} กก./ไร่; "
        f"กระสอบละ {bag_weight:,.2f} กก.; "
        f"ราคากระสอบละ {bag_price:,.2f} บาท"
    ),
    (
        f"ต้องใช้ {total_kg:,.2f} กก.; "
        f"ซื้อ {total_bags} กระสอบ; "
        f"จ่าย {purchase_cost:,.2f} บาท; "
        f"มูลค่าที่ใช้ {used_cost:,.2f} บาท"
    ),
)

    def create_profit_calculator(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        desc = QLabel(description)
        desc.setObjectName("description")
        layout.addWidget(desc)

        note = QLabel(
            "กรอกผลผลิตและค่าใช้จ่ายในรอบเวลาเดียวกัน "
            "เช่น 1 เดือน"
        )
        note.setObjectName("description")
        note.setWordWrap(True)
        layout.addWidget(note)

        # กล่องกรอกข้อมูล
        card = QFrame()
        card.setObjectName("infoCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(14)

        form = QFormLayout()
        form.setVerticalSpacing(12)

        # พื้นที่สวนทั้งหมด
        self.profit_area = QDoubleSpinBox()
        self.profit_area.setRange(0.01, 1000000)
        self.profit_area.setDecimals(2)
        self.profit_area.setValue(10)

        # ปริมาณผลผลิตในรอบที่ต้องการคำนวณ
        self.profit_yield = QDoubleSpinBox()
        self.profit_yield.setRange(0, 100000000)
        self.profit_yield.setDecimals(2)
        self.profit_yield.setValue(500)

        # ราคาขายต่อกิโลกรัม
        self.profit_price = QDoubleSpinBox()
        self.profit_price.setRange(0, 1000000)
        self.profit_price.setDecimals(2)
        self.profit_price.setValue(60)

        # ค่าใช้จ่ายในรอบเดียวกัน
        self.profit_labor = QDoubleSpinBox()
        self.profit_labor.setRange(0, 100000000)
        self.profit_labor.setDecimals(2)
        self.profit_labor.setValue(3000)

        self.profit_fertilizer = QDoubleSpinBox()
        self.profit_fertilizer.setRange(0, 100000000)
        self.profit_fertilizer.setDecimals(2)
        self.profit_fertilizer.setValue(4500)

        self.profit_water = QDoubleSpinBox()
        self.profit_water.setRange(0, 100000000)
        self.profit_water.setDecimals(2)
        self.profit_water.setValue(500)

        self.profit_other = QDoubleSpinBox()
        self.profit_other.setRange(0, 100000000)
        self.profit_other.setDecimals(2)
        self.profit_other.setValue(1000)

        form.addRow("พื้นที่สวน (ไร่)", self.profit_area)
        form.addRow(
            "ผลผลิตยาง (กก.)", self.profit_yield
        )
        form.addRow(
            "ราคาขาย (บาท/กก.)", self.profit_price
        )
        form.addRow(
            "ค่าแรง (บาท)", self.profit_labor
        )
        form.addRow(
            "ค่าปุ๋ย (บาท)", self.profit_fertilizer
        )
        form.addRow(
            "ค่าน้ำและพลังงาน (บาท)", self.profit_water
        )
        form.addRow(
            "ต้นทุนอื่น ๆ (บาท)", self.profit_other
        )

        card_layout.addLayout(form)

        # ปุ่มคำนวณ
        calculate_button = QPushButton("วิเคราะห์ความคุ้มค่า")
        calculate_button.setMinimumHeight(44)
        calculate_button.setStyleSheet("""
            QPushButton {
                background-color: #2F6B47;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #245738;
            }
        """)

        calculate_button.clicked.connect(
            self.calculate_profit
        )
        card_layout.addWidget(calculate_button)

        # แสดงผลลัพธ์
        self.profit_result = QLabel(
            "กรอกข้อมูล แล้วกดปุ่มวิเคราะห์ความคุ้มค่า"
        )
        self.profit_result.setWordWrap(True)
        self.profit_result.setStyleSheet("""
            QLabel {
                color: #1D3325;
                font-size: 15px;
                padding: 8px 0;
            }
        """)
        card_layout.addWidget(self.profit_result)

        layout.addWidget(card)
        layout.addStretch()

        return page

    def calculate_profit(self):
        # อ่านข้อมูล
        area = self.profit_area.value()
        yield_kg = self.profit_yield.value()
        price = self.profit_price.value()

        labor = self.profit_labor.value()
        fertilizer = self.profit_fertilizer.value()
        water = self.profit_water.value()
        other = self.profit_other.value()

        # คำนวณรายรับ
        revenue = yield_kg * price

        # รวมต้นทุน
        total_cost = labor + fertilizer + water + other

        # กำไรสุทธิหรือผลขาดทุน
        net_profit = revenue - total_cost

        # ต้นทุนและกำไรต่อไร่
        cost_per_rai = total_cost / area
        profit_per_rai = net_profit / area

        # ราคาขายขั้นต่ำเพื่อให้รายรับเท่าต้นทุน
        if yield_kg > 0:
            break_even_price = total_cost / yield_kg
            break_even_text = (
                f"{break_even_price:,.2f} บาท/กก."
            )
        else:
            break_even_text = (
                "คำนวณไม่ได้เมื่อผลผลิตเป็นศูนย์"
            )

        self.profit_result.setText(
            f"รายรับรวม: {revenue:,.2f} บาท\n\n"
            f"ต้นทุนรวม: {total_cost:,.2f} บาท\n\n"
            f"กำไรสุทธิ / ขาดทุน: "
            f"{net_profit:,.2f} บาท\n\n"
            f"ต้นทุนต่อไร่: {cost_per_rai:,.2f} บาท\n\n"
            f"กำไรสุทธิต่อไร่: "
            f"{profit_per_rai:,.2f} บาท\n\n"
            f"ราคาคุ้มทุน: {break_even_text}"
        )

        self.save_history(
    "ความคุ้มค่า",
    (
        f"พื้นที่ {area:,.2f} ไร่; "
        f"ผลผลิต {yield_kg:,.2f} กก.; "
        f"ราคาขาย {price:,.2f} บาท/กก."
    ),
    (
        f"รายรับ {revenue:,.2f} บาท; "
        f"ต้นทุน {total_cost:,.2f} บาท; "
        f"กำไร/ขาดทุน {net_profit:,.2f} บาท; "
        f"ต้นทุนต่อไร่ {cost_per_rai:,.2f} บาท; "
        f"ราคาคุ้มทุน {break_even_text}"
    ),
)

    def init_db(self):
        conn = sqlite3.connect(self.db_path)

        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS calculation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    category TEXT NOT NULL,
                    details TEXT NOT NULL,
                    result TEXT NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def save_history(self, category, details, result):
        conn = sqlite3.connect(self.db_path)

        try:
            conn.execute(
                """
                INSERT INTO calculation_history
                (created_at, category, details, result)
                VALUES (?, ?, ?, ?)
                """,
                (
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    category,
                    details,
                    result,
                ),
            )
            conn.commit()

        except sqlite3.Error as error:
            print("บันทึกประวัติไม่สำเร็จ:", error)

        finally:
            conn.close()

    def create_history_page(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        desc = QLabel(description)
        desc.setObjectName("description")
        layout.addWidget(desc)

        refresh_button = QPushButton("รีเฟรชประวัติ")
        refresh_button.clicked.connect(self.load_history)
        layout.addWidget(refresh_button)

        self.history_table = QTableWidget(0, 4)

        self.history_table.setHorizontalHeaderLabels([
            "วันและเวลา",
            "ประเภท",
            "ข้อมูลที่คำนวณ",
            "ผลลัพธ์",
        ])

        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setWordWrap(True)
        self.history_table.setAlternatingRowColors(True)
        layout.addWidget(self.history_table, 1)

        return page

    def load_history(self):
        if not hasattr(self, "history_table"):
            return

        conn = sqlite3.connect(self.db_path)

        try:
            rows = conn.execute(
                """
                SELECT created_at, category, details, result
                FROM calculation_history
                ORDER BY id DESC
                LIMIT 500
                """
            ).fetchall()

        except sqlite3.Error as error:
            print("อ่านประวัติไม่สำเร็จ:", error)
            return

        finally:
            conn.close()

        self.history_table.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.history_table.setItem(
                    row_index, column_index, item
                )

        self.history_table.resizeRowsToContents()

    def init_farm_db(self):
        conn = sqlite3.connect(self.db_path)

        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS farm_profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    farm_name TEXT NOT NULL,
                    area_rai REAL NOT NULL DEFAULT 0,
                    tree_count INTEGER NOT NULL DEFAULT 0,
                    tree_age_years REAL NOT NULL DEFAULT 0,
                    tapping_trees INTEGER NOT NULL DEFAULT 0,
                    soil_type TEXT NOT NULL DEFAULT 'ยังไม่ระบุ',
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def create_farm_page(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        desc = QLabel(description)
        desc.setObjectName("description")
        layout.addWidget(desc)

        card = QFrame()
        card.setObjectName("infoCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(22, 22, 22, 22)
        card_layout.setSpacing(16)

        form = QFormLayout()
        form.setVerticalSpacing(14)

        # ชื่อสวน
        self.farm_name_input = QLineEdit()
        self.farm_name_input.setPlaceholderText(
            "เช่น สวนยางบ้านเรา"
        )

        # พื้นที่สวน
        self.farm_area_input = QDoubleSpinBox()
        self.farm_area_input.setRange(0, 1000000)
        self.farm_area_input.setDecimals(2)
        self.farm_area_input.setSuffix(" ไร่")

        # จำนวนต้นยางทั้งหมด
        self.farm_tree_count_input = QSpinBox()
        self.farm_tree_count_input.setRange(0, 100000000)

        # อายุยางโดยประมาณ
        self.farm_age_input = QDoubleSpinBox()
        self.farm_age_input.setRange(0, 100)
        self.farm_age_input.setDecimals(1)
        self.farm_age_input.setSuffix(" ปี")

        # จำนวนต้นที่เปิดกรีดแล้ว
        self.farm_tapping_input = QSpinBox()
        self.farm_tapping_input.setRange(0, 100000000)

        # ชนิดดิน
        self.farm_soil_input = QComboBox()
        self.farm_soil_input.addItems([
            "ยังไม่ระบุ",
            "ดินร่วน",
            "ดินร่วนปนทราย",
            "ดินเหนียว",
            "ดินทราย",
            "อื่น ๆ",
        ])

        form.addRow("ชื่อสวน", self.farm_name_input)
        form.addRow("พื้นที่สวน", self.farm_area_input)
        form.addRow(
            "จำนวนต้นยางทั้งหมด",
            self.farm_tree_count_input
        )
        form.addRow("อายุยางเฉลี่ย", self.farm_age_input)
        form.addRow(
            "จำนวนต้นที่เปิดกรีด",
            self.farm_tapping_input
        )
        form.addRow("ชนิดดิน", self.farm_soil_input)

        card_layout.addLayout(form)

        save_button = QPushButton("บันทึกข้อมูลสวน")
        save_button.setMinimumHeight(44)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2F6B47;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #245738;
            }
        """)

        save_button.clicked.connect(self.save_farm_data)
        card_layout.addWidget(save_button)

        self.farm_status = QLabel("กำลังโหลดข้อมูลสวน...")
        self.farm_status.setWordWrap(True)
        self.farm_status.setObjectName("description")
        card_layout.addWidget(self.farm_status)

        layout.addWidget(card)
        layout.addStretch()

        # โหลดข้อมูลเก่าจากฐานข้อมูล
        self.load_farm_data()

        return page

    def save_farm_data(self):
        farm_name = self.farm_name_input.text().strip()
        area = self.farm_area_input.value()
        tree_count = self.farm_tree_count_input.value()
        tree_age = self.farm_age_input.value()
        tapping_trees = self.farm_tapping_input.value()
        soil_type = self.farm_soil_input.currentText()

        if not farm_name:
            QMessageBox.warning(
                self,
                "ข้อมูลไม่ครบ",
                "กรุณากรอกชื่อสวนก่อนบันทึก"
            )
            return

        if tapping_trees > tree_count:
            QMessageBox.warning(
                self,
                "ตรวจสอบข้อมูล",
                "จำนวนต้นที่เปิดกรีดต้องไม่เกินจำนวนต้นยางทั้งหมด"
            )
            return

        updated_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        conn = sqlite3.connect(self.db_path)

        try:
            conn.execute("""
                INSERT OR REPLACE INTO farm_profile (
                    id,
                    farm_name,
                    area_rai,
                    tree_count,
                    tree_age_years,
                    tapping_trees,
                    soil_type,
                    updated_at
                )
                VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            """, (
                farm_name,
                area,
                tree_count,
                tree_age,
                tapping_trees,
                soil_type,
                updated_at,
            ))

            conn.commit()

        except sqlite3.Error as error:
            QMessageBox.critical(
                self,
                "บันทึกไม่สำเร็จ",
                f"เกิดข้อผิดพลาดกับฐานข้อมูล:\n{error}"
            )
            return

        finally:
            conn.close()

        self.farm_status.setText(
            f"บันทึกล่าสุด: {updated_at}"
        )

        QMessageBox.information(
            self,
            "บันทึกสำเร็จ",
            "บันทึกข้อมูลสวนเรียบร้อยแล้ว"
        )

    def load_farm_data(self):
        conn = sqlite3.connect(self.db_path)

        try:
            row = conn.execute("""
                SELECT
                    farm_name,
                    area_rai,
                    tree_count,
                    tree_age_years,
                    tapping_trees,
                    soil_type,
                    updated_at
                FROM farm_profile
                WHERE id = 1
            """).fetchone()

        except sqlite3.Error as error:
            self.farm_status.setText(
                f"อ่านข้อมูลไม่สำเร็จ: {error}"
            )
            return

        finally:
            conn.close()

        if row is None:
            self.farm_status.setText(
                "ยังไม่มีข้อมูลสวน กรุณากรอกข้อมูลแล้วบันทึก"
            )
            return

        self.farm_name_input.setText(row[0])
        self.farm_area_input.setValue(row[1])
        self.farm_tree_count_input.setValue(row[2])
        self.farm_age_input.setValue(row[3])
        self.farm_tapping_input.setValue(row[4])

        soil_index = self.farm_soil_input.findText(row[5])

        if soil_index >= 0:
            self.farm_soil_input.setCurrentIndex(soil_index)

        self.farm_status.setText(
            f"ข้อมูลล่าสุดบันทึกเมื่อ: {row[6]}"
        )


    def init_production_db(self):
        conn = sqlite3.connect(self.db_path)

        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS production_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    product_type TEXT NOT NULL,
                    yield_kg REAL NOT NULL DEFAULT 0,
                    tapping_days INTEGER NOT NULL DEFAULT 0,
                    tapping_trees INTEGER NOT NULL DEFAULT 0,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(year, month, product_type)
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def create_production_page(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        desc = QLabel(description)
        desc.setObjectName("description")
        layout.addWidget(desc)

        # กล่องกรอกข้อมูลผลผลิต
        card = QFrame()
        card.setObjectName("infoCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(12)

        form = QFormLayout()
        form.setVerticalSpacing(10)

        # ปีที่บันทึก
        self.production_year = QSpinBox()
        self.production_year.setRange(2000, 2100)
        self.production_year.setValue(datetime.now().year)

        # เดือนที่บันทึก
        self.production_months = [
            "มกราคม", "กุมภาพันธ์", "มีนาคม",
            "เมษายน", "พฤษภาคม", "มิถุนายน",
            "กรกฎาคม", "สิงหาคม", "กันยายน",
            "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
        ]

        self.production_month = QComboBox()
        self.production_month.addItems(
            self.production_months
        )
        self.production_month.setCurrentIndex(
            datetime.now().month - 1
        )

        # ชนิดผลผลิต
        self.production_type = QComboBox()
        self.production_type.addItems([
            "น้ำยางสด",
            "ยางก้อนถ้วย",
            "ยางแผ่นดิบ",
            "ยางแผ่นรมควัน",
            "อื่น ๆ",
        ])

        # น้ำหนักผลผลิต
        self.production_yield = QDoubleSpinBox()
        self.production_yield.setRange(0, 100000000)
        self.production_yield.setDecimals(2)
        self.production_yield.setSuffix(" กก.")

        # จำนวนวันที่กรีดจริงในเดือนนั้น
        self.production_days = QSpinBox()
        self.production_days.setRange(0, 31)
        self.production_days.setSuffix(" วัน")

        # จำนวนต้นที่เปิดกรีดในเดือนนั้น
        self.production_trees = QSpinBox()
        self.production_trees.setRange(0, 100000000)

        # หมายเหตุ
        self.production_notes = QLineEdit()
        self.production_notes.setPlaceholderText(
            "เช่น ฝนตกหลายวัน หรือหยุดกรีดบางช่วง"
        )

        form.addRow("ปี พ.ศ./ค.ศ. ที่บันทึก", self.production_year)
        form.addRow("เดือน", self.production_month)
        form.addRow("ชนิดผลผลิต", self.production_type)
        form.addRow("ผลผลิตรวม", self.production_yield)
        form.addRow("จำนวนวันกรีดจริง", self.production_days)
        form.addRow("จำนวนต้นที่เปิดกรีด", self.production_trees)
        form.addRow("หมายเหตุ", self.production_notes)

        card_layout.addLayout(form)

        save_button = QPushButton("บันทึกผลผลิต")
        save_button.setMinimumHeight(42)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2F6B47;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #245738;
            }
        """)
        save_button.clicked.connect(
            self.save_production_record
        )
        card_layout.addWidget(save_button)

        layout.addWidget(card)

        # แสดงจำนวนประวัติและแนวทางการใช้ข้อมูล
        self.production_summary = QLabel("")
        self.production_summary.setObjectName("description")
        self.production_summary.setWordWrap(True)
        layout.addWidget(self.production_summary)

        self.production_table = QTableWidget(0, 6)
        self.production_table.setHorizontalHeaderLabels([
            "เดือน",
            "ชนิดผลผลิต",
            "ผลผลิต (กก.)",
            "วันกรีด",
            "ต้นเปิดกรีด",
            "หมายเหตุ",
        ])

        self.production_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.production_table.verticalHeader().setVisible(False)
        self.production_table.setAlternatingRowColors(True)
        self.production_table.setWordWrap(True)

        layout.addWidget(self.production_table, 1)

        # เติมจำนวนต้นเปิดกรีดจากข้อมูลสวน หากมี
        conn = sqlite3.connect(self.db_path)

        try:
            row = conn.execute("""
                SELECT tapping_trees
                FROM farm_profile
                WHERE id = 1
            """).fetchone()

            if row is not None:
                self.production_trees.setValue(row[0])

        except sqlite3.Error:
            pass

        finally:
            conn.close()

        self.load_production_records()

        return page

    def save_production_record(self):
        year = self.production_year.value()
        month = self.production_month.currentIndex() + 1
        product_type = self.production_type.currentText()
        yield_kg = self.production_yield.value()
        tapping_days = self.production_days.value()
        tapping_trees = self.production_trees.value()
        notes = self.production_notes.text().strip()

        # ตรวจสอบจำนวนต้นเทียบกับข้อมูลประจำสวน
        conn = sqlite3.connect(self.db_path)

        try:
            farm = conn.execute("""
                SELECT tree_count
                FROM farm_profile
                WHERE id = 1
            """).fetchone()

            if farm is not None and tapping_trees > farm[0]:
                QMessageBox.warning(
                    self,
                    "ตรวจสอบข้อมูล",
                    "จำนวนต้นที่เปิดกรีดมากกว่าจำนวนต้นยางทั้งหมดในข้อมูลสวน"
                )
                return

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn.execute("""
                INSERT INTO production_records (
                    year,
                    month,
                    product_type,
                    yield_kg,
                    tapping_days,
                    tapping_trees,
                    notes,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(year, month, product_type)
                DO UPDATE SET
                    yield_kg = excluded.yield_kg,
                    tapping_days = excluded.tapping_days,
                    tapping_trees = excluded.tapping_trees,
                    notes = excluded.notes,
                    updated_at = excluded.updated_at
            """, (
                year,
                month,
                product_type,
                yield_kg,
                tapping_days,
                tapping_trees,
                notes,
                now,
                now,
            ))

            conn.commit()

        except sqlite3.Error as error:
            QMessageBox.critical(
                self,
                "บันทึกไม่สำเร็จ",
                f"เกิดข้อผิดพลาดกับฐานข้อมูล:\n{error}"
            )
            return

        finally:
            conn.close()

        self.production_notes.clear()

        QMessageBox.information(
            self,
            "บันทึกสำเร็จ",
            "บันทึกผลผลิตเรียบร้อยแล้ว"
        )

        self.load_production_records()

    def load_production_records(self):
        if not hasattr(self, "production_table"):
            return

        conn = sqlite3.connect(self.db_path)

        try:
            rows = conn.execute("""
                SELECT
                    year,
                    month,
                    product_type,
                    yield_kg,
                    tapping_days,
                    tapping_trees,
                    notes
                FROM production_records
                ORDER BY year DESC, month DESC
                LIMIT 500
            """).fetchall()

        except sqlite3.Error as error:
            self.production_summary.setText(
                f"อ่านข้อมูลไม่สำเร็จ: {error}"
            )
            return

        finally:
            conn.close()

        self.production_table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            year, month, product, yield_kg, days, trees, notes = row

            values = [
                f"{self.production_months[month - 1]} {year}",
                product,
                f"{yield_kg:,.2f}",
                str(days),
                f"{trees:,}",
                notes,
            ]

            for j, value in enumerate(values):
                self.production_table.setItem(
                    i, j, QTableWidgetItem(str(value))
                )

        self.production_table.resizeRowsToContents()

        self.production_summary.setText(
            f"มีประวัติผลผลิต {len(rows)} รายการ "
            "ข้อมูลนี้จะใช้เป็นพื้นฐานสำหรับวิเคราะห์แนวโน้ม "
            "และคาดการณ์ผลผลิตในขั้นต่อไป"
        )


    def create_forecast_page(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        self.forecast_month_names = [
            "มกราคม", "กุมภาพันธ์", "มีนาคม",
            "เมษายน", "พฤษภาคม", "มิถุนายน",
            "กรกฎาคม", "สิงหาคม", "กันยายน",
            "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
        ]

        # หัวข้อหน้า
        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        desc = QLabel(description)
        desc.setObjectName("description")
        layout.addWidget(desc)

        # กล่องเลือกชนิดผลผลิต
        card = QFrame()
        card.setObjectName("infoCard")

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        form = QFormLayout()

        self.forecast_product = QComboBox()
        self.forecast_product.addItems([
            "น้ำยางสด",
            "ยางก้อนถ้วย",
            "ยางแผ่นดิบ",
            "ยางแผ่นรมควัน",
            "อื่น ๆ",
        ])

        form.addRow(
            "ชนิดผลผลิตที่ต้องการคาดการณ์",
            self.forecast_product
        )
        card_layout.addLayout(form)

        forecast_button = QPushButton(
            "วิเคราะห์และคาดการณ์เดือนถัดไป"
        )
        forecast_button.setMinimumHeight(44)
        forecast_button.setStyleSheet("""
            QPushButton {
                background-color: #2F6B47;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #245738;
            }
        """)

        forecast_button.clicked.connect(
            self.calculate_forecast
        )
        card_layout.addWidget(forecast_button)

        self.forecast_result = QLabel(
            "เลือกชนิดผลผลิต แล้วกดปุ่มคาดการณ์"
        )
        self.forecast_result.setWordWrap(True)
        self.forecast_result.setStyleSheet("""
            QLabel {
                color: #1D3325;
                font-size: 15px;
                padding: 8px 0;
            }
        """)
        card_layout.addWidget(self.forecast_result)

        layout.addWidget(card)

        # ตารางข้อมูลย้อนหลังที่นำมาใช้
        history_title = QLabel(
            "ข้อมูลย้อนหลังที่ใช้วิเคราะห์"
        )
        history_title.setObjectName("infoTitle")
        layout.addWidget(history_title)

        self.forecast_table = QTableWidget(0, 4)
        self.forecast_table.setHorizontalHeaderLabels([
            "เดือน",
            "ผลผลิต (กก.)",
            "วันกรีด",
            "ต้นเปิดกรีด",
        ])

        self.forecast_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.forecast_table.verticalHeader().setVisible(False)
        self.forecast_table.setAlternatingRowColors(True)
        self.forecast_table.setWordWrap(True)

        layout.addWidget(self.forecast_table, 1)

        note = QLabel(
            "หมายเหตุ: ผลลัพธ์เป็นค่าประมาณจากแนวโน้มย้อนหลัง "
            "ยังไม่รวมฤดูกาล สภาพอากาศ หรือปัจจัยการจัดการสวน "
            "จึงไม่ใช่การรับประกันผลผลิตจริง"
        )
        note.setObjectName("description")
        note.setWordWrap(True)
        layout.addWidget(note)

        return page

    def calculate_forecast(self):
        product_type = self.forecast_product.currentText()

        # อ่านข้อมูลล่าสุดไม่เกิน 6 เดือน
        conn = sqlite3.connect(self.db_path)

        try:
            rows = conn.execute("""
                SELECT
                    year,
                    month,
                    yield_kg,
                    tapping_days,
                    tapping_trees
                FROM production_records
                WHERE product_type = ?
                ORDER BY year DESC, month DESC
                LIMIT 6
            """, (product_type,)).fetchall()

        except sqlite3.Error as error:
            self.forecast_result.setText(
                f"อ่านข้อมูลไม่สำเร็จ: {error}"
            )
            return

        finally:
            conn.close()

        # เรียงจากเดือนเก่าไปใหม่
        rows = list(reversed(rows))

        # แสดงข้อมูลจริงที่ใช้วิเคราะห์
        self.forecast_table.setRowCount(len(rows))

        for i, row in enumerate(rows):
            year, month, yield_kg, days, trees = row

            values = [
                f"{self.forecast_month_names[month - 1]} {year}",
                f"{yield_kg:,.2f}",
                str(days),
                f"{trees:,}",
            ]

            for j, value in enumerate(values):
                self.forecast_table.setItem(
                    i, j, QTableWidgetItem(value)
                )

        self.forecast_table.resizeRowsToContents()

        # ต้องมีข้อมูลอย่างน้อย 3 เดือน
        if len(rows) < 3:
            self.forecast_result.setText(
                f"ยังคาดการณ์ไม่ได้สำหรับ {product_type}\n\n"
                f"พบข้อมูลย้อนหลังเพียง {len(rows)} เดือน\n"
                "กรุณาบันทึกข้อมูลผลผลิตชนิดเดียวกัน "
                "อย่างน้อย 3 เดือนก่อนใช้งาน"
            )
            return

        # แปลงปีและเดือนเป็นลำดับเดือน
        # เพื่อให้รองรับการข้ามปีและเดือนที่ไม่มีข้อมูล
        xs = [
            year * 12 + month - 1
            for year, month, yield_kg, days, trees in rows
        ]

        ys = [
            yield_kg
            for year, month, yield_kg, days, trees in rows
        ]

        # คำนวณแนวโน้มเชิงเส้นด้วยวิธี Least Squares
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n

        denominator = sum(
            (x - mean_x) ** 2 for x in xs
        )

        if denominator == 0:
            self.forecast_result.setText(
                "ข้อมูลเดือนซ้ำกันหรือไม่เพียงพอ "
                "จึงยังคำนวณแนวโน้มไม่ได้"
            )
            return

        slope = sum(
            (x - mean_x) * (y - mean_y)
            for x, y in zip(xs, ys)
        ) / denominator

        # คาดการณ์เดือนถัดจากข้อมูลล่าสุด
        target_x = xs[-1] + 1

        predicted_yield = (
            mean_y + slope * (target_x - mean_x)
        )

        # ผลผลิตไม่สามารถติดลบได้
        predicted_yield = max(0.0, predicted_yield)

        target_year = target_x // 12
        target_month = target_x % 12 + 1

        target_month_name = (
            self.forecast_month_names[target_month - 1]
        )

        # อธิบายแนวโน้ม
        if slope > 0.01:
            trend = (
                f"แนวโน้มเพิ่มขึ้นประมาณ "
                f"{slope:,.2f} กก./เดือน"
            )
        elif slope < -0.01:
            trend = (
                f"แนวโน้มลดลงประมาณ "
                f"{abs(slope):,.2f} กก./เดือน"
            )
        else:
            trend = "แนวโน้มค่อนข้างคงที่"

        self.forecast_result.setText(
            f"ชนิดผลผลิต: {product_type}\n\n"
            f"เดือนที่คาดการณ์: "
            f"{target_month_name} {target_year}\n\n"
            f"ผลผลิตที่คาดการณ์: "
            f"{predicted_yield:,.2f} กิโลกรัม\n\n"
            f"ข้อมูลที่ใช้: {n} เดือนล่าสุด\n"
            f"{trend}\n\n"
            "ค่าดังกล่าวคำนวณจากแนวโน้มเชิงเส้น "
            "ยังไม่ได้ปรับตามฤดูกาลหรือสภาพอากาศ"
        )


    def create_production_chart_page(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        desc = QLabel(description)
        desc.setObjectName("description")
        layout.addWidget(desc)

        controls = QHBoxLayout()

        self.chart_product_type = QComboBox()
        self.chart_product_type.addItems([
            "น้ำยางสด",
            "ยางก้อนถ้วย",
            "ยางแผ่นดิบ",
            "ยางแผ่นรมควัน",
            "อื่น ๆ",
        ])

        controls.addWidget(QLabel("ชนิดผลผลิต"))
        controls.addWidget(self.chart_product_type)
        controls.addStretch()

        refresh_button = QPushButton("อัปเดตกราฟ")
        refresh_button.clicked.connect(
            self.refresh_production_chart
        )
        controls.addWidget(refresh_button)

        layout.addLayout(controls)

        self.production_figure = Figure(figsize=(8, 4))
        self.production_canvas = FigureCanvasQTAgg(
            self.production_figure
        )

        layout.addWidget(self.production_canvas, 1)

        self.chart_summary = QLabel("")
        self.chart_summary.setWordWrap(True)
        self.chart_summary.setObjectName("description")
        layout.addWidget(self.chart_summary)

        self.chart_product_type.currentTextChanged.connect(
            self.refresh_production_chart
        )

        self.refresh_production_chart()

        return page

    def refresh_production_chart(self):
        if not hasattr(self, "production_figure"):
            return

        product_type = self.chart_product_type.currentText()

        conn = sqlite3.connect(self.db_path)

        try:
            rows = conn.execute("""
                SELECT year, month, yield_kg
                FROM production_records
                WHERE product_type = ?
                ORDER BY year, month
            """, (product_type,)).fetchall()

        except sqlite3.Error as error:
            self.chart_summary.setText(
                f"อ่านข้อมูลไม่สำเร็จ: {error}"
            )
            return

        finally:
            conn.close()

        self.production_figure.clear()
        ax = self.production_figure.add_subplot(111)

        if not rows:
            ax.text(
                0.5, 0.5,
                "ยังไม่มีข้อมูลผลผลิต",
                ha="center",
                va="center",
                transform=ax.transAxes
            )
            ax.set_axis_off()

            self.chart_summary.setText(
                "กรุณาบันทึกผลผลิตในเมนูผลผลิตก่อน"
            )

            self.production_canvas.draw()
            return

        # สร้างแกนเวลาต่อเนื่องรายเดือน
        # เพื่อให้เดือนที่ไม่มีข้อมูลไม่ถูกมองว่าอยู่ติดกัน
        first_year, first_month, _ = rows[0]
        last_year, last_month, _ = rows[-1]

        start = first_year * 12 + first_month - 1
        end = last_year * 12 + last_month - 1

        monthly = {
            year * 12 + month - 1: yield_kg
            for year, month, yield_kg in rows
        }

        xs = list(range(start, end + 1))
        actual = [
            monthly.get(x, float("nan"))
            for x in xs
        ]

        labels = [
            f"{self.forecast_month_names[x % 12][:3]} {x // 12}"
            for x in xs
        ]

        ax.plot(
            xs, actual,
            marker="o",
            linewidth=2,
            label="ผลผลิตจริง"
        )

        # แสดงเส้นแนวโน้มเมื่อมีข้อมูลอย่างน้อย 3 เดือน
        if len(rows) >= 3:
            observed_x = [
                year * 12 + month - 1
                for year, month, yield_kg in rows
            ]

            observed_y = [
                yield_kg
                for year, month, yield_kg in rows
            ]

            n = len(observed_x)
            mean_x = sum(observed_x) / n
            mean_y = sum(observed_y) / n

            denominator = sum(
                (x - mean_x) ** 2
                for x in observed_x
            )

            if denominator > 0:
                slope = sum(
                    (x - mean_x) * (y - mean_y)
                    for x, y in zip(observed_x, observed_y)
                ) / denominator

                trend = [
                    max(
                        0.0,
                        mean_y + slope * (x - mean_x)
                    )
                    for x in observed_x
                ]

                ax.plot(
                    observed_x,
                    trend,
                    linestyle="--",
                    linewidth=2,
                    label="แนวโน้มเชิงเส้น"
                )

        ax.set_title(f"ผลผลิตรายเดือน: {product_type}")
        ax.set_xlabel("เดือน")
        ax.set_ylabel("ผลผลิต (กิโลกรัม)")
        ax.set_xticks(xs)
        ax.set_xticklabels(
            labels,
            rotation=45,
            ha="right"
        )
        ax.grid(True, alpha=0.3)
        ax.legend()
        self.production_figure.tight_layout()

        self.chart_summary.setText(
            f"แสดงข้อมูล {len(rows)} รายการ "
            f"ตั้งแต่ {labels[0]} ถึง {labels[-1]}\n"
            "เส้นประแสดงแนวโน้มเชิงเส้นจากข้อมูลที่มี "
            "ไม่ใช่การรับประกันผลผลิตในอนาคต"
        )

        self.production_canvas.draw()

    def create_placeholder(self, title, description):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(12)

        heading = QLabel(title)
        heading.setObjectName("pageTitle")
        layout.addWidget(heading)

        desc = QLabel(description)
        desc.setObjectName("description")
        layout.addWidget(desc)

        layout.addSpacing(12)

        info = QFrame()
        info.setObjectName("infoCard")

        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(22, 22, 22, 22)
        info_layout.setSpacing(14)

        info_title = QLabel("เริ่มจัดการสวนของคุณ")
        info_title.setObjectName("infoTitle")
        info_layout.addWidget(info_title)

        info_desc = QLabel(
            "หรือเครื่องมือคำนวณที่พร้อมใช้งาน"
        )
        info_desc.setObjectName("infoDescription")
        info_desc.setWordWrap(True)
        info_layout.addWidget(info_desc)

        shortcuts = QHBoxLayout()
        shortcuts.setSpacing(10)
        for label, index in (
            ("ข้อมูลสวน", 5),
            ("บันทึกผลผลิต", 6),
            ("คำนวณน้ำ", 1),
            ("คำนวณปุ๋ย", 2),
        ):
            button = QPushButton(label)
            button.clicked.connect(
                lambda checked=False, page_index=index:
                self.show_page(page_index)
            )
            shortcuts.addWidget(button)

        info_layout.addLayout(shortcuts)

        layout.addWidget(info)
        layout.addStretch()

        return page

    def show_page(self, index):
        self.page_stack.setCurrentIndex(index)

        for i, button in enumerate(self.nav_buttons):
            button.setChecked(i == index)

        if index == 4:
            self.load_history()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = RubberFarmApp()
    window.show()

    sys.exit(app.exec())
