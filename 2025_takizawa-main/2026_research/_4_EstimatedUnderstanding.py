import networkx as nx
import numpy as np
from typing import Dict



# =======================================
# サブグラフの生成
# =======================================
def generate_subgraphs(G: nx.DiGraph) -> dict[int, nx.DiGraph]:
    """
    グラフから，葉ノードではない任意のノードを根ノードとし，そこから到達可能なすべての葉ノードを辿るサブグラフを生成する

    nx.descendants(G, root_node) は，指定したノード「未満」の全てのノードを返す
    """
        
    if G.number_of_nodes() == 0:
        return 0
    
    else:
        all_subgraphs = {}
        
        # 1. 根ノードを特定する
        root_candidates = [n for n, degree in G.out_degree() if degree > 0]

        for root_node in root_candidates:
            # 2. 根ノードから到達可能な全てのノード（子孫）を特定する
            descendant_nodes = nx.descendants(G, root_node)
            descendant_nodes = descendant_nodes | {root_node} 
            
            # 3. サブグラフの作成
            SG = G.subgraph(descendant_nodes)
            
            # 4. 結果を保存
            all_subgraphs[root_node] = SG

        return all_subgraphs



# ============================================================================
# 理解度の推定
# ============================================================================
def analyze_degree(G: nx.DiGraph):
    """
    与えられたグラフの全ノードにおける，次数の平均と分散を計算する
    """
        
    degrees = [degree for node, degree in nx.degree(G)]
    ave_degree = np.mean(degrees)
    var_degree = np.var(degrees)

    return ave_degree, var_degree



def calculate_graph_depth(G: nx.DiGraph) -> int:
    """
    与えられたグラフGの深さを計算する
    """
    
    # key : ノード, value : そこから始まる最長経路長
    memo: Dict[int, int] = {}

    def dfs_longest_path(u: int) -> int:
        """
        ノード u から開始する最長経路長を計算する再帰関数

        .successors()は，そこから直接伸びた先のノードの一覧を返す
        """

        if u in memo:
            return memo[u]
        
        if not G.successors(u): 
            memo[u] = 0
            return 0
        
        max_len = 0
        # 隣接ノードに対して再帰的に処理していくことで，最長経路を求める
        for v in G.successors(u):
            current_path_len = 1 + dfs_longest_path(v)
            max_len = max(max_len, current_path_len)
        
        memo[u] = max_len
        return max_len

    # グラフ全体の深さの計算
    max_depth = 0
    for node in G.nodes():
        depth_from_node = dfs_longest_path(node)
        max_depth = max(max_depth, depth_from_node)
        
    return max_depth



def estimate_understanding(G: nx.DiGraph):
    if G.number_of_nodes() == 0:
        return 0.0
    
    else:
        ave_degree, var_degree = analyze_degree(G)
        depth = calculate_graph_depth(G)
        understanding = (ave_degree * depth) / (var_degree + 0.4)

    return understanding



# =================================================================
# 理解不足の概念の特定
# =================================================================
def identify_min_understanding_node(subgraphs: dict[int, nx.DiGraph], theme_term: str) -> int:
    """
    全てのサブグラフに対して理解度を推定し，理解度最低のサブグラフにおける根ノードを特定する
    """
    
    min_understanding = float('inf') # infinity
    min_node = -1 

    for root_node, subgraph in subgraphs.items():
        # 1. root_nodeとtheme_termが等しい場合はスキップする
        if root_node == theme_term:
            continue

        # 2. 理解度の推定を実行
        current_understanding = estimate_understanding(subgraph)
        
        # 3. 現在の最小値と比較し、更新する
        if current_understanding < min_understanding:
            min_understanding = current_understanding
            min_node = root_node
            
    return min_node



# =================================================================
# パイプライン全体の実行
# =================================================================
def EstimatedUnderstandingPipeline(G, nodes, theme_term):
    # 1. 理解度の推定
    print("Step 1 : Estimating Understanding Starts...")
    understanding = estimate_understanding(G)
    print(f"理解度: {understanding}")

    # 2. サブグラフ作成
    print("Step 2 : Creating Subgraphs Starts...")
    subgraphs = generate_subgraphs(G)

    # 3. サブグラフの理解度が最低のときの，根ノードの特定
    print("Step 3 : Estimating Min Understanding Node Starts...")
    if subgraphs == 0:
        min_understanding_node = nodes # 一つしかない場合はノードを返す
    else:
        min_understanding_node = identify_min_understanding_node(subgraphs, theme_term)
    print(min_understanding_node)

    return understanding, min_understanding_node



# =============================================================
# 本コードの妥当性検証
# =============================================================
