# %%
import pandas as pd

# %%
with open("canais.txt", "r") as f:
    canais = f.readlines()

first_channel = canais[0].split("/@")[-1].strip()


# %%
# def get_data_from_folder(folder):
#     # recent = pd.read_csv(f"./data/{folder}/videos.csv")
#     # top = pd.read_csv(f"./data/{folder}/top_videos.csv")
#     recent_top = pd.read_parquet(f"./data/{folder}/videos_sorted.parquet")
#     lifetime = pd.read_csv(f"./data/{folder}/lifetime.csv")
#     last_30_days = pd.read_csv(f"./data/{folder}/last_30days.csv")

#     print(pd.concat([recent_top, lifetime, last_30_days], axis=1))
#     # join


# get_data_from_folder(first_channel)
