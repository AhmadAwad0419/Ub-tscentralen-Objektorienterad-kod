import os
import math
import concurrent.futures
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QListWidget, QMessageBox, QDialog, QLabel, QMainWindow
)
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QTimer

from src.config.paths import MOVEMENT_REPORTS_DIR
from src.data.file_reader import FileReader
from src.core.movement_manager import MovementManager
from src.core.torpedo_system import TorpedoSystem
from src.core.nuke_activation import NukeActivation
from src.data.secrets_loader import SecretsLoader
from src.core.sensor_manager import SensorManager


# === Start Menu ===
class StartMenu(QWidget):
    def __init__(self, start_simulation):
        super().__init__()
        self.start_simulation = start_simulation
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ubåtscentralen - Start Menu")
        layout = QVBoxLayout()

        run_btn = QPushButton("Run Simulation")
        run_btn.clicked.connect(self.run_simulation)
        layout.addWidget(run_btn)

        stats_btn = QPushButton("Show Stats (files etc)")
        stats_btn.clicked.connect(self.show_stats)
        layout.addWidget(stats_btn)

        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)

        self.setLayout(layout)

    def run_simulation(self):
        self.start_simulation()
        self.close()  # stäng startmenyn när simulationen börjar

    def show_stats(self):
        subs = [
            f.replace(".txt", "")
            for f in os.listdir(MOVEMENT_REPORTS_DIR)
            if f.endswith(".txt")
        ]
        stats = f"Antal ubåtar: {len(subs)}\n" + "\n".join(subs[:15])
        QMessageBox.information(self, "Stats", stats)


