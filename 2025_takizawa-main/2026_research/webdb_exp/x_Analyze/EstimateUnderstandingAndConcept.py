# ===========================================================
# 素のテキスト，重要概念リスト，記述テーマをもとに理解度と理解不足の概念を推測する
# tmuxで実行し，結果をpkl形式で保存する
# ============================================================

from _1_CleanedText import clean_text
from _3_ConceptsMap import ConceptsMapPipeline
from _4_EstimatedUnderstanding import EstimatedUnderstandingPipeline
import pandas as pd
import ast
import numpy as np
import pickle



def calculate(pre_text, important_concepts, theme_term):
    text = clean_text(pre_text)
    importantConcepts = important_concepts
    ConceptsMap, GraphEdges = ConceptsMapPipeline(text, importantConcepts, theme_term)
    Understanding, min_understanding_node = EstimatedUnderstandingPipeline(ConceptsMap, importantConcepts, theme_term)
    
    return GraphEdges, Understanding, min_understanding_node


def main_execute():
    data = pd.read_excel('/home/takizawa/2025_takizawa/2026_research/webdb_exp/x_Results/_0_2_実験2.xlsx', sheet_name='result1_export_add')
    
    for index in range(len(data)):
        pre_text = data.iloc[index, 2]

        important_concepts = ast.literal_eval(data.iloc[index, 8]) # 文字列をリスト型へ変換する

        if data.iloc[index, 6].item() == 1:
            theme_term = "食料市場機能の適正化と、情報公開による価格安定化の実現"
        elif data.iloc[index, 6].item() == 2:
            theme_term = "雇用創出を見据えた、若年層・成人のスキル向上とキャリアの多角化"
        elif data.iloc[index, 6].item() == 3:
            theme_term = "地域共生型の観光振興による、持続可能な雇用と地域経済の活性化"
        elif data.iloc[index, 6].item() == 4:
            theme_term = "児童に対するあらゆる人権侵害（虐待・搾取・暴力等）の根絶"
        
        GraphEdges, Understanding, min_understanding_node = calculate(pre_text, important_concepts, theme_term)

        # 1. 複数の変数を一つの辞書にまとめる
        exp_result = {
            'graph_edges': GraphEdges,   
            'understanding': Understanding,    
            'min_understanding_node': min_understanding_node 
        }

        # 2. pickle で保存する
        # ブロックが終了した瞬間に，エラーが発生したかどうかに関わらず，自動的にファイルを閉じてくれる
        file_name = f'2026_research/webdb_exp/x_Results/exp_results_{index}.pkl'
        with open(file_name, 'wb') as f:
            pickle.dump(exp_result, f)



# 実行
main_execute()