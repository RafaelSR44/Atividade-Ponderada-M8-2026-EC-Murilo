"""
Atividade Avaliativa Individual — Smart Grid (Módulo 8)
Rafael Santana Rodrigues · RA 510288

Etapa 3: TAD Grafo (armazenado em um networkx.Graph), Dijkstra e Prim
implementados manualmente e validados contra as funções do NetworkX.
"""

import math
import sys

import networkx as nx

sys.stdout.reconfigure(encoding="utf-8")

NULO = None
INF = math.inf


class Grafo:
    """TAD Grafo não orientado e ponderado, com vértices S0..S(n-1)."""

    def __init__(self, n):
        self._g = nx.Graph()
        self._g.add_nodes_from(range(n))

    @property
    def n(self):
        return self._g.number_of_nodes()

    def rotulo(self, v):
        return f"S{v}"

    def adicionar_aresta(self, u, v, peso, nome=None):
        if peso is None or peso < 0:
            raise ValueError(f"Peso inválido em ({self.rotulo(u)}, {self.rotulo(v)}): {peso}")
        if u == v:
            raise ValueError("Laços não são permitidos")
        self._g.add_edge(u, v, weight=peso, nome=nome)

    def remover_aresta(self, u, v):
        self._g.remove_edge(u, v)

    def peso(self, u, v):
        """Retorna o peso do ramal (u, v) ou NULO se não houver conexão direta."""
        if self._g.has_edge(u, v):
            return self._g[u][v]["weight"]
        return NULO

    def vizinhos(self, u):
        return sorted(self._g.neighbors(u))

    def arestas(self):
        return [(u, v, d["weight"]) for u, v, d in self._g.edges(data=True)]

    def matriz(self):
        return [[self.peso(i, j) for j in range(self.n)] for i in range(self.n)]

    def simetrica(self):
        m = self.matriz()
        return all(m[i][j] == m[j][i] for i in range(self.n) for j in range(self.n))

    def como_networkx(self):
        return self._g.copy()

    def imprimir_matriz(self):
        cabecalho = "      " + "".join(f"{self.rotulo(j):>6}" for j in range(self.n))
        print(cabecalho)
        for i, linha in enumerate(self.matriz()):
            celulas = "".join(f"{'NULO' if w is NULO else w:>6}" for w in linha)
            print(f"{self.rotulo(i):>6}{celulas}")


def calcular_pesos(ra):
    """Aplica as fórmulas do enunciado aos 6 dígitos do RA."""
    d1, d2, d3, d4, d5, d6 = (int(c) for c in ra)
    return {
        "e1": (0, 1, 10 + d6 % 5),
        "e2": (0, 2, 15 + d5 % 7),
        "e3": (1, 2, 8 + d4 % 4),
        "e4": (1, 3, 12 + d3 % 6),
        "e5": (2, 4, 14 + d2 % 5),
        "e6": (2, 5, 9 + d1 % 6),
        "e7": (3, 4, 7 + (d5 + d6) % 5),
        "e8": (3, 6, 11 + (d4 + d5) % 6),
        "e9": (4, 5, 6 + (d3 + d4) % 4),
        "e10": (4, 7, 16 + (d2 + d3) % 7),
        "e11": (5, 7, 18 + (d1 + d2) % 8),
        "e12": (6, 7, 9 + (d5 + d1) % 5),
        "e13": (1, 4, 20 + d6 % 4),
    }


def dijkstra(grafo, origem, destino=None, verbose=False):
    """Dijkstra O(V²); em empate fecha o vértice aberto de menor índice."""
    n = grafo.n
    L = [INF] * n
    ant = [None] * n
    fechado = [False] * n
    ordem = []
    L[origem] = 0

    def fmt(v):
        if L[v] == INF:
            return "∞"
        return f"[{L[v]}]" if fechado[v] else str(L[v])

    if verbose:
        print(f"{'Iter.':<6}{'u':<4}{'L[u]':<6}" + "".join(f"{'L[' + grafo.rotulo(v) + ']':<7}" for v in range(n)) + "Antecessores atualizados")
        print(f"{'Inic.':<6}{'—':<4}{'—':<6}" + "".join(f"{fmt(v):<7}" for v in range(n)) + "Inicialização na origem " + grafo.rotulo(origem))

    for it in range(1, n + 1):
        abertos = [v for v in range(n) if not fechado[v] and L[v] < INF]
        if not abertos:
            break
        u = min(abertos, key=lambda v: (L[v], v))
        fechado[u] = True
        ordem.append(u)

        atualizados = []
        for v in grafo.vizinhos(u):
            if fechado[v]:
                continue
            nova = L[u] + grafo.peso(u, v)
            if nova < L[v]:
                L[v] = nova
                ant[v] = u
                atualizados.append(f"Ant[{grafo.rotulo(v)}] = {grafo.rotulo(u)}")

        if verbose:
            print(f"{it:<6}{grafo.rotulo(u):<4}{L[u]:<6}" + "".join(f"{fmt(v):<7}" for v in range(n)) + (", ".join(atualizados) or "Nenhum"))

        if u == destino:
            break

    return L, ant, ordem


