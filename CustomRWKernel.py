import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Compute directed product graph

def add_edge_to_PDG_if_possible(G1xG2,fs_node, sd_node, G1_edges, G2_edges):
    fs_graph_nodes_adjacency = (fs_node[0], sd_node[0]) in G1_edges or (sd_node[0], fs_node[0]) in G1_edges
    sd_graph_nodes_adjacency = (fs_node[1], sd_node[1]) in G2_edges or (sd_node[1], fs_node[1]) in G2_edges
    if fs_graph_nodes_adjacency and sd_graph_nodes_adjacency:
        if (fs_node, sd_node) not in G1xG2.edges:
            G1xG2.add_edge(fs_node, sd_node)
        else:
            if (sd_node, fs_node) not in G1xG2.edges:
                G1xG2.add_edge(sd_node, fs_node)
    return G1xG2

def compute_directed_product_graph(G1, G2):
    G1xG2 = nx.Graph()
        
    # Create nodes
    for g1_node in G1.nodes:
        for g2_node in G2.nodes:
            G1xG2.add_node((g1_node, g2_node))
    
    # Create edges
    G1_edges = G1.edges
    G2_edges = G2.edges
    
    for fs_node in G1xG2:
        for sd_node in G1xG2:
            if fs_node != sd_node:
                G1xG2 = add_edge_to_PDG_if_possible(G1xG2, fs_node, sd_node, G1_edges, G2_edges)
            
    return G1xG2
    
# Compute random walk kernel

def rwk_f(lbda, pdg, adj_matrix):
    E = np.array([[1] for i in range(0, len(pdg.nodes))])
    E_transposed = np.transpose(E)
    I = np.identity(len(pdg.nodes))
    rwk = np.dot(E_transposed, I-lbda*adj_matrix).dot(E)[0][0]
    if rwk < 0:
        rwk = 0
    return rwk

def compute_random_walk_kernel(G1, G2):
    pdg = nx.cartesian_product(G1, G2)
    lbda = -0.1
    adj_matrix = np.array(nx.adjacency_matrix(pdg).todense())
    return rwk_f(lbda, pdg, adj_matrix)
