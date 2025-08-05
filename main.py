
import shutil
import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QFileSystemModel, QTreeView, QFileDialog, QDialog, QComboBox,
    QCheckBox, QDialogButtonBox, QMenu, QAction, QInputDialog, QStackedLayout, QMessageBox, QTextEdit, QTabWidget, QSplitter
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon


class ProjectEditor(QWidget):
    def __init__(self, path, theme="dark"):
        super().__init__()
        self.project_path = path
        self.theme = theme
        self.open_tabs = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        toolbar = QHBoxLayout()
        for icon, label in [("▶️", "Run"), ("🔧", "Build"), ("💾", "Save"), ("🐞", "Debug")]:
            btn = QPushButton(f"{icon} {label}")
            btn.setFixedHeight(30)
            toolbar.addWidget(btn)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        splitter = QSplitter(Qt.Horizontal)
        self.model = QFileSystemModel()
        self.model.setRootPath(self.project_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.project_path))
        self.tree.doubleClicked.connect(self.open_file_from_tree)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

        if self.theme == "dark":
            tree_style = "background-color: #2b2b2b; color: white;"
            tab_style = '''
                QTabBar::tab {
                    height: 24px;
                    padding: 6px;
                    font-weight: bold;
                    font-family: Consolas;
                    background: #3c3f41;
                    color: white;
                }
                QTabBar::tab:selected {
                    background: #555;
                    color: #fff;
                    border-bottom: 2px solid #ffaa00;
                }
            '''
            self.editor_style = "background-color: #1e1e1e; color: #ffffff; padding: 10px;"
        else:
            tree_style = "background-color: #f0f0f0; color: black;"
            tab_style = '''
                QTabBar::tab {
                    height: 24px;
                    padding: 6px;
                    font-weight: bold;
                    font-family: Consolas;
                    background: #e0e0e0;
                    color: black;
                }
                QTabBar::tab:selected {
                    background: #ccc;
                    color: #000;
                    border-bottom: 2px solid #007acc;
                }
            '''
            self.editor_style = "background-color: #ffffff; color: #000000; padding: 10px;"

        self.tree.setStyleSheet(tree_style)
        splitter.addWidget(self.tree)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(tab_style)
        splitter.addWidget(self.tabs)
        splitter.setSizes([250, 800])
        layout.addWidget(splitter)

        bottom = QLabel("No problems found.")
        bottom.setStyleSheet("padding: 6px; background-color: #444; color: white;")
        layout.addWidget(bottom)

        toolbar.itemAt(0).widget().clicked.connect(self.run_project)
        toolbar.itemAt(1).widget().clicked.connect(self.build_project)
        toolbar.itemAt(2).widget().clicked.connect(self.save_current_file)
        toolbar.itemAt(3).widget().clicked.connect(self.debug_project)

    def open_file_from_tree(self, index):
        if not self.model.isDir(index):
            filepath = self.model.filePath(index)
            filename = os.path.basename(filepath)
            if filename in self.open_tabs:
                self.tabs.setCurrentWidget(self.open_tabs[filename])
            else:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    content = f"Error opening file: {e}"
                editor = QTextEdit()
                editor.setText(content)
                editor.setFontFamily("Consolas")
                editor.setStyleSheet(self.editor_style)
                self.tabs.addTab(editor, filename)
                self.tabs.setCurrentWidget(editor)
                self.open_tabs[filename] = editor

    def save_current_file(self):
        index = self.tabs.currentIndex()
        if index == -1:
            return
        editor = self.tabs.currentWidget()
        filename = self.tabs.tabText(index)
        filepath = os.path.join(self.project_path, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(editor.toPlainText())
        except Exception:
            QMessageBox.critical(self, "Error", "Could not save file.")

    def run_project(self):
        main_file = os.path.join(self.project_path, "main.py")
        if os.path.exists(main_file):
            subprocess.Popen(["python", main_file], cwd=self.project_path)
        else:
            QMessageBox.warning(self, "Run", "main.py not found.")

    def build_project(self):
        QMessageBox.information(self, "Build", "Build successful (placeholder).")

    def debug_project(self):
        main_file = os.path.join(self.project_path, "main.py")
        if os.path.exists(main_file):
            subprocess.Popen(["python", "-m", "pdb", main_file], cwd=self.project_path)
        else:
            QMessageBox.warning(self, "Debug", "main.py not found.")

    def show_context_menu(self, position):
        index = self.tree.indexAt(position)
        if not index.isValid():
            return
        menu = QMenu()
        new_action = QAction("New File", self)
        delete_action = QAction("Delete", self)
        rename_action = QAction("Rename", self)
        new_action.triggered.connect(lambda: self.new_file(index))
        delete_action.triggered.connect(lambda: self.delete_item(index))
        rename_action.triggered.connect(lambda: self.rename_item(index))
        menu.addAction(new_action)
        menu.addAction(delete_action)
        menu.addAction(rename_action)
        menu.exec_(self.tree.viewport().mapToGlobal(position))

    def new_file(self, index):
        dir_path = self.model.filePath(index)
        if not os.path.isdir(dir_path):
            dir_path = os.path.dirname(dir_path)
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            full_path = os.path.join(dir_path, name)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("")
            self.tree.setRootIndex(self.model.index(self.project_path))

    def delete_item(self, index):
        path = self.model.filePath(index)
        confirm = QMessageBox.question(self, "Delete", f"Delete {os.path.basename(path)}?")
        if confirm == QMessageBox.Yes:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            self.tree.setRootIndex(self.model.index(self.project_path))

    def rename_item(self, index):
        path = self.model.filePath(index)
        name, ok = QInputDialog.getText(self, "Rename", "Enter new name:", text=os.path.basename(path))
        if ok and name:
            new_path = os.path.join(os.path.dirname(path), name)
            os.rename(path, new_path)
            self.tree.setRootIndex(self.model.index(self.project_path))


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to Android Studio")
        self.setMinimumSize(1080, 650)
        self.theme = "dark"
        self.ensure_required_folders()
        self.init_ui()

    def ensure_required_folders(self):
        for folder in ["projects", "utils"]:
            os.makedirs(folder, exist_ok=True)

    def init_ui(self):
        self.main_layout = QHBoxLayout(self)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20, 20, 10, 20)
        sidebar_layout.setSpacing(15)

        logo = QLabel("🪶➰")
        logo.setFont(QFont("Arial", 28))
        studio_label = QLabel("Simplic Editor")
        studio_label.setFont(QFont("Arial", 14, QFont.Bold))
        version_label = QLabel("Unknown Studios SE.A1.2025")
        version_label.setFont(QFont("Arial", 9))
        version_label.setStyleSheet("color: #aaa;")

        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(studio_label)
        sidebar_layout.addWidget(version_label)
        sidebar_layout.addSpacing(20)

        self.nav_list = QListWidget()
        self.nav_list.addItems(["Projects", "Customize", "Libraries", "Know More"])
        self.nav_list.setCurrentRow(0)
        self.nav_list.setFixedWidth(180)
        self.nav_list.currentRowChanged.connect(self.switch_tab)
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()
        self.main_layout.addLayout(sidebar_layout)

        self.stack_layout = QStackedLayout()
        self.current_widget = QWidget()

        self.projects_tab = QWidget()
        proj_layout = QVBoxLayout()
        top_row = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search projects")
        top_row.addWidget(self.search)

        self.new_btn = QPushButton("New Project")
        self.new_btn.clicked.connect(self.create_project)
        top_row.addWidget(self.new_btn)

        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.open_folder)
        top_row.addWidget(self.open_btn)

        self.clone_btn = QPushButton("Clone Repository")
        self.clone_btn.clicked.connect(self.clone_repository)
        top_row.addWidget(self.clone_btn)

        proj_layout.addLayout(top_row)
        self.project_label = QLabel("Projects in /projects:")
        proj_layout.addWidget(self.project_label)

        self.project_view = QTreeView()
        self.project_model = QFileSystemModel()
        self.project_model.setRootPath("projects")
        self.project_view.setModel(self.project_model)
        self.project_view.setRootIndex(self.project_model.index("projects"))
        self.project_view.setColumnHidden(1, True)
        self.project_view.setColumnHidden(2, True)
        self.project_view.setColumnHidden(3, True)
        proj_layout.addWidget(self.project_view)

        self.projects_tab.setLayout(proj_layout)
        self.stack_layout.addWidget(self.projects_tab)

        customize_tab = QWidget()
        customize_layout = QVBoxLayout()
        self.theme_btn = QPushButton("Switch to Light Theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        customize_layout.addWidget(self.theme_btn)
        customize_layout.addStretch()
        customize_tab.setLayout(customize_layout)
        self.stack_layout.addWidget(customize_tab)

        libraries_tab = QWidget()
        lib_layout = QVBoxLayout()
        lib_label = QLabel("Installed Python Libraries:")
        lib_layout.addWidget(lib_label)
        for lib in ["numpy", "pandas", "matplotlib", "PyQt5", "requests", "flask", "django"]:
            lib_layout.addWidget(QLabel(f"• {lib}"))
        libraries_tab.setLayout(lib_layout)
        self.stack_layout.addWidget(libraries_tab)

        empty_tab = QWidget()
        empty_tab.setLayout(QVBoxLayout())
        self.stack_layout.addWidget(empty_tab)

        self.current_widget.setLayout(self.stack_layout)
        self.main_layout.addWidget(self.current_widget)
        self.apply_dark_theme()

    def switch_tab(self, index):
        self.stack_layout.setCurrentIndex(index)

    def create_project(self):
        name, ok = QFileDialog.getSaveFileName(self, "New Project Name", "projects/", "")
        if ok and name:
            folder_name = os.path.basename(name)
            full_path = os.path.join("projects", folder_name)
            os.makedirs(full_path, exist_ok=True)
            open(os.path.join(full_path, "outputs"), "w").close()
            self.project_view.setRootIndex(self.project_model.index("projects"))

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder", "projects/")
        if folder:
            self.load_project_view(folder)

    def load_project_view(self, path):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        editor = ProjectEditor(path, self.theme)
        self.main_layout.addWidget(editor)
        self.setWindowTitle(f"{os.path.basename(path)} - Android Studio")

    def clone_repository(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Clone Repository")
        dlg.setMinimumSize(500, 250)
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Version control:"))
        version_select = QComboBox()
        version_select.addItems(["Git"])
        layout.addWidget(version_select)

        layout.addWidget(QLabel("URL:"))
        url_field = QLineEdit()
        layout.addWidget(url_field)

        layout.addWidget(QLabel("Directory:"))
        dir_field = QLineEdit("projects/")
        layout.addWidget(dir_field)

        shallow = QCheckBox("Shallow clone with a history truncated to 1 commit")
        layout.addWidget(shallow)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)
        dlg.setLayout(layout)
        dlg.exec_()

    def toggle_theme(self):
        if self.theme == "dark":
            self.apply_light_theme()
            self.theme = "light"
            self.theme_btn.setText("Switch to Dark Theme")
        else:
            self.apply_dark_theme()
            self.theme = "dark"
            self.theme_btn.setText("Switch to Light Theme")

    def apply_dark_theme(self):
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        self.project_view.setStyleSheet("background-color: #3c3f41; color: white;")

    def apply_light_theme(self):
        self.setStyleSheet("background-color: #ffffff; color: black;")
        self.project_view.setStyleSheet("background-color: #f0f0f0; color: black;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
