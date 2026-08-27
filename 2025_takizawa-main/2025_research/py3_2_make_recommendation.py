import numpy as np
import pandas as pd
import py1_data_clean as pydc


# 基本的な変数の定義
dictionary = pydc.dictionary
matrix_test = pydc.matrix_test


# 準備① : rulesをもとに, 各ルールの前提部・結論部(幸福度)・確信度から成る「rules_df」を作成
def make_rules_df(rules, dictionary):

  rules = rules[rules['confidence'] >= 0.5]

  # 処理結果を格納するためのリスト
  rules_list = []

  for antecedents, consequents, confidence in rules[['antecedents', 'consequents', 'confidence']].values:
    
    # 各ルール（DataFrameの将来の1行）を辞書として作成
    rule_dict = {}
    
    # 確信度を辞書に追加
    rule_dict['確信度'] = confidence
    
    # 前提部（antecedents）と結論部（consequents）を結合
    all_items = antecedents.union(consequents)
    
    for item in all_items:
      # アイテムが 'カラム名_値' の形式であるかチェック
      if isinstance(item, str) and '_' in item:
        # カラム名と値に分割
        column_name, value_str = item.split('_')
        value = int(float(value_str))
                
        # 辞書に {カラム名: 値} をセット
        rule_dict[column_name] = value
    
    # 完成した辞書をリストに追加
    rules_list.append(rule_dict)

  # 辞書のリストからDataFrameを作成
  columns_order = list(dictionary.keys()) + ['確信度']
  rules_df = pd.DataFrame(rules_list, columns=columns_order)

  return rules_df


#準備② : 「profiles_df」を作成
def make_profile_df(matrix_test, dictionary):
  profiles_df = matrix_test.copy()

  #profileに欠損値や非該当値が含まれている場合, Noneに置換する
  for index, row in profiles_df.iterrows():
    for col_name, value in row.items():
        
      if value in list(dictionary[col_name]):
        continue
      else:
        profiles_df.loc[index, col_name] = None

  return profiles_df


#準備③ : happiness_estimationを実行するための決まった処理
def happiness_estimation_pre(rules_df):
  
  #rules_dfの, 幸福度と確信度以外の列から成る「rules_df_rules」を作成する
  rules_df_rules = rules_df.drop(columns=['本人の幸福感（最近１年間）', '確信度'])

  #各ルールの確信度が格納されたリスト「confidence_list」を作成する
  rules_df_confidence = rules_df['確信度']
  confidence_list = rules_df_confidence.tolist()
  confidence_list = [min(0.7, conf) for conf in confidence_list]

  #rules_dfにおける「幸福度」の値の頻度を格納
  frequency_dict = rules_df['本人の幸福感（最近１年間）'].value_counts().to_dict()
  frequency_dict_max = max ( value_list for value_list in frequency_dict.values() )
  frequency_dict_min = min ( value_list for value_list in frequency_dict.values() )

  return rules_df_rules, confidence_list, frequency_dict, frequency_dict_max, frequency_dict_min


