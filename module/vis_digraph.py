from typing import List
import pandas as pd
import networkx as nx
import plotly.graph_objects as go


def get_nodes(
    df: pd.DataFrame,
    balance_df: pd.DataFrame,
    target_wallet: List[str],
    from_: str,
    to_: str,
    node_location=None,
):
    _df = df[[from_, to_]]
    _nx_network_info = nx.from_pandas_edgelist(
        _df,
        source=from_,
        target=to_,
    )
    if node_location is None:
        node_location = nx.layout.spring_layout(_nx_network_info)
    node_x = []
    node_y = []
    node_names = []
    node_labels = []
    node_colors = []
    for node in _nx_network_info.nodes():
        _balance_change = balance_df.loc[balance_df["address_"] == node][
            ["name", "balance_change"]
        ].to_dict(orient="records")
        _location_x, _location_y = node_location[node]
        node_names.append(node)
        node_labels.append(
            "P/L: "
            + "<br>".join(
                [
                    _bc["name"] + " " + str(round(_bc["balance_change"], 2))
                    for _bc in _balance_change
                ]
            )
        )
        if node in target_wallet:
            node_colors.append("blue")
        else:
            node_colors.append("red")
        node_x.append(_location_x)
        node_y.append(_location_y)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        text=node_names,
        mode="markers+text",
        hoverinfo="text",
        hovertext=node_labels,
        textposition="top center",
        marker=dict(
            size=10,
            color=node_colors,
        ),
        textfont=dict(
            color=node_colors,
        ),
    )
    return (node_location, node_trace)


def vis_digraph(
    df: pd.DataFrame,
    edge_label_df: pd.DataFrame,
    from_: str,
    to_: str,
    node_location,
    node_trace: go.Scatter,
    height: int,
    width: int,
) -> go.Figure:
    fig = go.Figure(
        node_trace,
        layout=go.Layout(
            hovermode="closest",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            showlegend=False,
        ),
    )
    fig.update_layout(height=height, width=width)
    for _, edges in df.iterrows():
        _from = edges[from_]
        _to = edges[to_]
        _addresses = edges["addresses"]
        _edge_attr = edge_label_df.loc[edge_label_df["addresses"] == _addresses][
            "edge_attr"
        ].values[0]
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
                text=_edge_attr,
                font=dict(color="grey", size=12),
                showarrow=True,
                arrowhead=0,
                arrowcolor="grey",
            )
        )
    return fig
