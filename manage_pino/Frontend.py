import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QLineEdit, QTextEdit,
    QListWidget, QListWidgetItem, QMessageBox, QInputDialog,
    QComboBox, QSpinBox, QSlider, QColorDialog, QFontComboBox,
    QGroupBox, QFormLayout, QDateEdit, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QTabWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor, QPalette


class TaskManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Менеджер задач")
        self.setMinimumSize(1100, 700)
        
        # Данные задач
        self.tasks = []  # [(название, описание, статус, дата), ...]
        self.task_history = []
        
        self.setup_ui()
        self.apply_style()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # ========== Левая панель (как на фото - Favorites, Containers, Input Widgets) ==========
        left_panel = QWidget()
        left_panel.setFixedWidth(220)
        left_panel.setStyleSheet("background-color: #2c3e50; border-radius: 10px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(5)
        left_layout.setContentsMargins(10, 15, 10, 15)
        
        # Заголовок панели
        title_label = QLabel("Менеджер задач")
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title_label)
        
        # Кнопки навигации (как вкладки на фото)
        self.btn_tasks = self.create_nav_button("📋 Актуальные задачи")
        self.btn_history = self.create_nav_button("📜 История задач")
        self.btn_stats = self.create_nav_button("📊 Статистика")
        self.btn_settings = self.create_nav_button("⚙️ Nastrohijki")
        self.btn_appearance = self.create_nav_button("🎨 Nastrohijki vida")
        
        left_layout.addWidget(self.btn_tasks)
        left_layout.addWidget(self.btn_history)
        left_layout.addWidget(self.btn_stats)
        left_layout.addWidget(self.btn_settings)
        left_layout.addWidget(self.btn_appearance)
        left_layout.addStretch()
        
        # ========== Центральная область с вкладками (Stacked Widget) ==========
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #ecf0f1; border-radius: 10px;")
        
        # Создание вкладок
        self.tasks_tab = self.create_tasks_tab()
        self.history_tab = self.create_history_tab()
        self.stats_tab = self.create_stats_tab()
        self.settings_tab = self.create_settings_tab()
        self.appearance_tab = self.create_appearance_tab()
        
        self.stacked_widget.addWidget(self.tasks_tab)      # индекс 0
        self.stacked_widget.addWidget(self.history_tab)    # индекс 1
        self.stacked_widget.addWidget(self.stats_tab)      # индекс 2
        self.stacked_widget.addWidget(self.settings_tab)   # индекс 3
        self.stacked_widget.addWidget(self.appearance_tab) # индекс 4
        
        # Добавление в главный layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.stacked_widget, stretch=1)
        
        # Подключение кнопок
        self.btn_tasks.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.btn_history.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.btn_stats.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.btn_settings.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.btn_appearance.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        
        # Добавляем пример задач
        self.add_sample_tasks()
        
    def create_nav_button(self, text):
        """Создание стилизованной кнопки навигации"""
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 12px;
                text-align: left;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """)
        return btn
    
    def create_tasks_tab(self):
        """Вкладка с актуальными задачами (Aktualnye zadach)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # Верхняя панель с кнопками управления (как на фото: Dobawite, Udolet, Izmenite)
        controls_group = QGroupBox("Управление задачами")
        controls_layout = QHBoxLayout(controls_group)
        
        self.btn_add = QPushButton("➕ Dobawite zadachu")
        self.btn_delete = QPushButton("❌ Udolet zadachu")
        self.btn_edit = QPushButton("✏️ Izmenite zadachu")
        
        for btn in [self.btn_add, self.btn_delete, self.btn_edit]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            controls_layout.addWidget(btn)
        
        controls_layout.addStretch()
        layout.addWidget(controls_group)
        
        # Список задач (как на фото - Wypisane zadachy)
        tasks_group = QGroupBox("Aktualnye zadach:")
        tasks_layout = QVBoxLayout(tasks_group)
        
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        tasks_layout.addWidget(self.task_list)
        layout.addWidget(tasks_group)
        
        # Подключение кнопок
        self.btn_add.clicked.connect(self.add_task)
        self.btn_delete.clicked.connect(self.delete_task)
        self.btn_edit.clicked.connect(self.edit_task)
        
        return tab
    
    def create_history_tab(self):
        """Вкладка истории задач (Istorija zadachu)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        label = QLabel("📜 Istorija zadach")
        label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(label)
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
                color: #7f8c8d;
            }
        """)
        layout.addWidget(self.history_list)
        
        btn_clear_history = QPushButton("Очистить историю")
        btn_clear_history.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_clear_history.clicked.connect(self.clear_history)
        layout.addWidget(btn_clear_history)
        
        return tab
    
    def create_stats_tab(self):
        """Вкладка статистики (Statystykę)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        label = QLabel("📊 Statystykę")
        label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(label)
        
        # Статистическая информация
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            font-size: 14px;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #bdc3c7;
        """)
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)
        
        # Кнопка обновления статистики
        btn_refresh = QPushButton("Обновить статистику")
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        btn_refresh.clicked.connect(self.update_stats)
        layout.addWidget(btn_refresh)
        
        layout.addStretch()
        
        return tab
    
    def create_settings_tab(self):
        """Вкладка настроек (Nastrohijki)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        label = QLabel("⚙️ Nastrohijki")
        label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(label)
        
        # Настройки
        settings_group = QGroupBox("Общие настройки")
        form_layout = QFormLayout(settings_group)
        
        self.notification_check = QCheckBox("Включить уведомления")
        self.notification_check.setChecked(True)
        form_layout.addRow("Уведомления:", self.notification_check)
        
        self.auto_save_check = QCheckBox("Автосохранение")
        self.auto_save_check.setChecked(True)
        form_layout.addRow("Автосохранение:", self.auto_save_check)
        
        self.default_priority = QComboBox()
        self.default_priority.addItems(["Низкий", "Средний", "Высокий"])
        form_layout.addRow("Приоритет по умолчанию:", self.default_priority)
        
        layout.addWidget(settings_group)
        layout.addStretch()
        
        return tab
    
    def create_appearance_tab(self):
        """Вкладка настройки вида (Nastrohijki vida)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        label = QLabel("🎨 Nastrohijki vida")
        label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(label)
        
        # Настройки внешнего вида
        appearance_group = QGroupBox("Настройки внешнего вида")
        form_layout = QFormLayout(appearance_group)
        
        # Выбор шрифта
        self.font_combo = QFontComboBox()
        form_layout.addRow("Шрифт:", self.font_combo)
        
        # Размер шрифта
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 20)
        self.font_size.setValue(10)
        form_layout.addRow("Размер шрифта:", self.font_size)
        
        # Цвет фона
        self.bg_color_btn = QPushButton("Выбрать цвет фона")
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        form_layout.addRow("Цвет фона:", self.bg_color_btn)
        
        # Цвет текста
        self.text_color_btn = QPushButton("Выбрать цвет текста")
        self.text_color_btn.clicked.connect(self.choose_text_color)
        form_layout.addRow("Цвет текста:", self.text_color_btn)
        
        # Применить настройки
        btn_apply = QPushButton("Применить настройки")
        btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        btn_apply.clicked.connect(self.apply_appearance)
        
        layout.addWidget(appearance_group)
        layout.addWidget(btn_apply)
        layout.addStretch()
        
        return tab
    
    def add_sample_tasks(self):
        """Добавление примера задач"""
        self.tasks = [
            ("Создать интерфейс", "Разработать GUI на PyQt6", "В процессе", QDate.currentDate().addDays(0)),
            ("Написать документацию", "Описать все функции", "Не начата", QDate.currentDate().addDays(3)),
            ("Протестировать", "Провести тестирование", "Завершена", QDate.currentDate().addDays(-2)),
        ]
        self.refresh_task_list()
    
    def refresh_task_list(self):
        """Обновление списка задач"""
        self.task_list.clear()
        for i, (title, desc, status, date) in enumerate(self.tasks):
            status_icon = "🟢" if status == "Завершена" else "🟡" if status == "В процессе" else "🔴"
            item_text = f"{status_icon} {title} - {status} (до: {date.toString('dd.MM.yyyy')})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.task_list.addItem(item)
    
    def add_task(self):
        """Добавление новой задачи"""
        title, ok = QInputDialog.getText(self, "Добавить задачу", "Название задачи:")
        if ok and title:
            desc, ok = QInputDialog.getText(self, "Добавить задачу", "Описание задачи:")
            if ok:
                statuses = ["Не начата", "В процессе", "Завершена"]
                status, ok = QInputDialog.getItem(self, "Добавить задачу", "Статус:", statuses, 0, False)
                if ok:
                    self.tasks.append((title, desc, status, QDate.currentDate()))
                    self.refresh_task_list()
                    self.add_to_history(f"Добавлена задача: {title}")
                    QMessageBox.information(self, "Успех", "Задача добавлена!")
    
    def delete_task(self):
        """Удаление задачи"""
        current = self.task_list.currentRow()
        if current >= 0:
            task_title = self.tasks[current][0]
            reply = QMessageBox.question(self, "Удалить", f"Удалить задачу '{task_title}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.add_to_history(f"Удалена задача: {task_title}")
                del self.tasks[current]
                self.refresh_task_list()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для удаления")
    
    def edit_task(self):
        """Редактирование задачи"""
        current = self.task_list.currentRow()
        if current >= 0:
            title, desc, status, date = self.tasks[current]
            new_title, ok = QInputDialog.getText(self, "Редактировать", "Название:", text=title)
            if ok:
                new_desc, ok = QInputDialog.getText(self, "Редактировать", "Описание:", text=desc)
                if ok:
                    statuses = ["Не начата", "В процессе", "Завершена"]
                    new_status, ok = QInputDialog.getItem(self, "Редактировать", "Статус:", statuses, 
                                                          statuses.index(status) if status in statuses else 0, False)
                    if ok:
                        self.add_to_history(f"Изменена задача: {title} -> {new_title}")
                        self.tasks[current] = (new_title, new_desc, new_status, date)
                        self.refresh_task_list()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите задачу для редактирования")
    
    def add_to_history(self, action):
        """Добавление в историю"""
        from datetime import datetime
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.task_history.append(f"[{time_str}] {action}")
        self.refresh_history()
    
    def refresh_history(self):
        """Обновление истории"""
        self.history_list.clear()
        for action in reversed(self.task_history[-50:]):  # последние 50
            self.history_list.addItem(action)
    
    def clear_history(self):
        """Очистка истории"""
        self.task_history.clear()
        self.refresh_history()
        QMessageBox.information(self, "История", "История очищена")
    
    def update_stats(self):
        """Обновление статистики"""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t[2] == "Завершена")
        in_progress = sum(1 for t in self.tasks if t[2] == "В процессе")
        not_started = sum(1 for t in self.tasks if t[2] == "Не начата")
        
        stats_text = f"""
        📊 Статистика задач:
        
        • Всего задач: {total}
        • ✅ Завершено: {completed} ({completed/total*100 if total > 0 else 0:.1f}%)
        • 🔄 В процессе: {in_progress}
        • ⏳ Не начато: {not_started}
        
        • 📜 История действий: {len(self.task_history)} записей
        """
        self.stats_label.setText(stats_text)
    
    def choose_bg_color(self):
        """Выбор цвета фона"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = color
    
    def choose_text_color(self):
        """Выбор цвета текста"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color
    
    def apply_appearance(self):
        """Применение настроек внешнего вида"""
        font = QFont(self.font_combo.currentFont().family(), self.font_size.value())
        QApplication.setFont(font)
        
        if hasattr(self, 'bg_color'):
            self.setStyleSheet(f"""
                QMainWindow {{ background-color: {self.bg_color.name()}; }}
                QListWidget::item:selected {{ background-color: #3498db; }}
            """)
        
        QMessageBox.information(self, "Настройки", "Настройки внешнего вида применены")
    
    def apply_style(self):
        """Применение общего стиля"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)


def main():
    app = QApplication(sys.argv)
    window = TaskManagerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
