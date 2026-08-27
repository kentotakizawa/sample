import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


#データを読み込む
def data_imput():
   matrix_1_path = '/home/takizawa/2025_takizawa/2025_research/JHPS2023data_ver2.0_FTA-Energy_deleted.csv'
   matrix_1 = pd.read_csv(matrix_1_path, header=None)
   
   matrix_2_path = '/home/takizawa/2025_takizawa/2025_research/JHPS2023newcohort-B_data_ver2.0_FTA-Energy_deleted.csv'
   matrix_2 = pd.read_csv(matrix_2_path, header=None)

   matrix_detail_path = '/home/takizawa/2025_takizawa/2025_research/JHPS2023codebook_ver2.1.xlsx'
   matrix_detail = pd.read_excel(matrix_detail_path)
   
   return matrix_1, matrix_2, matrix_detail

matrix_1, matrix_2, matrix_detail = data_imput()


#matrix_1と_matrix_2を結合して, matrixとして保存する
def make_matrix(matrix_1, matrix_2):
   matrix = pd.concat([matrix_1, matrix_2], ignore_index=True)
   
   #matrixから, 使用する列のみを選択する
   matrix = matrix.loc[:, [3, 4, 5, 8, 9, 11, 13, 15, 16, 17, 19, 20, 556, 557, 564, 587, 610, 611, 612, 614, 615, 618, 627, 634, 637, 643, 651, 652, 675, 677, 690, 692, 707, 769, 782, 808, 811, 853, 872, 907, 908, 1249, 1589, 1590]]
   
   return matrix

matrix = make_matrix(matrix_1, matrix_2)


#matrixのカラム名リストを作成して, matrixのカラム名を変更する
def make_matrix_column(matrix, matrix_detail):
   column_list = []
   for index in range(len(matrix_detail['項目'])):
      if ( pd.isna( matrix_detail['ｓｕｂ項目'].iloc[index] ) ) or (matrix_detail['ｓｕｂ項目'].iloc[index] == '　'):
        column_list.append( str( matrix_detail['項目'].iloc[index] ) )
      else:
        column_list.append( str( matrix_detail['項目'].iloc[index] )+ '（' + str( matrix_detail['ｓｕｂ項目'].iloc[index] ) + '）' )
        
   column_list = [column_list[i] for i in [3, 4, 5, 8, 9, 11, 13, 15, 16, 17, 19, 20, 556, 557, 564, 587, 610, 611, 612, 614, 615, 618, 627, 634, 637, 643, 651, 652, 675, 677, 690, 692, 707, 769, 782, 808, 811, 853, 872, 907, 908, 1249, 1589, 1590]]

   #カラム名の重複を回避するために, column_listを改良
   column_list[6] = '世帯員が単身赴任から戻る'
   column_list[7] = '世帯員が単身赴任する'
   column_list[34] = '本人の幸福感（最近１年間）'
   column_list[41] = '配偶者の幸福感（最近１年間）'

   matrix.columns = column_list

   return matrix

matrix = make_matrix_column(matrix, matrix_detail)


#いくつかの属性について、とりうる値の数を少なくすることでデータサイズを小さくする
def make_matrix_minimum(matrix):

   #対象者生年月日（生年）
   filtered = matrix['対象者生年月日（生年）'].copy()

   binned_data = pd.qcut(filtered, q=10, duplicates='drop')
   transformed_data = binned_data.apply(lambda x: x.left)
   result = matrix['対象者生年月日（生年）'].copy()
   result.loc[filtered.index] = transformed_data.astype(float).round(0).astype(int)

   matrix['対象者生年月日（生年）'] = result

   #両親への経済援助
   exclude_values = [99999, 88888]
   filtered = matrix['両親への経済援助'][~matrix['両親への経済援助'].isin(exclude_values)]

   binned_data = pd.qcut(filtered, q=10, duplicates='drop')
   transformed_data = binned_data.apply(lambda x: x.left)
   result = matrix['両親への経済援助'].copy()
   result.loc[filtered.index] = transformed_data.astype(float).round(0).astype(int)

   matrix['両親への経済援助'] = result

   #両親からの経済援助
   exclude_values = [99999, 88888]
   filtered = matrix['両親からの経済援助'][~matrix['両親からの経済援助'].isin(exclude_values)]

   binned_data = pd.qcut(filtered, q=10, duplicates='drop')
   transformed_data = binned_data.apply(lambda x: x.left)
   result = matrix['両親からの経済援助'].copy()
   result.loc[filtered.index] = transformed_data.astype(float).round(0).astype(int)

   matrix['両親からの経済援助'] = result

   #仕事からの収入（昨年）
   exclude_values = [99999, 88888]
   filtered = matrix['仕事からの収入（昨年）'][~matrix['仕事からの収入（昨年）'].isin(exclude_values)]

   binned_data = pd.qcut(filtered, q=10, duplicates='drop')
   transformed_data = binned_data.apply(lambda x: x.left)
   result = matrix['仕事からの収入（昨年）'].copy()
   result.loc[filtered.index] = transformed_data.astype(float).round(0).astype(int)

   matrix['仕事からの収入（昨年）'] = result

   #週平均残業時間
   exclude_values = [999, 888]
   filtered = matrix['週平均残業時間'][~matrix['週平均残業時間'].isin(exclude_values)]

   binned_data = pd.qcut(filtered, q=10, duplicates='drop')
   transformed_data = binned_data.apply(lambda x: x.left)
   result = matrix['週平均残業時間'].copy()
   result.loc[filtered.index] = transformed_data.astype(float).round(0).astype(int)

   matrix['週平均残業時間'] = result

   #平日睡眠時間（平均時間）
   exclude_values = [999.9]
   filtered = matrix['平日睡眠時間（平均時間）'][~matrix['平日睡眠時間（平均時間）'].isin(exclude_values)]

   binned_data = pd.qcut(filtered, q=10, duplicates='drop')
   transformed_data = binned_data.apply(lambda x: x.left)
   result = matrix['平日睡眠時間（平均時間）'].copy()
   result.loc[filtered.index] = transformed_data.astype(float).round(0).astype(int)

   matrix['平日睡眠時間（平均時間）'] = result

   #休日睡眠時間（平均時間）
   exclude_values = [999.9]
   filtered = matrix['休日睡眠時間（平均時間）'][~matrix['休日睡眠時間（平均時間）'].isin(exclude_values)]

   binned_data = pd.qcut(filtered, q=10, duplicates='drop')
   transformed_data = binned_data.apply(lambda x: x.left)
   result = matrix['休日睡眠時間（平均時間）'].copy()
   result.loc[filtered.index] = transformed_data.astype(float).round(0).astype(int)

   matrix['休日睡眠時間（平均時間）'] = result

   #幸福感（最近１年間）_配偶者
   exclude_values = [99, 88]
   filtered = matrix['配偶者の幸福感（最近１年間）'][~matrix['配偶者の幸福感（最近１年間）'].isin(exclude_values)]

   binned_data = pd.qcut(filtered, q=5, duplicates='drop')
   transformed_data = binned_data.apply(lambda x: x.left)
   result = matrix['配偶者の幸福感（最近１年間）'].copy()
   result.loc[filtered.index] = transformed_data.astype(float).round(0).astype(int)

   matrix['配偶者の幸福感（最近１年間）'] = result

   return matrix

