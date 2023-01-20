import pandas as pd
import streamlit as st
from streamlit_tags import st_tags_sidebar
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
    _df = df.loc[df["transaction_hash"].isin(st.session_state.transactions)]
    if len(_df) == 0:
        st.write("Not available")
    else:
        _df = _df.assign(
            _amount=[
                str(round(int(amount) / 10**18, 3))
                if (
                    name
                    in [
                        "Wrapped Ether",
                        "Aave interest bearing WETH",
                        "Bend debt bearing WETH",
                        "Bend interest bearing WETH",
                    ]
                    or "WETH" in name
                    or name is None
                )
                else amount
                for amount, name in zip(_df["amount"], _df["name"])
            ]
        )
        _df = _df.assign(
            edge_attr=[
                f"{name}_{_amount}"
                for name, _amount in zip(_df["name"], _df["_amount"])
            ],
        )
        _df = _df.assign(
            from_address_=[address[-5:] for address in _df["from_address"]],
            to_address_=[address[-5:] for address in _df["to_address"]],
        )
        
        _aggrid_df = _df[[
                "from_address_", 
                "to_address_",
                "token_address",
                "name",
                "_amount",
                "edge_attr",
        ]]
        grid_options_builder = GridOptionsBuilder.from_dataframe(_aggrid_df)
        grid_options_builder.configure_pagination(
            paginationAutoPageSize=True
        )
        grid_options_builder.configure_side_bar()
        grid_options_builder.configure_selection(
            "multiple",
            use_checkbox=True,
            groupSelectsChildren="Group checkbox select children",
        )
        gridOptions = grid_options_builder.build()

        aggrid_response = AgGrid(
            _aggrid_df,
            gridOptions=gridOptions,
            height=350,
            width="100%",
            reload_data=False,
        )
        _selected_df = pd.DataFrame(aggrid_response["selected_rows"])
        
        node_location, node_trace = get_nodes(
            df = _df,
            from_ = "from_address_",
            to_ = "to_address_",
        )
        whole_transaction_fig = vis_digraph(
            _df,
            "from_address_",
            "to_address_",
            "edge_attr",
            node_location,
            node_trace,
            height,
            width,
        )
        st.plotly_chart(whole_transaction_fig, height=height, width=width)
        if len(_selected_df) != 0:
            selected_transaction_fig = vis_digraph(
                _selected_df,
                "from_address_",
                "to_address_",
                "edge_attr",
                node_location,
                node_trace,
                height,
                width,
            )
            st.plotly_chart(selected_transaction_fig, height=height, width=width)
        
        
