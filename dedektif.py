import sys
import asyncio
import aiohttp
import ssl
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLineEdit, QLabel, QFileDialog, QGroupBox, QTextBrowser, QDesktopWidget, QProgressBar,
                             QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QTextCursor, QIcon, QPixmap



class DedektifUygulama(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dedektif")
        self.setWindowIcon(QIcon('icon.ico'))
        self.initUI()
    def initUI(self):
        main_layout = QVBoxLayout()

        user_input_group = QGroupBox("Kullanıcı Adı Ara (Virgülle ayırarak birden fazla arayabilirisiniz.")
        user_input_group.setStyleSheet("""
        QGroupBox {
        border: 2px solid #8f8f91;
        border-radius: 10px;
        margin-top: 20px;
        padding: 10px;
        background-color: #f9f9f9;
        }
        QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 10px;
        font-size: 14pt;
        font-weight: bold;
        color: #333;
        }
        """)
        user_input_layout = QVBoxLayout()
        self.label = QLabel("Kullanıcı Adı Girin:")
        self.label.setFont(QFont('Arial',12,QFont.Bold))
        self.label.setStyleSheet("color: #333;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(
            "Kullanıcı adlarını virgülle ayırarak girin (örnek: kullanıcı1, kullanıcı2)"
        )
        self.username_input.setFont(QFont('Arial',11))
        self.username_input.returnPressed.connect(self.search_username)
        self.username_input.setStyleSheet("""
        background-color: #fff;
        border: 2px solid #ccc;
        padding: 10px;
        border-radius: 8px;
        color: #333;
        """)

        user_input_layout.addWidget(self.label)
        user_input_layout.addWidget(self.username_input)
        user_input_group.setLayout(user_input_layout)

        category_layout = QHBoxLayout()

        self.category_label = QLabel("Kategori Seçimi:")
        self.category_label.setFont(QFont('Arial',12,QFont.Bold))
        self.category_label.setStyleSheet("color: #333;")

        self.category_selector = QComboBox()
        self.category_selector.addItems([
            "Hepsi","Sosyal Medya", "Forumlar", "Video Platformları"
        ])
        self.category_selector.setFont(QFont('Arial',12))
        self.category_selector.setStyleSheet("""
        background-color: #fff;
        border: 2px solid #ccc;
        padding: 5px;
        border-radius: 8px;
        color: #333;
        """)

        category_layout.addWidget(self.category_label)
        category_layout.addWidget(self.category_selector)

        button_layout = QHBoxLayout()

        self.search_button = QPushButton("Ara")
        self.search_button.setFont(QFont('Arial',12))
        self.search_button.clicked.connect(self.search_username)
        self.search_button.setStyleSheet("""
        QPushButton{
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        }
        QPushButton:hover{
        background-color: #45a049;
        }
        """)
        #self.search_button.clicked.connect()

        self.save_button = QPushButton("Sonuçları Kaydet")
        self.save_button.setFont(QFont('Arial', 12))
        self.save_button.clicked.connect(self.save_results)
        self.save_button.setStyleSheet("""
        QPushButton{
        background-color: #008CBA;
        color: white;
        padding: 10px;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        }
        QPushButton:hover{
        background-color: #007bb5;
        }
        """)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.save_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
        QProgressBar{
        border: 2px solid #8f8f91;
        border-radius: 5px;
        background: #e0e0e0;
        }
        QProgressBar::chunk{
        background-color: #4CAF50;
        width:20px
        }
        """)

        self.result_area = QTextBrowser()
        self.result_area.setFont(QFont('Arial',11))
        self.result_area.setStyleSheet("""
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        border: 2px solid #ccc;
        color: #333;
        """)
        self.result_area.setOpenExternalLinks(True)
        self.result_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        main_layout.addWidget(user_input_group)
        main_layout.addLayout(category_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.result_area)


        self.setLayout(main_layout)
        self.setFixedSize(600,500)
        self.username_input.setFocus()
        self.results=[]
    def search_username(self):
        usernames = self.username_input.text().split(',')
        if not usernames[0]:
            QMessageBox.warning(self,"Hata","Lütfen en az bir kullanıcı adı girin.")
            return
        self.result_area.clear()
        self.results=[]
        self.progress_bar.setValue(0)

        selected_category = self.category_selector.currentText()

        for username in usernames:
            username = username.strip()
            if username:
                self.result_area.append(
                    f"'{username}' kullanıcısı aranıyor...\n"
                )
                asyncio.run(self.run_search(username, selected_category))
    async def run_search(self, username, category):
        sites = [
            {"name": "GitHub", "url": f"https://api.github.com/users/{username}", "api": True, "category": "Hepsi"},
            {"name": "Reddit", "url": f"https://www.reddit.com/user/{username}", "api": False, "category": "Forumlar"},
            {"name": "Instagram", "url": f"https://www.instagram.com/{username}/", "api": False,
             "category": "Sosyal Medya"},
            {"name": "Twitter", "url": f"https://twitter.com/{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "LinkedIn", "url": f"https://www.linkedin.com/in/{username}/", "api": False,
             "category": "Sosyal Medya"},
            {"name": "9GAG", "url": f"https://9gag.com/u/{username}", "api": False, "category": "Forumlar"},
            {"name": "1337x", "url": f"https://1337x.to/user/{username}/", "api": False, "category": "Forumlar"},
            {"name": "Twitch", "url": f"https://www.twitch.tv/{username}", "api": False,
             "category": "Video Platformları"},
            {"name": "Pinterest", "url": f"https://www.pinterest.com/{username}/", "api": False,
             "category": "Sosyal Medya"},
            {"name": "Discord", "url": f"https://discord.com/users/{username}", "api": False, "ssl_verify": False,
             "category": "Sosyal Medya"},
            {"name": "Facebook", "url": f"https://www.facebook.com/{username}", "api": False,
             "category": "Sosyal Medya"},
            {"name": "YouTube", "url": f"https://www.youtube.com/{username}", "api": False,
             "category": "Video Platformları"},
            {"name": "Tumblr", "url": f"https://{username}.tumblr.com/", "api": False, "category": "Sosyal Medya"},
            {"name": "Flickr", "url": f"https://www.flickr.com/people/{username}/", "api": False,
             "category": "Sosyal Medya"},
            {"name": "SoundCloud", "url": f"https://soundcloud.com/{username}", "api": False,
             "category": "Sosyal Medya"},
            {"name": "Steam", "url": f"https://steamcommunity.com/id/{username}", "api": False,
             "category": "Sosyal Medya"},
            {"name": "DeviantArt", "url": f"https://www.deviantart.com/{username}", "api": False, "ssl_verify": False,
             "category": "Forumlar"},
            {"name": "VK", "url": f"https://vk.com/{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "Medium", "url": f"https://medium.com/@{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "StackOverflow", "url": f"https://stackoverflow.com/users/{username}", "api": False,
             "category": "Forumlar"},
            {"name": "HackerNews", "url": f"https://news.ycombinator.com/user?id={username}", "api": False,
             "category": "Forumlar"},
            {"name": "Vimeo", "url": f"https://vimeo.com/{username}", "api": False, "category": "Video Platformları"},
            {"name": "TikTok", "url": f"https://www.tiktok.com/@{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "MyAnimeList", "url": f"https://myanimelist.net/profile/{username}", "api": False,
             "category": "Sosyal Medya"},
            {"name": "Dribbble", "url": f"https://dribbble.com/{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "Behance", "url": f"https://www.behance.net/{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "Foursquare", "url": f"https://foursquare.com/{username}", "api": False,
             "category": "Sosyal Medya"},
            {"name": "Dailymotion", "url": f"https://www.dailymotion.com/{username}", "api": False,
             "category": "Video Platformları"},
            {"name": "Slack", "url": f"https://{username}.slack.com", "api": False, "category": "Sosyal Medya"},
            {"name": "Unsplash", "url": f"https://unsplash.com/@{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "ProductHunt", "url": f"https://www.producthunt.com/@{username}", "api": False,
             "category": "Sosyal Medya"},
            {"name": "Telegram", "url": f"https://t.me/{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "Snapchat", "url": f"https://www.snapchat.com/add/{username}", "api": False,
             "category": "Sosyal Medya"},
            {"name": "Quora", "url": f"https://www.quora.com/profile/{username}", "api": False,
             "category": "Sosyal Medya"},
            {"name": "X", "url": f"https://x.com/{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "OK.ru", "url": f"https://ok.ru/{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "Weibo", "url": f"https://weibo.com/{username}", "api": False, "category": "Sosyal Medya"},
            {"name": "Douyin", "url": f"https://www.douyin.com/user/{username}", "api": False,
             "category": "Sosyal Medya"},
            {"name": "Baidu", "url": f"https://www.baidu.com/s?wd={username}", "api": False, "category": "Sosyal Medya"}
        ]

        if category !="Hepsi":
            sites = [site for site in sites if site['category'] == category]
        total_sites = len(sites)
        tasks = []
        async with aiohttp.ClientSession() as session:
            for index, site in enumerate(sites):
                if not site.get("ssl_verify",True):
                    ssl_context = ssl.create_default_context()
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE
                    tasks.append(self.search_website(username, site, session, ssl_context))
                else:
                    if site['api']:
                        tasks.append(self.search_api(username,site,session))
                    else:
                        tasks.append(self.search_website(username,site,session))
                progress = int(((index + 1)/total_sites)*100)
                self.progress_bar.setValue(progress)

            results = await asyncio.gather(*tasks)

        for result in results:
            self.result_area.append(result)
            self.result_area.moveCursor(QTextCursor.Start)
            self.results.append(result)
        QMessageBox.information(self,"Bilgi","Arama Tamamlandı!")
    async def search_api(self,username,site,session):
        try:
            async with session.get(site['url']) as response:
                if response.status ==200:
                    data = await response.json()
                    profile_url = data.get("html_url")
                    if profile_url:
                        return self.format_result(username,site['name'],profile_url,True)
                    else:
                        return self.format_result(username, site['name'], site['url'], True)
                else:
                    return self.format_result(username,site['name'],site['url'],False)
        except Exception as e:
            return f"{site['name']} üzerinde hata: {str(e)}"
    async def search_website(self,username, site, session, ssl_context=None):
        try:
            async with session.get(site["url"], ssl=ssl_context) as response:
                if response.status == 200:
                    return self.format_result(username, site["name"], site["url"], True)
                else:
                    return self.format_result(username, site["name"], site["url"], False)
        except Exception as e:
            return f'{site["name"]} üzerinde hata: {str(e)}'
    def format_result(self,username,site_name,url,found):
        if found:
            icon = "✔️"
            link = f'<a href="{url}" style="text-decoration:none; color:#4CAF50;">{username} {site_name} üzerinde bulundu {icon}</a>'
            return f'<div>{link}</div>'
        else:
            icon = "❌"
            return f'<div style="color:#f44336;">{username} {site_name} üzerinde bulunamadı {icon}'
    def save_results(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Sonuçları Kaydet","","Text Files (*.txt)",options=options)
        if filename:
            if filename.endswith('.txt'):
                with open(filename,'w',encoding='utf-8') as file:
                    file.write(self.result_area.toPlainText())
                    QMessageBox.information(self,"Bilgi","Kayıt Tamamlandı!")
if __name__ =='__main__':
    app = QApplication(sys.argv)
    dedektif = DedektifUygulama()
    dedektif.show()
    sys.exit(app.exec_())