# === Main Menu ===
class MainMenu(QMainWindow):
    def __init__(self, manager, torpedo_system, nuke_activation, sensor_manager):
        super().__init__()
        self.manager = manager
        self.torpedo_system = torpedo_system
        self.nuke_activation = nuke_activation
        self.sensor_manager = sensor_manager

        # Widgets för status
        self.status_label = QLabel("Simulation not started")
        self.round_label = QLabel("")
        self.subs_label = QLabel("")

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ubåtscentralen - Main Menu")
        layout = QVBoxLayout()

        layout.addWidget(self.status_label)
        layout.addWidget(self.round_label)
        layout.addWidget(self.subs_label)

        search_btn = QPushButton("Search Submarine")
        search_btn.clicked.connect(self.search_submarine)
        layout.addWidget(search_btn)

        show_stats_btn = QPushButton("Show All Statistics")
        show_stats_btn.clicked.connect(self.show_all_stats)
        layout.addWidget(show_stats_btn)

        fire_btn = QPushButton("Fire Torpedo")
        fire_btn.clicked.connect(self.fire_torpedo)
        layout.addWidget(fire_btn)

        nuke_btn = QPushButton("Activate Nuke")
        nuke_btn.clicked.connect(self.activate_nuke)
        layout.addWidget(nuke_btn)

        sensor_btn = QPushButton("Show Sensor Errors")
        sensor_btn.clicked.connect(self.show_sensor_errors)
        layout.addWidget(sensor_btn)

        distance_btn = QPushButton("Distance Analysis")
        distance_btn.clicked.connect(self.distance_analysis)
        layout.addWidget(distance_btn)

        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def update_status(self, round_number: int, active_subs: int):
        """Kallas av SimulationWorker varje runda"""
        self.status_label.setText("Simulation running...")
        self.round_label.setText(f"Round {round_number}")
        self.subs_label.setText(f"Active submarines: {active_subs}")

    def simulation_finished(self):
        self.status_label.setText("Simulation finished")

    # === Hjälpmetod ===
    def populate_sub_list(self, list_widget, active_only=False):
        """Fyller en QListWidget med alla ubåtar eller bara aktiva."""
        list_widget.clear()
        for sub in self.manager.submarines.values():
            if not active_only or sub.is_active:
                list_widget.addItem(f"{sub.id} → pos {sub.position}, active={sub.is_active}")

   # === Funktioner ===
    def search_submarine(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Search Submarine")
        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        self.populate_sub_list(list_widget)  # alla subs
        layout.addWidget(list_widget)

        active_btn = QPushButton("Show Active Only")
        active_btn.clicked.connect(lambda: self.populate_sub_list(list_widget, active_only=True))
        layout.addWidget(active_btn)

        select_btn = QPushButton("Close")
        select_btn.clicked.connect(dialog.accept)
        layout.addWidget(select_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def show_all_stats(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("All Submarines")
        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        self.populate_sub_list(list_widget)  # alla subs
        layout.addWidget(list_widget)

        active_btn = QPushButton("Show Active Only")
        active_btn.clicked.connect(lambda: self.populate_sub_list(list_widget, active_only=True))
        layout.addWidget(active_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def fire_torpedo(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Choose Submarine to Fire Torpedo From")
        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        for sub in self.manager.submarines.values():
            if sub.is_active:
                list_widget.addItem(f"{sub.id} → pos {sub.position}")
        layout.addWidget(list_widget)

        fire_btn = QPushButton("Fire")
        fire_btn.clicked.connect(dialog.accept)
        layout.addWidget(fire_btn)

        dialog.setLayout(layout)
        if dialog.exec_():
            selected = list_widget.currentItem()
            if not selected:
                QMessageBox.warning(self, "Error", "No submarine selected.")
                return
            sub_id = selected.text().split(" ")[0]
            sub = self.manager.submarines.get(sub_id)
            report = self.torpedo_system.get_friendly_fire_report(
                list(self.manager.submarines.values()), sub
            )
            msg = f"Torpedo check for {sub_id}:\n"
            for direction, info in report.items():
                msg += f"{direction}: {'SAFE' if info['safe'] else 'RISK'}\n"
            QMessageBox.information(self, "Torpedo Report", msg)

    def activate_nuke(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Choose Submarine to Activate Nuke")
        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        for sub in self.manager.submarines.values():
            if sub.is_active:
                list_widget.addItem(f"{sub.id} → pos {sub.position}")
        layout.addWidget(list_widget)

        activate_btn = QPushButton("Activate")
        activate_btn.clicked.connect(dialog.accept)
        layout.addWidget(activate_btn)

        dialog.setLayout(layout)
        if dialog.exec_():
            selected = list_widget.currentItem()
            if not selected:
                QMessageBox.warning(self, "Error", "No submarine selected.")
                return
            sub_id = selected.text().split(" ")[0]
            sub = self.manager.submarines.get(sub_id)
            allowed = self.nuke_activation.allowed_to_activate(
                list(self.manager.submarines.values()), sub
            )
            if allowed:
                QMessageBox.information(self, "Nuke Activation", f"Nuke activated for {sub_id}")
            else:
                QMessageBox.warning(self, "Nuke Activation", f"Activation blocked (friendly fire risk) for {sub_id}")

    def show_sensor_errors(self):
        results = []
        for sub in self.manager.submarines.values():
            if sub.is_active:
                result = self.sensor_manager.process_sensor_by_serial(sub.id)
                if result["status"] == "ok":
                    results.append(
                        f"{sub.id}: max errors={result['max_errors']} (lines={result['lines']})"
                    )
                else:
                    results.append(f"{sub.id}: MISSING ({result['msg']})")

        if results:
            QMessageBox.information(self, "Sensor Errors", "\n".join(results))
        else:
            QMessageBox.information(self, "Sensor Errors", "No active submarines.")

    def distance_analysis(self):
        subs = [s for s in self.manager.submarines.values() if s.is_active]
        if len(subs) < 2:
            QMessageBox.warning(self, "Distance Analysis", "Not enough active submarines.")
            return

        distances = []
        for i, s1 in enumerate(subs):
            for s2 in subs[i + 1:]:
                dist = math.dist(s1.position, s2.position)
                distances.append((dist, s1.id, s2.id))

        nearest = min(distances, key=lambda x: x[0])
        farthest = max(distances, key=lambda x: x[0])

        msg = (
            f"Nearest: {nearest[1]} ↔ {nearest[2]} = {nearest[0]:.2f}\n"
            f"Farthest: {farthest[1]} ↔ {farthest[2]} = {farthest[0]:.2f}"
        )
        QMessageBox.information(self, "Distance Analysis", msg)

class SimulationWorker(QObject):
    finished = pyqtSignal()
    round_update = pyqtSignal(int, int)  # round_number, active_subs

    def __init__(self, manager, sensor_manager):
        super().__init__()
        self.manager = manager
        self.sensor_manager = sensor_manager

    def run(self):
        round_counter = 1
        while any(sub.is_active for sub in self.manager.submarines.values()):
            # kör en runda med nya step_round
            self.manager.step_round(round_counter, self.sensor_manager)

            # skicka status till GUI
            self.round_update.emit(round_counter, len(self.manager.active_subs))
            round_counter += 1

        self.finished.emit()

def launch_gui():
    app = QApplication([])

    reader = FileReader()
    manager = MovementManager(reader, tick_delay=0.0)
    manager.load_submarines_from_generator(reader.load_all_movement_files())

    torpedos = TorpedoSystem()
    secrets = SecretsLoader()
    nuke = NukeActivation(secrets_loader=secrets, torpedo_system=torpedos)
    sensor_manager = SensorManager(reader, manager)

    def start_simulation():
        app.thread = QThread()
        app.worker = SimulationWorker(manager, sensor_manager)
        app.worker.moveToThread(app.thread)

        app.main_menu = MainMenu(manager, torpedos, nuke, sensor_manager)
        app.main_menu.show()

        app.thread.started.connect(app.worker.run)
        app.worker.round_update.connect(app.main_menu.update_status)
        app.worker.finished.connect(app.thread.quit)
        app.worker.finished.connect(app.worker.deleteLater)
        app.thread.finished.connect(app.thread.deleteLater)
        app.worker.finished.connect(app.main_menu.simulation_finished)

        app.thread.start()

    def cleanup():
        # körs när appen stänger → säkerställer att tråden avslutas korrekt
        if hasattr(app, "thread") and app.thread.isRunning():
            app.thread.quit()
            app.thread.wait()

    app.aboutToQuit.connect(cleanup)

    sm = StartMenu(start_simulation)
    sm.show()

    app.exec_()
