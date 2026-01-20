import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeView,
    QFileSystemModel,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QAbstractItemView,
)
from PySide6.QtCore import QDir, QItemSelection, QItemSelectionModel, Qt, QModelIndex
from PIL import Image, ExifTags

class CustomFileSystemModel(QFileSystemModel):
    def __init__(self):
        super().__init__()

    def columnCount(self, parent=QModelIndex()):
        return 5  # Zusätzliche Spalte für EXIF

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return "Name"
            elif section == 1:
                return "Größe"
            elif section == 2:
                return "Typ"
            elif section == 3:
                return "Geändert"
            elif section == 4:
                return "Erstelldatum (Metadata)"
        return super().headerData(section, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and index.column() == 4:
            path = self.filePath(index)
            if self.isDir(index):
                return ""
            if path.lower().endswith('.jpg'):
                try:
                    with Image.open(path) as img:
                        exif_data = img.getexif()
                        print(f"EXIF data for {path}: {exif_data}")
                        if exif_data:
                            dt = exif_data.get(306)  # DateTime (da DateTimeOriginal nicht vorhanden)
                            print(f"DateTime for {path}: {dt}")
                            if dt:
                                return dt
                except Exception as e:
                    print(f"Error for {path}: {e}")
            return ""
        return super().data(index, role)


class FileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bildumbenennung für Papa")
        self.resize(900, 600)

        # Dateisystem-Modell
        self.model = CustomFileSystemModel()
        self.model.setRootPath(QDir.rootPath())

        # TreeView (Explorer-Ansicht)
        self.view = QTreeView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(QDir.homePath()))

        # Mehrfachauswahl aktivieren
        self.view.setSelectionMode(QAbstractItemView.MultiSelection)

        # Auswahl-Änderungen überwachen
        self.view.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Optional: Spalten anpassen
        self.view.setColumnWidth(0, 300)  # Name
        self.view.setColumnWidth(4, 150)  # EXIF Datum
        self.view.setSortingEnabled(True)

        # Verknüpfung des Klickereignisses
        self.view.clicked.connect(self.on_item_clicked)

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.view)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.current_folder = None
        self.selected_files = []
        self.files_selected = False

    def on_item_clicked(self, index):
        if self.model.isDir(index):
            self.current_folder = index
            self.select_all_files_in_current_folder()
        else:
            print(f"📄 Datei gewählt: {self.model.filePath(index)}")

    def select_all_files_in_current_folder(self):
        if self.current_folder:
            folder_path = self.model.filePath(self.current_folder)
            self.selected_files = []
            for item in os.listdir(folder_path):
                full_path = os.path.join(folder_path, item)
                if os.path.isfile(full_path):
                    index = self.model.index(full_path)
                    if index.isValid():
                        self.selected_files.append(index)
            
            if self.files_selected:
                # Abwählen
                selection = QItemSelection()
                for idx in self.selected_files:
                    selection.select(idx, idx)
                self.view.selectionModel().select(selection, QItemSelectionModel.Deselect)
                self.files_selected = False
                print("Dateien abgewählt.")
            else:
                # Auswählen
                selection = QItemSelection()
                for idx in self.selected_files:
                    selection.select(idx, idx)
                self.view.selectionModel().select(selection, QItemSelectionModel.ClearAndSelect)
                self.files_selected = True
                print("Ausgewählte Dateien:")
                for idx in self.selected_files:
                    print(f"📄 {self.model.filePath(idx)}")

    def on_selection_changed(self, selected, deselected):
        current_selection = self.view.selectionModel().selection()
        new_selection = QItemSelection()
        for range_item in current_selection:
            for i in range(range_item.top(), range_item.bottom() + 1):
                for j in range(range_item.left(), range_item.right() + 1):
                    idx = self.model.index(i, j, range_item.parent())
                    if idx.isValid() and not self.model.isDir(idx):
                        new_selection.select(idx, idx)
        
        if new_selection != current_selection:
            self.view.selectionModel().select(new_selection, QItemSelectionModel.ClearAndSelect)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileExplorer()
    window.show()
    sys.exit(app.exec())
