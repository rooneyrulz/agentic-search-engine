from langgraph.graph import StateGraph


def export_graph_visualizations(graph: StateGraph) -> None:
    """
    Export the compiled graph as Mermaid (always) and PNG (if supported).
    Outputs:
    - graph.mmd: Mermaid diagram source
    - graph.png: PNG image (optional, if Graphviz/pydot available)
    """
    try:
        compiled_view = graph.get_graph(xray=True)
    except TypeError:
        # Fallback for older versions that don't support xray
        compiled_view = graph.get_graph()

    # Always write Mermaid
    mermaid_source = compiled_view.draw_mermaid()
    with open("graph.mmd", "w", encoding="utf-8") as fp:
        fp.write(mermaid_source)

    # Try to write PNG if the environment supports it
    try:
        compiled_view.draw_png("graph.png")
    except Exception:
        # Silently skip if PNG export isn't available
        pass

