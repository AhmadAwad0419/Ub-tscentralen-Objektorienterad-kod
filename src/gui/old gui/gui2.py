import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QTextEdit, QLabel, QSplitter, QProgressBar,
                             QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor

# Add project root to path (same as in your existing code)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import your existing modules
from src.data.file_reader import FileReader
from src.config.paths import MOVEMENT_REPORTS_DIR
from src.core.submarine import Submarine
from src.core.movement_manager import MovementManager
from src.core.collision_checker import CollisionChecker
from src.core.torpedo_system import TorpedoSystem


class SimulationThread(QThread):
    """Thread for running the simulation without freezing the GUI"""
    update_signal = pyqtSignal(dict)  # Signal to send updates to the GUI
    finished_signal = pyqtSignal()    # Signal when simulation is finished
    
    def __init__(self, movement_manager, continuous=False, parent=None):
        super().__init__(parent)
        self.movement_manager = movement_manager
        self.continuous = continuous
        self.running = True
        
    def run(self):
        """Run the simulation"""
        collision_checker = CollisionChecker()
        
        while self.running and any(sub.is_active for sub in self.movement_manager.submarines.values()):
            finished_subs = []
            
            # Process movements for all active submarines
            for sub_id, generator in list(self.movement_manager.active_generators.items()):
                sub = self.movement_manager.submarines.get(sub_id)
                if not sub or not sub.is_active:
                    continue
                    
                try:
                    movement = next(generator)
                    if movement is not None:
                        command, value = movement
                        sub = self.movement_manager.submarines.get(sub_id)
                        if sub is not None:
                            self.movement_manager.move_from_position_and_distance(sub, command, value)
                            
                            # Emit update with submarine data
                            update_data = {
                                'type': 'movement',
                                'sub_id': sub_id,
                                'command': command,
                                'value': value,
                                'position': sub.get_position(),
                                'active': sub.is_active
                            }
                            self.update_signal.emit(update_data)
                except StopIteration:
                    finished_subs.append(sub_id)
            
            # Remove finished submarines
            for sub_id in finished_subs:
                if sub_id in self.movement_manager.active_generators:        
                    del self.movement_manager.active_generators[sub_id]
            
            # Check collisions only on active submarines
            active_subs = [s for s in self.movement_manager.submarines.values() if s.is_active]
            new_collisions = collision_checker.check_for_collisions(active_subs)
            
            for sub1, sub2, position in new_collisions:
                sub1.is_active = False
                sub2.is_active = False

                if sub1.id in self.movement_manager.active_generators:
                    del self.movement_manager.active_generators[sub1.id]
                if sub2.id in self.movement_manager.active_generators:
                    del self.movement_manager.active_generators[sub2.id]
                
                # Emit collision update
                collision_data = {
                    'type': 'collision',
                    'sub1_id': sub1.id,
                    'sub2_id': sub2.id,
                    'position': position
                }
                self.update_signal.emit(collision_data)
            
            if not self.continuous:
                break  # Only run one step in step-by-step mode
                
            if not self.movement_manager.active_generators:
                break
                
            self.msleep(500)  # Similar to your sleep(0.5)
        
        # Run friendly-fire checks when simulation is done
        torpedo_system = TorpedoSystem()
        for sub in self.movement_manager.submarines.values():
            report = torpedo_system.get_friendly_fire_report(list(self.movement_manager.submarines.values()), sub)
            torpedo_system.log_torpedo_launch(sub, report)
            
            # Emit friendly fire report
            ff_data = {
                'type': 'friendly_fire',
                'sub_id': sub.id,
                'report': report
            }
            self.update_signal.emit(ff_data)
        
        self.finished_signal.emit()
    
    def stop(self):
        """Stop the simulation"""
        self.running = False


