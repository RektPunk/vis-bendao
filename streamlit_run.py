import pandas as pd
import streamlit as st
from streamlit_tags import st_tags_sidebar
from module.refine import (
    valid_data,
    assign_numeric_columns,
    assign_address_columns,
    assign_edge_attr_columns,
    get_loss_gain,
    get_edge_label,
)
from module.vis_digraph import get_nodes, vis_digraph
from st_aggrid import AgGrid, GridOptionsBuilder


DATA_FILENAME = "data/benddao.parquet"
df = pd.read_parquet(DATA_FILENAME)

st.set_page_config(
    page_title="BendDao txs",
    layout="wide",
)

st.write("# BendDao trace tracker")

st.sidebar.write("### Input transaction hash:")
maxtags_sidebar = st.sidebar.slider(
    label="Number of transactions allowed?",
    min_value=1,
    max_value=5,
    value=3,
)
st.session_state.transactions = st_tags_sidebar(
    text="Press enter to add more",
    label="",
    value=[
        "0x9a44a532e4798e49a4a5c87bba0f4aba95a36fdac0235513e48c8a9785d6ea44",
        "0xfff014e873e471a3de285ea90d0392036d11a28439fbfc2adab571e2af55b6e0",
    ],
    maxtags=maxtags_sidebar,
)
st.sidebar.write("### Inputs:")
st.sidebar.write((st.session_state.transactions))

st.sidebar.write("### Wallet encoding rule:")
wallet_encoding_rule_input = st.sidebar.text_area(
    label="",
    value="""{
    "00000": "NULL address"
}""",
)
try:
    wallet_encoding_rule = eval(wallet_encoding_rule_input)
    st.sidebar.json(wallet_encoding_rule)
except:
    wallet_encoding_rule = {}
    st.sidebar.write("Encoding failed")


st.sidebar.write("### Target wallet:")
st.session_state.target_wallet = st_tags_sidebar(
    text="Press enter to add more",
    label="",
    value=[
        "NULL address",
    ],
    maxtags=maxtags_sidebar,
)
st.sidebar.write("### Inputs:")
st.sidebar.write((st.session_state.target_wallet))


st.sidebar.write("### Viewable image size:")
height = st.sidebar.slider(
    label="Height",
    min_value=100,
    max_value=1000,
    value=800,
)
width = st.sidebar.slider(
    label="Width",
    min_value=100,
    max_value=1000,
    value=800,
)


if len(st.session_state.transactions) != 0:
    _df = valid_data(
        df=df,
        txs=st.session_state.transactions,
    )
    _selected_df = None
    if _df is None:
        st.write("Not availiable")
    else:
        _df = assign_numeric_columns(
            df=_df,
        )
        _df = assign_address_columns(
            df=_df,
        )
        _df = _df.replace(wallet_encoding_rule)
        _df = assign_edge_attr_columns(
            df=_df,
        )
        _edge_labels_df = get_edge_label(_df)
        _balance_df = get_loss_gain(
            df=_df,
        )
        _aggrid_df = _df[
            [
                "from_address_",
                "to_address_",
                "token_address",
                "name",
                "_amount",
                "edge_attr",
                "from_address",
                "to_address",
                "addresses",
                "_amount_num",
            ]
        ]
        st.write("### Raw data:")
        transactions_vis_builder = GridOptionsBuilder.from_dataframe(_aggrid_df)
        transactions_vis_builder.configure_pagination(paginationAutoPageSize=True)
        transactions_vis_builder.configure_side_bar()
        transactions_vis_builder.configure_selection(
            "multiple",
            use_checkbox=True,
            groupSelectsChildren="Group checkbox select children",
        )
        transactions_vis_grid_options = transactions_vis_builder.build()
        transactions_aggrid_response = AgGrid(
            data=_aggrid_df,
            gridOptions=transactions_vis_grid_options,
            height=350,
            width="100%",
            reload_data=False,
        )
        node_location, node_trace = get_nodes(
            df=_df,
            balance_df=_balance_df,
            target_wallet=st.session_state.target_wallet,
            from_="from_address_",
            to_="to_address_",
        )
        if len(transactions_aggrid_response["selected_rows"]) != 0:
            _selected_df = pd.DataFrame(transactions_aggrid_response["selected_rows"])
    transactions_tab, selected_tab = st.tabs(["Transactions", "Selected"])

    with transactions_tab:
        st.write("### Balance change:")
        st.dataframe(_balance_df)

        st.write("### Transactions graph:")
        transactions_fig = vis_digraph(
            df=_df,
            edge_label_df=_edge_labels_df,
            from_="from_address_",
            to_="to_address_",
            node_location=node_location,
            node_trace=node_trace,
            height=height,
            width=width,
        )
        st.plotly_chart(transactions_fig, height=height, width=width)

    with selected_tab:
        if _selected_df is not None:
            st.write("### Selected rows balance change:")
            _selected_balance_df = get_loss_gain(_selected_df)
            st.dataframe(_selected_balance_df)

            st.write("### Selected rows transactions graph:")
            _selected_node_location, _selected_node_trace = get_nodes(
                df=_df,
                balance_df=_selected_balance_df,
                target_wallet=st.session_state.target_wallet,
                from_="from_address_",
                to_="to_address_",
                node_location=node_location,
            )
            _selected_edge_labels_df = get_edge_label(_selected_df)
            selected_transaction_fig = vis_digraph(
                df=_selected_df,
                edge_label_df=_selected_edge_labels_df,
                from_="from_address_",
                to_="to_address_",
                node_location=_selected_node_location,
                node_trace=_selected_node_trace,
                height=height,
                width=width,
            )
            st.plotly_chart(selected_transaction_fig, height=height, width=width)
else:
    pass
