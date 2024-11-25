import openai
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton,
    QFileDialog, QScrollArea, QStackedWidget, QMessageBox, QHBoxLayout, QFrame, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
from PyPDF2 import PdfReader
from docx import Document

# 设置 OpenAI API Key
openai.api_key = "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"

USER_DATA_FILE = "users.json"
HISTORY_FILE_TEMPLATE = "chat_history_{username}.json"

class StyledWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f5;
                font-family: Arial;
                font-size: 15px;
            }
            QLabel {
                color: #4a4a4a;
                font-size: 17px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 12px;
                padding: 7px;
            }
            QPushButton {
                background-color: #8B8989;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color:#696969;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 12px;
                padding: 7px;
            }
        """)

if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump({}, file)


def load_users():
    with open(USER_DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_users(users):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

def read_file_content(file_path):
    """
    读取文件内容，支持 .txt, .pdf, .docx 文件
    """
    try:
        if file_path.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        elif file_path.endswith(".pdf"):
            pdf_reader = PdfReader(file_path)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])

        else:
            return "不支持的文件类型"
    except Exception as e:
        return f"文件读取错误: {str(e)}"


def load_chat_history(username):
    history_file = HISTORY_FILE_TEMPLATE.format(username=username)
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as file:
            return json.load(file)
    return [{"role": "system", "content": "你是一个友好的助手，可以回答各种问题。"}]


def save_chat_history(username, messages):
    history_file = HISTORY_FILE_TEMPLATE.format(username=username)
    with open(history_file, "w", encoding="utf-8") as file:
        json.dump(messages, file, ensure_ascii=False, indent=4)


def get_gpt_response(user_input, messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini", messages=messages
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"错误: {str(e)}"



class ChatBubble(QFrame):
    def __init__(self, text, is_user):
        super().__init__()
        layout = QHBoxLayout(self)

        label = QLabel(text, self)
        label.setWordWrap(True)
        label.setStyleSheet("font-weight: bold; font-size: 16px;")
        font_metrics = QFontMetrics(label.font())
        text_width = font_metrics.horizontalAdvance(text)
        max_width = 400
        bubble_width = min(text_width + 50, max_width)
        label.setFixedWidth(bubble_width)

        if is_user:
            self.setStyleSheet("QFrame { background-color: #2c2c2c; color: white; border-radius: 10px; padding: 10px; }")
            layout.setAlignment(Qt.AlignRight)
        else:
            self.setStyleSheet("QFrame { background-color: #e0e0e0; color: black; border-radius: 10px; padding: 10px; }")
            layout.setAlignment(Qt.AlignLeft)

        layout.addWidget(label)
        self.setMinimumWidth(bubble_width + 20)
        self.setMinimumHeight(label.sizeHint().height() + 20)


class LoginPage(StyledWidget):
    def __init__(self, stacked_widget, users):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.users = users
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel("登录到系统")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("用户名")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("登录", self)
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.register_button = QPushButton("注册新账户", self)
        self.register_button.clicked.connect(self.go_to_register)
        layout.addWidget(self.register_button)

        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username in self.users and self.users[username] == password:
            QMessageBox.information(self, "成功", "登录成功！")
            self.stacked_widget.username = username
            self.stacked_widget.setCurrentIndex(2)
        else:
            QMessageBox.warning(self, "失败", "用户名或密码错误！")

    def go_to_register(self):
        self.stacked_widget.setCurrentIndex(1)


class RegisterPage(StyledWidget):
    def __init__(self, stacked_widget, users):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.users = users
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("用户名")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.register_button = QPushButton("注册", self)
        self.register_button.clicked.connect(self.handle_register)
        layout.addWidget(self.register_button)

        self.back_button = QPushButton("返回登录", self)
        self.back_button.clicked.connect(self.handle_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def handle_register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username in self.users:
            QMessageBox.warning(self, "注册失败", "用户名已存在！")
        else:
            self.users[username] = password
            save_users(self.users)
            QMessageBox.information(self, "注册成功", f"欢迎加入, {username}!")
            self.stacked_widget.setCurrentIndex(0)

    def handle_back(self):
        self.stacked_widget.setCurrentIndex(0)

class MainPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 滚动区域显示聊天记录
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.chat_layout = QVBoxLayout(self.scroll_content)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_content.setLayout(self.chat_layout)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area, stretch=1)

        # 输入区域
        bottom_layout = QHBoxLayout()

        self.input = QTextEdit(self)
        self.input.setPlaceholderText("请输入消息...")
        self.input.setFixedHeight(50)
        bottom_layout.addWidget(self.input)

        # 发送按钮
        self.send_button = QPushButton("发送", self)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #8B8989;  
                color: white; 
                border-radius: 12px; 
                padding: 10px; 
            }
            QPushButton:hover {
                background-color:#696969;  
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.send_button)

        # 上传按钮
        self.upload_button = QPushButton("上传文件", self)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #8B8989;  
                color: white; 
                border-radius: 12px; 
                padding: 10px; 
            }
            QPushButton:hover {
                background-color:#696969; 
            }
        """)
        self.upload_button.clicked.connect(self.upload_file)
        bottom_layout.addWidget(self.upload_button)

        layout.addLayout(bottom_layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.setLayout(layout)

    def add_message(self, text, is_user):
        bubble = ChatBubble(text, is_user)
        self.chat_layout.addWidget(bubble)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def send_message(self):
        user_message = self.input.toPlainText().strip()
        if not user_message:
            return

        self.add_message(user_message, is_user=True)
        self.input.clear()

        username = self.stacked_widget.username
        messages = load_chat_history(username)
        messages.append({"role": "user", "content": user_message})
        ai_reply = get_gpt_response(user_message, messages)
        messages.append({"role": "assistant", "content": ai_reply})
        save_chat_history(username, messages)

        self.add_message(ai_reply, is_user=False)

    def upload_file(self):
        """
        上传文件并调用 AI 处理
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "文本文件 (*.txt);;PDF 文件 (*.pdf);;Word 文件 (*.docx)",
            options=options,
        )

        if not file_path:
            return  # 用户取消操作

        try:
            # 读取文件内容
            content = read_file_content(file_path)
            if content.startswith("文件读取错误") or content == "不支持的文件类型":
                QMessageBox.warning(self, "错误", content)
                return

            # 在聊天记录中显示文件内容（截断预览）
            self.add_message(f"文件内容预览:\n{content[:500]}...\n(预览最多 500 字)", is_user=True)

            # 调用 GPT API 分析文件内容
            ai_reply = get_gpt_response(f"请分析以下文件内容:\n{content[:1000]}", [])
            self.add_message(f"AI 分析结果:\n{ai_reply}", is_user=False)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法读取文件: {str(e)}")


class ChatBubble(QFrame):
    def __init__(self, text, is_user):
        super().__init__()
        layout = QHBoxLayout(self)

        label = QLabel(text, self)
        label.setWordWrap(True)
        font_metrics = QFontMetrics(label.font())
        text_width = font_metrics.horizontalAdvance(text)
        max_width = 400
        bubble_width = min(text_width + 50, max_width)
        label.setFixedWidth(bubble_width)

        if is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2c2c2c;
                    color: white;
                    border-radius: 15px;
                    padding: 15px;
                }
            """)
            layout.setAlignment(Qt.AlignRight)
        else:
            self.setStyleSheet(""" 
                QFrame {
                    background-color: #e0e0e0;
                    color: black;
                    border-radius: 15px;
                    padding: 15px;
                }
                """
                )
            layout.setAlignment(Qt.AlignLeft)

        layout.addWidget(label)
        self.setMinimumWidth(bubble_width + 20)
        self.setMinimumHeight(label.sizeHint().height() + 20)


class App(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.username = None

        users = load_users()
        self.stacked_widget.addWidget(LoginPage(self.stacked_widget, users))
        self.stacked_widget.addWidget(RegisterPage(self.stacked_widget, users))
        self.stacked_widget.addWidget(MainPage(self.stacked_widget))
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.show()
        self.stacked_widget.resize(800, 600)


if __name__ == "__main__":
    import sys
    app = App(sys.argv)
    sys.exit(app.exec_())
