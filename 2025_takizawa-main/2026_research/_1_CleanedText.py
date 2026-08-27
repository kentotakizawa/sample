import re # 正規表現を扱うためのモジュール



def clean_text(pre_text: str) -> str:
    """
    手法適用可能な形へ整形する関数

    型ヒントは，実行に直接影響するわけではない
    re.sub(r' パターン, 置換後の文字列, 対象文字列 ')は正規表現を認識するメソッド
    　・[]は，この中のどれか一つ
    　・\sは空白
    　・\u3000は全角スペース
    　・+は1回以上の繰り返し
    　・\nは改行
    　・{2,}は2回以上の繰り返し
    stripは，先頭と末尾に存在するすべての空白文字（スペース、タブ、改行文字など）を削除するメソッド
    rfindは，文字列から，最後に指定した文字が出現する場所（インデックス）を探すメソッド
    """
    
    # 句点後のスペースを除去する
    pre_text = re.sub(r'。[\s\u3000]+', '。', pre_text)
    # 複数の改行を一つの改行にする
    pre_text = re.sub(r'\n{2,}', '\n', pre_text)
    # 文章前後のスペースを除去する
    text = pre_text.strip()

    # # 文章が句点で終わっていない場合，最後の句点以降の文章を除去する
    # last_period_index = -1
    # index_full_dot = pre_text.rfind('。')
    # index_half_dot = pre_text.rfind('.')
    
    # if index_full_dot == -1 and index_half_dot == -1:
    #     text = pre_text
    # else:
    #     if index_full_dot == -1:
    #         last_period_index = index_half_dot
    #     elif index_half_dot == -1:
    #         last_period_index = index_full_dot
    #     else:
    #         last_period_index = max(index_full_dot, index_half_dot)
    #     text = pre_text[:last_period_index + 1]

    return text



if __name__ == "__main__":
    text1 = "これはテスト文章です。\n\nノイズ情報が付加されています."
    print( text1 )
    print( clean_text(text1) )