def reconstruir_rota(ant, origem, destino):
    rota = [destino]
    while rota[-1] != origem:
        anterior = ant[rota[-1]]
        if anterior is None:
            return None
        rota.append(anterior)
    return rota[::-1]


def prim(grafo, raiz=0):
    """Prim O(V²) a partir da raiz; retorna as arestas da MST e o custo total."""
    n = grafo.n
    chave = [INF] * n
    pai = [None] * n
    na_arvore = [False] * n
    chave[raiz] = 0
    arestas = []

    for _ in range(n):
        u = min((v for v in range(n) if not na_arvore[v]), key=lambda v: (chave[v], v))
        if chave[u] == INF:
            raise ValueError("Grafo desconexo: não existe árvore geradora")
        na_arvore[u] = True
        if pai[u] is not None:
            arestas.append((pai[u], u, chave[u]))
        for v in grafo.vizinhos(u):
            w = grafo.peso(u, v)
            if not na_arvore[v] and w < chave[v]:
                chave[v] = w
                pai[v] = u

    return arestas, sum(w for _, _, w in arestas)


def main():
    ra = "510288"
    origem = 0
    destino = 7 if int(ra[5]) % 2 == 0 else 6

    grafo = Grafo(8)
    pesos = calcular_pesos(ra)
    for nome, (u, v, w) in pesos.items():
        grafo.adicionar_aresta(u, v, w, nome)

    rot = grafo.rotulo
    print(f"RA {ra} · origem {rot(origem)} · destino {rot(destino)}\n")

    print("Pesos dos ramais (km):")
    for nome, (u, v, w) in pesos.items():
        print(f"  {nome:<4}({rot(u)}, {rot(v)}) = {w}")
    assert all(w >= 0 for _, _, w in grafo.arestas()), "Há pesos negativos"
    print("  Validação: todos os pesos são não negativos\n")

    print("Matriz de adjacência 8×8 (km):")
    grafo.imprimir_matriz()
    print(f"  Simetria M[i][j] = M[j][i]: {grafo.simetrica()}\n")

    print("Teste de mesa (Dijkstra):")
    L, ant, ordem = dijkstra(grafo, origem, destino, verbose=True)
    rota = reconstruir_rota(ant, origem, destino)
    print(f"\nCusto mínimo acumulado {rot(origem)} → {rot(destino)}: {L[destino]} km")
    print("Rota ótima: " + " → ".join(rot(v) for v in rota))
    print("Ordem de fechamento: " + ", ".join(rot(v) for v in ordem) + "\n")

    arestas_mst, custo_mst = prim(grafo, origem)
    print("Árvore Geradora Mínima (Prim, raiz S0):")
    for u, v, w in arestas_mst:
        print(f"  ({rot(u)}, {rot(v)}) = {w}")
    print(f"  Custo total da MST: {custo_mst} km\n")

    print("Validação com NetworkX:")
    g_nx = grafo.como_networkx()
    custo_nx, rota_nx = nx.single_source_dijkstra(g_nx, origem, destino, weight="weight")
    mst_nx = nx.minimum_spanning_tree(g_nx, weight="weight", algorithm="prim")
    custo_mst_nx = mst_nx.size(weight="weight")
    print(f"  nx.single_source_dijkstra: {custo_nx} km, rota " + " → ".join(rot(v) for v in rota_nx))
    print(f"  nx.minimum_spanning_tree (prim): {custo_mst_nx:g} km")
    print(f"  Dijkstra confere: {custo_nx == L[destino] and rota_nx == rota}")
    print(f"  Prim confere: {custo_mst_nx == custo_mst}")


if __name__ == "__main__":
    main()
