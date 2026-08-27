import json
from typing import List, Optional, Tuple, Set
from openai import OpenAI
# 実行時に型ヒント通りになっているかを確認する
# 型ヒントを定義するクラスの親クラスをBaseModelにすることでそれを実現する
from pydantic import BaseModel 
import numpy as np
import torch
from sentence_transformers import SentenceTransformer
import networkx as nx
# import matplotlib
# import matplotlib.pyplot as plt
# import japanize_matplotlib
# from matplotlib import font_manager




client = OpenAI(
    base_url="http://10.0.1.127:11434/v1",
    api_key="ollama"
)
MODEL_NAME = "gemma4:e4b"

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("cl-nagoya/ruri-v3-30m", device=device)



# ============================================================
# 出力関連の定義
# =================================================================
class ConceptEdge(BaseModel):
    source: str
    target: str
    label: str
    evidence_sentence: str



class ConceptGraph(BaseModel):
    edges: List[ConceptEdge]



def graph_to_json_list(edges: List["ConceptEdge"]) -> str:
    """
    概念グラフを，ターミナルで表示しやすいJSONリストに変換する関数

    [
      {"概念間の関係の根拠となる文": "...", "from": "...", "to": "...", "関係の種類": "..."},
      ...
    ]
    """

    output_data = []
    for e in edges:
        output_data.append({
            "概念間の関係の根拠となる文": e.evidence_sentence,
            "from": e.source,
            "to": e.target,
            "関係の種類": e.label,
        })
    return json.dumps(output_data, ensure_ascii=False, indent=2)



# =================================================================
# 概念グラフの作成
# =================================================================
def generate_concept_graph(text: str, terms: List[str]) -> ConceptGraph:
    prompt = f"""
        入力文章を読み、重要概念リストの要素間の関係性を有向グラフのエッジとして抽出してください。
        # 入力文章
        {text}
        # 重要概念リスト
        {terms}
        # 制約
        1. 結果的に見つかる関係性の数が少なくなっても良く，入力文章には表れない関係性を無理やり推測しないこと
        2. source と target は必ず重要概念リストから選択し、リストにない語彙やフレーズを絶対に使用しないこと
        3. label は「source と target の関係」であり、日本語の簡潔な名詞または名詞句として文章から推定すること
        4. evidence_sentence は「label の根拠」であり、文章中の該当箇所をそのまま引用すること．ただし複数箇所が該当する場合は，複数の文で構成すること．
        """
    
    response = client.responses.parse(
        model=MODEL_NAME,
        input=prompt,
        text_format=ConceptGraph,
        reasoning={"effort": "none"},
        temperature=0.0
    )
    raw_graph: ConceptGraph = response.output_parsed

    # コードによるフィルタリング
    filtered_edges: List[ConceptEdge] = []
    for edge in raw_graph.edges:
        source = edge.source
        target = edge.target

        is_valid = (source in terms) and (target in terms)

        # sourceとtargetが同じ（自己ループ）でないことを確認
        is_not_self_loop = (source != target)
        if is_valid and is_not_self_loop:
            filtered_edges.append(edge)
            
    return ConceptGraph(edges=filtered_edges)



