from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas 
import matplotlib.pyplot as plt
from PyQt4 import QtCore, QtGui
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

class Canvas(FigureCanvas):
    def __init__(self, parent=None):
        self.figure = plt.figure()
        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)

