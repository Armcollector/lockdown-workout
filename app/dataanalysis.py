import pandas as pd


def medals(df, player_df):
    """Dataframe

    Args:
        df (Pandas dataframe): pandas dataframe with (at least) player_id, exercise_id and reps
        player_df (pd): pandas dataframe with player_id and username


    Returns:
        Dataframe with username, gold, silver, bronze and points
    """

    if df.empty:
        table = pd.DataFrame([]).to_json(orient="split", index=False)
    else:
        df = df.pivot(
            index=["player_id", "dt"], columns="exercise_id", values="reps"
        ).fillna(0)
        df["sum_reps"] = df.sum(axis=1)

        df = df.reset_index()[["player_id", "dt", "sum_reps"]]

        df["rank"] = (
            df.groupby("dt")["sum_reps"].rank("min", ascending=False).astype(int)
        )
        df = df[df["rank"] <= 3]
        df = (
            df.groupby(["player_id", "rank"])
            .count()
            .reset_index()
            .pivot(index="player_id", columns="rank", values="dt")
            .fillna(0)
        )

        df = df.astype(int)

        if 2 not in df.columns:
            df[2] = 0
        if 3 not in df.columns:
            df[3] = 0

        df["points"] = df[1] * 3 + df[2] * 2 + df[3]
        df = df.merge(
            player_df[["id", "username"]], left_on="player_id", right_on="id"
        ).drop("id", axis=1)
        df = df[["username", 1, 2, 3, "points"]]

        table = df.to_json(orient="split", index=False)
    return table
