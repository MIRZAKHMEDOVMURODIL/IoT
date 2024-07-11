import os
import csv

# タブまたは空白で区切られたCSVファイルを読み込む関数
def read_csv_with_multiple_separators(file_path):
    separators = ['\t', ' ']
    for sep in separators:
        try:
            with open(file_path, 'r', encoding='utf-16') as file:
                reader = csv.reader(file, delimiter=sep)
                data = list(reader)
                # 複数列が認識された場合、適切な区切り文字と判断
                if len(data[0]) > 1:
                    return data
        except UnicodeError:
            continue
    # 適切な区切り文字が見つからなかった場合はNoneを返す
    return None

# CSVデータ内の文字列を置換する関数
def replace_string_in_csv_data(data, target_string, replacement_string):
    return [[cell.replace(target_string, replacement_string) for cell in row] for row in data]

# 単一のCSVファイルを処理する関数
def process_single_csv(file_path, output_folder):
    # CSVファイルを読み込む
    data = read_csv_with_multiple_separators(file_path)
    if data is None:
        print(f"Skipping {file_path} due to unsupported format or separator")
        return

    # 文字列置換処理を追加
    data = replace_string_in_csv_data(data, "ビアシフト", "viashift")

    # パスと拡張子を除いたファイル名を抽出
    file_name = os.path.basename(file_path).split('.')[0]

    # 列数に基づいてパターンを決定
    num_columns = len(data[0])
    if num_columns == 2:
        data_names = [row[0] for row in data]
        data_values = [row[1] for row in data]
    elif num_columns == 4:
        data_names = [row[i] for row in data for i in [0, 2] if len(row) > i]
        data_values = [row[i] for row in data for i in [1, 3] if len(row) > i]
    elif num_columns == 6:
        data_names = [row[i] for row in data for i in [0, 2, 4] if len(row) > i]
        data_values = [row[i] for row in data for i in [1, 3, 5] if len(row) > i]
    else:
        print(f"Skipping {file_path} due to unsupported number of columns")
        return

    # 必要な形式で新しいデータを作成
    new_data = [data_names, data_values]

    # 出力ファイルのパスを定義
    output_file_path = os.path.join(output_folder, f"{file_name}_re.csv")

    # UTF-8エンコーディングで新しいCSVファイルに保存
    with open(output_file_path, 'w', newline='', encoding='utf-16') as file:
        writer = csv.writer(file)
        writer.writerows(new_data)

# 指定されたフォルダ内の全てのCSVファイルを処理する関数
def process_all_csv_files(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_folder, filename)
            process_single_csv(file_path, output_folder)

# 入力フォルダと出力フォルダのパスを定義
input_folder_path = r'C:\Users\00230800134\Documents\Python Scripts\ayabe\SHIFT_data\VIA'  # ここに元データ保存先フォルダのパスを指定してください
output_folder_path = r'C:\Users\00230800134\Documents\Python Scripts\ayabe\SHIFT_output\VIA'  # ここに出力先フォルダのパスを指定してください

# 出力フォルダが存在しない場合は作成
os.makedirs(output_folder_path, exist_ok=True)

# 指定された入力フォルダ内の全てのCSVファイルを処理
process_all_csv_files(input_folder_path, output_folder_path)

output_folder_path
