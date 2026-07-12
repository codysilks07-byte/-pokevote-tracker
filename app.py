    # Load previous votes if they exist
    if os.path.exists("votes.csv"):
        total_votes = pd.read_csv("votes.csv")
    else:
        total_votes = pd.DataFrame(columns=["pokemon", "votes"])

    new_votes = pd.DataFrame(
        leaderboard.items(),
        columns=["pokemon", "votes"]
    )

    combined = pd.concat([total_votes, new_votes], ignore_index=True)

    combined = (
        combined
        .groupby("pokemon", as_index=False)["votes"]
        .sum()
        .sort_values("votes", ascending=False)
    )

    combined.to_csv("votes.csv", index=False)

    df = combined.rename(
        columns={
            "pokemon": "Pokemon",
            "votes": "Votes"
        }
    )

    df["Drawn"] = df["Pokemon"].str.lower().isin(drawn)

    df = df.sort_values("Votes", ascending=False)

    st.success(f"Downloaded {len(comments)} comments")

    st.dataframe(df, use_container_width=True)

    remaining = df[df["Drawn"] == False]

    if len(remaining):
        winner = remaining.iloc[0]

        st.success(
            f"⭐ Recommended Next Pokémon: {winner['Pokemon']} ({winner['Votes']} votes)"
        )
