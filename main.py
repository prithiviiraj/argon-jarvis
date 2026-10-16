import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QLineEdit, QFormLayout, QTextEdit, QFrame, QCheckBox
from PyQt6.QtCore import QTimer, QTime, Qt
from PyQt6.QtGui import QFont

class ArgonJarvisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Argon-Jarvis Desktop")
        self.resize(900, 650)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        header_layout = QHBoxLayout()
        title_label = QLabel("ARGON-JARVIS AI SUITE")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Arial", 14))
        self.update_clock()
        
        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.clock_label)
        main_layout.addLayout(header_layout)
        
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        dash_tab = QWidget()
        dash_layout = QVBoxLayout(dash_tab)
        agents_layout = QHBoxLayout()
        
        agents_layout.addWidget(self.create_agent_card("JARVIS", "Core AI", "#00E5FF"))
        agents_layout.addWidget(self.create_agent_card("LYRA", "Creative AI", "#FF4D8D"))
        agents_layout.addWidget(self.create_agent_card("DEX", "Logic AI", "#10B981"))
        
        dash_layout.addLayout(agents_layout)
        
        voice_frame = QFrame()
        voice_layout = QVBoxLayout(voice_frame)
        voice_layout.addWidget(QLabel("Voice & Interactive Controls"))
        
        controls_layout = QHBoxLayout()
        self.voice_toggle = QPushButton("Voice Call: OFF")
        self.voice_toggle.setCheckable(True)
        self.voice_toggle.clicked.connect(self.toggle_voice_call)
        controls_layout.addWidget(self.voice_toggle)
        
        controls_layout.addWidget(QCheckBox("Enable Barge-In"))
        controls_layout.addWidget(QCheckBox("Tanglish Support"))
        
        debate_btn = QPushButton("Lyra vs Dex Debate")
        debate_btn.clicked.connect(self.start_debate)
        controls_layout.addWidget(debate_btn)
        
        voice_layout.addLayout(controls_layout)
        self.log_area = QTextEdit()
        voice_layout.addWidget(self.log_area)
        dash_layout.addWidget(voice_frame)
        
        tabs.addTab(dash_tab, "Dashboard")
        
        settings_tab = QWidget()
        settings_layout = QFormLayout(settings_tab)
        
        self.groq_key = QLineEdit()
        settings_layout.addRow("Groq API Key:", self.groq_key)
        self.gemini_key = QLineEdit()
        settings_layout.addRow("Gemini API Key:", self.gemini_key)
        self.nvidia_key = QLineEdit()
        settings_layout.addRow("NVIDIA NIM API Key:", self.nvidia_key)
        self.lmstudio_key = QLineEdit()
        settings_layout.addRow("LM Studio API Key:", self.lmstudio_key)
        
        tabs.addTab(settings_tab, "Settings")

    def create_agent_card(self, name, role, color_hex):
        card = QFrame()
        card.setStyleSheet(f"border: 2px solid {color_hex}; border-radius: 8px; padding: 10px;")
        layout = QVBoxLayout(card)
        lbl = QLabel(f"<h3 style='color:{color_hex};'>{name}</h3><p>{role}</p>")
        layout.addWidget(lbl)
        return card

    def update_clock(self):
        self.clock_label.setText(f"IST: {QTime.currentTime().toString('hh:mm:ss AP')}")

    def toggle_voice_call(self):
        state = "ON" if self.voice_toggle.isChecked() else "OFF"
        self.voice_toggle.setText(f"Voice Call: {state}")
        self.log_area.append(f"[Voice Call] State changed to {state} (Barge-In & Tanglish active)")

    def start_debate(self):
        self.log_area.append("[Debate] LYRA vs DEX debate started!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ArgonJarvisApp()
    window.show()
    sys.exit(app.exec())
