import sys, getopt, random, itertools
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

    # Calculate starting B and B_min (that is the minimum value B could obtain)
    # B_min is the max of the two minimal spanning trees
    # B is the minimum of the maximum weights in the two minimum spanning trees
    tree_edges = nx.minimum_spanning_edges(G, algorithm="kruskal", weight="weight")
    m_tree_edges = nx.minimum_spanning_edges(G, algorithm="kruskal", weight="m_weight")

    w_sum, mw_sum = 0, 0
    for edge in tree_edges:
        w_sum += edge[2]["weight"]
        mw_sum += edge[2]["m_weight"]

    if mw_sum <= w_sum:
        tree = nx.Graph()
        tree.add_edges_from(tree_edges)
        output_solution(G, tree, w_sum)

    B, B_min = max(w_sum, mw_sum), w_sum

    w_sum, mw_sum = 0, 0
    for edge in m_tree_edges:
        w_sum += edge[2]["weight"]
        mw_sum += edge[2]["m_weight"]

    if w_sum <= mw_sum:
        tree = nx.Graph()
        tree.add_edges_from(m_tree_edges)
        output_solution(G, tree, mw_sum)

    B, B_min = min(B, max(w_sum, mw_sum)), max(B_min, mw_sum)

    # Initial weight check - O(n) time
    edges_to_remove = []
    for (u, v, wt) in G.edges.data("weight"):
        if wt > B:
            edges_to_remove.append((u, v))
    for u, v in edges_to_remove:
        G.remove_edge(u, v)
        print("Edge ({0},{1}) removed in initial weight check".format(u, v))

    tree, B_opt = naive_edge_solution(G, B, B_min)
    # tree, B_opt = find_random_tree(G, B, B_min, 10000)
    # tree, B_opt = naive_tree_solution(G, B, B_min)

    output_solution(G, tree, B_opt)


def find_random_tree(G, B, B_min, iterations):
    bridge_data = []
    for u, v in nx.bridges(G):
        bridge_data.append((u, v, G[u][v]))
    non_bridges = [e for e in G.edges.data() if e not in bridge_data]

    mirror_friendly_spanning_tree = None
    for _ in range(iterations):
        guess = random.sample(non_bridges, k=len(G.nodes) - 1 - len(bridge_data))
        temp_G = nx.Graph()
        temp_G.add_edges_from(guess)
        temp_G.add_edges_from(bridge_data)
        if nx.is_tree(temp_G):
            w_, mw_ = 0, 0
            for u, v in temp_G.edges:
                w_ += temp_G[u][v]["weight"]
                mw_ += temp_G[u][v]["m_weight"]
            if max(w_, mw_) < B:
                print("The value of B is " + str(B))        # TODO: Remove
                B = max(w_, mw_)
                mirror_friendly_spanning_tree = temp_G
                if B == B_min: break
    print("The value of B is " + str(B))                    # TODO: Remove
    return mirror_friendly_spanning_tree, B


def naive_edge_solution(G, B, B_min):
    bridge_data = []
    for u, v in nx.bridges(G):
        bridge_data.append((u, v, G[u][v]))
    non_bridges = [e for e in G.edges.data() if e not in bridge_data]
    combinations = itertools.combinations(non_bridges, len(G.nodes) - 1 - len(bridge_data))

    mirror_friendly_spanning_tree = None
    for comb in combinations:
        temp_G = nx.Graph()
        temp_G.add_edges_from(comb)
        temp_G.add_edges_from(bridge_data)
        if nx.is_tree(temp_G):
            w_, mw_ = 0, 0
            for u, v in temp_G.edges:
                w_ += temp_G[u][v]["weight"]
                mw_ += temp_G[u][v]["m_weight"]
            if max(w_, mw_) < B:
                print("The value of B is " + str(B))        # TODO: Remove
                B = max(w_, mw_)
                mirror_friendly_spanning_tree = temp_G
                if B == B_min: break
    print("The value of B is " + str(B))                    # TODO: Remove
    return mirror_friendly_spanning_tree, B


def naive_tree_solution(G, B, B_min):
    mirror_friendly_spanning_tree = None
    itertools.p
    return mirror_friendly_spanning_tree, B


def output_solution(G, tree, B):
    G_layout = nx.spring_layout(G)
    G_labels = nx.get_edge_attributes(G, 'weight')
    tree_layout = nx.spring_layout(tree)
    tree_labels = nx.get_edge_attributes(tree, 'weight')
    plt.subplot(121)
    plt.text(0.0, 1.0, "The optimal solution for B is " + str(B))
    nx.drawing.draw(G, pos=G_layout, with_labels=True, node_size=150, font_size=9)
    nx.drawing.nx_pylab.draw_networkx_edge_labels(G, pos=G_layout, font_size=9, edge_labels=G_labels)
    plt.subplot(122)
    nx.drawing.draw(tree, pos=tree_layout, with_labels=True, node_size=150, font_size=9)
    nx.drawing.nx_pylab.draw_networkx_edge_labels(tree, pos=tree_layout, font_size=9, edge_labels=tree_labels)
    plt.show()
    sys.exit()


def powerset(iterable):
    # powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    # Function from official doc: https://docs.python.org/3/library/itertools.html
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))


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