import sqlite3
from datetime import datetime

DB_FILE = 'todo.db'

def get_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """テーブル作成（初回のみ）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # tasksテーブル
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # categoriesテーブル（新規）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # task_categoriesテーブル（中間テーブル，新規）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_categories (
            task_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            PRIMARY KEY (task_id, category_id),
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        )
    ''')
    
    # time_recordsテーブル
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS time_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            duration_minutes INTEGER NOT NULL,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def get_or_create_category(category_name):
    """カテゴリを取得または作成"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 既存のカテゴリを検索
    cursor.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
    result = cursor.fetchone()
    
    if result:
        category_id = result['id']
    else:
        # 新規作成
        cursor.execute('INSERT INTO categories (name) VALUES (?)', (category_name,))
        category_id = cursor.lastrowid
        conn.commit()
    
    conn.close()
    return category_id

def add_task(name, description='', due_date='', categories=None):
    """タスクを追加（categoriesはリスト）"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # タスク追加
    cursor.execute('''
        INSERT INTO tasks (name, description, due_date)
        VALUES (?, ?, ?)
    ''', (name, description, due_date))
    task_id = cursor.lastrowid
    
    # カテゴリの紐付け
    if categories:
        for cat_name in categories:
            if cat_name.strip():  # 空文字列は除外
                cat_id = get_or_create_category(cat_name.strip())
                cursor.execute('''
                    INSERT INTO task_categories (task_id, category_id)
                    VALUES (?, ?)
                ''', (task_id, cat_id))
    
    conn.commit()
    conn.close()
    return task_id

def get_task_categories(task_id):
    """タスクのカテゴリ一覧を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.name
        FROM categories c
        JOIN task_categories tc ON c.id = tc.category_id
        WHERE tc.task_id = ?
    ''', (task_id,))
    categories = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return categories

def list_tasks(show_completed=False):
    """タスク一覧を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if show_completed:
        cursor.execute('SELECT * FROM tasks ORDER BY id')
    else:
        cursor.execute('SELECT * FROM tasks WHERE completed = 0 ORDER BY id')
    
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_task_total_time(task_id):
    """タスクの累計時間を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(duration_minutes) as total
        FROM time_records
        WHERE task_id = ?
    ''', (task_id,))
    result = cursor.fetchone()
    conn.close()
    return result['total'] if result['total'] else 0

def record_time(task_id, minutes):
    """作業時間を記録"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO time_records (task_id, duration_minutes)
        VALUES (?, ?)
    ''', (task_id, minutes))
    conn.commit()
    conn.close()

def complete_task(task_id):
    """タスクを完了にする"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET completed = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def delete_task(task_id):
    """タスクを削除"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

def get_daily_stats():
    """日別累計時間を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(recorded_at) as date, SUM(duration_minutes) as total
        FROM time_records
        GROUP BY DATE(recorded_at)
        ORDER BY date DESC
    ''')
    stats = cursor.fetchall()
    conn.close()
    return stats

def get_completion_rate():
    """完了率を計算"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM tasks')
    total = cursor.fetchone()['total']
    cursor.execute('SELECT COUNT(*) as completed FROM tasks WHERE completed = 1')
    completed = cursor.fetchone()['completed']
    conn.close()
    
    if total == 0:
        return 0.0
    return (completed / total) * 100

def get_category_stats():
    """カテゴリ別の累計時間を取得（追加機能）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.name, SUM(tr.duration_minutes) as total
        FROM categories c
        JOIN task_categories tc ON c.id = tc.category_id
        JOIN time_records tr ON tc.task_id = tr.task_id
        GROUP BY c.id
        ORDER BY total DESC
    ''')
    stats = cursor.fetchall()
    conn.close()
    return stats