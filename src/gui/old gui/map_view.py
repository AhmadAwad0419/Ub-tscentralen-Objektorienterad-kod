import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MapView(QWidget):
    """Simple map view: plots submarine final positions and collision points."""
    def __init__(self, submarines, collisions, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Karta - Submarines och Kollisioner")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.submarines = submarines
        self.collisions = collisions  # list of tuples (sub1, sub2, position)

        self._draw_map()

    def _draw_map(self):
        ax = self.figure.add_subplot(111)
        ax.clear()
        # plot submarines final positions
        xs = [sub.get_position()[0] for sub in self.submarines]
        ys = [sub.get_position()[1] for sub in self.submarines]
        labels = [str(getattr(sub, "id", "")) for sub in self.submarines]

        if xs and ys:
            ax.scatter(xs, ys, c='blue', label='Submarines', zorder=3)
            for x, y, lbl in zip(xs, ys, labels):
                ax.annotate(lbl, (x, y), textcoords="offset points", xytext=(5,5), fontsize=8)

        # plot collision points
        coll_points = [pos for (_s1, _s2, pos) in self.collisions]
        if coll_points:
            cx = [p[0] for p in coll_points]
            cy = [p[1] for p in coll_points]
            ax.scatter(cx, cy, c='red', marker='x', s=80, label='Kollisioner', zorder=4)
            for x, y in zip(cx, cy):
                ax.annotate(f"({x},{y})", (x, y), textcoords="offset points", xytext=(5,-10), color='red', fontsize=8)

        ax.set_xlabel("Horizontal position")
        ax.set_ylabel("Vertical position")
        ax.grid(True)
        ax.legend()
        self.canvas.draw()