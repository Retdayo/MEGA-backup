# MEGA-backup
MEGAにpythonでバックアップするコードです

# 使い方
1,`git clone https://github.com/Retdayo/MEGA-backup.git`
2,以下のところを自分の情報に変更
```py
# MEGAのアカウント情報
email = 'MEGAアカウントのメアド'
password = "MEGAアカウントのパスワード"

# 圧縮するファイルやフォルダのパス
favorite_filename = "バックアップしたファイルの名前"
input_path = 'バックアップするフォルダーのパス'
output_dir = 'バックアップしたファイルを一時的に置くフォルダーのパス'
output_file = f"{output_dir}{favorite_filename}.7z"
metadata_file = f"{output_dir}backup_metadata.json"  # メタデータを保存するファイル
```
3,`pip install mega.py`
4,`python app.py`
