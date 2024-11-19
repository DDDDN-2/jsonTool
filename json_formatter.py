import sys
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, 
                           QPushButton, QVBoxLayout, QWidget, QSystemTrayIcon, QMenu)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import winreg
import os
import keyboard
import threading
import signal  # 添加 signal 模块
import psutil   # 添加 psutil 模块

class JsonFormatter(QMainWindow):
    def __init__(self):
        super().__init__()
        # 确保在初始化时先设置托盘
        self.setupSystemTray()
        self.initUI()
        # self.create_tray_menu()  # 已经在 setupSystemTray 中调用
        self.setup_hotkey()
        # 记录当前进程ID
        self.pid = os.getpid()
        # 添加启动提示
        self.tray_icon.showMessage(
            "JSON格式化工具",
            "程序已启动，按Ctrl+3可快速打开窗口",
            QSystemTrayIcon.Information,
            2000
        )
        
    def initUI(self):
        # 主窗口设置
        self.setWindowTitle('JSON格式化工具')
        self.setGeometry(300, 300, 500, 400)
        
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建输入文本框
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText('在此输入JSON文本...')
        layout.addWidget(self.input_text)
        
        # 创建输出文本框
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)
        
        # 创建格式化按钮
        format_button = QPushButton('格式化')
        # 设置按钮样式
        format_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        format_button.clicked.connect(self.format_json)
        layout.addWidget(format_button)
        
        # 设置按钮的固定宽度（可选）
        format_button.setFixedWidth(200)
        # 让按钮居中
        layout.setAlignment(format_button, Qt.AlignHCenter)
    
    def setupSystemTray(self):
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 确保图标文件存在并正确加载
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if os.path.exists(icon_path):
            self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
        else:
            # 如果找不到图标文件，创建一个
            from create_icon import create_json_icon
            create_json_icon()
            self.tray_icon = QSystemTrayIcon(QIcon('icon.png'), self)
        
        # 设置托盘图标属性
        self.tray_icon.setToolTip('JSON格式化工具')
        
        # 确保托盘图标可见
        self.tray_icon.show()  # 使用 show() 替代 setVisible(True)
        
        # 连接托盘图标的信号
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # 创建并设置托盘菜单
        self.create_tray_menu()
    
    def format_json(self):
        try:
            # 获取输入文本
            input_text = self.input_text.toPlainText()
            # 解析JSON
            parsed = json.loads(input_text)
            # 格式化JSON
            formatted = json.dumps(parsed, indent=4, ensure_ascii=False)
            # 显示格式化结果
            self.output_text.setText(formatted)
        except json.JSONDecodeError as e:
            self.output_text.setText(f'JSON格式错误: {str(e)}')
            
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            # 双击显示/隐藏窗口
            if self.isVisible():
                self.hide()
            else:
                self.show_window()
    
    def closeEvent(self, event):
        # 点击关闭按钮时最小化到托盘
        if self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            # 确保托盘图标显示
            self.tray_icon.show()
            self.tray_icon.showMessage(
                "JSON格式化工具",
                "程序已最小化到系统托盘\n右键点击托盘图标可以彻底退出程序",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            event.accept()
    
    def create_tray_menu(self):
        # 创建托盘菜单
        self.tray_menu = QMenu()
        
        # 添加显示/隐藏选项
        show_action = self.tray_menu.addAction('显示窗口')
        show_action.triggered.connect(self.show_window)
        
        # 添加分隔线
        self.tray_menu.addSeparator()
        
        # 添加开机启动选项
        self.startup_action = self.tray_menu.addAction('开机启动')
        self.startup_action.setCheckable(True)
        self.startup_action.setChecked(self.check_startup())
        self.startup_action.triggered.connect(self.toggle_startup)
        
        # 添加分隔线
        self.tray_menu.addSeparator()
        
        # 添加退出选项
        quit_action = self.tray_menu.addAction('彻底退出')
        quit_action.triggered.connect(self.quit_application)
        
        # 设置托盘图标的菜单
        self.tray_icon.setContextMenu(self.tray_menu)
    
    def check_startup(self):
        # 检查是否已设置开机启动
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            winreg.QueryValueEx(key, "JSON格式化工具")
            return True
        except WindowsError:
            return False
    
    def toggle_startup(self):
        # 切换开机启动状态
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        if self.startup_action.isChecked():
            # 添加开机启动
            winreg.SetValueEx(
                key,
                "JSON格式化工具",
                0,
                winreg.REG_SZ,
                sys.executable
            )
        else:
            # 移除开机启动
            try:
                winreg.DeleteValue(key, "JSON格式化工具")
            except WindowsError:
                pass
    
    def setup_hotkey(self):
        # 在新线程中监听快捷键
        def hotkey_thread():
            keyboard.add_hotkey('ctrl+3', self.show_window)
            keyboard.wait()
        
        # 启动快捷键监听线程
        thread = threading.Thread(target=hotkey_thread, daemon=True)
        thread.start()
    
    def show_window(self):
        # 显示并激活窗口
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
    
    def quit_application(self):
        # 彻底退出应用
        try:
            # 移除托盘图标
            self.tray_icon.setVisible(False)
            
            # 停止键盘监听
            keyboard.unhook_all()
            
            # 结束当前进程及其子进程
            current_process = psutil.Process(self.pid)
            children = current_process.children(recursive=True)
            
            # 结束子进程
            for child in children:
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            
            # 结束主进程
            QApplication.quit()
            
            # 确保进程被终止
            if sys.platform.startswith('win'):
                os.kill(self.pid, signal.SIGTERM)
            else:
                os.kill(self.pid, signal.SIGKILL)
                
        except Exception as e:
            print(f"退出时发生错误: {str(e)}")
            # 强制退出
            os._exit(0)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    json_formatter = JsonFormatter()
    json_formatter.show()
    sys.exit(app.exec_()) 