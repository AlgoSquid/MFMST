import sys, getopt, random
import networkx as nx
import matplotlib.pyplot as plt


def main(argv):
    graph_file = ""
    try:
        # We get arguments that can be -h, -f, --help, --uwg
        opts, args = getopt.getopt(argv, "h:f:g:", ["help"])
    except getopt.GetoptError as err:
        # If argument in execution is unknown, an error is thrown
        print("\n" + str(err))
        usage("help")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h" or opt == "--help":
            usage("help")
            sys.exit()
        elif opt == "-f":
            graph_file = arg
        elif opt == "-g":
            graph_file = "Graphs\\test" + arg + ".uwg"
    if not graph_file:
        # If there is no graph file, we exit
        usage("file")
        sys.exit()

    # File is opened and data is parsed
    with open(graph_file) as file:
        num_nodes = int(file.readline())
        num_edges = int(file.readline())
        edge_list = [line.rstrip('\n') for line in file]

    # Each edge is given its mirror weight and is enumerated
    for i in range(num_edges):
        edge = edge_list[i]
        mirror_weight = edge_list[num_edges - 1 - i].split()[2]
        edge_list[i] = "{0} {1} {2}".format(edge, mirror_weight, i)

    # Graph is created using NetworkX
    G = nx.parse_edgelist(edge_list, data=(('weight', int), ("m_weight", int), ("id", int)))

    # Calculate the max of B - O(n log n) time
    weights = []
    for (u, v, wt) in G.edges.data("weight"):
        weights.append(wt)
    B = sum(sorted(weights, reverse=True)[:num_nodes - 1])

    # Calculate the min of B, that is the max of the two minimum spanning tress
    tree_edges = nx.minimum_spanning_edges(G, algorithm="kruskal", weight="weight")
    m_tree_edges = nx.minimum_spanning_edges(G, algorithm="kruskal", weight="m_weight")

    w_sum = 0
    mw_sum = 0
    for edge in tree_edges:
        w_sum += edge[2]["weight"]
    for edge in m_tree_edges:
        mw_sum += edge[2]["m_weight"]
    B_min = max(w_sum, mw_sum)

    # TODO: Insert function to call decision algorithm here

    # Initial weight check - O(n) time
    edges_to_remove = []
    for (u, v, wt) in G.edges.data("weight"):
        if wt > B:
            edges_to_remove.append((u, v))
    for u,v in edges_to_remove:
        G.remove_edge(u, v)
        print("Edge ({0},{1}) removed in initial weight check".format(u, v))

    # Connectivity check
    if len(list(nx.k_edge_components(G, k=1))) > 1:
        print("No solution was possible with chosen B (connectivity)")
        sys.exit()

    # All bridges are identified and compared to B
    bridges = list(nx.bridges(G))
    bridge_w = 0
    bridge_mw = 0
    for u, v in bridges:
        bridge_w += G[u][v]["weight"]
        bridge_mw += G[u][v]["m_weight"]
    if bridge_w > B or bridge_mw > B:
        print("No solution was possible with chosen B (bridge weight)")
        sys.exit()

    # Naive MFMST algorithm
    # root = '1' # int(random.uniform(1, num_nodes + 1))
    # weight, m_weight = 0, 0
    # visited, stack = set(root), [root]
    # while(stack):
    #     v = stack.pop()
    #     neighbors = G.adj[v]
    #     for u in neighbors:
    #         if u not in visited:
    #             stack.append(u)
    #             visited.add(u)
    #             weight += G[v][u]["weight"]
    #             m_weight += G[v][u]["m_weight"]
    #
    # print(visited, weight, m_weight)

    print(B, B_min)
    i = 100000

    bridge_data = []
    for u, v in bridges:
        bridge_data.append((u, v, G[u][v]))
    non_bridges = [e for e in G.edges.data() if e not in bridge_data]

    mirror_friendly_spanning_tree = None
    w, mw = B, B
    sand = 0
    for _ in range(i):
        guess = random.sample(non_bridges, k= num_nodes - 1 - len(bridge_data))
        temp_G = nx.Graph()
        temp_G.add_edges_from(guess)
        temp_G.add_edges_from(bridge_data)
        if nx.is_tree(temp_G):
            sand += 1
            w_, mw_ = 0, 0
            for u, v in temp_G.edges:
                w_ += temp_G[u][v]["weight"]
                mw_ += temp_G[u][v]["m_weight"]
            if max(w_, mw_) < B:
                B = max(w_, mw_)
                w, mw = w_, mw_
                mirror_friendly_spanning_tree = temp_G

    print(w, mw)
    print(sand)
    G = mirror_friendly_spanning_tree

    # TODO: Printing, for fun
    layout = nx.spring_layout(G)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.drawing.draw(G, pos=layout, with_labels=True, node_size=150, font_size=9)
    nx.drawing.nx_pylab.draw_networkx_edge_labels(G, pos=layout, font_size=9, edge_labels=labels)
    plt.show()


def guess_tree(G, bridges, guesses):
    pass

def usage(usage_type):
    # Method for showing help, if this tool is running through commandline
    if usage_type == "help":
        print('\n*** USAGE ***' +
              '\n\n"mfmst_optimize.py -f <uwg file>" OR "mfmst_optimize.py -g <XX>"' +
              '\n\n*** WHERE ***' +
              '\n\n-f <uwg file>           is the path of an undirected weight graph (uwg) file' +
              '\n-g <XX>                 uses the graph at \\Graphs\\test<XX>.uwg' +
              '\n-h, --help              show this help' +
              '\n\n*************')
    elif usage_type == "file":
        print("\nError: missing graph file")
        usage("help")


if __name__ == "__main__":
    main(sys.argv[1:])
