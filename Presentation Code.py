import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pyXSteam.XSteam import XSteam




class MplWidget(QWidget):
   def __init__(self, parent=None):
       super(MplWidget, self).__init__(parent)
       self.canvas = FigureCanvas(Figure())
       vertical_layout = QVBoxLayout()
       vertical_layout.addWidget(self.canvas)
       self.canvas.axes = self.canvas.figure.add_subplot(111)
       self.setLayout(vertical_layout)




class ThermodynamicAnalysis(QWidget):
   def __init__(self):
       super().__init__()


       self.setWindowTitle("Thermodynamic Analysis")
       self.setGeometry(100, 100, 800, 600)
       self.setWindowIcon(QIcon('icon.png'))


       self.init_ui()




   def init_ui(self):
       # Input fields
       self.temp_label = QLabel("Turbine Temperature (°C):")
       self.temp_input = QLineEdit()
       self.pressure_turbine_label = QLabel("Turbine Pressure (MPa):")
       self.pressure_turbine_input = QLineEdit()
       self.pressure_condenser_label = QLabel("Condenser Pressure (kPa):")
       self.pressure_condenser_input = QLineEdit()




       # Calculate button
       self.calculate_button = QPushButton("Calculate")
       self.calculate_button.clicked.connect(self.calculate)




       # Output labels
       self.output_label_h1 = QLabel("h1:")
       self.output_label_h2 = QLabel("h2:")
       self.output_label_h3 = QLabel("h3:")
       self.output_label_h4 = QLabel("h4:")
       self.output_label_qin = QLabel("Qin:")
       self.output_label_qout = QLabel("Qout:")
       self.output_label_Nth = QLabel("Thermal Efficiency:")




       # Matplotlib widget
       self.graph = MplWidget()




       # Layouts
       input_layout = QVBoxLayout()
       input_layout.addWidget(self.temp_label)
       input_layout.addWidget(self.temp_input)
       input_layout.addWidget(self.pressure_turbine_label)
       input_layout.addWidget(self.pressure_turbine_input)
       input_layout.addWidget(self.pressure_condenser_label)
       input_layout.addWidget(self.pressure_condenser_input)
       input_layout.addWidget(self.calculate_button)




       output_layout = QVBoxLayout()
       output_layout.addWidget(self.output_label_h1)
       output_layout.addWidget(self.output_label_h2)
       output_layout.addWidget(self.output_label_h3)
       output_layout.addWidget(self.output_label_h4)
       output_layout.addWidget(self.output_label_qin)
       output_layout.addWidget(self.output_label_qout)
       output_layout.addWidget(self.output_label_Nth)




       main_layout = QHBoxLayout()
       main_layout.addLayout(input_layout)
       main_layout.addLayout(output_layout)
       main_layout.addWidget(self.graph)




       self.setLayout(main_layout)




   def calculate(self):
       try:
           turbine_pressure_mpa = float(self.pressure_turbine_input.text())
           condenser_pressure_kpa = float(self.pressure_condenser_input.text())
           turbine_temperature_celsius = float(self.temp_input.text())
       except ValueError:
           print("Invalid input. Please enter valid numerical values.")
           return


       if turbine_pressure_mpa <= 0 or condenser_pressure_kpa <= 0 or turbine_temperature_celsius <= -273.15:
           print("Invalid input. Please enter values greater than 0 for pressure and a temperature greater than absolute zero.")
           return


       # Integration of rankine_cycle_properties function
       steamTable = XSteam(XSteam.UNIT_SYSTEM_MKS)
       turbine_pressure = turbine_pressure_mpa * 10
       condenser_pressure = condenser_pressure_kpa / 100
       p1 = condenser_pressure
       h1 = steamTable.hL_p(p1)
       v1 = steamTable.vL_p(p1)
       wp2 = v1 * (turbine_pressure - p1) * 100
       h2 = h1 + wp2
       p3 = turbine_pressure
       t3 = turbine_temperature_celsius
       h3 = steamTable.h_pt(p3, t3)
       p4 = condenser_pressure
       s4 = steamTable.s_pt(p3, t3)
       sf = steamTable.sL_p(p4)
       sfg = steamTable.sV_p(p4) - sf
       x4 = (s4 - sf) / sfg
       h4 = steamTable.h_px(p4, x4)
       Qin = h3 - h2
       Qout = h4 - h1
       efficiency = 1 - Qout / Qin


       # Round the values for better output
       h1 = round(h1, 2)
       h2 = round(h2, 2)
       h3 = round(h3, 2)
       h4 = round(h4, 2)
       Qin = round(Qin, 2)
       Qout = round(Qout, 2)
       efficiency = round(efficiency, 4)


       # Update output labels with rounded values
       self.output_label_h1.setText(f"h1: {h1} kJ/kg")
       self.output_label_h2.setText(f"h2: {h2} kJ/kg")
       self.output_label_h3.setText(f"h3: {h3} kJ/kg")
       self.output_label_h4.setText(f"h4: {h4} kJ/kg")
       self.output_label_qin.setText(f"Qin: {Qin} kJ/kg")
       self.output_label_qout.setText(f"Qout: {Qout} kJ/kg")
       self.output_label_Nth.setText(f"Thermal Efficiency: {efficiency:.2%}")




       # Update graph
       self.graph.canvas.axes.clear()
       states = ['State 1', 'State 2', 'State 3', 'State 4']
       enthalpies = [h1, h2, h3, h4]
       self.graph.canvas.axes.plot(states, enthalpies, marker='o', label='State')
       self.graph.canvas.axes.set_xlabel('State')
       self.graph.canvas.axes.set_ylabel('Specific Enthalpy (kJ/kg)')
       self.graph.canvas.axes.set_title('Thermodynamic Analysis')
       self.graph.canvas.axes.legend()
       self.graph.canvas.draw()




if __name__ == '__main__':
   app = QApplication(sys.argv)
   window = ThermodynamicAnalysis()
   window.show()
   sys.exit(app.exec_())
