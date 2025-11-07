import sys
import threading
import json
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.Learning import run as LearningRecommender
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.Model import FirstLayerDMM
from Backend.ImageGenration import GenerateImage
from Backend.IoT import iot
from Backend.TextToSpeech import TextToSpeech

class WaveformWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.value = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_wave)
        self.timer.start(50)

    def update_wave(self):
        self.value = (self.value + 1) % 100
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor("#00eaff"), 3)
        painter.setPen(pen)
        w = self.width()
        h = self.height()
        center = h // 2

        for i in range(0, w, 6):
            amp = abs((self.value - i) % 60 - 30) * 1.8
            painter.drawLine(i, center - amp, i, center + amp)


class NeuroApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neuro AI Assistant")
        self.setGeometry(200, 150, 950, 650)

        # ✅ Load Dark theme
        self.dark_theme = True
        self.apply_theme()

        layout = QHBoxLayout()

        # -----------------------
        # LEFT: CHAT PANEL
        # -----------------------
        chatLayout = QVBoxLayout()

        self.title = QLabel("🤖 Neuro – AI Personal Assistant")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:24px; font-weight:bold; margin:10px;")
        chatLayout.addWidget(self.title)

        self.outputBox = QTextEdit()
        self.outputBox.setReadOnly(True)
        self.outputBox.setStyleSheet("border-radius:10px; padding:10px; font-size:15px;")
        chatLayout.addWidget(self.outputBox)

        inputLayout = QHBoxLayout()
        self.inputField = QLineEdit()
        self.inputField.setPlaceholderText("Type here...")
        self.inputField.setStyleSheet("padding:10px; border-radius:6px; font-size:16px;")
        inputLayout.addWidget(self.inputField)

        sendBtn = QPushButton("Send")
        sendBtn.clicked.connect(self.send_text)
        sendBtn.setStyleSheet(self.button_style("#0078ff"))
        inputLayout.addWidget(sendBtn)

        micBtn = QPushButton("🎤 Speak")
        micBtn.clicked.connect(self.speech_to_text)
        micBtn.setStyleSheet(self.button_style("#ff0055"))
        inputLayout.addWidget(micBtn)

        themeBtn = QPushButton("🌗 Theme")
        themeBtn.setStyleSheet(self.button_style("#00c896"))
        themeBtn.clicked.connect(self.toggle_theme)
        inputLayout.addWidget(themeBtn)

        chatLayout.addLayout(inputLayout)

        # ✅ Siri-style waveform bar
        self.wave = WaveformWidget()
        self.wave.setFixedHeight(60)
        chatLayout.addWidget(self.wave)

        layout.addLayout(chatLayout, 65)

        # -----------------------
        # RIGHT: LEARNING PANEL
        # -----------------------
        self.learningPanel = QVBoxLayout()
        self.learningTitle = QLabel("📚 Learning Recommendations")
        self.learningTitle.setStyleSheet("font-size:20px; font-weight:bold;")
        self.learningList = QListWidget()

        self.exportBtn = QPushButton("📄 Export Study Plan (PDF)")
        self.exportBtn.clicked.connect(self.export_pdf)
        self.exportBtn.setVisible(False)
        self.exportBtn.setStyleSheet(self.button_style("#00b359"))

        self.learningPanel.addWidget(self.learningTitle)
        self.learningPanel.addWidget(self.learningList)
        self.learningPanel.addWidget(self.exportBtn)

        sideWidget = QWidget()
        sideWidget.setLayout(self.learningPanel)
        sideWidget.setMaximumWidth(300)
        layout.addWidget(sideWidget, 35)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.studyPlan = []
        self.check_for_updates()

    # ✅ Auto update checker
    def check_for_updates(self):
        try:
            repo_url = "https://api.github.com/repos/Ameyk-byte/DES646/releases/latest"
            import requests
            r = requests.get(repo_url).json()
            latest = r.get("tag_name", "v0")
            self.outputBox.append(f"🔍 Checking updates… Latest version: {latest}")
        except:
            self.outputBox.append("⚠️ Unable to check updates")

    # ✅ Apply themes
    def apply_theme(self):
        if self.dark_theme:
            self.setStyleSheet("""
                QMainWindow { background: #0f0f17; color:white; }
                QTextEdit { background:#1b1b29; color:white; }
                QLineEdit { background:#1b1b29; color:white; }
                QListWidget { background:#1b1b29; color:white; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background:white; color:black; }
                QTextEdit { background:#e8e8e8; color:black; }
                QLineEdit { background:#e8e8e8; color:black; }
                QListWidget { background:#f0f0f0; color:black; }
            """)

    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.apply_theme()

    def button_style(self, color):
        return f"""
            QPushButton {{
                background:{color}; color:white;
                border-radius:6px; padding:7px; font-size:15px;
            }}
            QPushButton:hover {{
                background:white; color:{color}; font-weight:bold;
            }}
        """

    # ✅ Handlers
    def send_text(self):
        txt = self.inputField.text().strip()
        self.inputField.clear()
        if txt:
            self.process_query(txt)

    def speech_to_text(self):
        self.outputBox.append("🎙 Listening…")
        threading.Thread(target=self.speech_thread).start()

    def speech_thread(self):
        text = SpeechRecognition()
        if text:
            self.outputBox.append(f"🗣 You: {text}")
            clean = text.lower().replace("neuro", "").strip()
            self.process_query(clean)

    # ✅ Query Processor
    def process_query(self, query):
        self.outputBox.append(f"🧑 You: {query}")
        self.loading_animation(True)
        threading.Thread(target=self.process_thread, args=(query,)).start()

    def loading_animation(self, state):
        if state:
            self.outputBox.append("⏳ Thinking…")
        else:
            self.outputBox.append("")

    def process_thread(self, query):
        try:
            decisions = FirstLayerDMM(query)

            # ✅ Learning
            if any(d.startswith("LearningRecommender") for d in decisions):
                text, payload = LearningRecommender(query)
                self.outputBox.append(f"📚 {text}")
                TextToSpeech("Here are learning resources")
                self.update_learning_ui(payload)
                self.loading_animation(False)
                return

            # ✅ Realtime
            if any(d.startswith("realtime") for d in decisions):
                ans = RealtimeSearchEngine(query)
                self.outputBox.append(f"🌍 {ans}")
                TextToSpeech(ans)
                self.loading_animation(False)
                return

            # ✅ Image
            for d in decisions:
                if d.startswith("generate image"):
                    GenerateImage(d.replace("generate image ", ""))
                    self.outputBox.append("🖼 Image Generated!")
                    TextToSpeech("Image generated")
                    self.loading_animation(False)
                    return

            # ✅ IoT
            for d in decisions:
                if d.startswith("iot"):
                    ans = iot(d.replace("iot ", ""))
                    self.outputBox.append(f"🔧 {ans}")
                    TextToSpeech(ans)
                    self.loading_animation(False)
                    return

            # ✅ Automation
            if any(d.startswith(x) for x in ["open","close","play","system"] for d in decisions):
                Automation(decisions)
                self.outputBox.append("✅ Task executed.")
                TextToSpeech("Task done")
                self.loading_animation(False)
                return

            # ✅ Chatbot
            ans = ChatBot(query)
            self.outputBox.append(f"🤖 Neuro: {ans}")
            TextToSpeech(ans)
            self.loading_animation(False)

        except Exception as e:
            self.outputBox.append("❌ Error occurred")
            print(e)

    def update_learning_ui(self, payload):
        self.learningList.clear()
        self.studyPlan = payload.get("weekly_plan", [])
        recs = payload.get("recommendations", [])
        for r in recs:
            item = QListWidgetItem(f"{r['title']} ({r['level']}) - {r['duration_min']} min")
            item.setToolTip(r['url'])
            self.learningList.addItem(item)
        self.exportBtn.setVisible(True)

    def export_pdf(self):
        file, _ = QFileDialog.getSaveFileName(self, "Save Study Plan", "study_plan.pdf", "PDF Files (*.pdf)")
        if not file: return
        c = canvas.Canvas(file, pagesize=A4)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, 800, "Neuro – Study Plan")
        y = 760
        c.setFont("Helvetica", 12)
        for wk in self.studyPlan:
            c.drawString(50, y, f"Week {wk['week']}:")
            y -= 20
            for item in wk["items"]:
                c.drawString(60, y, f"- {item['title']} ({item['duration_min']} min)")
                y -= 15
            y -= 10
        c.save()
        self.outputBox.append("✅ PDF Saved!")
        TextToSpeech("Study plan exported successfully.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NeuroApp()
    window.setWindowIcon(QIcon("appicon.icns"))  # ✅ Add custom icon
    window.show()
    sys.exit(app.exec_())
