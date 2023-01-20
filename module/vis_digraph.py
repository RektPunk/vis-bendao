import pandas as pd
import networkx as nx
import plotly.graph_objects as go


def get_nodes(
    df: pd.DataFrame,
    balance_df: pd.DataFrame,
    from_: str,
    to_: str,
    _nx_network_info = None,
):
    _df = df[[from_, to_]]
    if _nx_network_info is None:
        _nx_network_info = nx.from_pandas_edgelist(
            _df,
            source=from_,
            target=to_,
        )
    _node_location = nx.layout.spring_layout(_nx_network_info)
    node_x = []
    node_y = []
    node_names = []
    node_labels = []
    for node in _nx_network_info.nodes():
        _balance_change = balance_df.loc[balance_df["address_"] == node][["name", "balance_change"]].to_dict(orient = "records")
        _location_x, _location_y = _node_location[node]
        node_names.append(node)
        node_labels.append("P/L: " + '<br>'.join([_bc["name"] + " " + str(round(_bc["balance_change"], 2)) for _bc in _balance_change]))
        node_x.append(_location_x)
        node_y.append(_location_y)

    node_trace = go.Scatter(
        x = node_x,
        y = node_y,
        text = node_names,
        mode = "markers+text",
        hoverinfo = "text",
        hovertext = node_labels,
        textposition="top center",
        marker=dict(
            size=10,
            color="red",
        ),
        textfont=dict(
            color="red",
        ),
    )
    return (_node_location, node_trace, _nx_network_info)


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
            showlegend=True,
        ),
    )
    fig.update_layout(height=height, width=width)
    for _, edges in df.iterrows():
        _from = edges[from_]
        _to = edges[to_]
        _addresses = edges["addresses"]
        _edge_attr = edge_label_df.loc[edge_label_df["addresses"] == _addresses]["edge_attr"].values[0]
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
