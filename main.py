import flet as ft
import sqlite3
import os
import shutil
import uuid

# データベースの初期化関数を定義
def init_db():
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            original_name TEXT,
            path TEXT
        )
    ''')
    conn.commit()
    conn.close()
# 画像保存関数
def save_image(file):
    if not os.path.exists('assets/img'):
        os.makedirs('assets/img')
    # 一意のファイル名を生成
    unique_filename = str(uuid.uuid4()) + os.path.splitext(file.name)[1]
    file_path = os.path.join('assets/img', unique_filename)
    # ファイルをコピー
    shutil.copy(file.path, file_path)
    # データベースに保存
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute("INSERT INTO images (original_name, path) VALUES (?, ?)", (file.name, file_path))
    conn.commit()
    conn.close()

# 保存された画像の取得
def get_images():
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    c.execute("SELECT id, original_name, path FROM images")
    images = c.fetchall()
    conn.close()
    return images

def main(page: ft.Page):
    init_db()
    selected_files = []

    def on_result(e: ft.FilePickerResultEvent):
        nonlocal selected_files
        if e.files:
            selected_files = e.files
            status_text.value = "画像が選択されました。保存ボタンをクリックしてください。"
            save_button.visible = True
            page.update()

    def on_save(e):
        if selected_files:
            for file in selected_files:
                save_image(file)
            status_text.value = "画像が保存されました。"
            save_button.visible = False
            # 画像リストを更新
            image_list.controls = [ft.Image(src=img[2], width=100, height=100) for img in get_images()]
            page.update()

    # UI要素の定義
    # ああああ
    upload = ft.FilePicker(on_result=on_result)
    page.overlay.append(upload)

    status_text = ft.Text("")
    save_button = ft.ElevatedButton("保存", on_click=on_save, visible=False)
    image_list = ft.ListView(
        controls=[ft.Image(src=img[2], width=100, height=100) for img in get_images()],
        expand=True
    )

    page.add(
        ft.Column(
            [
                ft.Text("画像をアップロードしてください:"),
                ft.ElevatedButton(
                    "画像を選択",
                    on_click=lambda _: upload.pick_files(
                        allow_multiple=True,
                        allowed_extensions=["png", "jpg", "jpeg", "gif"]
                    )
                ),
                status_text,
                save_button,
                ft.Text("保存された画像:"),
                image_list
            ]
        )
    )

if __name__ == '__main__':
    ft.app(target=main)