import pandas as pd
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules
import datetime
print('ライブラリのimport完了')


matrix_fpgrowth = pd.read_pickle('/home/takizawa/2025_takizawa/2025_research/matrix_fpgrowth.pkl')


def make_rules(min_support, max_len):
    
    #相関ルール学習開始時刻
    time_start = datetime.datetime.now()
    print(f"time_start_minsup{min_support}_maxlen{max_len}: {time_start}")


    #データから相関ルールを学習する
    frequent_itemsets = fpgrowth(matrix_fpgrowth, min_support=min_support, use_colnames=True, max_len=max_len)
    rules = association_rules(frequent_itemsets, min_threshold=0.1)


    #相関ルール学習終了時刻
    time_end = datetime.datetime.now()
    print(f"time_minsup{min_support}_maxlen{max_len}: {time_end - time_start}")


    #rulesの内, 結論部が「最近1年間の幸福度」のものを抽出
    target_features = [
        frozenset({'本人の幸福感（最近１年間）_0'}),
        frozenset({'本人の幸福感（最近１年間）_1'}),
        frozenset({'本人の幸福感（最近１年間）_2'}),
        frozenset({'本人の幸福感（最近１年間）_3'}),
        frozenset({'本人の幸福感（最近１年間）_4'}),
        frozenset({'本人の幸福感（最近１年間）_5'}),
        frozenset({'本人の幸福感（最近１年間）_6'}),
        frozenset({'本人の幸福感（最近１年間）_7'}),
        frozenset({'本人の幸福感（最近１年間）_8'}),
        frozenset({'本人の幸福感（最近１年間）_9'}),
        frozenset({'本人の幸福感（最近１年間）_10'})
    ]
    rules = rules[rules['consequents'].isin(target_features)]


    #rulesを保存
    rules.to_pickle(f'rules_minsup{min_support}_maxlen{max_len}.pkl')

    return 

make_rules(0.01, 4)
make_rules(0.01, 5)
make_rules(0.009, 4)
make_rules(0.009, 5)
make_rules(0.008, 4)
make_rules(0.008, 5)
make_rules(0.007, 4)
make_rules(0.007, 5)
make_rules(0.006, 4)
make_rules(0.006, 5)
make_rules(0.005, 4)
make_rules(0.005, 5)
make_rules(0.004, 4)
make_rules(0.004, 5)
make_rules(0.003, 4)
make_rules(0.003, 5)