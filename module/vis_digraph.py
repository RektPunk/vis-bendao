import pandas as pd
import networkx as nx
import plotly.graph_objects as go


def get_nodes(
    df: pd.DataFrame,
    from_: str,
    to_: str,
):
    _df = df[[from_, to_]]
    _nx_network_info = nx.from_pandas_edgelist(
        _df,
        source=from_,
        target=to_,
    )
    _node_location = nx.layout.spring_layout(_nx_network_info)
    node_x = []
    node_y = []
    node_labels = []
    for node in _nx_network_info.nodes():
        _location_x, _location_y = _node_location[node]
        node_labels.append(node)
        node_x.append(_location_x)
        node_y.append(_location_y)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        text=node_labels,
        mode="markers+text",
        hoverinfo="text",
        textposition="top center",
        marker=dict(
            size=10,
            color="red",
        ),
        textfont=dict(
            color="red",
        ),
        name="wallet",
    )
    return (_node_location, node_trace)


def vis_digraph(
    df: pd.DataFrame,
    from_: str,
    to_: str,
    edge_label_name: str,
    node_location,
    node_trace: go.Scatter,
    height: int,
    width: int,
) -> go.Figure:
    _df = df[[from_, to_, edge_label_name]]
    _edge_df = (
        _df.groupby([from_, to_])[edge_label_name]
        .apply(lambda x: ", ".join(x))
        .reset_index()
    )
    fig = go.Figure(
        node_trace,
        layout=go.Layout(
            hovermode="closest",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            showlegend=True,
        ),
    )
    fig.update_layout(height=height, width=width)
    for _, edges in _edge_df.iterrows():
        _from = edges[from_]
        _to = edges[to_]
        _edge_label = edges[edge_label_name]
        _location_from_x, _location_from_y = node_location[_from]
        _location_to_x, _location_to_y = node_location[_to]
        fig.add_annotation(
            dict(
                x=_location_to_x,
                y=_location_to_y,
                ax=_location_from_x,
                ay=_location_from_y,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                showarrow=True,
                arrowhead=3,
                arrowsize=3,
                arrowwidth=1,
                arrowcolor="grey",
            ),
        )
        fig.add_annotation(
            dict(
                x=(_location_from_x + _location_to_x) / 2,
                y=(_location_from_y + _location_to_y) / 2,
                text=_edge_label,
                font=dict(color="grey", size=12),
                showarrow=True,
                arrowhead=0,
                arrowcolor="grey",
            )
        )
    return fig
