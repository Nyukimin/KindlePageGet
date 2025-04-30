import img2pdf
import os
import glob
import re
import argparse # argparse を直接使う

def natural_sort_key(s):
    """ファイル名から数値部分を抽出し、自然順ソート用のキーを返す"""
    basename = os.path.basename(s)
    match = re.search(r'(\d+)', basename)
    return int(match.group(1)) if match else float('inf')

# add_pdf_arguments 関数は削除

def create_pdf_from_images(input_folder, output_filepath, start_index, count):
    """指定されたフォルダ内の画像から範囲を指定してPDFを生成する"""
    print("\nPDFファイルの生成を開始します...")
    print(f"入力フォルダ: {input_folder}")
    print(f"出力ファイル: {output_filepath}")
    print(f"開始ファイル番号: {start_index}")
    print(f"含める枚数: {count}")

    # フォルダ内のPNGファイルを取得 (page_*.png 形式を想定)
    all_png_files = glob.glob(os.path.join(input_folder, 'page_*.png'))

    if not all_png_files:
        print(f"エラー: フォルダ「{input_folder}」内に 'page_*.png' ファイルが見つかりません。")
        return False # 失敗したことを示す

    # ファイル名を自然順ソート
    sorted_files = sorted(all_png_files, key=natural_sort_key)
    print(f"フォルダ内で {len(sorted_files)} 個のPNGファイルが見つかりました (自然順ソート済)。")

    # 開始インデックスと枚数に基づいて対象ファイルを抽出
    start_zero_based = start_index - 1
    end_zero_based = start_zero_based + count

    if start_zero_based < 0:
        print("エラー: 開始ファイル番号は1以上である必要があります。")
        return False
    if start_zero_based >= len(sorted_files):
        print(f"エラー: 開始ファイル番号 ({start_index}) がフォルダ内のファイル数 ({len(sorted_files)}) を超えています。")
        return False
    
    end_zero_based = min(end_zero_based, len(sorted_files))
    target_files = sorted_files[start_zero_based:end_zero_based]

    if not target_files:
        print("エラー: 指定された範囲に該当するファイルが見つかりません。")
        return False

    # 出力ファイルパスの拡張子確認
    if not output_filepath.lower().endswith(".pdf"):
        output_filepath += ".pdf"
        print(f"警告: 出力ファイル名に .pdf 拡張子がないため追加しました: {output_filepath}")

    try:
        print(f"以下の {len(target_files)} ファイルを結合します:")
        for f in target_files:
             print(f"- {os.path.basename(f)}")

        with open(output_filepath, "wb") as f:
            f.write(img2pdf.convert(target_files))
        print(f"\nPDFファイル「{output_filepath}」が正常に作成されました。")
        return True # 成功したことを示す
    except img2pdf.AlphaChannelError:
         print("\nエラー: PDF生成に失敗しました。PNGファイルにアルファチャンネル (透過情報) が含まれている可能性があります。")
         return False
    except Exception as e:
        print(f"\nエラー: PDFファイルの生成中に予期せぬエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='指定フォルダ内のPNGファイルを結合してPDFを作成します。')
    parser.add_argument(
        '-i', '--input', # 引数名を変更 (--input-dir から --input へ)
        type=str, 
        required=True, # 必須引数に変更
        help='入力PNGファイルが含まれるフォルダへのパス。'
    )
    parser.add_argument(
        '-o', '--output', 
        type=str, 
        default='output.pdf', 
        help='出力するPDFのファイルパス。デフォルト: output.pdf'
    )
    parser.add_argument(
        '--start', 
        type=int, 
        default=1, 
        metavar='N', 
        help='PDFに含める最初のPNGファイルの番号 (1始まり)。デフォルト: 1'
    )
    parser.add_argument(
        '--count', 
        type=int, 
        default=10, 
        metavar='M', 
        help='PDFに含めるPNGファイルの枚数。デフォルト: 10'
    )

    args = parser.parse_args()

    # PDF生成関数を呼び出し
    create_pdf_from_images(
        args.input, 
        args.output, 
        args.start, 
        args.count
    ) 