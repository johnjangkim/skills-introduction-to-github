import sys
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty
from kivy.clock import mainthread

from bible_search import load_verses, search_verses, semantic_search_verses, init_db
import sqlite3

KV = """
#:import os os

<Label>:
    font_name: app.font_path if app.font_path else self.font_name
<TextInput>:
    font_name: app.font_path if app.font_path else self.font_name

ScreenManager:
    SearchScreen:
    AddScreen:
    AllScreen:

<SearchScreen>:
    name: 'search'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            TextInput:
                id: keyword_input
                hint_text: '검색어를 입력하세요'
                text: root.keyword
            Spinner:
                id: search_type
                text: root.search_type
                values: ['keyword', 'semantic']
            Button:
                text: '검색'
                on_release: root.on_search(keyword_input.text, search_type.text)
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            Button:
                text: '구절 추가'
                on_release: app.root.current = 'add'
            Button:
                text: '모든 구절'
                on_release: root.load_all(); app.root.current = 'all'
        Label:
            size_hint_y: None
            height: '30dp'
            text: root.message
            color: (1,0,0,1)
        RecycleView:
            viewclass: 'ResultItem'
            data: root.rv_data
            RecycleBoxLayout:
                default_size: None, dp(60)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'

<ResultItem@BoxLayout>:
    orientation: 'vertical'
    padding: 6
    spacing: 4
    reference: ''
    content: ''
    search_type: ''
    keyword: ''
    BoxLayout:
        size_hint_y: None
        height: '24dp'
        Label:
            text: root.reference
            bold: True
            halign: 'left'
            text_size: self.size
    Label:
        text: root.content
        halign: 'left'
        valign: 'top'
        text_size: self.size
    BoxLayout:
        size_hint_y: None
        height: '32dp'
        Widget:
        Button:
            size_hint_x: None
            width: '110dp'
            text: '추가 등록'
            opacity: 1 if root.search_type=='semantic' else 0
            disabled: False if root.search_type=='semantic' else True
            on_release: app.add_verse_from_result(root.reference, root.content, root.search_type, root.keyword)

<AddScreen>:
    name: 'add'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        TextInput:
            id: ref_input
            hint_text: '참조 (예: 요한복음 3:16)'
        TextInput:
            id: cont_input
            hint_text: '내용'
            multiline: True
            height: '140dp'
            size_hint_y: None
        Label:
            id: add_msg
            size_hint_y: None
            height: '30dp'
            color: (1,0,0,1)
            text: ''
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            Button:
                text: '추가'
                on_release: app.add_verse(ref_input.text, cont_input.text)
            Button:
                text: '뒤로'
                on_release: app.root.current = 'search'

<AllScreen>:
    name: 'all'
    BoxLayout:
        orientation: 'vertical'
        padding: 10
        spacing: 10
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            Button:
                text: '뒤로'
                on_release: app.root.current = 'search'
            Button:
                text: '새로고침'
                on_release: root.load_all()
        RecycleView:
            id: all_rv
            viewclass: 'ResultItem'
            data: []
            RecycleBoxLayout:
                default_size: None, dp(60)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
"""

class SearchScreen(Screen):
    keyword = StringProperty('')
    search_type = StringProperty('keyword')
    message = StringProperty('')
    rv_data = ListProperty([])

    def on_pre_enter(self):
        init_db()

    @mainthread
    def on_search(self, keyword: str, search_type: str):
        self.keyword = (keyword or '').strip()
        self.search_type = search_type or 'keyword'
        if not self.keyword:
            self.message = '검색어를 입력하세요.'
            self.rv_data = []
            return
        verses = load_verses()
        if self.search_type == 'keyword':
            results = search_verses(verses, self.keyword)
        else:
            results = semantic_search_verses(verses, self.keyword)
        self.message = '' if results else '검색 결과가 없습니다.'
        self.rv_data = [{
            'reference': r.get('reference', ''),
            'content': r.get('content', ''),
            'search_type': self.search_type,
            'keyword': self.keyword,
        } for r in results]

    def load_all(self):
        self.manager.get_screen('all').load_all()

class AddScreen(Screen):
    pass

class AllScreen(Screen):
    def load_all(self):
        verses = load_verses()
        data = [{
            'reference': v.get('reference', ''),
            'content': v.get('content', ''),
            'search_type': 'keyword',
            'keyword': '',
        } for v in verses]
        self.ids.all_rv.data = data

class BibleSearchApp(App):
    font_path = StringProperty('')

    def _detect_korean_font(self) -> str:
        candidates = [
            # Windows
            r"C:/Windows/Fonts/malgun.ttf",
            r"C:/Windows/Fonts/malgunbd.ttf",
            r"C:/Windows/Fonts/NanumGothic.ttf",
            r"C:/Windows/Fonts/NGULIM.TTF",
            # macOS
            r"/System/Library/Fonts/AppleSDGothicNeo.ttc",
            r"/System/Library/Fonts/Supplemental/AppleGothic.ttf",
            # Linux (Ubuntu with Noto)
            r"/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            r"/usr/share/fonts/truetype/noto/NotoSansKR-Regular.otf",
            r"/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        return ''

    def build(self):
        init_db()
        self.font_path = self._detect_korean_font()
        return Builder.load_string(KV)

    @mainthread
    def add_verse(self, reference: str, content: str):
        reference = (reference or '').strip()
        content = (content or '').strip()
        add_msg = self.root.get_screen('add').ids.add_msg
        if not reference or not content:
            add_msg.text = '참조와 내용을 모두 입력하세요.'
            return
        try:
            with sqlite3.connect('bible_verses.db', timeout=10) as conn:
                c = conn.cursor()
                c.execute('INSERT INTO bible_verses (reference, content) VALUES (?, ?)', (reference, content))
                conn.commit()
            add_msg.color = (0,0.6,0,1)
            add_msg.text = f'추가 완료: {reference}'
        except sqlite3.IntegrityError:
            add_msg.color = (0.8,0.4,0,1)
            add_msg.text = f'[중복] 이미 존재: {reference}'

    def add_verse_from_result(self, reference: str, content: str, search_type: str, keyword: str):
        try:
            with sqlite3.connect('bible_verses.db', timeout=10) as conn:
                c = conn.cursor()
                c.execute('INSERT INTO bible_verses (reference, content) VALUES (?, ?)', (reference, content))
                conn.commit()
            screen = self.root.get_screen('search')
            screen.message = f'추가 완료: {reference}'
        except sqlite3.IntegrityError:
            screen = self.root.get_screen('search')
            screen.message = f'[중복] 이미 존재: {reference}'

if __name__ == '__main__':
    BibleSearchApp().run()