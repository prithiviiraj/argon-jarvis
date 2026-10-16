import sys
import os
import json
import datetime
import psutil
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QFrame, QCheckBox, QComboBox, QTextEdit, QDialog
)
from PyQt6.QtCore import QTimer, QTime, Qt, QDateTime, QTimeZone, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None


class AgentOrb(QWidget):
    def __init__(self, name, color_hex, role, parent=None):
        super().__init__(parent)
        self.agent_name = name
        self.color_hex = color_hex
        self.role = role
        self.pulse_size = 0
        self.growing = True
        self.setMinimumSize(120, 140)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def animate(self):
        if self.growing:
            self.pulse_size += 1
            if self.pulse_size >= 10:
                self.growing = False
        else:
            self.pulse_size -= 1
            if self.pulse_size <= 0:
                self.growing = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() // 2
        center_y = 50

        color = QColor(self.color_hex)
        glow_color = QColor(color)
        glow_color.setAlpha(60)

        radius = 35 + self.pulse_size
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        painter.setBrush(QBrush(color))
        painter.drawEllipse(center_x - 30, center_y - 30, 60, 60)

        painter.setPen(QPen(QColor("#FFFFFF")))
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 100, self.width(), 20, Qt.AlignmentFlag.AlignCenter, self.agent_name)

        role_font = QFont("Arial", 8)
        painter.setFont(role_font)
        painter.setPen(QPen(QColor("#AAAAAA")))
        painter.drawText(0, 118, self.width(), 20, Qt.AlignmentFlag.AlignCenter, f"({self.role})")


class HUDWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Argon-Jarvis HUD")
        self.resize(220, 50)
        self.setStyleSheet("""
            QWidget {
                background-color: #121824;
                border: 2px solid #00E5FF;
                border-radius: 25px;
                color: #FFFFFF;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)

        self.label = QLabel("ARGON-JARVIS HUD ACTIVE")
        self.label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.label.setStyleSheet("color: #00E5FF; border: none;")
        layout.addWidget(self.label)


class ArgonJarvisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Argon-Jarvis Desktop Interface")
        self.resize(950, 700)
        self.setStyleSheet("background-color: #0F172A; color: #F8FAFC;")

        self.is_call_active = False
        self.is_screen_sharing = False
        self.hud_window = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        header_layout = QHBoxLayout()
        title_label = QLabel("ARGON-JARVIS AI SUITE")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #00E5FF;")

        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.clock_label.setStyleSheet("color: #10B981; background: #1E293B; padding: 6px 12px; border-radius: 6px;")
        self.update_ist_clock()

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_ist_clock)
        self.clock_timer.start(1000)

        self.hud_btn = QPushButton("Toggle HUD Pill Window")
        self.hud_btn.setStyleSheet("background-color: #334155; color: white; padding: 6px 12px; border-radius: 6px;")
        self.hud_btn.clicked.connect(self.toggle_hud_pill)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.hud_btn)
        header_layout.addWidget(self.clock_label)
        main_layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #334155; background: #0F172A; }
            QTabBar::tab { background: #1E293B; color: #94A3B8; padding: 10px 20px; font-weight: bold; border-top-left-radius: 6px; border-top-right-radius: 6px; }
            QTabBar::tab:selected { background: #00E5FF; color: #0F172A; }
        """)

        self.tab_agents = QWidget()
        self.setup_agents_tab()
        self.tabs.addTab(self.tab_agents, "Agents & Call")

        self.tab_processes = QWidget()
        self.setup_processes_tab()
        self.tabs.addTab(self.tab_processes, "Hands & Processes")

        self.tab_settings = QWidget()
        self.setup_settings_tab()
        self.tabs.addTab(self.tab_settings, "Settings & Keys")

        main_layout.addWidget(self.tabs)

    def update_ist_clock(self):
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        ist_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        ist_now = utc_now.astimezone(ist_tz)
        time_str = ist_now.strftime("%I:%M:%S %p IST")
        self.clock_label.setText(time_str)

    def toggle_hud_pill(self):
        if self.hud_window is None or not self.hud_window.isVisible():
            self.hud_window = HUDWindow()
            self.hud_window.show()
        else:
            self.hud_window.close()

    def setup_agents_tab(self):
        layout = QVBoxLayout(self.tab_agents)

        orbs_layout = QHBoxLayout()
        self.orb_jarvis = AgentOrb("JARVIS", "#00E5FF", "Leader")
        self.orb_lyra = AgentOrb("LYRA", "#FF4D8D", "Companion")
        self.orb_dex = AgentOrb("DEX", "#10B981", "Coder")

        orbs_layout.addWidget(self.orb_jarvis)
        orbs_layout.addWidget(self.orb_lyra)
        orbs_layout.addWidget(self.orb_dex)
        layout.addLayout(orbs_layout)

        debate_btn = QPushButton("Lyra vs Dex Debate")
        debate_btn.setStyleSheet("background-color: #8B5CF6; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        debate_btn.clicked.connect(self.start_debate)
        layout.addWidget(debate_btn)

        call_frame = QFrame()
        call_frame.setStyleSheet("background-color: #1E293B; border-radius: 8px; padding: 10px;")
        call_layout = QVBoxLayout(call_frame)

        call_controls_layout = QHBoxLayout()

        self.call_btn = QPushButton("Start Voice Call")
        self.call_btn.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        self.call_btn.clicked.connect(self.toggle_call)

        self.barge_btn = QPushButton("Barge-In Stop")
        self.barge_btn.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        self.barge_btn.clicked.connect(self.barge_in_stop)

        self.screen_share_btn = QPushButton("Screen Share: OFF")
        self.screen_share_btn.setStyleSheet("background-color: #64748B; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        self.screen_share_btn.clicked.connect(self.toggle_screen_share)

        call_controls_layout.addWidget(self.call_btn)
        call_controls_layout.addWidget(self.barge_btn)
        call_controls_layout.addWidget(self.screen_share_btn)
        call_layout.addLayout(call_controls_layout)

        input_opt_layout = QHBoxLayout()
        lang_label = QLabel("Language Input:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "Tamil", "Tanglish"])
        self.lang_combo.setStyleSheet("background-color: #0F172A; color: white; padding: 5px;")

        input_opt_layout.addWidget(lang_label)
        input_opt_layout.addWidget(self.lang_combo)
        input_opt_layout.addStretch()
        call_layout.addLayout(input_opt_layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #0F172A; color: #F8FAFC; font-size: 13px; border: 1px solid #334155;")
        call_layout.addWidget(self.chat_display)

        text_input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your prompt or question here...")
        self.user_input.setStyleSheet("background-color: #0F172A; color: white; padding: 8px; border: 1px solid #334155; border-radius: 4px;")
        self.user_input.returnPressed.connect(self.send_user_message)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("background-color: #00E5FF; color: #0F172A; font-weight: bold; padding: 8px 16px; border-radius: 4px;")
        send_btn.clicked.connect(self.send_user_message)

        text_input_layout.addWidget(self.user_input)
        text_input_layout.addWidget(send_btn)
        call_layout.addLayout(text_input_layout)

        layout.addWidget(call_frame)

    def start_debate(self):
        self.chat_display.append("<b>[SYSTEM]:</b> Initiating 'Lyra vs Dex Debate' mode...")
        self.chat_display.append("<b style='color:#FF4D8D;'>[LYRA]:</b> I believe user experience and intuitive design should always come first!")
        self.chat_display.append("<b style='color:#10B981;'>[DEX]:</b> Design is meaningless if the code architecture and performance aren't optimized!")
        self.chat_display.append("<b style='color:#00E5FF;'>[JARVIS]:</b> Balance is key, teammates. Excellent arguments from both.")

    def toggle_call(self):
        self.is_call_active = not self.is_call_active
        if self.is_call_active:
            self.call_btn.setText("End Voice Call")
            self.call_btn.setStyleSheet("background-color: #DC2626; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
            self.chat_display.append("<b>[SYSTEM]:</b> Voice Call Started. Listening for English/Tamil/Tanglish voice input...")
            self.speak_text("Voice Call Started, Master.")
        else:
            self.call_btn.setText("Start Voice Call")
            self.call_btn.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
            self.chat_display.append("<b>[SYSTEM]:</b> Voice Call Ended.")

    def barge_in_stop(self):
        self.chat_display.append("<b>[SYSTEM]:</b> Barge-In Stop triggered! Speech output interrupted.")

    def toggle_screen_share(self):
        self.is_screen_sharing = not self.is_screen_sharing
        if self.is_screen_sharing:
            self.screen_share_btn.setText("Screen Share: ON")
            self.screen_share_btn.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
            self.chat_display.append("<b>[SYSTEM]:</b> Screen Share enabled.")
        else:
            self.screen_share_btn.setText("Screen Share: OFF")
            self.screen_share_btn.setStyleSheet("background-color: #64748B; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
            honesty_msg = "I cannot see your screen because share is off, Master. Turn it on?"
            self.chat_display.append(f"<b style='color:#00E5FF;'>[JARVIS Honesty Guard]:</b> {honesty_msg}")
            self.speak_text(honesty_msg)

    def send_user_message(self):
        text = self.user_input.text().strip()
        if not text:
            return
        lang = self.lang_combo.currentText()
        self.chat_display.append(f"<b>[USER ({lang})]:</b> {text}")
        self.user_input.clear()

        if ("screen" in text.lower() or "see" in text.lower()) and not self.is_screen_sharing:
            honesty_msg = "I cannot see your screen because share is off, Master. Turn it on?"
            self.chat_display.append(f"<b style='color:#00E5FF;'>[JARVIS Honesty Guard]:</b> {honesty_msg}")
            self.speak_text(honesty_msg)
        else:
            reply = f"Received your message in {lang}. How may I assist you further, Master?"
            self.chat_display.append(f"<b style='color:#00E5FF;'>[JARVIS]:</b> {reply}")

    def speak_text(self, text):
        if pyttsx3:
            try:
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            except Exception:
                pass

    def setup_processes_tab(self):
        layout = QVBoxLayout(self.tab_processes)

        top_bar = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Heavy Processes")
        refresh_btn.setStyleSheet("background-color: #00E5FF; color: #0F172A; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        refresh_btn.clicked.connect(self.load_heavy_processes)

        brave_btn = QPushButton("Launch Brave Browser")
        brave_btn.setStyleSheet("background-color: #FF5722; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        brave_btn.clicked.connect(self.launch_brave)

        top_bar.addWidget(refresh_btn)
        top_bar.addWidget(brave_btn)
        top_bar.addStretch()
        layout.addLayout(top_bar)

        self.proc_list = QListWidget()
        self.proc_list.setStyleSheet("background-color: #1E293B; color: #F8FAFC; border: 1px solid #334155; font-size: 13px;")
        layout.addWidget(self.proc_list)

        terminate_btn = QPushButton("Terminate Selected Process (Requires Approval)")
        terminate_btn.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        terminate_btn.clicked.connect(self.terminate_process_with_approval)
        layout.addWidget(terminate_btn)

        self.load_heavy_processes()

    def load_heavy_processes(self):
        self.proc_list.clear()
        heavy_procs = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                mem_mb = proc.info['memory_info'].rss / (1024 * 1024) if proc.info['memory_info'] else 0
                heavy_procs.append((proc.info['pid'], proc.info['name'], mem_mb))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        heavy_procs.sort(key=lambda x: x[2], reverse=True)

        for pid, name, mem in heavy_procs[:25]:
            item = QListWidgetItem(f"PID: {pid} | Process: {name} | Memory Usage: {mem:.2f} MB")
            item.setData(Qt.ItemDataRole.UserRole, pid)
            self.proc_list.addItem(item)

    def terminate_process_with_approval(self):
        current_item = self.proc_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a process from the list.")
            return

        pid = current_item.data(Qt.ItemDataRole.UserRole)
        proc_text = current_item.text()

        reply = QMessageBox.question(
            self,
            "Approval Card Required",
            f"Are you sure you approve closing this heavy process?\n\n{proc_text}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                p = psutil.Process(pid)
                p.terminate()
                QMessageBox.information(self, "Process Terminated", f"Process {pid} has been terminated.")
                self.load_heavy_processes()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not terminate process: {e}")

    def launch_brave(self):
        try:
            brave_paths = [
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                "brave"
            ]
            launched = False
            for path in brave_paths:
                if os.path.exists(path) or path == "brave":
                    try:
                        subprocess.Popen([path])
                        launched = True
                        break
                    except Exception:
                        continue
            if launched:
                QMessageBox.information(self, "Brave Browser", "Brave browser launched successfully!")
            else:
                QMessageBox.warning(self, "Brave Browser", "Brave executable not found at standard locations.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to launch Brave browser: {e}")

    def setup_settings_tab(self):
        layout = QVBoxLayout(self.tab_settings)

        info_label = QLabel("API Keys Configuration (~/.argon_jarvis/config.json)")
        info_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_label.setStyleSheet("color: #00E5FF; margin-bottom: 10px;")
        layout.addWidget(info_label)

        self.groq_key = QLineEdit()
        self.gemini_key = QLineEdit()
        self.nvidia_key = QLineEdit()
        self.lmstudio_key = QLineEdit()

        fields = [
            ("Groq API Key:", self.groq_key),
            ("Gemini API Key:", self.gemini_key),
            ("NVIDIA NIM API Key:", self.nvidia_key),
            ("LM Studio Local Endpoint/Key:", self.lmstudio_key)
        ]

        for label_text, widget in fields:
            f_layout = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(200)
            widget.setStyleSheet("background-color: #1E293B; color: white; padding: 8px; border: 1px solid #334155; border-radius: 4px;")
            f_layout.addWidget(lbl)
            f_layout.addWidget(widget)
            layout.addLayout(f_layout)

        save_btn = QPushButton("Save Settings & API Keys")
        save_btn.setStyleSheet("background-color: #10B981; color: white; font-weight: bold; padding: 12px; border-radius: 6px; margin-top: 15px;")
        save_btn.clicked.connect(self.save_keys)
        layout.addWidget(save_btn)

        layout.addStretch()

        self.load_keys()

    def get_config_path(self):
        config_dir = Path.home() / ".argon_jarvis"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"

    def load_keys(self):
        config_file = self.get_config_path()
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    data = json.load(f)
                    self.groq_key.setText(data.get("GROQ_API_KEY", ""))
                    self.gemini_key.setText(data.get("GEMINI_API_KEY", ""))
                    self.nvidia_key.setText(data.get("NVIDIA_NIM_API_KEY", ""))
                    self.lmstudio_key.setText(data.get("LM_STUDIO_KEY", ""))
            except Exception:
                pass

    def save_keys(self):
        data = {
            "GROQ_API_KEY": self.groq_key.text().strip(),
            "GEMINI_API_KEY": self.gemini_key.text().strip(),
            "NVIDIA_NIM_API_KEY": self.nvidia_key.text().strip(),
            "LM_STUDIO_KEY": self.lmstudio_key.text().strip()
        }
        config_file = self.get_config_path()
        try:
            with open(config_file, "w") as f:
                json.dump(data, f, indent=4)
            QMessageBox.information(self, "Success", f"API Keys saved successfully to:\n{config_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")


def main():
    app = QApplication(sys.argv)
    window = ArgonJarvisApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
