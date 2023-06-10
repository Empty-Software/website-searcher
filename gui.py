import sys
import time
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QToolButton
from PyQt5.QtCore import Qt, QCoreApplication, QTimer
from PyQt5.QtGui import QFont, QDesktopServices

def search_and_send_results(search_engine, query, output_field, webhook_url):
    if search_engine == 'dosya.co':
        search_query = f'site:dosya.co {query}'
    else:
        output_field.append('Geçersiz seçim!')
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        sent_urls = []
        count = 0
        page = 1
        while True:
            response = requests.get(f'https://duckduckgo.com/html/?q={search_query}&p={page}', headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.find_all('a', class_='result__url')

            if search_results:
                for result in search_results:
                    result_url = result['href']

                    if search_engine == 'dosya.co' and 'dosya.co' in result_url or result_url not in sent_urls:
                        message = f'{result_url}'
                        output_field.append(message)

                        payload = {
                            'content': message
                        }

                        try:
                            webhook_response = requests.post(webhook_url, json=payload)
                            webhook_response.raise_for_status()
                            sent_urls.append(result_url)
                            count += 1
                            output_field.append(' ')
                            time.sleep(3)
                        except requests.exceptions.RequestException as e:
                            output_field.append(f'Hata: Webhooka mesaj gönderilemedi: {str(e)}')

                page += 1
            else:
                break

        if count == 0:
            output_field.append('Belirtilen arama motorunda dosya ile ilgili sonuç bulunamadı.')
    except requests.exceptions.RequestException as e:
        output_field.append(f'Hata: Arama yapılamadı: {str(e)}')


class DiscordSearch(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Empty Software")
        self.setGeometry(200, 200, 400, 400)

        self.layout = QVBoxLayout()

        self.title_label = QLabel("<b><font size=4>Dosya.co Discord Search</font></b>\n\n")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)



        self.search_engine_label = QLabel("\nArama Motorunu Seçin: (dosya.co) Yazın!")
        self.layout.addWidget(self.search_engine_label)

        self.search_engine_input = QLineEdit()
        self.layout.addWidget(self.search_engine_input)

        self.query_label = QLabel("Aranacak Kelime:")
        self.layout.addWidget(self.query_label)

        self.query_input = QLineEdit()
        self.layout.addWidget(self.query_input)

        self.webhook_label = QLabel("Discord Webhook URL'si:")
        self.layout.addWidget(self.webhook_label)

        self.webhook_input = QLineEdit()
        self.layout.addWidget(self.webhook_input)

        self.search_button = QPushButton("Ara")
        self.search_button.clicked.connect(self.search_button_clicked)
        self.layout.addWidget(self.search_button)

        self.clear_button = QPushButton("Log'u Temizle")
        self.clear_button.clicked.connect(self.clear_button_clicked)
        self.layout.addWidget(self.clear_button)

        self.output_field = QTextEdit()
        self.layout.addWidget(self.output_field)

        self.setLayout(self.layout)

        self.add_bottom_text("Empty Software")

    def add_bottom_text(self, text):
        bottom_text = QLabel(text)
        bottom_text.setAlignment(Qt.AlignBottom | Qt.AlignLeft)
        bottom_text.setStyleSheet("color: black")
        bottom_text.setFont(QFont("Bold", 8))
        self.layout.addWidget(bottom_text)

    def search_button_clicked(self):
        search_engine = self.search_engine_input.text()
        query = self.query_input.text()
        webhook_url = self.webhook_input.text()
        QTimer.singleShot(0, lambda: search_and_send_results(search_engine, query, self.output_field, webhook_url))
        self.search_button.setEnabled(False)

    def enable_search_button(self):
        self.search_button.setEnabled(True)

    def clear_button_clicked(self):
        self.output_field.clear()

    def closeEvent(self, event):
        QCoreApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DiscordSearch()
    window.show()
    sys.exit(app.exec_())
