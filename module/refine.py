from typing import List
import pandas as pd


def assign_columns(
    df: pd.DataFrame,
    txs: List[str],
    address_len: int = 5,
):
    _df = df.loc[df["transaction_hash"].isin(txs)]
    if len(_df) == 0:
        return None
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
        _amount_num=_df._amount.astype(float),
    )
    _df = _df.assign(
        addresses=[
            ",".join(sorted([from_address, to_address]))
            for from_address, to_address in zip(_df["from_address"], _df["to_address"])
        ],
        from_address_=[address[-address_len:] for address in _df["from_address"]],
        to_address_=[address[-address_len:] for address in _df["to_address"]],
    )
    _df = _df.assign(
        edge_attr=[
            f"{from_address_}->{to_address_}: {name_}_{amount_}"
            for from_address_, to_address_, name_, amount_ in zip(
                _df["from_address_"],
                _df["to_address_"],
                _df["name"],
                _df["_amount_num"],
            )
        ],
    )
    return _df


def get_loss_gain(
    df,
    address_len: int = 5,
):
    _loss_df = (
        df.groupby(["from_address", "name"])
        ._amount_num.sum()
        .reset_index()
        .rename(
            columns={
                "from_address": "address",
                "_amount_num": "loss",
            }
        )
    )
    _gain_df = (
        df.groupby(["to_address", "name"])
        ._amount_num.sum()
        .reset_index()
        .rename(columns={"to_address": "address", "_amount_num": "gain"})
    )
    _balance_df = _loss_df.merge(_gain_df, how="outer", on=["address", "name"]).fillna(
        0
    )
    _balance_df = _balance_df.assign(
        balance_change=round(_balance_df["gain"] - _balance_df["loss"], 3)
    )
    _balance_df = _balance_df.loc[_balance_df["balance_change"] != 0]
    _balance_df = _balance_df.assign(
        address_=[address[-address_len:] for address in _balance_df["address"]],
    )
    return _balance_df


def get_edge_label(df, edge_label_name="edge_attr"):
    _edge_labels_df = (
        df.groupby(["addresses"])[edge_label_name]
        .apply(lambda x: "<br>".join(x))
        .reset_index()
    )
    return _edge_labels_df