matrix = make_matrix_minimum(matrix)


##欠損値リスト・非該当値リストを作成する（dictionaryやmatrix_fpgrowthの作成で使用する）
def make_missing_unapplicable_list(matrix_detail):
   missing_list = []
   missing_list = matrix_detail['無回答'].iloc[[3, 4, 5, 8, 9, 11, 13, 15, 16, 17, 19, 20, 556, 557, 564, 587, 610, 611, 612, 614, 615, 618, 627, 634, 637, 643, 651, 652, 675, 677, 690, 692, 707, 769, 782, 808, 811, 853, 872, 907, 908, 1249, 1589, 1590]].to_list()
   unapplicable_list = []
   unapplicable_list = matrix_detail['非該当'].iloc[[3, 4, 5, 8, 9, 11, 13, 15, 16, 17, 19, 20, 556, 557, 564, 587, 610, 611, 612, 614, 615, 618, 627, 634, 637, 643, 651, 652, 675, 677, 690, 692, 707, 769, 782, 808, 811, 853, 872, 907, 908, 1249, 1589, 1590]].to_list()

   return missing_list, unapplicable_list

missing_list, unapplicable_list = make_missing_unapplicable_list(matrix_detail)


#カラム名と値の対応が分かる辞書を作成する
def make_dictionary(matrix, missing_list, unapplicable_list):
   dictionary = {}
   for column_name in matrix.columns:
      unique_values_array = matrix[column_name].unique()
      unique_values_list = unique_values_array.tolist()
      dictionary[column_name] = unique_values_list
      
   #辞書の各キーの値から欠損値を削除
   for i in range(len(missing_list)):
      if pd.isna(missing_list[i]):
         continue
      else:
         for item_to_remove in list(dictionary.values())[i]:
            if item_to_remove == missing_list[i]:
               dictionary[list(dictionary.keys())[i]].remove(item_to_remove)

   #辞書の各キーの値から非該当値を削除
   for i in range(len(unapplicable_list)):
      if pd.isna(unapplicable_list[i]):
         continue
      else:
         for item_to_remove in list(dictionary.values())[i]:
            if item_to_remove == unapplicable_list[i]:
               dictionary[list(dictionary.keys())[i]].remove(item_to_remove)
        
   return dictionary

dictionary = make_dictionary(matrix, missing_list, unapplicable_list)


#相関ルールを作成するためのmake_trainと, ユーザプロフィールを作成するためのmatirx_testに分割する
matrix_train, matrix_test = train_test_split(matrix, test_size=0.1, random_state=42)


#fpgrowth関数に入力するために、matrix_trainをダミー変数化
def make_matrix_fpgrowth(matrix_train, missing_list, unapplicable_list, dictionary):
   matrix_fpgrowth = pd.get_dummies(matrix_train, columns=list(dictionary.keys()))
   
   #matrix_aprioriから欠損値を示す列を削除
   drop_columns = []
   for i in range(len(missing_list)):
      if pd.isna(missing_list[i]):
         continue
      else:
         drop_column = str( list(dictionary.keys())[i] ) + '_' + str( int(missing_list[i]) )
         if drop_column in matrix_fpgrowth.columns:
            matrix_fpgrowth = matrix_fpgrowth.drop(drop_column, axis=1)

   #matrix_fpgrowthから非該当値を示す列を削除
   drop_columns_2 = []
   for i in range(len(unapplicable_list)):
      if pd.isna(unapplicable_list[i]):
         continue
      else:
         drop_column_2 = str( list(dictionary.keys())[i] ) + '_' + str( int(unapplicable_list[i]) )
         if drop_column_2 in matrix_fpgrowth.columns:
            matrix_fpgrowth = matrix_fpgrowth.drop(drop_column_2, axis=1)

   return matrix_fpgrowth

matrix_fpgrowth = make_matrix_fpgrowth(matrix_train, missing_list, unapplicable_list, dictionary)