#推定幸福度を計算する
def happiness_estimation(profile_df, rules_df, rules_df_rules, dictionary, confidence_list, frequency_dict, frequency_dict_max, frequency_dict_min):

  # プロフィールの値 (1D配列)
  profile_df_main = profile_df.drop(columns='本人の幸福感（最近１年間）')
  profile_values = profile_df_main.iloc[0].values # (n_features,)
  
  # 比較対象の列名
  feature_names = profile_df_main.columns.tolist()
  
  # ルールの値 (2D配列)
  rules_values = rules_df_rules[feature_names].values # (n_rules, n_features)
  
  
  # ①各ルールのプロフィールとのマッチ度が格納されたリスト「matching_list」を作成する

  # (a) 各属性の範囲 (a_under) を事前に一括計算 (1D配列)
  ranges = np.array([
      max(dictionary[col]) - min(dictionary[col]) for col in feature_names
  ])
  
  # (b) ゼロ除算対策
  # rangesが0の場所は分母を1にし(safe_ranges)、
  # 該当箇所を後で1.0で上書きするためにマスク(zero_range_mask)を作成
  safe_ranges = np.where(ranges == 0, 1.0, ranges)
  zero_range_mask = (ranges == 0) # (n_features,)
  
  # (c) カテゴリカル属性のマスク (1D配列)
  categorical_features_list = [
      '両親の生死', '技術・技能の習得', '副業の有無', '仕事の内容', '経営組織', '職位', 
      '働き方', '現在の仕事の継続', '仕事を変えたい理由', '１年前の就業', 
      '通勤通学以外で運動する日数', '介護を必要とする家族', '地域ブロック', '市群規模'
  ]
  categorical_mask = np.array([col in categorical_features_list for col in feature_names])

  # (d) NaNのチェック (2Dマスク)
  # ルールとプロフィールの両方がNaNでないことを確認
  notna_mask = ~np.isnan(rules_values) & ~np.isnan(profile_values) # (n_rules, n_features)

  
  # (e) マッチ度を一括計算 
  
  # (e-1) 数値属性としての計算: 1 - abs(rule - profile) / range
  numerical_matching = 1.0 - (np.abs(rules_values - profile_values) / safe_ranges)
  
  # (e-2) カテゴリカル属性としての計算 
  # 一致: 1.0
  # 不一致: 1.0 - (1.0 / safe_ranges)
  categorical_matching = np.where(
      rules_values == profile_values, 
      1.0,                            
      1.0 - (1.0 / safe_ranges)       
  )

  # (e-3) カテゴリカル属性の箇所だけ計算結果を差し替え
  matching_scores = np.where(
      categorical_mask,     
      categorical_matching, 
      numerical_matching    
  )

  # (e-4) a_under=0 (zero_range_mask) の箇所を 1.0 で上書き
  matching_scores = np.where(
      zero_range_mask,       
      1.0,                  
      matching_scores       
  )
  
  # (e-5) NaNだった箇所を 0 に (合計に寄与させない)
  final_matching_scores = np.where(notna_mask, matching_scores, 0.0)

  # (f) 各ルール（行ごと）の合計を計算 (axis=1)
  matching_list = np.sum(final_matching_scores, axis=1)


  # ②各ルールの「confidence_list」と「matching_list」から計算した「importance_pre_1_list」
  importance_pre_1_list = [confidence * matching for confidence, matching in zip(confidence_list, matching_list)]
  
  # ③各ルールの「幸福度」と「frequency_dict」から作成した「importance_pre_2_list」
  importance_pre_2_list = []
  for value in rules_df['本人の幸福感（最近１年間）']:
    importance_pre_2_list.append( frequency_dict_min + frequency_dict_max - frequency_dict[value] )

  # ④幸福度推定に直接的に使用する, importance_listを計算
  importance_list = [importance_pre_1 * importance_pre_2 for importance_pre_1, importance_pre_2 in zip(importance_pre_1_list, importance_pre_2_list)]

  # 推定幸福度を計算
  estimated_happiness_apper = 0 #推定幸福度を計算する加重平均の式における, 分子
  estimated_happiness_under = sum(importance_list) #推定幸福度を計算する加重平均の式における, 分母

  for i in range(len(importance_list)):
    estimated_happiness_apper += importance_list[i] * rules_df.iloc[i]['本人の幸福感（最近１年間）']

  estimated_happiness = estimated_happiness_apper / estimated_happiness_under

  return estimated_happiness


# 基本的な変数の定義
profiles_df = make_profile_df(matrix_test, dictionary)


# 精度計算（推定幸福度を常に, 全幸福度の平均とした場合）
def calculate_rmse_xx(rules):
  squared_errors = []
  rules_df = make_rules_df(rules, dictionary)

  for index in range(len(profiles_df)):
    estimated_happiness = rules_df['本人の幸福感（最近１年間）'].mean()
    correct_happiness = profiles_df.iloc[index, :].to_frame().T['本人の幸福感（最近１年間）'].iloc[0]
    squared_error = (estimated_happiness - correct_happiness) ** 2
    squared_errors.append(squared_error)
  rmse = np.sqrt( np.nanmean(squared_errors) )
  return rmse


# 精度計算（RMSE)
def calculate_rmse(rules):
  squared_errors = []
  rules_df = make_rules_df(rules, dictionary)
  rules_df_rules, confidence_list, frequency_dict, frequency_dict_max, frequency_dict_min = happiness_estimation_pre(rules_df)

  for index in range(len(profiles_df)):
    estimated_happiness = happiness_estimation(profiles_df.iloc[index, :].to_frame().T, rules_df, rules_df_rules, dictionary, confidence_list, frequency_dict, frequency_dict_max, frequency_dict_min)
    correct_happiness = profiles_df.iloc[index, :].to_frame().T['本人の幸福感（最近１年間）'].iloc[0]
    squared_error = (estimated_happiness - correct_happiness) ** 2
    squared_errors.append(squared_error)
  rmse = np.sqrt( np.nanmean(squared_errors) )
  return rmse


print( 'RMSE_minsup0.003_maxlen4_xx：', calculate_rmse_xx( rules = pd.read_pickle('rules_minsup0.003_maxlen4.pkl') ) )
print( 'RMSE_minsup0.003_maxlen4：', calculate_rmse( rules = pd.read_pickle('rules_minsup0.003_maxlen4.pkl') ) )

