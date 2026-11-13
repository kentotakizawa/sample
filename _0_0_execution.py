# ===========================================================
# 1 -> 2 -> 3 -> 4 を連続実行する
# ============================================================



from _1_CleanedText import clean_text
from _2_ImportantConcepts import ImportantConceptsPipeline
from _3_ConceptsMap import ConceptsMapPipeline
from _4_EstimatedUnderstanding import EstimatedUnderstandingPipeline



def execute(pre_text, theme_term):
    text = clean_text(pre_text)
    ImportantConcepts = ImportantConceptsPipeline(text)
    ConceptsMap, GraphEdges = ConceptsMapPipeline(text, ImportantConcepts, theme_term)
    Ave_degree, Var_degree, Depth, Understanding, Min_understanding_node = EstimatedUnderstandingPipeline(ConceptsMap, ImportantConcepts, theme_term)

    return GraphEdges, Ave_degree, Var_degree, Depth, Understanding, Min_understanding_node



if __name__ == "__main__":
    
    pre_text = "現実問題として、食糧価格の変動（高騰）は日本のみならず、他国でも少なからず確認できる現象であり、それが深刻なればなるほど飢餓に苦しむ人たちが増えるため、できる限り早急に対応すべきという点は同意です。食料市場においては、人件費や原材料費の高騰などを理由にどうしても安定した生産ができない事情が存在しているはずで、結果的に公平に行き渡らない、特定の層における不足といった状況が観察されます。この問題においては、人間以外の生産設備の充実などが重要であり、機械による労働量を増やすやり方が必要だと考えています。"

    theme_term = "持続可能な社会の実現"
    
    execute(pre_text, theme_term)