def connect_theme_term(
    theme_term: str,
    existing_edges: List[ConceptEdge]
) -> List[ConceptEdge]:
    """
    テーマ概念を起点とし，各Componentにおけるルートノードに対して有向線を引く
    weakly_connected_componentsは、エッジの方向に関わらず、クラスターを抽出するのに適する
    """
    
    # 1. 既存のエッジからノードを抽出し，グラフを構築する
    G_temp = nx.DiGraph()
    for edge in existing_edges:
        G_temp.add_edge(edge.source, edge.target)
        
    # 2. グラフを連結成分（Connected Components）に分割する
    components_generator = nx.weakly_connected_components(G_temp)
    components: List[Set[str]] = list(components_generator)
    
    # 3. 各連結成分ごとにループ処理を行い、テーマ概念を接続する
    new_edges_list: List[ConceptEdge] = []
    
    # 既存のエッジのターゲットを追跡し、入口ノードを特定するのに使用する集合
    all_targets = set(edge.target for edge in existing_edges)
    
    for i, component_nodes in enumerate(components):
        
        # ルートノードを特定する
        root_nodes = component_nodes - all_targets
        
        if not root_nodes:
             root_nodes = component_nodes
        
        for node in root_nodes:
            # 新しいエッジを作成する
            new_evidence = f"テーマ「{theme_term}」との関係性（特殊エッジ）"
            new_edge = ConceptEdge(
                source=theme_term,
                target=node,
                label="テーマ的な関連性",
                evidence_sentence=new_evidence
            )
            new_edges_list.append(new_edge)
            
    return existing_edges + new_edges_list



# ================================================
# 3色法によるDAG判定と修正
# ==================================================
def find_back_edge_dfs(
    edges: List[ConceptEdge],
) -> Optional[Tuple[int, List[str]]]:
    '''
    まず，全てのエッジをadjという辞書に変換する
    次に，adjのキーである各ノードをキーに持つcolorという辞書を作成する
    次に，3色法に基づいて閉路を検出し，閉路が見つかった場合には逆行エッジのインデックスと閉路上のノードのリストを返す

    ・setdefault()は第一引数に指定したキーが辞書に存在しない場合には指定した値を設返し，ない場合には空リストを返すメソッド
    ・get()は辞書からキーを指定して値を取得する際，キーが存在しない場合にエラーを出さず，代わりにNoneを返すメソッド
    ・index(x)はリスト内の要素xの最初のインデックスを返すメソッド
    ・pop()はリストの最後の要素を削除して返すメソッド
    '''

    adj = {}
    for i, e in enumerate(edges):
        adj.setdefault(e.source, []).append((e.target, i))
        adj.setdefault(e.target, [])
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in adj}
    path_nodes: List[str] = [] # 訪問履歴

    def dfs(u: str):
        color[u] = GRAY
        path_nodes.append(u)
        for v, edge_idx in adj.get(u, []):
            if color[v] == WHITE:
                result = dfs(v)
                if result is not None:
                    return result
            elif color[v] == GRAY:
                cycle_start = path_nodes.index(v)
                cycle_nodes = path_nodes[cycle_start:] + [v]
                return edge_idx, cycle_nodes
        color[u] = BLACK
        path_nodes.pop()
        return None
    
    for node in list(adj.keys()):
        if color[node] == WHITE:
            result = dfs(node)
            if result is not None:
                return result
            
    return None



def is_dag(edges: List[ConceptEdge]) -> bool:
    return find_back_edge_dfs(edges) is None



def get_reversed_label(label: str) -> str:
    return f"{label}（逆）"



def reverse_edge(edges: List[ConceptEdge], idx: int, text: str) -> List[ConceptEdge]:
    e = edges[idx]
    new_label = get_reversed_label(e.label)
    edges = list(edges)
    edges[idx] = ConceptEdge(
        source=e.target, 
        target=e.source, 
        label=new_label, 
        evidence_sentence=e.evidence_sentence
    )
    return edges



def make_dag(edges: List[ConceptEdge], text: str, max_iter: int = 100) -> List[ConceptEdge]:
    edges = list(edges)
    for iteration in range(max_iter):
        result = find_back_edge_dfs(edges)
        if result is None:
            return edges
        
        edge_idx, cycle_nodes = result
        e = edges[edge_idx]
        
        edges = reverse_edge(edges, edge_idx, text)
     
    raise RuntimeError("最大試行回数を超過したためDAGへの変換に失敗しました")



