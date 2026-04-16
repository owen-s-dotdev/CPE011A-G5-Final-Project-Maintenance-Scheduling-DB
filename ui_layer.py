from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget
)


# GLOBAL STYLE
def apply_global_style(app):
    app.setStyleSheet("""
    QWidget {
        background-color: #f6f8fb;
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 14px;
        color: #333;
    }

    QLineEdit, QDateEdit {
        background: white;
        border: 1px solid #e3e6ea;
        border-radius: 8px;
        padding: 8px;
    }

    QPushButton {
        background-color: transparent;
        border: 2px solid #2563eb;
        color: #2563eb;
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 500;
    }

    QPushButton[class="no-style"] {
        border: none;
        background: transparent;
        color: #111111;
    }

    QPushButton.icon {
        border: none;
        background: transparent;
        color: #111111;
    }
                        
    QPushButton:hover {
        background-color: rgba(37, 99, 235, 0.1);
    }

                      

    /* PRIMARY (blue) */
    QPushButton.primary {
        border: 2px solid #2563eb;
        color: #2563eb;
    }
    QPushButton.primary:hover {
        background-color: rgba(37, 99, 235, 0.1);
    }

    /* SUCCESS (optional: green) */
    QPushButton.success {
        border: 2px solid #16a34a;
        color: #16a34a;
    }
    QPushButton.success:hover {
        background-color: rgba(22, 163, 74, 0.1);
    }

    /* DANGER (delete) */
    QPushButton.danger {
        border: 2px solid #dc2626;
        color: #dc2626;
    }
    QPushButton.danger:hover {
        background-color: rgba(220, 38, 38, 0.1);
    }

    /* NEUTRAL */
    QPushButton.neutral {
        border: 2px solid #6b7280;
        color: #6b7280;
    }
    QPushButton.neutral:hover {
        background-color: rgba(107, 114, 128, 0.1);
    }                      

    QPushButton.secondary {
        background-color: #f3f4f6;
        color: #333;
    }

                      

    QTableWidget {
        background: white;
        alternate-background-color: #f9fafb;  /* light grey */
        border: none;
        gridline-color: transparent;
    }

    QHeaderView::section {
        background-color: #f9fafb;
        border: none;
        padding: 8px;
        font-weight: 600;
    }

    QTableWidget::item {
        padding: 12px;
    }
                      
    QTableWidget::item:focus {
    outline: none;
    border: none;
    }
                      
    QTableWidget {
    outline: none;
    }

    QTableWidget::item:selected {
        background-color: #e0ecff;
        color: black;
    }

    #card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #e5e7eb;
    }
                      
    QTableWidget {
    gridline-color: transparent;
    border: none;
    }

    QTableWidget::item {
    border-bottom: 1px solid #e5e7eb;
    }


    """)


# SIDEBAR
from PyQt6.QtCore import QRect, QPropertyAnimation, QEasingCurve


class Sidebar(QWidget):
    def __init__(self, parent, on_select):
        super().__init__(parent)

        self.on_select = on_select
        self.setFixedWidth(220)
        self.setGeometry(-220, 0, 220, parent.height())
        #self.setEnabled(False)
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet("""
            Sidebar {
                background-color: #ffffff;
                border-right: 1px solid #e5e7eb;
            }
        """)

        from PyQt6.QtWidgets import QGraphicsDropShadowEffect

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(2, 0)
        self.setGraphicsEffect(shadow)

        self.is_visible = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Close button
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(10, 10, 10, 10)
        top_bar.addStretch()

        close_btn = QPushButton("X")
        close_btn.setFixedSize(36, 36)
        close_btn.setAccessibleName("Close sidebar")

        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 0, 0, 0.02);
                color: #111111;
                border: 1px solid rgba(0, 0, 0, 0.12);
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #111111;
                background-color: rgba(0, 0, 0, 0.08);
            }
        """)

        close_btn.clicked.connect(self.toggle)

        close_btn.setProperty("class", "")
        close_btn.style().unpolish(close_btn)
        close_btn.style().polish(close_btn)

        top_bar.addWidget(close_btn)
        layout.addLayout(top_bar)

        # Menu buttons
        self.add_menu_button(layout, "Dashboard", lambda: self.on_select(0))
        self.add_menu_button(layout, "Database", lambda: self.on_select(1))

        layout.addStretch()

        # Animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def add_menu_button(self, layout, text, callback):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #222222;
                text-align: left;
                padding: 12px 20px;
                border: none;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)

        def wrapped():
            callback()
            self.toggle()

        btn.clicked.connect(wrapped)
        layout.addWidget(btn)

    def toggle(self):
        width = self.width()
        height = self.parent().height()

        if self.is_visible:
            start = QRect(0, 0, width, height)
            end = QRect(-width, 0, width, height)
            self.setEnabled(False)  # disable interaction when closing
        else:
            self.setEnabled(True)   # enable interaction when opening
            self.raise_()           # bring to front
            start = QRect(-width, 0, width, height)
            end = QRect(0, 0, width, height)

        self.animation.stop()
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()

        self.is_visible = not self.is_visible

# DASHBOARD (LANDING PAGE)
class DashboardPage(QWidget):
    def __init__(self, enter_callback):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Maintenance System")
        title.setStyleSheet("font-size: 28px; font-weight: bold;")

        subtitle = QLabel("Manage devices, records, and logs.")
        subtitle.setStyleSheet("color: #666;")

        btn_enter = QPushButton("Enter Dashboard")
        btn_enter.clicked.connect(enter_callback)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(btn_enter)
        layout.addStretch()

        self.setLayout(layout)


# MAIN WRAPPER
from PyQt6.QtCore import Qt


class MainUIWrapper(QWidget):
    def __init__(self, existing_main_widget):
        super().__init__()

        self.setWindowTitle("Maintenance Record Management System")
        self.stack = QStackedWidget()

        # Pages
        self.dashboard = DashboardPage(self.enter_main)
        self.main_app = existing_main_widget

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.main_app)

        # Sidebar (floating animated)
        self.sidebar = Sidebar(self, self.switch_page)
        self.sidebar.setParent(self)
        self.sidebar.move(0, 0)
        self.sidebar.setStyleSheet("""
            background-color: white;
            border-right: 1px solid #ddd;
        """)

        # BUTTON 
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setFixedSize(40, 40)
        #self.toggle_btn.raise_()
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #222222;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #555555;
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 6px;
            }
        """)

        self.toggle_btn.clicked.connect(self.toggle_sidebar)

        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Now this works
        content_layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        content_layout.addWidget(self.stack)

        layout.addLayout(content_layout)

        self.setLayout(layout)

        # Start on dashboard
        self.stack.setCurrentIndex(0)

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)

    def enter_main(self):
        self.stack.setCurrentIndex(1)

    def toggle_sidebar(self):
        self.sidebar.toggle()
        self.toggle_btn.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        if self.sidebar.is_visible:
            self.sidebar.setGeometry(0, 0, self.sidebar.width(), self.height())
        else:
            self.sidebar.setGeometry(-self.sidebar.width(), 0, self.sidebar.width(), self.height())