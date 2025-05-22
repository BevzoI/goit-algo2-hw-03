import networkx as nx
import pandas as pd
from typing import Dict, Tuple, List


def build_graph() -> nx.DiGraph:
    """Створюєм орієнтований граф логістичної мережі з пропускними здатностями."""
    G = nx.DiGraph()

    edges = [
        ("Термінал 1", "Склад 1", 25),
        ("Термінал 1", "Склад 2", 20),
        ("Термінал 1", "Склад 3", 15),
        ("Термінал 2", "Склад 3", 15),
        ("Термінал 2", "Склад 4", 30),
        ("Термінал 2", "Склад 2", 10),
        ("Склад 1", "Магазин 1", 15),
        ("Склад 1", "Магазин 2", 10),
        ("Склад 1", "Магазин 3", 20),
        ("Склад 2", "Магазин 4", 15),
        ("Склад 2", "Магазин 5", 10),
        ("Склад 2", "Магазин 6", 25),
        ("Склад 3", "Магазин 7", 20),
        ("Склад 3", "Магазин 8", 15),
        ("Склад 3", "Магазин 9", 10),
        ("Склад 4", "Магазин 10", 20),
        ("Склад 4", "Магазин 11", 10),
        ("Склад 4", "Магазин 12", 15),
        ("Склад 4", "Магазин 13", 5),
        ("Склад 4", "Магазин 14", 10),
    ]

    for u, v, capacity in edges:
        G.add_edge(u, v, capacity=capacity)

    return G


def compute_max_flow(G: nx.DiGraph, sources: List[str], sinks: List[str]) -> Tuple[int, Dict[str, Dict[str, int]]]:
    """Обчислює максимальний потік у мережі з використанням надджерела та надстоку."""
    super_source, super_sink = "Джерело", "Стік"

    for source in sources:
        G.add_edge(super_source, source, capacity=float('inf'))
    for sink in sinks:
        G.add_edge(sink, super_sink, capacity=float('inf'))

    flow_value, flow_dict = nx.maximum_flow(G, super_source, super_sink, flow_func=nx.algorithms.flow.edmonds_karp)

    G.remove_node(super_source)
    G.remove_node(super_sink)

    return flow_value, flow_dict


def calculate_terminal_to_store_flows(flow_dict: Dict[str, Dict[str, int]], sources: List[str], intermediate_nodes: List[str], sinks: List[str]) -> pd.DataFrame:
    """Обчислює потоки між терміналами та магазинами через склади та повертає їх у вигляді таблиці."""
    data = []

    for source in sources:
        for sink in sinks:
            total_flow = 0
            for intermediate in intermediate_nodes:
                flow_to_intermediate = flow_dict.get(source, {}).get(intermediate, 0)
                flow_from_intermediate = flow_dict.get(intermediate, {}).get(sink, 0)
                # Реальний потік через склад не може перевищувати найменший із двох
                flow = min(flow_to_intermediate, flow_from_intermediate)
                if flow > 0:
                    total_flow += flow
            if total_flow > 0:
                data.append({
                    "Термінал": source,
                    "Магазин": sink,
                    "Фактичний Потік (одиниць)": total_flow
                })

    return pd.DataFrame(data)


def analyze_results(flow_df: pd.DataFrame, total_flow: int) -> None:
    """Виводимо аналітику по отриманому потоку."""
    top_terminal = flow_df.groupby("Термінал")["Фактичний Потік (одиниць)"].sum().idxmax()
    bottom_stores = flow_df.groupby("Магазин")["Фактичний Потік (одиниць)"].sum().nsmallest(3)

    print(f"\nЗагальний максимальний потік: {total_flow} одиниць")
    print(f"Термінал з найбільшим потоком: {top_terminal}")
    print("Магазини з найменшим отриманим потоком:")
    print(bottom_stores)


def main() -> None:
    G = build_graph()
    sources = ["Термінал 1", "Термінал 2"]
    intermediate_nodes = ["Склад 1", "Склад 2", "Склад 3", "Склад 4"]
    sinks = [f"Магазин {i}" for i in range(1, 15)]

    max_flow, flow_distribution = compute_max_flow(G, sources, sinks)
    flow_df = calculate_terminal_to_store_flows(flow_distribution, sources, intermediate_nodes, sinks)

    print("Фактичні потоки між терміналами та магазинами:")
    print(flow_df.to_string(index=False))

    analyze_results(flow_df, max_flow)


main()
