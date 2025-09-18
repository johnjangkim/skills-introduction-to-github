from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from add_verse_cli import add_verse, search_verses, crawl_biblegateway, BOOK_CHAPTERS

app = Flask(__name__)
app.secret_key = 'bibleverse_secret_key'

# 버전 목록
VERSIONS = [
    ("KLB", "우리말성경"),
    ("KRV", "개역한글"),
    ("KOR", "개역개정"),
    ("NIV", "NIV"),
    ("KJV", "KJV")
]

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    gw_results = []
    selected_version = VERSIONS[0][0]
    keyword = ''
    if request.method == 'POST':
        selected_version = request.form.get('version', VERSIONS[0][0])
        keyword = request.form.get('keyword', '').strip()
        if keyword:
            # 책 전체 자동 추가는 웹에서는 지원하지 않음(보안/성능상)
            parts = keyword.split(maxsplit=1)
            if len(parts) == 2 and parts[0] in BOOK_CHAPTERS:
                book, search_kw = parts
            else:
                book, search_kw = None, keyword
            results = search_verses(search_kw, book)
            gw_results = crawl_biblegateway(keyword, selected_version)
    return render_template('index.html', versions=VERSIONS, selected_version=selected_version, keyword=keyword, results=results, gw_results=gw_results)

@app.route('/add', methods=['POST'])
def add():
    reference = request.form.get('reference', '').strip()
    content = request.form.get('content', '').strip()
    if not reference or not content:
        flash('참조와 내용을 모두 입력하세요.', 'danger')
        return redirect(url_for('index'))
    if add_verse(reference, content):
        flash(f'구절이 추가되었습니다: {reference}', 'success')
    else:
        flash(f'[중복] 이미 존재하는 구절: {reference}', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 