print( 'RMSE_minsup0.004_maxlen4_xx：', calculate_rmse_xx( rules = pd.read_pickle('rules_minsup0.004_maxlen4.pkl') ) )
print( 'RMSE_minsup0.004_maxlen4：', calculate_rmse( rules = pd.read_pickle('rules_minsup0.004_maxlen4.pkl') ) )

print( 'RMSE_minsup0.004_maxlen5_xx：', calculate_rmse_xx( rules = pd.read_pickle('rules_minsup0.004_maxlen5.pkl') ) )
print( 'RMSE_minsup0.004_maxlen5：', calculate_rmse( rules = pd.read_pickle('rules_minsup0.004_maxlen5.pkl') ) )

print( 'RMSE_minsup0.006_maxlen4_xx：', calculate_rmse_xx( rules = pd.read_pickle('rules_minsup0.006_maxlen4.pkl') ) )
print( 'RMSE_minsup0.006_maxlen4：', calculate_rmse( rules = pd.read_pickle('rules_minsup0.006_maxlen4.pkl') ) )

print( 'RMSE_minsup0.006_maxlen5_xx：', calculate_rmse_xx( rules = pd.read_pickle('rules_minsup0.006_maxlen5.pkl') ) )
print( 'RMSE_minsup0.006_maxlen5：', calculate_rmse( rules = pd.read_pickle('rules_minsup0.006_maxlen5.pkl') ) )

print( 'RMSE_minsup0.008_maxlen4_xx：', calculate_rmse_xx( rules = pd.read_pickle('rules_minsup0.008_maxlen4.pkl') ) )
print( 'RMSE_minsup0.008_maxlen4：', calculate_rmse( rules = pd.read_pickle('rules_minsup0.008_maxlen4.pkl') ) )

print( 'RMSE_minsup0.008_maxlen5_xx：', calculate_rmse_xx( rules = pd.read_pickle('rules_minsup0.008_maxlen5.pkl') ) )
print( 'RMSE_minsup0.008_maxlen5：', calculate_rmse( rules = pd.read_pickle('rules_minsup0.008_maxlen5.pkl') ) )

print( 'RMSE_minsup0.01_maxlen4_xx：', calculate_rmse_xx( rules = pd.read_pickle('rules_minsup0.01_maxlen4.pkl') ) )
print( 'RMSE_minsup0.01_maxlen4：', calculate_rmse( rules = pd.read_pickle('rules_minsup0.01_maxlen4.pkl') ) )

print( 'RMSE_minsup0.01_maxlen5_xx：', calculate_rmse_xx( rules = pd.read_pickle('rules_minsup0.01_maxlen5.pkl') ) )
print( 'RMSE_minsup0.01_maxlen5：', calculate_rmse( rules = pd.read_pickle('rules_minsup0.01_maxlen5.pkl') ) )




#とりあえず, 以下は実行しない（というか後から多分消す）



# #worried_column='配偶者の有無'にして実行（今回の設定③）
# def execute_py3(rules, dictionary=pydc.dictionary, matrix_test=pydc.matrix_test, worried_column='配偶者の有無'):

#   #準備
#   rules_df = make_rules_df(rules, dictionary)
#   profile_df = make_profile_df(matrix_test, dictionary)
#   rules_df_rules, confidence_list = happiness_estimation_pre(rules_df)
  
#   #現在の推定幸福度を計算
#   current_estimated_happiness = happiness_estimation(profile_df, rules_df, rules_df_rules, dictionary, confidence_list)
#   print('current_estimated_happiness =', current_estimated_happiness) #あとで消す
  
#   recommendations = []
#   #new_profile_dfの推定幸福度を計算
#   for worried_column_value in pydc.dictionary[worried_column]:
#     new_profile_df = profile_df.copy()
#     new_profile_df[worried_column] = worried_column_value
    
#     if new_profile_df[worried_column].iloc[0] != profile_df[worried_column].iloc[0]:
#       new_estimated_happiness = happiness_estimation(new_profile_df, rules_df, rules_df_rules, dictionary, confidence_list)
#       print(new_estimated_happiness) #あとで消す
      
#       if new_estimated_happiness > current_estimated_happiness:
#         recommendations.append(worried_column_value) #あとで, 推定幸福度が大きいものから順にrecommendationsに格納するようにする
  
#   if recommendations == []:
#     print('推薦内容はありません')
#   else:
#     print(recommendations)

#   return 


# print( execute_py3(rules=pd.read_pickle('/home/takizawa/2025_takizawa/2025_research/rules_minsup0.05_maxlen4.pkl')) )
