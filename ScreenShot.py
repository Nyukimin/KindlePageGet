import pyautogui
import time
import os
import pygetwindow as gw
import argparse

# --- コマンドライン引数の設定 ---
parser = argparse.ArgumentParser(description='指定したウィンドウのスクリーンショットを連続撮影し、指定した矢印キーでページをめくります。')
parser.add_argument('--direction', type=str, choices=['left', 'right'], default='left',
                    help='ページめくりに使用する矢印キー (left または right)。デフォルト: left')
parser.add_argument('--title', type=str, default='Kindle',
                    help='対象ウィンドウのタイトルに含まれる文字列。デフォルト: Kindle')
parser.add_argument('--count', type=int, default=10,
                    help='撮影するスクリーンショットの枚数。デフォルト: 10')
parser.add_argument('--delay', type=float, default=1.0,
                    help='ページめくり後の待機時間 (秒)。デフォルト: 1.0')
parser.add_argument('--output', type=str, default='screenshots',
                    help='スクリーンショットの保存先フォルダ名。デフォルト: screenshots')

args = parser.parse_args() # 引数を解析
# ------------------------------

# 保存先フォルダを指定 (引数から取得)
output_folder = args.output
os.makedirs(output_folder, exist_ok=True) # フォルダが存在しない場合は作成

# 対象ウィンドウのタイトル（引数から取得）
target_window_title = args.title

# 連続でスクリーンショットを撮る回数 (引数から取得)
num_screenshots = args.count

# ページめくりキー (引数から取得)
page_turn_key = args.direction

# ページめくり後の待機時間 (引数から取得)
page_turn_delay = args.delay

# スクリーンショットを開始する前に少し待機（アプリをアクティブにする時間）
print(f"ウィンドウタイトルに「{target_window_title}」を含むウィンドウを探しています...")
kindle_windows = gw.getWindowsWithTitle(target_window_title)

if not kindle_windows:
    print(f"エラー: タイトルに「{target_window_title}」を含むウィンドウが見つかりません。")
    print("対象アプリが起動しているか、または --title 引数が正しいか確認してください。")
    exit()

# 最初のウィンドウを取得 (複数見つかった場合)
kindle_window = kindle_windows[0]
print(f"ウィンドウ「{kindle_window.title}」を対象にします。")
print(f"ページめくりキー: {page_turn_key}")
print(f"撮影枚数: {num_screenshots}")
print(f"保存先フォルダ: {output_folder}")

# ウィンドウをアクティブにする (任意ですが推奨)
# try:
#     kindle_window.activate()
#     print("ウィンドウをアクティブにしました。")
#     time.sleep(1) # アクティブになるのを少し待つ
# except Exception as e:
#     print(f"ウィンドウのアクティブ化に失敗しました: {e}")

print("5秒後にスクリーンショットを開始します。")
time.sleep(5)
print("開始します。")

# 連続でスクリーンショットを撮る回数
# num_screenshots = 10 # 例として10回 ← 引数で指定するためコメントアウト

try:
    for i in range(num_screenshots):
        # ウィンドウが存在するか再確認 -> isAlive がないため try-except で対応
        try:
            # ウィンドウが有効かどうかの間接的なチェック
            # ウィンドウタイトルなどを取得しようとしてエラーが出れば閉じたと判断
            _ = kindle_window.title # ウィンドウが無効ならここでエラーが出るはず

            window_region = (kindle_window.left, kindle_window.top, kindle_window.width, kindle_window.height)
            if window_region[2] <= 0 or window_region[3] <= 0:
                print("エラー: ウィンドウサイズが不正です (最小化されている可能性があります)。")
                break
        except gw.PyGetWindowException: # pygetwindow の例外をキャッチ
             print("エラー: 対象ウィンドウが見つからないか、閉じられました。")
             break
        except Exception as e: # その他の予期せぬエラー
            print(f"エラー: ウィンドウ情報の取得中にエラーが発生しました: {e}")
            break

        # 指定領域のスクリーンショットを撮影
        # 注意: macOSで高解像度ディスプレイの場合、座標が2倍になることがあるため調整が必要な場合があります
        screenshot = pyautogui.screenshot(region=window_region)

        # ファイル名を生成して保存
        file_path = os.path.join(output_folder, f'page_{i+1:03d}.png') # 例: page_001.png
        screenshot.save(file_path)
        print(f'{file_path} を保存しました。')

        # 次のページへ（引数で指定されたキーを押す） - ウィンドウがアクティブでないと効かない場合がある
        # kindle_window.activate() # 念のため毎回アクティブ化する
        # time.sleep(0.1)
        pyautogui.press(page_turn_key) # 引数で指定されたキーを使用
        print(f"キー「{page_turn_key}」を押して次のページへ移動します。")

        # ページがめくれるまでの待機時間（必要に応じて調整）
        time.sleep(page_turn_delay) # 引数で指定された待機時間を使用

except KeyboardInterrupt:
    print("\n処理を中断しました。")
except Exception as e:
    print(f"エラーが発生しました: {e}")

print(f"スクリーンショット撮影処理を終了します。") 