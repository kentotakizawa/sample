実験結果（予測モデルのRMSE）を出すために必要な手順について述べる．なおvscodeによる実行を想定する．



実行するファイルは，py1_data_clean.py，py2_make_rules.py，py3_1_make_recommendation.pyの3つ．



py1_data_clean.pyを，末尾に以下のコードを加えた状態で実行すると，matrix_fpgrowth.pklというファイルが実行ディレクトリに生成される．

import pickle
matrix_fpgrowth.to_pickle('matrix_fpgrowth.pkl')



py2_make_rules.pyを実行すると，各パラメータ（min_support，max_len）における相関ルール行列（rules_minsup{min_support}_maxlen{max_len}.pklというファイル）が生成される．



py3_1_make_recommendation.pyを実行すると特定パラメータで生成された相関ルール行列を使用して構築した予測モデルごとに，RMSEが出力される．その際，単純モデル（相関ルール行列の結論部の幸福度の平均値のみを常に出力するモデル）におけるRMSEも同時に出力される．この結果を通じ，予測モデルが単純モデルよりも精度が良いことが確認できる．