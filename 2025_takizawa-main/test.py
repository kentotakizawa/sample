import numpy as np

# 問題の状況を再現（a は np.int64 型のスカラー）
a = np.array(10, dtype=np.int64) 
print(f"aの型: {type(a)}") # <class 'numpy.int64'>

# 修正後のコード
if a.item() == 1:
    print("aは1です")
else:
    print(f"aの値は1ではありません（実際は {a.item()} です）")

# 別の値でテスト
b = np.array(1, dtype=np.int64)
if b.item() == 1:
    print("bは1です")