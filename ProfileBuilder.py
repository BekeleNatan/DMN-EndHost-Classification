import networkx as nx
import csv
import pandas as pd


class Graphlet():

    def __init__(self,file):
        self.end_host_lbls = {}  # for every endhost count of normal and anomaly flow
        self.activity_graphlets = self.get_graphlets(file)
        self.profile_graphlets = None

    def build_graphlets_profile(self):
        pass

    def get_graphlets_label(self, threshold=0):
        res = []
        for key, val in self.end_host_lbls.items():
            if 'normal' not in val:
                res.append('anomaly')
            elif 'anomaly' in val and val['anomaly'] / (val['normal'] + val['anomaly']) >= threshold:
                res.append('anomaly')
            else:
                res.append('normal')
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
            data.append([row[0], row[1], row[2], row[3], row[4], row[5]])
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
            src_ip = data[0]
            dst_ip = data[1]
            protocol = data[2]
            s_port = data[3]
            d_port = '_' + data[4]

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
            G.add_node(dst_ip, type='dstIP')
            G.add_node('_' + dst_ip, type='dstIP')

        for protocol in protocol_set:
            G.add_node(protocol, type='protocol')

        for sport in sport_set:
            G.add_node(sport, type='sPort')

        for dport in dport_set:
            G.add_node('_' + dport, type='dPort')

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