class SubmarineGUI(QMainWindow):
    """Main GUI window for the submarine simulation"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Submarine Simulation")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize simulation components
        self.movement_manager = MovementManager()
        self.simulation_thread = None
        
        self.init_ui()
        self.load_submarines()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for submarine list and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(300)
        
        # Submarine list
        sub_group = QGroupBox("Submarines")
        sub_layout = QVBoxLayout(sub_group)
        self.submarine_list = QListWidget()
        sub_layout.addWidget(self.submarine_list)
        left_layout.addWidget(sub_group)
        
        # Controls
        control_group = QGroupBox("Simulation Controls")
        control_layout = QVBoxLayout(control_group)
        
        self.load_btn = QPushButton("Load Submarines")
        self.load_btn.clicked.connect(self.load_submarines)
        control_layout.addWidget(self.load_btn)
        
        self.step_btn = QPushButton("Step Simulation")
        self.step_btn.clicked.connect(self.step_simulation)
        control_layout.addWidget(self.step_btn)
        
        self.start_btn = QPushButton("Start Continuous Simulation")
        self.start_btn.clicked.connect(self.start_continuous_simulation)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop Simulation")
        self.stop_btn.clicked.connect(self.stop_simulation)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.reset_btn = QPushButton("Reset Simulation")
        self.reset_btn.clicked.connect(self.reset_simulation)
        control_layout.addWidget(self.reset_btn)
        
        left_layout.addWidget(control_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)
        
        # Right panel for details and logs
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        
        # Position tab
        position_tab = QWidget()
        position_layout = QVBoxLayout(position_tab)
        self.position_table = QTableWidget()
        self.position_table.setColumnCount(3)
        self.position_table.setHorizontalHeaderLabels(["Submarine", "Horizontal", "Vertical"])
        self.position_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        position_layout.addWidget(self.position_table)
        self.tabs.addTab(position_tab, "Positions")
        
        # Log tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        self.tabs.addTab(log_tab, "Log")
        
        # Collision tab
        collision_tab = QWidget()
        collision_layout = QVBoxLayout(collision_tab)
        self.collision_table = QTableWidget()
        self.collision_table.setColumnCount(4)
        self.collision_table.setHorizontalHeaderLabels(["Submarine 1", "Submarine 2", "X", "Y"])
        self.collision_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        collision_layout.addWidget(self.collision_table)
        self.tabs.addTab(collision_tab, "Collisions")
        
        right_layout.addWidget(self.tabs)
        
        # Add panels to main layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def load_submarines(self):
        """Load all submarines from movement reports"""
        self.log_text.append("Loading submarines...")
        
        # Clear previous data
        self.submarine_list.clear()
        self.movement_manager = MovementManager()
        
        # Get drone IDs from movement reports directory
        drone_ids = [filename.replace(".txt", "") for filename in os.listdir(MOVEMENT_REPORTS_DIR) 
                    if filename.endswith(".txt")]
        
        submarines = []
        for drone_id in drone_ids:
            submarine = Submarine(drone_id)
            submarines.append(submarine)
            self.submarine_list.addItem(f"Submarine {drone_id}")
        
        self.movement_manager.load_submarines(submarines)
        
        # Update position table
        self.update_position_table()
        
        self.log_text.append(f"Loaded {len(drone_ids)} submarines")
        self.statusBar().showMessage(f"Loaded {len(drone_ids)} submarines")
        
    def update_position_table(self):
        """Update the position table with current submarine positions"""
        self.position_table.setRowCount(len(self.movement_manager.submarines))
        
        for row, (sub_id, sub) in enumerate(self.movement_manager.submarines.items()):
            self.position_table.setItem(row, 0, QTableWidgetItem(sub_id))
            self.position_table.setItem(row, 1, QTableWidgetItem(str(sub.horizontal_position)))
            self.position_table.setItem(row, 2, QTableWidgetItem(str(sub.vertical_position)))
            
            # Color inactive submarines red
            if not sub.is_active:
                for col in range(3):
                    self.position_table.item(row, col).setBackground(QColor(255, 200, 200))
    
    def step_simulation(self):
        """Run simulation one step at a time"""
        self.log_text.append("Running simulation step...")
        self.simulation_thread = SimulationThread(self.movement_manager, continuous=False)
        self.simulation_thread.update_signal.connect(self.handle_simulation_update)
        self.simulation_thread.finished_signal.connect(self.simulation_finished)
        self.simulation_thread.start()
        
        self.step_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def start_continuous_simulation(self):
        """Start continuous simulation"""
        self.log_text.append("Starting continuous simulation...")
        self.simulation_thread = SimulationThread(self.movement_manager, continuous=True)
        self.simulation_thread.update_signal.connect(self.handle_simulation_update)
        self.simulation_thread.finished_signal.connect(self.simulation_finished)
        self.simulation_thread.start()
        
        self.step_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def stop_simulation(self):
        """Stop the simulation"""
        if self.simulation_thread:
            self.simulation_thread.stop()
            self.simulation_thread.wait()
            self.log_text.append("Simulation stopped")
            
        self.step_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def reset_simulation(self):
        """Reset the simulation to initial state"""
        self.stop_simulation()
        self.load_submarines()
        self.collision_table.setRowCount(0)
        self.log_text.append("Simulation reset")
    
    def simulation_finished(self):
        """Handle simulation finished signal"""
        self.log_text.append("Simulation finished")
        self.step_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def handle_simulation_update(self, data):
        """Handle updates from the simulation thread"""
        if data['type'] == 'movement':
            self.log_text.append(
                f"Submarine {data['sub_id']} moved {data['command']} {data['value']} "
                f"to position {data['position']}"
            )
        elif data['type'] == 'collision':
            self.log_text.append(
                f"COLLISION: Submarine {data['sub1_id']} and {data['sub2_id']} "
                f"at position {data['position']}"
            )
            
            # Add to collision table
            row = self.collision_table.rowCount()
            self.collision_table.insertRow(row)
            self.collision_table.setItem(row, 0, QTableWidgetItem(data['sub1_id']))
            self.collision_table.setItem(row, 1, QTableWidgetItem(data['sub2_id']))
            self.collision_table.setItem(row, 2, QTableWidgetItem(str(data['position'][0])))
            self.collision_table.setItem(row, 3, QTableWidgetItem(str(data['position'][1])))
        
        # Update position table
        self.update_position_table()
        
        # Update progress bar
        active_subs = sum(1 for sub in self.movement_manager.submarines.values() if sub.is_active)
        total_subs = len(self.movement_manager.submarines)
        self.progress_bar.setValue(100 - int(active_subs / total_subs * 100))


def main():
    """Main function to run the GUI"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    gui = SubmarineGUI()
    gui.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()