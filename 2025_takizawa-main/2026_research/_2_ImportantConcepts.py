import numpy as np
import torch
import re # 正規表現を扱うためのモジュール
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from janome.tokenizer import Tokenizer
from typing import List, Tuple
import math



# 基本的にGPU「cuda」を使用する
device = "cuda" if torch.cuda.is_available() else "cpu"
# SentenceTransformerは入力された文章をベクトルとして返すためのクラス
model = SentenceTransformer("cl-nagoya/ruri-v3-30m", device=device)



# ===========================================
# EmbedRankのコアロジック
# ============================================
def generate_candidate_keywords(text: str) -> list[str]:
    """
    文章から複合名詞を含む全ての名詞を抽出し、重複を除くことで，候補語リストを出力する関数

    set()は重複を排除するための組み込み関数
    """

    t = Tokenizer()
    
    candidate_keywords = set()
    current_noun_sequence: list[str] = [] 
    
    # 名詞の要素にしてはならない記号を定義する
    NOISE_PATTERN = re.compile(r'[\[\]()《》「」；：、\（）\-\–\u3000]') 
    
    for token in t.tokenize(text):
        # 1. 名詞の場合のみ，シーケンスに蓄積する
        if token.part_of_speech.startswith('名詞'):
            current_noun_sequence.append(token.surface)

        else:
            # 2. 名詞ではないトークンに遭遇した場合，名詞の連続が途切れたとみなし，処理を行う
            if current_noun_sequence:
                # 単体名詞、複合名詞の全パターン（サブシーケンス）を抽出する
                L = len(current_noun_sequence)

                for i in range(L):  # i: 開始インデックス
                    for j in range(i, L):  # j: 終了インデックス
                        sub_sequence = current_noun_sequence[i : j + 1]
                        keyword = "".join(sub_sequence)
                        
                        cleaned_keyword = NOISE_PATTERN.sub('', keyword)
                        # クリーニング後、空文字や純粋な記号になってしまっているものは除外する
                        if cleaned_keyword and len(cleaned_keyword) > 0:
                            candidate_keywords.add(cleaned_keyword)
                
                # シーケンスをリセットする
                current_noun_sequence = []
            
    # 3. テキストが名詞で終了した場合，句点で終了したものとして処理する
    if current_noun_sequence:
        L = len(current_noun_sequence)

        for i in range(L):
            for j in range(i, L):
                sub_sequence = current_noun_sequence[i : j + 1]
                keyword = "".join(sub_sequence)
                
                cleaned_keyword = NOISE_PATTERN.sub('', keyword)
                
                if cleaned_keyword and len(cleaned_keyword) > 0:
                    candidate_keywords.add(cleaned_keyword)
            
    candidate_keywords = list(candidate_keywords)
    return candidate_keywords



def mmr(doc_embedding: np.ndarray, words_embeddings: np.ndarray, candidate_keywords: List[str], top_k: int, lambda_param: float = 0.7, doc_sim_threshold: float = 0.4) -> Tuple[List[str], List[int]]:
    """
    類似度と多様性の両方を考慮することで，候補語リストから重要概念リストを抽出する関数

    0.0 < score < 1.0 である
    """

    # 1. 類似度計算
    doc_sim = cosine_similarity(words_embeddings, doc_embedding.reshape(1, -1)).flatten()
    sent_sim = cosine_similarity(words_embeddings)
    
    selected = []
    selected_indices = []
    
    # 2. 最初の候補（純粋に類似度最大のもの）を選ぶ
    valid_indices = [i for i in range(len(candidate_keywords)) if doc_sim[i] >= doc_sim_threshold]
    if not valid_indices:
        return [], []
    
    idx = np.argmax(doc_sim)
    selected.append(candidate_keywords[idx])
    selected_indices.append(idx)
    
    # 3. 2候補目以降の選択する（MMRの適用）
    for _ in range(top_k - 1):
        mmr_scores = []
        
        # 未選択の全ての候補語を評価
        for i in range(len(candidate_keywords)):
            if i in selected_indices:
                mmr_scores.append(-np.inf) # 既に選択済みならスコアを無効化
                continue
            
            # Diversity Penaltyを計算する
            diversity_penalty = 0
            max_sim = 0
            for j in selected_indices:
                max_sim = max(max_sim, sent_sim[i, j])
            diversity_penalty = max_sim
            
            # MMRスコアを計算する
            score = lambda_param * doc_sim[i] - (1 - lambda_param) * diversity_penalty
            mmr_scores.append(score)
        
        # 最もMMRスコアが高いインデックスを選ぶ
        idx = np.argmax(mmr_scores)
        selected.append(candidate_keywords[idx])
        selected_indices.append(idx)
        
    return selected, selected_indices



# ===========================================
# パイプライン全体の実行
# ============================================
def ImportantConceptsPipeline(text):
    # 1. 候補語リストの作成
    candidate_keywords = generate_candidate_keywords(text) 

    # 2. ベクトル化
    doc_emb = model.encode([text], normalize_embeddings=True)
    candidate_embs = model.encode(candidate_keywords, normalize_embeddings=True)

    # 3. パラメータの設定
    MIN_SIM = 0.4
    TOP_N = math.ceil( len(text) / 50 )
    LAMBDA = 0.5
    
    # 4. 重要概念リストの実行
    selected_concepts, _ = mmr(
        doc_embedding=doc_emb, 
        words_embeddings=candidate_embs, 
        candidate_keywords=candidate_keywords, 
        top_k=TOP_N,
        lambda_param=LAMBDA,
        doc_sim_threshold=MIN_SIM
    )

    # 5. 結果の表示
    print("\nEmbedRank Result is...")
    if selected_concepts:
        print(selected_concepts)
        return selected_concepts
    else:
        print("概念を抽出できませんでした．パラメータ（MIN_SIM）の調整を推奨します．")

    return 



# ==========================================
# 本コードの妥当性検証
# ============================================
if __name__ == "__main__":
    text = "私は大学の授業を通じてSDGs(持続可能な開発目標)を学び、その理念に強く共感する一方で、実践のあり方には課題があると感じている。SDGsが掲げる貧困や教育、環境問題への取り組みは、現代社会にとって不可欠なものだ。大学でもエコバッグの利用や食品ロス削減など、学生の環境意識は着実に高まっている。こうした身近な行動の積み重ねが、社会全体の変化につながる可能性は大きい。しかし懸念もある。それは「SDGsウォッシュ」と呼ばれる、実質的な効果を伴わずに取り組みの姿勢だけを示す現象だ。SNSでSDGs関連の投稿をすることが一種の流行になっている面もあり、それが本当に課題解決につながっているのか疑問に思うことがある。大切なのは行動の「見た目」ではなく、実際にどれだけ変化を生み出しているかである。そこで私は、大学生として二つのことを意識したい。第一に、自分の行動の効果を検証する姿勢を持つこと。満足感で終わらせず、事実やデータに基づいて成果を確認する必要がある。第二に、個人の行動だけでなく、貧困や環境破壊を生む社会構造そのものにも目を向けることだ。政策提言やボランティア活動など、より大きな枠組みに関わる視点も欠かせないだろう。SDGsは単なるスローガンではなく、批判的に検証しながら実践すべき目標だと考える。理想と現実のギャップに向き合い、持続可能な社会の実現に向けて主体的に行動していきたい。"

    ImportantConceptsPipeline(text)