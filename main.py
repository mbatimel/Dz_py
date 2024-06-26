import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import rfft
from scipy.signal import find_peaks
class DataProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Data Processor')
        self.setGeometry(100, 100, 600, 400)

        self.file_path = None
        self.data = None

        self.init_ui()

    def init_ui(self):
        self.lbl_file = QLabel('Выберите файл:', self)
        self.lbl_file.setGeometry(20, 20, 200, 20)

        self.btn_open_file = QPushButton('Открыть файл', self)
        self.btn_open_file.setGeometry(120, 50, 200, 30)
        self.btn_open_file.clicked.connect(self.open_file_dialog)

        self.lbl_duration = QLabel('', self)
        self.lbl_duration.setGeometry(20, 100, 300, 20)

        self.btn_plot_signals = QPushButton('Построить сигналы', self)
        self.btn_plot_signals.setGeometry(20, 150, 150, 30)
        self.btn_plot_signals.clicked.connect(self.plot_signals)

        self.btn_plot_spectrum = QPushButton('Построить спектр', self)
        self.btn_plot_spectrum.setGeometry(200, 150, 150, 30)
        self.btn_plot_spectrum.clicked.connect(self.plot_spectrum)

        self.btn_plot_instant_power = QPushButton('Построить мгновенную мощность', self)
        self.btn_plot_instant_power.setGeometry(20, 200, 250, 30)
        self.btn_plot_instant_power.clicked.connect(self.plot_instant_power)

        self.btn_plot_power = QPushButton('Построить мощности', self)
        self.btn_plot_power.setGeometry(300, 200, 200, 30)
        self.btn_plot_power.clicked.connect(self.plot_power)

        self.btn_plot_harmonics = QPushButton('Построить гармоники', self)
        self.btn_plot_harmonics.setGeometry(20, 250, 200, 30)
        self.btn_plot_harmonics.clicked.connect(self.plot_harmonics)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, 'Открыть файл', '', 'Текстовые файлы (*.txt)', options=options)
        if file_path:
            self.file_path = file_path
            self.load_data()

    def load_data(self):
        with open(self.file_path, 'r') as file:
            self.data = file.readlines()

        # Calculate duration
        duration = self.calculate_duration(self.data)
        self.lbl_duration.setText(f'Продолжительность эксперимента: {duration}')

    def convert_to_seconds(self, time_str):
        hms = time_str.split(':')
        if len(hms) == 3:
            h, m, s = map(int, hms)
            return h * 3600 + m * 60 + s
        else:
            return 0  # Handle improperly formatted time strings

    def calculate_duration(self, data):
        # Extract time from data
        time_values = [self.convert_to_seconds(line.split()[0]) for line in data]
        time_values = [t for t in time_values if t > 0]  # Filter out negative or improperly formatted times
        if time_values:
            duration = max(time_values) - min(time_values)
            hours = int(duration / 3600)
            minutes = int((duration % 3600) / 60)
            seconds = int(duration % 60)
            return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        else:
            return '00:00:00'  # Return default duration if no valid times found

    def plot_signals(self):
        try:
            # Load data from Ub.txt and Ib.txt
            with open('Ub.txt', 'r') as file_ub, open('Ib.txt', 'r') as file_ib:
                data_ub = file_ub.readlines()
                data_ib = file_ib.readlines()

            print(len(data_ub), len(data_ib))
            # Find the 333rd line (index 332)
            
            line_ub = []
            line_ib = []
            
            for line in range(0, len(data_ub), 2):
                line_ub.append(data_ub[line])
                
            for line in range(0, len(data_ib), 2):
                line_ib.append(data_ib[line])
            
            ub_line = line_ub[332]
            ib_line = line_ib[332]

            # Extract time, uk(t), and ik(t) values
            
            ub_values = []
            ib_values = []
            
            for line in ub_line.split():
                ub_values.append(float(line.replace(',', '.')))
                
            for line in ib_line.split():
                ib_values.append(float(line.replace(',', '.')))

            # Plot the signals
            
            seconds = []
            point = 0
            
            for i in range (0, 80):
                seconds.append(point)
                point += 0.000625
                
            plt.figure()
            # plt.scatter(seconds, ub_values)
            plt.plot(seconds, ub_values, '-o', label='uk(t)')
            plt.figure()
            plt.plot(seconds, ib_values, 'o-', label='ik(t)')
            plt.xlabel('Время (с)')
            plt.ylabel('Сигналы')
            plt.grid(True)
            plt.legend()
            plt.show()

        except Exception as e:
            print(f"Ошибка при построении сигналов: {e}")


    
    def plot_spectrum(self):
        if not self.data:
            return
        
        line_ib = []
        
        for line in range(0, len(self.data), 2):
            line_ib.append(self.data[line])
        
        ib_line = line_ib[332]
        ib_values = []
            
        for line in ib_line.split():
            ib_values.append(float(line.replace(',', '.')))
        # Extract data for one cycle
       

        # Calculate FFT
        spectrum = rfft(ib_values)

        
        freq = []
        for i in range (0, len(spectrum)):
            freq.append((800/64) * (i + 1))
        
        # freq = np.fft.fftfreq(len(seconds))

        # Plot spectrum
        plt.figure()
        plt.plot(freq, np.abs(spectrum))
        plt.xlabel('ГЦ')
        plt.ylabel('Амплитуда')
        plt.title('Спектр сигнала')
        plt.grid(True)
        plt.show()


    def extract_cycle_data(self, data):
        # Assuming data format is consistent and one cycle is one line
        return data[:len(data)//2]

   
    def plot_instant_power(self):
        try:
            # Load data from Ub.txt and Ib.txt
            with open('Ub.txt', 'r') as file_ub, open('Ib.txt', 'r') as file_ib:
                data_ub = file_ub.readlines()
                data_ib = file_ib.readlines()

            print(len(data_ub), len(data_ib))
            # Find the 333rd line (index 332)
            
            line_ub = []
            line_ib = []
            
            for line in range(0, len(data_ub), 2):
                line_ub.append(data_ub[line])
                
            for line in range(0, len(data_ib), 2):
                line_ib.append(data_ib[line])
            
            ub_line = line_ub[332]
            ib_line = line_ib[332]

            # Extract time, uk(t), and ik(t) values
            
            ub_values = []
            ib_values = []
            
            for line in ub_line.split():
                ub_values.append(float(line.replace(',', '.')))
                
            for line in ib_line.split():
                ib_values.append(float(line.replace(',', '.')))

            # Plot the signals
            
            seconds = []
            point = 0
            
            for i in range (0, 80):
                seconds.append(point)
                point += 0.000625

            # Calculate instant power
            power = []
            
            for i in range(0, len(ub_values), 1):
                power.append(ub_values[i] * ib_values[i])

            # Построение графика
            plt.figure()
            plt.plot(seconds, power)
            plt.xlabel('Время (с)')
            plt.ylabel('Мгновенная мощность (p)')
            plt.grid(True)
            plt.show()

        except Exception as e:
            print(f"Ошибка при построении мгновенной мощности: {e}")


    def plot_power(self):
        if not self.data:
            return

        # Extract uk(t) and ik(t)
        time_values = np.array([self.convert_to_seconds(line.split()[0]) for line in self.data])
        uk_values = np.array([float(line.split()[1].replace(',', '.')) for line in self.data])
        ik_values = np.array([float(line.split()[2].replace(',', '.')) for line in self.data])

        # Calculate instant power
        power = uk_values * ik_values

        # Calculate active, reactive, and apparent power
        active_power = np.mean(power)
        reactive_power = np.sqrt(np.mean(power**2 - active_power**2))
        apparent_power = np.sqrt(active_power**2 + reactive_power**2)

        # Save calculated powers to files
        file_dir = os.path.dirname(self.file_path)
        active_power_file = os.path.join(file_dir, 'active_power.txt')
        reactive_power_file = os.path.join(file_dir, 'reactive_power.txt')
        apparent_power_file = os.path.join(file_dir, 'apparent_power.txt')
        np.savetxt(active_power_file, [active_power], fmt='%.4f')
        np.savetxt(reactive_power_file, [reactive_power], fmt='%.4f')
        np.savetxt(apparent_power_file, [apparent_power], fmt='%.4f')

        # Plot powers
        plt.figure()
        plt.plot(time_values, active_power * np.ones_like(time_values), label='Active Power (P)')
        plt.plot(time_values, reactive_power * np.ones_like(time_values), label='Reactive Power (Q)')
        plt.plot(time_values, apparent_power * np.ones_like(time_values), label='Apparent Power (S)')
        plt.xlabel('Время (с)')
        plt.ylabel('Мощность')
        plt.grid(True)
        plt.legend()
        plt.show()


    def plot_harmonics(self):
        if not self.data:
            return

        # Extract uk(t) and ik(t)
        with open('Ub.txt', 'r') as file_ub, open('Ib.txt', 'r') as file_ib:
                data_ub = file_ub.readlines()
                data_ib = file_ib.readlines()

        
            # Find the 333rd line (index 332)
            
        line_ub = []
        line_ib = []
            
        for line in range(0, len(data_ub), 2):
            line_ub.append(data_ub[line])
                
        for line in range(0, len(data_ib), 2):
            line_ib.append(data_ib[line])
            
        ub_line = line_ub[332]
        ib_line = line_ib[332]

            # Extract time, uk(t), and ik(t) values
            
        ub_values = []
        ib_values = []
            
        for line in ub_line.split():
            ub_values.append(float(line.replace(',', '.')))
                
        for line in ib_line.split():
            ib_values.append(float(line.replace(',', '.')))


        # Calculate FFT
        spectrum = rfft(ub_values)
        freq = np.fft.fftfreq(len(ib_values))

        # Find peaks
        peaks, _ = find_peaks(np.abs(spectrum), height=0, distance=1)
        harmonics_freq = freq[peaks][1:4]  # first three harmonics excluding DC
        harmonics_amp = np.abs(spectrum[peaks][1:4])  # amplitude of first three harmonics

        # Plot harmonics
        plt.figure()
        plt.stem(harmonics_freq, harmonics_amp)
        plt.xlabel('Частота (Гц)')
        plt.ylabel('Амплитуда')
        plt.title('Гармоники')
        plt.grid(True)
        plt.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataProcessor()
    window.show()
    sys.exit(app.exec_())