import networkx as nx
import matplotlib.pyplot as plt
import random
import math

def generate_rpl_dodag(num_nodes=30, area_size=100, tx_range=35):
    """
    生成一个随机的RPL DODAG网络拓扑。
    
    :param num_nodes: 节点总数（节点0默认为DODAG Root）
    :param area_size: 部署区域的边长 (m)
    :param tx_range: 节点的最大通信半径 (m)
    """
    # 1. 物理层：随机生成节点位置
    physical_graph = nx.Graph()
    pos = {i: (random.uniform(0, area_size), random.uniform(0, area_size)) for i in range(num_nodes)}
    
    # 强制将Root节点（节点0）放置在区域中心以提高连通率
    pos[0] = (area_size / 2, area_size / 2)
    physical_graph.add_nodes_from(pos.keys())
    
    # 2. 链路层：基于通信半径建立物理链路
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            dist = math.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1])
            if dist <= tx_range:
                # 使用距离模拟链路质量（ETX的近似考量）
                physical_graph.add_edge(i, j, weight=dist)
                
    # 3. 网络层：构建DODAG (Destination Oriented Directed Acyclic Graph)
    root = 0
    dodag = nx.DiGraph()
    dodag.add_nodes_from(physical_graph.nodes(data=True))
    
    try:
        # 模拟DIO消息传播：计算从Root到所有节点的最短路径
        # RPL中DIO消息从Root向下游广播，节点根据目标函数(OF)选择父节点
        paths = nx.single_source_dijkstra_path(physical_graph, root, weight='weight')
        
        for node, path in paths.items():
            if node != root and len(path) > 1:
                # path列表的顺序是从root到node
                # 在DODAG中，当前节点的首选父节点（Preferred Parent）是路径上的前驱节点
                preferred_parent = path[-2]
                # 添加从子节点指向父节点的有向边（表示流量的默认上行方向）
                dodag.add_edge(node, preferred_parent)
                
    except nx.NetworkXNoPath:
        print("警告：存在孤立节点，网络未完全连通。请尝试增加tx_range或节点密度。")

    return physical_graph, dodag, pos

def visualize_topology(dodag, pos, root=0):
    """
    可视化DODAG拓扑
    """
    plt.figure(figsize=(10, 8))
    
    # 区分Root节点和普通节点
    node_colors = ['red' if node == root else 'skyblue' for node in dodag.nodes()]
    node_sizes = [500 if node == root else 300 for node in dodag.nodes()]
    
    # 绘制网络
    nx.draw(dodag, pos, 
            with_labels=True, 
            node_color=node_colors, 
            node_size=node_sizes, 
            edge_color='gray', 
            arrows=True, 
            arrowstyle='-|>', 
            arrowsize=15, 
            font_size=10, 
            font_weight='bold')
    
    plt.title("RPL DODAG Topology (Red = Root/LBR)")
    plt.show()

if __name__ == "__main__":
    # 生成包含40个节点，通信半径为30米的随机拓扑
    physical_g, rpl_dodag, node_positions = generate_rpl_dodag(num_nodes=40, area_size=100, tx_range=30)
    visualize_topology(rpl_dodag, node_positions)