import img2pdf
import os
import glob
import re # 自然順ソートのために追加

def natural_sort_key(s):
    """ファイル名から数値部分を抽出し、自然順ソート用のキーを返す"""
    # os.path.basename() を使ってファイル名部分のみを取得
    basename = os.path.basename(s)
    # ファイル名内の数値部分を抽出 (例: page_001.png -> 1)
    match = re.search(r'(\d+)', basename)
    # 数値が見つかればそれを、見つからなければ非常に大きな数を返し、数値なしファイルを最後に回す
    return int(match.group(1)) if match else float('inf')

def add_pdf_arguments(parser):
    """ArgumentParser に PDF 生成関連の引数を追加する"""
    group = parser.add_argument_group('PDF Generation Options') # オプションをグループ化
    group.add_argument(
        '--pdf', 
        action='store_true', 
        help='スクリーンショット完了後にPNGファイルを結合してPDFを作成します。'
    )
    group.add_argument(
        '--pdf-filename', 
        type=str, 
        default='output.pdf', 
        help='作成するPDFのファイル名。--pdf が指定された場合のみ有効。デフォルト: output.pdf'
    )
    group.add_argument(
        '--pdf-start', 
        type=int, 
        default=1, 
        metavar='N', # ヘルプ表示用
        help='PDFに含める最初のPNGファイルの番号 (1始まり)。デフォルト: 1'
    )
    group.add_argument(
        '--pdf-count', 
        type=int, 
        default=10, 
        metavar='M', # ヘルプ表示用
        help='PDFに含めるPNGファイルの枚数。デフォルト: 10'
    )

def create_pdf_from_images(output_folder, pdf_filename, start_index, count):
    """指定されたフォルダ内の画像から範囲を指定してPDFを生成する"""
    print("\nPDFファイルの生成を開始します...")
    print(f"対象フォルダ: {output_folder}")
    print(f"開始ファイル番号: {start_index}")
    print(f"含める枚数: {count}")

    # フォルダ内のPNGファイルを取得 (page_*.png 形式を想定)
    # ここでは 'page_*.png' に限定せず、'*.png' を対象にする方が汎用的かもしれない
    # 要件に応じて変更: glob.glob(os.path.join(output_folder, '*.png'))
    all_png_files = glob.glob(os.path.join(output_folder, 'page_*.png'))

    if not all_png_files:
        print(f"エラー: フォルダ「{output_folder}」内に 'page_*.png' ファイルが見つかりません。")
        return

    # ファイル名を自然順ソート
    sorted_files = sorted(all_png_files, key=natural_sort_key)
    print(f"フォルダ内で {len(sorted_files)} 個のPNGファイルが見つかりました (自然順ソート済)。")

    # 開始インデックスと枚数に基づいて対象ファイルを抽出
    # start_index は 1始まりなので、リストのインデックス (0始まり) に変換
    start_zero_based = start_index - 1
    end_zero_based = start_zero_based + count

    # 範囲チェック
    if start_zero_based < 0:
        print("エラー: 開始ファイル番号は1以上である必要があります。")
        return
    if start_zero_based >= len(sorted_files):
        print(f"エラー: 開始ファイル番号 ({start_index}) がフォルダ内のファイル数 ({len(sorted_files)}) を超えています。")
        return
    
    # 実際の終了インデックスはファイル数を超えないように調整
    end_zero_based = min(end_zero_based, len(sorted_files))
    
    target_files = sorted_files[start_zero_based:end_zero_based]

    if not target_files:
        print("エラー: 指定された範囲に該当するファイルが見つかりません。")
        return

    # PDFファイルパスを構築
    pdf_filepath = os.path.join(output_folder, pdf_filename)
    if not pdf_filepath.lower().endswith(".pdf"): # 拡張子がなければ追加
        pdf_filepath += ".pdf"

    try:
        print(f"以下の {len(target_files)} ファイルを結合します:")
        for f in target_files:
             print(f"- {os.path.basename(f)}")

        # img2pdfを使用してPDFを生成
        with open(pdf_filepath, "wb") as f:
            # 画像ファイルの存在確認 (img2pdfがエラーを出す前に行う - globで取得してるので不要かも)
            # valid_files = [img for img in target_files if os.path.exists(img)] ...
                 
            f.write(img2pdf.convert(target_files))
        print(f"\nPDFファイル「{pdf_filepath}」が正常に作成されました。")
    except img2pdf.AlphaChannelError:
         print("\nエラー: PDF生成に失敗しました。PNGファイルにアルファチャンネル (透過情報) が含まれている可能性があります。")
         print("       画像をアルファチャンネルなしで保存し直すか、別のツールを試してください。")
    except Exception as e:
        print(f"\nエラー: PDFファイルの生成中に予期せぬエラーが発生しました: {e}") 