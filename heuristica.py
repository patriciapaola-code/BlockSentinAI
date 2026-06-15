from networkx.utils import UnionFind

def multiInputHeuristic(G):

    uf = UnionFind()

    for no in G.nodes():

        predecessores = list(
            G.predecessors(no)
        )

        if len(predecessores) > 1:

            principal = predecessores[0]

            for carteira in predecessores[1:]:

                uf.union(
                    principal,
                    carteira
                )

    return uf