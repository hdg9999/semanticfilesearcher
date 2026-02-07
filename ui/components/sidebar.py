from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QFileSystemModel, QHeaderView
from PySide6.QtCore import Qt, Signal, QDir, QModelIndex

class FileSidebar(QWidget):
    folder_selected = Signal(str)  # Emits the absolute path of the selected folder

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("fileSidebar")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # File System Model
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Drives)

        # Tree View
        self.tree_view = QTreeView()
        self.tree_view.setObjectName("dirTree")
        self.tree_view.setModel(self.model)
        
        # Hide unnecessary columns (Size, Type, Date)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.AscendingOrder)
        
        # Signals
        self.tree_view.clicked.connect(self._on_clicked)
        self.tree_view.doubleClicked.connect(self._on_clicked) # Both actions trigger selection

        layout.addWidget(self.tree_view)

        # Style (Basic structure, detailed styling via main window or qss)
        self.tree_view.setStyleSheet("""
            QTreeView {
                border: none;
                background-color: transparent;
            }
            QTreeView::item {
                padding: 4px;
            }
        """)

    def _on_clicked(self, index: QModelIndex):
        path = self.model.filePath(index)
        self.folder_selected.emit(path)

    def select_path(self, path):
        """Programmatically select a path in the tree"""
        index = self.model.index(path)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            self.tree_view.scrollTo(index)
            self.tree_view.expand(index)
