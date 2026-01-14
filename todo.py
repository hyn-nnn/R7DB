import database as db

def show_menu():
    """メニューを表示"""
    print("\n=== TODOトラッカー ===")
    print("1. タスク登録")
    print("2. タスク一覧表示")
    print("3. 作業時間記録")
    print("4. タスク完了")
    print("5. タスク削除")
    print("6. 統計表示")
    print("0. 終了")

def add_task_menu():
    """タスク登録メニュー"""
    print("\n[タスク登録]")
    name = input("タスク名: ")
    description = input("詳細（任意）: ")
    due_date = input("期日（YYYY-MM-DD，任意）: ")
    categories_input = input("カテゴリ（カンマ区切り，任意）: ")
    
    # カテゴリをリストに変換
    categories = [c.strip() for c in categories_input.split(',')] if categories_input else []
    
    task_id = db.add_task(name, description, due_date, categories)
    print(f"タスクを登録しました（ID: {task_id}）")

def list_tasks_menu():
    """タスク一覧表示メニュー"""
    print("\n[タスク一覧]")
    show_all = input("完了済みも表示しますか？ (y/n): ").lower() == 'y'
    # カテゴリで絞る（空なら全表示）
    category_input = input("カテゴリで絞りますか？ カテゴリ名を入力（空で全表示）: ").strip()
    category = category_input if category_input else None
    # 並び替え方法を選択
    sort_choice = input("並び替え方法：1) ID順（デフォルト）2) 期限が近い順: ").strip()
    sort_by_due_date = sort_choice == '2'

    tasks = db.list_tasks(show_completed=show_all, category=category, sort_by_due_date=sort_by_due_date)
    if not tasks:
        print("タスクがありません")
        return
    
    for task in tasks:
        total_time = db.get_task_total_time(task['id'])
        categories = db.get_task_categories(task['id'])
        status = "完了" if task['completed'] else "未完了"
        due = task['due_date'] if task['due_date'] else "なし"
        cat_str = ", ".join(categories) if categories else "なし"
        print(f"[{task['id']}] {task['name']}（期日: {due}，カテゴリ: {cat_str}，累計: {total_time}分）{status}")

def record_time_menu():
    """作業時間記録メニュー"""
    print("\n[作業時間記録]")
    task_id = int(input("タスクID: "))
    minutes = int(input("作業時間（分）: "))
    
    db.record_time(task_id, minutes)
    print(f"{minutes}分を記録しました")

def complete_task_menu():
    """タスク完了メニュー"""
    print("\n[タスク完了]")
    task_id = int(input("完了するタスクのID: "))
    
    db.complete_task(task_id)
    print("タスクを完了にしました")

def delete_task_menu():
    """タスク削除メニュー"""
    print("\n[タスク削除]")
    task_id = int(input("削除するタスクのID: "))
    
    confirm = input(f"本当に削除しますか？ (y/n): ").lower()
    if confirm == 'y':
        db.delete_task(task_id)
        print("タスクを削除しました")

def show_stats_menu():
    """統計表示メニュー"""
    print("\n[統計]")
    
    # 日別累計
    print("\n日別累計時間:")
    daily_stats = db.get_daily_stats()
    if daily_stats:
        for stat in daily_stats:
            print(f"  {stat['date']}: {stat['total']}分")
    else:
        print("  記録がありません")
    
    # 完了率
    rate = db.get_completion_rate()
    print(f"\n完了率: {rate:.1f}%")
    
    # カテゴリ別累計（追加）
    print("\nカテゴリ別累計時間:")
    cat_stats = db.get_category_stats()
    if cat_stats:
        for stat in cat_stats:
            print(f"  {stat['name']}: {stat['total']}分")
    else:
        print("  記録がありません")

def main():
    """メインループ"""
    db.init_database()
    
    while True:
        show_menu()
        choice = input("\n選択してください: ")
        
        if choice == '1':
            add_task_menu()
        elif choice == '2':
            list_tasks_menu()
        elif choice == '3':
            record_time_menu()
        elif choice == '4':
            complete_task_menu()
        elif choice == '5':
            delete_task_menu()
        elif choice == '6':
            show_stats_menu()
        elif choice == '0':
            print("終了します")
            break
        else:
            print("無効な選択です")

if __name__ == '__main__':
    main()