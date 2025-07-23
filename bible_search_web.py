from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from bible_search import load_verses, search_verses, semantic_search_verses, init_db
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'biblesearch_secret_key'

# Initialize DB
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    verses = load_verses()
    results = []
    search_type = 'keyword'
    keyword = ''
    if request.method == 'POST':
        search_type = request.form.get('search_type', 'keyword')
        keyword = request.form.get('keyword', '').strip()
        if keyword:
            if search_type == 'keyword':
                results = search_verses(verses, keyword)
            else:
                results = semantic_search_verses(verses, keyword)
    return render_template('bible_search_index.html', results=results, keyword=keyword, search_type=search_type)

@app.route('/add', methods=['POST'])
def add():
    reference = request.form.get('reference', '').strip()
    content = request.form.get('content', '').strip()
    # For semantic search result add, preserve search context
    search_type = request.form.get('search_type')
    keyword = request.form.get('keyword')
    from_semantic = request.form.get('from_semantic')
    if not reference or not content:
        flash('참조와 내용을 모두 입력하세요.', 'danger')
        if from_semantic:
            # Re-render index with previous context
            verses = load_verses()
            results = []
            if search_type and keyword:
                if search_type == 'keyword':
                    results = search_verses(verses, keyword)
                else:
                    results = semantic_search_verses(verses, keyword)
            return render_template('bible_search_index.html', results=results, keyword=keyword or '', search_type=search_type or 'keyword')
        return redirect(url_for('index'))
    try:
        with sqlite3.connect('bible_verses.db', timeout=10) as conn:
            c = conn.cursor()
            c.execute('INSERT INTO bible_verses (reference, content) VALUES (?, ?)', (reference, content))
            conn.commit()
        flash(f'구절이 추가되었습니다: {reference}', 'success')
    except sqlite3.IntegrityError:
        flash(f'[중복] 이미 존재하는 구절: {reference}', 'warning')
        if from_semantic:
            verses = load_verses()
            results = []
            if search_type and keyword:
                if search_type == 'keyword':
                    results = search_verses(verses, keyword)
                else:
                    results = semantic_search_verses(verses, keyword)
            return render_template('bible_search_index.html', results=results, keyword=keyword or '', search_type=search_type or 'keyword')
    if from_semantic:
        verses = load_verses()
        results = []
        if search_type and keyword:
            if search_type == 'keyword':
                results = search_verses(verses, keyword)
            else:
                results = semantic_search_verses(verses, keyword)
        return render_template('bible_search_index.html', results=results, keyword=keyword or '', search_type=search_type or 'keyword')
    return redirect(url_for('index'))

@app.route('/all')
def show_all():
    verses = load_verses()
    return render_template('bible_search_all.html', verses=verses)

@app.route('/edit/<reference>', methods=['GET', 'POST'])
def edit_verse(reference):
    if request.method == 'POST':
        new_content = request.form.get('content', '').strip()
        if not new_content:
            flash('내용을 입력하세요.', 'danger')
            return redirect(url_for('edit_verse', reference=reference))
        with sqlite3.connect('bible_verses.db', timeout=10) as conn:
            c = conn.cursor()
            c.execute('UPDATE bible_verses SET content = ? WHERE reference = ?', (new_content, reference))
            conn.commit()
        flash(f'{reference} 내용이 수정되었습니다.', 'success')
        return redirect(url_for('show_all'))
    with sqlite3.connect('bible_verses.db', timeout=10) as conn:
        c = conn.cursor()
        c.execute('SELECT reference, content FROM bible_verses WHERE reference = ?', (reference,))
        verse = c.fetchone()
    if not verse:
        flash('구절을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('show_all'))
    return render_template('bible_search_edit.html', verse={'reference': verse[0], 'content': verse[1]})

@app.route('/delete/<reference>', methods=['POST'])
def delete_verse(reference):
    with sqlite3.connect('bible_verses.db', timeout=10) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM bible_verses WHERE reference = ?', (reference,))
        conn.commit()
    flash(f'{reference} 구절이 삭제되었습니다.', 'success')
    return redirect(url_for('show_all'))

if __name__ == '__main__':
    app.run(debug=True) 