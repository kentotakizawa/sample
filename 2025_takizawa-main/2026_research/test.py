import pandas as pd 

dict = pd.read_pickle('2026_research/webdb_exp/x_Results/exp_results_2.pkl')
for key, value in dict.items():
    print(f"Key: {key}, Value: {value}")