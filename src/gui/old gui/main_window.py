import sys
import os
# Ensure the project's src folder is on sys.path so "from core..." works
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from core.submarine import Submarine
from core.collision_checker import CollisionChecker
from gui.map_view import MapView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ubåtscentralen")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Välkommen till Ubåtscentralen!")
        layout.addWidget(label)

        map_button = QPushButton("Karta")
        log_button = QPushButton("Loggar")
        layout.addWidget(map_button)
        layout.addWidget(log_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect buttons
        map_button.clicked.connect(self.open_map_view)
        # log_button.clicked.connect(self.open_log_view)  # implementera vid behov

    def open_map_view(self):
        """Load submarines from Sensordata folder, check collisions and open map."""
        # Anta projektrot två nivåer upp från denna fil
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        data_folder = os.path.join(project_root, "Sensordata")
        submarines = []

        if os.path.isdir(data_folder):
            for fname in os.listdir(data_folder):
                if not fname.lower().endswith(".txt"):
                    continue
                file_path = os.path.join(data_folder, fname)
                sub_id = os.path.splitext(fname)[0]  # filnamn utan .txt
                sub = Submarine(sub_id)
                for direction, distance in sub.load_movements_data_from_file(file_path):
                    try:
                        sub.move_from_position_and_distance(direction, distance)
                    except ValueError:
                        # hoppa över ogiltiga kommandon
                        continue
                submarines.append(sub)

        # Kolla kollisioner
        checker = CollisionChecker()
        collisions = checker.check_for_collisions(submarines)

        # Visa kartan
        self.map_window = MapView(submarines, collisions)
        self.map_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())