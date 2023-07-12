# %%
import pandas as pd

# %%
df = pd.read_csv("videos_sorted.csv")
# %%
df = df.sort_values(by=["channel_name", "subscribers"]).assign(
    subscribers=lambda df: df["subscribers"].fillna(method="ffill")
)
# %%
df.to_csv("videos_sorted.csv", index=False)
