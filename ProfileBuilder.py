import networkx as nx
import csv
import pandas as pd
from itertools import permutations 

class Graphlet():

    def __init__(self,file= None, test= False):
        self.test = test
        if file:
            self.end_host_lbls = {}  # for every endhost count of normal and anomaly flow
            #self.activity_graphlets = self.get_graphlets(file)
            #self.profile_graphlets = self.build_graphlets_profile()
            self.activity_graphlets = sorted(self.get_graphlets(file), key = lambda g: list(filter(lambda n : n[1]['type'] =='srcIP', list(g.nodes(data= True))))[0][0])
            self.profile_graphlets = sorted(self.build_graphlets_profile(), key = lambda g: list(filter(lambda n : n[1]['type'] =='srcIP', list(g.nodes(data= True))))[0][0])

    def build_graphlets_profile(self):
        graphlets =[]

        for graph in self.activity_graphlets:

            G = graph.copy()   

            srcIp_node = list(filter(lambda n : n[1]['type'] =='srcIP', list(G.nodes(data= True))))[0][0]
            #srcIP = list(filter(lambda n: n[1] =='srcIP', list(G.nodes(data = 'type')))) 
            #srcIp_node = list(G.nodes)[0] # to recheck

            datas = []

            significant_set = [node for (node, degree) in G.degree() if degree > 2]

            protocols = list(filter(lambda n: n[1] =='protocol', list(G.nodes(data = 'type')))) 
            dstIPs = list(filter(lambda n: n[1] =='dstIP', list(G.nodes(data = 'type')))) 


            for protocol_node in protocols:
                #print("Protocol: ", protocol_node)
                add_protocol = False

                for dstIp_node in G.neighbors(protocol_node[0]):
                    #print("** dstIP: ", dstIp_node)
                    add_dstIP = False 

                    if dstIp_node in significant_set:
                        add_protocol = True 
                        add_dstIP = True


                    for sPort_node in G.neighbors(dstIp_node):
                       # print("*** sPort: ",sPort_node)

                        if sPort_node in significant_set:
                            add_protocol = True 
                            add_dstIP = True


                        for dPort_node in G.neighbors(sPort_node):

                            if dPort_node in significant_set:
                                add_protocol = True 
                                add_dstIP = True


                            for dstIP_ in G.neighbors(dPort_node):
                                if add_dstIP:
                                    datas.append([srcIp_node,dstIp_node,protocol_node[0], sPort_node, dPort_node])

            graphlets.append(self.generate_graphlet(srcIp_node, datas))
        
        for activity_g, prof_g in zip(self.activity_graphlets, graphlets):
            true_edges = activity_g.edges.data()
            edges_to_remove = []
            for edge in prof_g.edges.data():
                if edge not in true_edges:
                    edges_to_remove.append(edge)
            #print(edges_to_remove)
            prof_g.remove_edges_from(edges_to_remove)

        return graphlets

    def get_graphlets_label(self, threshold=0):
        res = []
        for key, val in self.end_host_lbls.items():
            if 'normal' not in val:
                res.append('anomaly')
            elif 'anomaly' in val and val['anomaly'] / (val['normal'] + val['anomaly']) >= threshold:
                res.append('anomaly')
            else:
                res.append('normal')
        
        res = [x for _, x in sorted(zip(self.end_host_lbls.keys(),res), key=lambda pair: pair[0])]
        
        return res


    def draw_graphlets(self):
        pass

    # Reads the csv file and generates a list with all srcIP (the number of graphlets to generate) and all the data
    def get_infos(self,file):
        csv_reader = csv.reader(open(file), delimiter=',')

        # Get the number of graphlets
        src_ip_set = set()
        data = []

        for row in csv_reader:
            src_ip_set.add(row[0])
            l = [row[0], row[1], row[2], row[3], row[4], row[5]] if not self.test else [row[0], row[1], row[2], row[3], row[4]]
            data.append(l)
            if not self.test:
                if row[0] in self.end_host_lbls.keys():
                    if row[5] in self.end_host_lbls[row[0]]:
                        self.end_host_lbls[row[0]][row[5]] += 1
                    else:
                        self.end_host_lbls[row[0]][row[5]] = 1
                else:
                    self.end_host_lbls[row[0]] = {row[5]:1}

        return src_ip_set, data


    # Filters the data according to a given srcIP
    def filter_data(self, src_ip, data_list):
        filtered_data_list = []

        for data in data_list:
            if data[0] == src_ip:
                filtered_data_list.append(data)

        return filtered_data_list


    def add_edges_to_graphlet(self,G, src_ip, data_list):
        for data in data_list:
            src_ip =  data[0]
            if not data[1].startswith('di'):
                dst_ip = 'di' + data[1]
                protocol = 'pr' +  data[2]
                s_port = 'sp' + data[3]
                d_port = 'dp' + data[4]
            else:
                dst_ip =  data[1]
                protocol =   data[2]
                s_port =  data[3]
                d_port = data[4]

            G.add_edge(src_ip, protocol)
            G.add_edge(protocol, dst_ip)
            G.add_edge(dst_ip, s_port)
            G.add_edge(s_port, d_port)
            G.add_edge(d_port, '_' + dst_ip)

        return G



    def add_nodes_to_graphlet(self, G, src_ip, data_list):
        dst_ip_set = set()
        protocol_set = set()
        sport_set = set()
        dport_set = set()

        for data in data_list:
            dst_ip_set.add(data[1])
            protocol_set.add(data[2])
            sport_set.add(data[3])
            dport_set.add(data[4])
        
        G.add_node(src_ip, type='srcIP')
        

        for dst_ip in dst_ip_set:
            if not dst_ip.startswith('di'):
                G.add_node('di' + dst_ip, type='dstIP')
                G.add_node('_di' + dst_ip, type='_dstIP')
            else:
                G.add_node(dst_ip, type='dstIP')
                G.add_node('_' + dst_ip, type='_dstIP')

        for protocol in protocol_set:
            if not protocol.startswith('pr'):
                G.add_node('pr' + protocol, type='protocol')
            else:
                G.add_node(protocol, type='protocol')

        for sport in sport_set:
            if not sport.startswith('sp'):
                G.add_node('sp' + sport, type='sPort')
            else:
                G.add_node(sport, type='sPort')

        for dport in dport_set:
            if not dport.startswith('dp'):
                G.add_node('dp' + dport, type='dPort')
            else:
                G.add_node(dport, type='dPort')        
      
        return G


    # Generates a graphlet for an srcIP
    def generate_graphlet(self, src_ip, data_list):
        G = nx.DiGraph()

        G = self.add_nodes_to_graphlet(G, src_ip, data_list)
        G = self.add_edges_to_graphlet(G, src_ip, data_list)

        return G


    # Generates all graphlets
    def get_graphlets(self,file):
        graphlets = []
        src_ip_set, data_list = self.get_infos(file)

        for src_ip in src_ip_set:
            data_src_ip = self.filter_data(src_ip, data_list)            
            graphlets.append(self.generate_graphlet(src_ip, data_src_ip))

        return graphlets