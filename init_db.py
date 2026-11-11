"""データベースを作成する： python init_db.py"""
from app import create_app
import db

app = create_app()
with app.app_context():
    db.init_db()
print("データベースを作成しました。ログインID: admin / パスワード: admin1234（開発用）")
