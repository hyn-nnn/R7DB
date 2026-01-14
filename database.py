import sqlite3
from datetime import datetime

DB_FILE = 'todo.db'

def get_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 列名でアクセス可能にする
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
            category TEXT,
            completed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
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

def add_task(name, description='', due_date='', category=''):
    """タスクを追加"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (name, description, due_date, category)
        VALUES (?, ?, ?, ?)
    ''', (name, description, due_date, category))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

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