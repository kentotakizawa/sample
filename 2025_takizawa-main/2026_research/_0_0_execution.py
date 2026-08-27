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
    if len(ImportantConcepts) <= 1:
        print('重要概念が一つ以下しかないため，理解度の推定ができません．')
        return None
    
    else:
        ConceptsMap = ConceptsMapPipeline(text, ImportantConcepts, theme_term)
        Understanding, min_understanding_node = EstimatedUnderstandingPipeline(ConceptsMap)
        return Understanding, min_understanding_node



if __name__ == "__main__":
    
    pre_text = "私は大学の授業を通じてSDGs(持続可能な開発目標)を学び、その理念に強く共感する一方で、実践のあり方には課題があると感じている。SDGsが掲げる貧困や教育、環境問題への取り組みは、現代社会にとって不可欠なものだ。大学でもエコバッグの利用や食品ロス削減など、学生の環境意識は着実に高まっている。こうした身近な行動の積み重ねが、社会全体の変化につながる可能性は大きい。しかし懸念もある。それは「SDGsウォッシュ」と呼ばれる、実質的な効果を伴わずに取り組みの姿勢だけを示す現象だ。SNSでSDGs関連の投稿をすることが一種の流行になっている面もあり、それが本当に課題解決につながっているのか疑問に思うことがある。大切なのは行動の「見た目」ではなく、実際にどれだけ変化を生み出しているかである。そこで私は、大学生として二つのことを意識したい。第一に、自分の行動の効果を検証する姿勢を持つこと。満足感で終わらせず、事実やデータに基づいて成果を確認する必要がある。第二に、個人の行動だけでなく、貧困や環境破壊を生む社会構造そのものにも目を向けることだ。政策提言やボランティア活動など、より大きな枠組みに関わる視点も欠かせないだろう。SDGsは単なるスローガンではなく、批判的に検証しながら実践すべき目標だと考える。理想と現実のギャップに向き合い、持続可能な社会の実現に向けて主体的に行動していきたい。"

    theme_term = "持続可能な社会の実現"
    
    execute(pre_text, theme_term)