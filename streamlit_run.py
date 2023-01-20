import pandas as pd
import streamlit as st
from streamlit_tags import st_tags_sidebar
from module.refine import assign_columns, get_loss_gain, get_edge_label
from module.vis_digraph import get_nodes, vis_digraph
from st_aggrid import AgGrid, GridOptionsBuilder


DATA_FILENAME = "data/benddao.parquet"
df = pd.read_parquet(DATA_FILENAME)

st.set_page_config(
    page_title="BendDao txs",
    layout="wide",
)
st.write("# BendDao trace tracker")

st.sidebar.write("# Input transaction hash")

maxtags_sidebar = st.sidebar.slider(
    "Number of transactions allowed?", 1, 5, 3, key="ehikwegrjifbwreuk"
)

height = st.sidebar.slider("Height", 100, 1000, 800)

width = st.sidebar.slider("Width", 100, 1000, 800)

st.session_state.transactions = st_tags_sidebar(
    label="# Input transaction hash:",
    text="Press enter to add more",
    value=[],
    maxtags=maxtags_sidebar,
    key="afrfae",
)

st.sidebar.write("### Inputs:")
st.sidebar.write((st.session_state.transactions))

if len(st.session_state.transactions) != 0:
    _df = assign_columns(
        df=df,
        txs=st.session_state.transactions,
    )
    if _df is None:
        st.write("Not availiable")
    else:
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
            _aggrid_df,
            gridOptions=transactions_vis_grid_options,
            height=350,
            width="100%",
            reload_data=False,
        )

        _balance_df = get_loss_gain(
            df=_df,
        )

        st.write("### Balance change:")
        balance_vis_builder = GridOptionsBuilder.from_dataframe(_balance_df)
        balance_vis_builder.configure_pagination(paginationAutoPageSize=True)
        balance_vis_builder.configure_side_bar()
        balance_vis_grid_options = balance_vis_builder.build()
        balance_aggrid_response = AgGrid(
            _balance_df,
            gridOptions=balance_vis_grid_options,
            height=350,
            width="100%",
            reload_data=False,
        )
        _selected_df = pd.DataFrame(transactions_aggrid_response["selected_rows"])

        node_location, node_trace = get_nodes(
            df=_df,
            balance_df=_balance_df,
            from_="from_address_",
            to_="to_address_",
        )
        whole_transaction_fig = vis_digraph(
            _df,
            _edge_labels_df,
            "from_address_",
            "to_address_",
            node_location,
            node_trace,
            height,
            width,
        )
        whole_info_col, selected_info_col = st.columns(2)
        with whole_info_col:
            st.write("### Transactions graph")
            st.plotly_chart(whole_transaction_fig, height=height, width=width)

        with selected_info_col:
            if len(_selected_df) != 0:
                st.write("### Selected rows graph")
                _selected_balance_df = get_loss_gain(_selected_df)
                _selected_node_location, _selected_node_trace = get_nodes(
                    df=_df,
                    balance_df=_selected_balance_df,
                    from_="from_address_",
                    to_="to_address_",
                    node_location=node_location,
                )
                _selected_edge_labels_df = get_edge_label(_selected_df)
                selected_transaction_fig = vis_digraph(
                    _selected_df,
                    _selected_edge_labels_df,
                    "from_address_",
                    "to_address_",
                    _selected_node_location,
                    _selected_node_trace,
                    height,
                    width,
                )
                st.plotly_chart(selected_transaction_fig, height=height, width=width)
                st.write("### Selected rows balance change")
                _selected_balance_df = get_loss_gain(_selected_df)
                selected_balance_vis_builder = GridOptionsBuilder.from_dataframe(
                    _selected_balance_df
                )
                selected_balance_vis_builder.configure_pagination(
                    paginationAutoPageSize=True
                )
                selected_balance_vis_builder.configure_side_bar()
                selected_balance_vis_builder.configure_selection(
                    groupSelectsChildren="Group checkbox select children",
                )
                selected_balance_grid_options = selected_balance_vis_builder.build()
                selected_balance_response = AgGrid(
                    _selected_balance_df,
                    gridOptions=selected_balance_grid_options,
                    height=350,
                    width="100%",
                    reload_data=False,
                )