# =================================================================
# パイプライン全体の実行
# =================================================================
def ConceptsMapPipeline(text: str, terms: List[str], theme_term:str) -> nx.DiGraph:
    print("\nSTEP 1 : Generate Graph...")
    graph = generate_concept_graph(text, terms)
    print(graph_to_json_list(graph.edges))

    print("\nSTEP 2 : Generate Connected Graph...")
    final_edges = connect_theme_term(theme_term, graph.edges)
    print(graph_to_json_list(final_edges))
    
    print("\nSTEP 3 : Judge DAG...")
    if is_dag(final_edges):
        print("　既にDAGでした")
        print(graph_to_json_list(final_edges))

    else:
        print("　DAGではありませんでした\nChange to DAG...")
        final_edges = make_dag(final_edges, text)
        print(graph_to_json_list(final_edges))
    
    # networkX型にしてreturnする
    G = nx.DiGraph()
    for edge in final_edges:
        G.add_edge(
            edge.source,
            edge.target
        )

    # 描画用
    # font_manager.fontManager.addfont("2026_research/ipaexg.ttf")
    # matplotlib.rc('font', family="IPAexGothic")
    # nx.draw(G, with_labels=True, font_family='IPAexGothic')
    # plt.savefig("graph.png")

    return G, graph_to_json_list(final_edges)



# ============================================================
# DAG化の妥当性検証（通常時コメントアウト）
# ================================================================
'''
def test_dag_recovery():
    """
    仮想データを用いて，DAG判定アルゴリズム及びDAG化アルゴリズムの妥当性を検証する関数
    """
    
    # 1. サイクル構造を持つエッジデータを作成する
    synthetic_edges: List[ConceptEdge] = [
        ConceptEdge(source="A", target="B", label="初期接触", evidence_sentence="AはBに関わる。"),
        ConceptEdge(source="B", target="C", label="影響拡大", evidence_sentence="BはCに影響を与える。"),
        ConceptEdge(source="C", target="A", label="フィードバック", evidence_sentence="Cは再びAに影響を及ぼす。"),
        # DAGとなるエッジを追加 (A -> D)
        ConceptEdge(source="A", target="D", label="直接的関連", evidence_sentence="AはDと直接関係する。"),
    ]
    
    text = "テスト用の文章です。"
    
    print("--- Step1 : DAG判定アルゴリズムの妥当性検証 ---")
    
    # 2. DAG判定の実行
    is_cyclic = find_back_edge_dfs(synthetic_edges)
    
    if is_cyclic is None:
        print("サイクルが存在するにもかかわらず、DAGと判定されました。")
    else:
        print("サイクルを正しく検出し、DAGと判定されました。")
        print(f"　検出されたサイクル: {is_cyclic[1]}")

    print("\n--- Step2 : DAG化アルゴリズムの妥当性検証 ---")
    
    # 3. ラベル変換処理をモック化し，常に「逆転した関係」というラベルを返す仕組みを作る
    def mock_get_reversed_label(*args, **kwargs) -> str:
        """
        *argは位置引数をタプルとして受け取り，**kwargsはキーワード引数を辞書として受け取る
        """
        return "逆転した関係"

    # 4. 実際に，ラベルをモック化した状態を作る
    global get_reversed_label
    get_reversed_label = mock_get_reversed_label
    
    # 5. DAG化の実行
    final_edges = make_dag(synthetic_edges, text, max_iter=5)
    is_final_dag = is_dag(final_edges)
    if is_final_dag:
        print("DAG化が確認できました")
    else:
        print("DAG化が確認できませんでした")
'''



# ============================================================
# 本コードの妥当性検証
# ================================================================
if __name__ == "__main__":
    text = """現実問題として、食糧価格の高騰は日本のみならず、他国でも少なからずみられている"""
    
    terms = ['食糧価格']

    theme_term = "食料市場機能の適正化と、情報公開による価格安定化の実現"
    
    # 実行
    ConceptsMapPipeline(text, terms, theme_term)

    # DAG化の妥当性検証の実行
    # test_dag_recovery()