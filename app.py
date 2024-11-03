import py7zr
from mega import Mega
import time
import os
import uuid
import json
from datetime import datetime, timedelta, timezone

# MEGAのアカウント情報
email = 'MEGAアカウントのメアド'
password = "MEGAアカウントのパスワード"

# 圧縮するファイルやフォルダのパス
favorite_filename = "バックアップしたファイルの名前"
input_path = 'バックアップするフォルダーのパス'
output_dir = 'バックアップしたファイルを一時的に置くフォルダーのパス'
output_file = f"{output_dir}{favorite_filename}.7z"
metadata_file = f"{output_dir}backup_metadata.json"  # メタデータを保存するファイル

# 日本時間 (JST) のタイムゾーン
JST = timezone(timedelta(hours=9))

# MEGAにログイン
mega = Mega()
m = mega.login(email, password)

# メタデータの初期化
metadata = []

while True:
    try:
        # 1. 一意のIDを生成し、現在の時刻をJSTで取得
        backup_id = str(uuid.uuid4())  # UUIDを生成してIDに
        upload_time = datetime.now(JST).isoformat()  # JSTでISO形式の日時を取得

        # 2. ファイルを圧縮
        with py7zr.SevenZipFile(output_file, 'w') as archive:
            archive.writeall(input_path, arcname='')
        print(f"{output_file} に圧縮完了")

        # 3. 圧縮ファイルをMEGAにアップロード
        upload_result = m.upload(output_file)

        # アップロード結果のデバッグ
        print(f"アップロード結果: {upload_result}")

        if upload_result and 'f' in upload_result and len(upload_result['f']) > 0:
            mega_file_id = upload_result['f'][0]['h']  # ファイルIDを取得
            print(f"{output_file} をMEGAにアップロードしました。")
            os.remove(output_file)  # 圧縮した7zファイルを削除
            print(f"{output_file} をサーバーから削除しました。")

            # 4. JSONファイルにメタデータを保存
            # 新しいメタデータエントリを作成
            metadata_entry = {
                "id": backup_id,
                "file_name": "{favorite_filename}.7z",
                "upload_time": upload_time,
                "mega_file_id": mega_file_id
            }

            # 既存のメタデータを読み込み、追記
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    try:
                        # JSONの内容がリストであることを確認
                        metadata = json.load(f)
                        if not isinstance(metadata, list):
                            raise ValueError("メタデータはリストである必要があります。")
                    except json.JSONDecodeError:
                        print(f"エラー: {metadata_file} の読み込みに失敗しました。空のリストを使用します。")
                        metadata = []  # 空のリストに初期化
            else:
                metadata = []  # メタデータファイルが存在しない場合は空のリスト

            metadata.append(metadata_entry)

            # メタデータをJSONファイルに書き込み
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=4)
            print(f"メタデータを {metadata_file} に保存しました。")
        else:
            print("エラー: アップロード結果にファイルIDが含まれていません。")

        # 5. JSON内のメタデータを確認し、11時間以上前のファイルを削除
        current_time = datetime.now(JST)  # 現在のJST時刻

        # メタデータを再ロード（アップロードの際に変更される可能性があるため）
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

        to_keep = []  # 削除対象外のメタデータ

        print(f"現在の時刻: {current_time.isoformat()}")

        for entry in metadata:
            entry_time = datetime.fromisoformat(entry["upload_time"])  # メタデータのアップロード時刻
            print(f"ファイル: {entry['file_name']}, アップロード時刻: {entry_time.isoformat()}")

            if (current_time - entry_time) >= timedelta(hours=11):
                try:
                    # MEGAから11時間以上経過したファイルを削除
                    m.delete(entry["mega_file_id"])
                    print(f"ファイル {entry['file_name']} (ID: {entry['id']}) をMEGAから削除しました。")
                except Exception as e:
                    print(f"ファイル {entry['id']} の削除に失敗しました: {e}")
            else:
                # 11時間以内のファイルは削除対象外リストに追加
                to_keep.append(entry)

        # 6. 削除対象外のエントリのみを保持したJSONを保存
        with open(metadata_file, 'w') as f:
            json.dump(to_keep, f, indent=4)
        print("メタデータファイルを更新しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    # 3時間待機（3時間 = 10800秒）
    time.sleep(10800)
