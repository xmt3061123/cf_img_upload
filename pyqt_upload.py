# -*- coding: GBK -*-
import sys
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QFileDialog, QLabel, QTextEdit, QMessageBox, QLineEdit)
from PyQt5.QtGui import QFont
import webbrowser
import time
from urllib.parse import urlparse  # 添加这行导入语句
class UploadApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.layout = QVBoxLayout()
        
        self.label = QLabel("选择并上传图片", self)
        self.label.setFont(QFont('Arial', 16))
        self.layout.addWidget(self.label)
        
        # 添加域名输入框
        self.domain_label = QLabel("上传域名:", self)
        self.domain_label.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.domain_label)
        
        self.domain_input = QLineEdit(self)
        self.domain_input.setFont(QFont('Arial', 12))
        self.domain_input.setText("https://example.xyz")  # 设置默认域名
        self.layout.addWidget(self.domain_input)
        
        self.btn = QPushButton('选择图片并上传', self)
        self.btn.setFont(QFont('Arial', 14))
        self.btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        self.btn.clicked.connect(self.select_and_upload_file)
        self.layout.addWidget(self.btn)
        
        self.responseText = QTextEdit(self)
        self.responseText.setFont(QFont('Arial', 12))
        self.responseText.setReadOnly(True)
        self.layout.addWidget(self.responseText)
        
        self.setLayout(self.layout)
        
        self.setWindowTitle('图片上传')
        self.setGeometry(300, 300, 400, 300)
        self.setStyleSheet("background-color: #f0f0f0;")

    def select_and_upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择要上传的图片", "", "Image Files (*.jpg *.jpeg *.png)")
        if file_path:
            self.upload_file(file_path)
    
    def upload_file(self, file_path):
        base_domain = self.domain_input.text().rstrip('/')
        url = f"{base_domain}/upload"
        base_url = f"{base_domain}/file/"
        
        # 更可靠的 headers 设置
        parsed_url = urlparse(base_domain)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Host': parsed_url.netloc,
            'Origin': f"{parsed_url.scheme}://{parsed_url.netloc}",
            'Referer': base_domain,
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        
        max_retries = 3
        retry_delay = 5  # 秒

        for attempt in range(max_retries):
            try:
                with open(file_path, 'rb') as f:
                    file_name = file_path.split('/')[-1]
                    files = {'file': (file_name, f, self.get_content_type(file_name))}
                    response = requests.post(url, headers=headers, files=files, timeout=30)
                    
                    response.raise_for_status()  # 检查HTTP错误
                    
                    response_json = response.json()
                    if isinstance(response_json, list) and 'src' in response_json[0]:
                        file_relative_path = response_json[0]['src']
                        complete_url = base_url + file_relative_path.split('/file/')[-1]
                        self.responseText.append("上传成功!")
                        self.responseText.append(f"图片链接: {complete_url}")
                        webbrowser.open(complete_url)
                        return  # 成功上传，退出函数
                    else:
                        raise ValueError("响应中没有找到预期的 'src' 字段")
                
            except FileNotFoundError:
                QMessageBox.critical(self, "错误", f"文件未找到: {file_path}")
                return
            
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    self.responseText.append(f"上传失败（尝试 {attempt+1}/{max_retries}）: {str(e)}")
                    self.responseText.append(f"将在 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    QMessageBox.critical(self, "错误", f"上传失败，已达到最大重试次数: {str(e)}")
            
            except ValueError as e:
                self.responseText.append(f"上传失败: {str(e)}")
                return
        
        self.responseText.append("上传失败: 达到最大重试次数")

    def get_content_type(self, filename):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return f'image/{filename.split(".")[-1].lower()}'
        else:
            return 'application/octet-stream'

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = UploadApp()
    ex.show()
    sys.exit(app.exec_())