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

    # Calculate start B - O(n log n) time
    weights = []
    for (u, v, wt) in G.edges.data("weight"):
        weights.append(wt)
    B = sum(sorted(weights, reverse=True)[:num_nodes - 1])

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
        print("No solution was possible with chosen B")
        sys.exit()

    # All bridges are identified and compared to B
    bridges = list(nx.bridges(G))
    bridge_w = 0
    bridge_mw = 0
    for u, v in bridges:
        bridge_w += G[u][v]["weight"]
        bridge_mw += G[u][v]["m_weight"]
    if bridge_w > B or bridge_mw > B:
        print("No solution was possible with chosen B")
        sys.exit()

    # Naive MFMST algorithm
    visited = set()
    root = int(random.uniform(0, num_nodes))

    # TODO: Printing, for fun
    layout = nx.spring_layout(G)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.drawing.draw(G, pos=layout, with_labels=True, node_size=150, font_size=9)
    nx.drawing.nx_pylab.draw_networkx_edge_labels(G, pos=layout, font_size=9, edge_labels=labels)
    plt.show()


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
