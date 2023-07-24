# %%
import re, json, time
from selenium import webdriver
import os

# import By
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# from webdriver_manager.chrome import ChromeDriverManager
from parsel import Selector

import pandas as pd
import numpy as np


def scroll_page(url):
    # service = Service(ChromeDriverManager().install())

    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--lang=en")
    # options.add_argument(
    #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    # )

    driver = webdriver.Chrome()
    driver.get(url)

    # old_height = driver.execute_script(
    #     """
    #     function getHeight() {
    #         return document.querySelector('ytd-app').scrollHeight;
    #     }
    #     return getHeight();
    # """
    # )

    # while True:
    #     driver.execute_script(
    #         "window.scrollTo(0, document.querySelector('ytd-app').scrollHeight)"
    #     )

    #     time.sleep(2)

    #     new_height = driver.execute_script(
    #         """
    #         function getHeight() {
    #             return document.querySelector('ytd-app').scrollHeight;
    #         }
    #         return getHeight();
    #     """
    #     )

    #     if new_height == old_height:
    #         break

    #     old_height = new_height

    time.sleep(3)
    selector = Selector(driver.page_source)
    driver.quit()

    return selector


def scrape_all_data(selector):
    youtube_video_page = []

    all_script_tags = selector.css("script").getall()

    title = selector.css(".title .ytd-video-primary-info-renderer::text").get()

    # https://regex101.com/r/gHeLwZ/1
    views = int(
        re.search(r"(.*)\s", selector.css(".view-count::text").get())
        .group()
        .replace(",", "")
    )

    # https://regex101.com/r/9OGwJp/1
    likes = int(
        re.search(
            r"(.*)\s",
            selector.css(
                "#top-level-buttons-computed > ytd-toggle-button-renderer:first-child #text::attr(aria-label)"
            ).get(),
        )
        .group()
        .replace(",", "")
    )

    date = selector.css("#info-strings yt-formatted-string::text").get()

    duration = selector.css(".ytp-time-duration::text").get()

    # https://regex101.com/r/0JNma3/1
    keywords = (
        "".join(
            re.findall(r'"keywords":\[(.*)\],"channelId":".*"', str(all_script_tags))
        )
        .replace('"', "")
        .split(",")
    )

    # https://regex101.com/r/9VhH1s/1
    thumbnail = re.findall(
        r'\[{"url":"(\S+)","width":\d*,"height":\d*},', str(all_script_tags)
    )[0].split('",')[0]

    channel = {
        # https://regex101.com/r/xFUzq5/1
        "id": "".join(
            re.findall(r'"channelId":"(.*)","isOwnerViewing"', str(all_script_tags))
        ),
        "name": selector.css("#channel-name a::text").get(),
        "link": f'https://www.youtube.com{selector.css("#channel-name a::attr(href)").get()}',
        "subscribers": selector.css("#owner-sub-count::text").get(),
        "thumbnail": selector.css("#img::attr(src)").get(),
    }

    description = selector.css(
        ".ytd-expandable-video-description-body-renderer span:nth-child(1)::text"
    ).get()

    hash_tags = [
        {
            "name": hash_tag.css("::text").get(),
            "link": f'https://www.youtube.com{hash_tag.css("::attr(href)").get()}',
        }
        for hash_tag in selector.css(
            ".ytd-expandable-video-description-body-renderer a"
        )
    ]

    # https://regex101.com/r/onRk9j/1
    category = "".join(
        re.findall(r'"category":"(.*)","publishDate"', str(all_script_tags))
    )

    comments_amount = int(
        selector.css("#count .count-text span:nth-child(1)::text")
        .get()
        .replace(",", "")
    )

    comments = []

    for comment in selector.css("#contents > ytd-comment-thread-renderer"):
        comments.append(
            {
                "author": comment.css("#author-text span::text").get().strip(),
                "link": f'https://www.youtube.com{comment.css("#author-text::attr(href)").get()}',
                "date": comment.css(".published-time-text a::text").get(),
                "likes": comment.css("#vote-count-middle::text").get().strip(),
                "comment": comment.css("#content-text::text").get(),
                "avatar": comment.css("#author-thumbnail #img::attr(src)").get(),
            }
        )

    suggested_videos = []

    for video in selector.css("ytd-compact-video-renderer"):
        suggested_videos.append(
            {
                "title": video.css("#video-title::text").get().strip(),
                "link": f'https://www.youtube.com{video.css("#thumbnail::attr(href)").get()}',
                "channel_name": video.css("#channel-name #text::text").get(),
                "date": video.css("#metadata-line span:nth-child(2)::text").get(),
                "views": video.css("#metadata-line span:nth-child(1)::text").get(),
                "duration": video.css("#overlays #text::text").get().strip(),
                "thumbnail": video.css("#thumbnail img::attr(src)").get(),
            }
        )

    youtube_video_page.append(
        {
            "title": title,
            "views": views,
            "likes": likes,
            "date": date,
            "duration": duration,
            "channel": channel,
            "keywords": keywords,
            "thumbnail": thumbnail,
            "description": description,
            "hash_tags": hash_tags,
            "category": category,
            "suggested_videos": suggested_videos,
            "comments_amount": comments_amount,
            "comments": comments,
        }
    )

    print(json.dumps(youtube_video_page, indent=2, ensure_ascii=False))


def get_info_from_channel(channel_link: str):
    driver = webdriver.Chrome()

    driver.get(channel_link)
    driver.maximize_window()

    time.sleep(5)

    selector = Selector(text=driver.page_source)
    driver.quit()

    # channel title
    channel_title = selector.css("#text-container #text::text").get()

    # date joined //*[@id="right-column"]/yt-formatted-string[2]/span[2]
    date_joined = selector.css(
        "#right-column > yt-formatted-string:nth-child(2) > span:nth-child(2)::text"
    ).get()

    # total views //*[@id="right-column"]/yt-formatted-string[3]

    total_views = selector.css(
        "#right-column > yt-formatted-string:nth-child(3)::text"
    ).get()

    # total subs //*[@id="subscriber-count"]

    total_subs = selector.css("#subscriber-count::text").get()

    # total videos //*[@id="videos-count"]/span[1]

    total_videos = selector.css("#videos-count > span:nth-child(1)::text").get()

    channel_info = {
        "channel_title": channel_title,
        "date_joined": date_joined,
        "total_views": total_views,
        "total_subs": total_subs,
        "total_videos": total_videos,
    }

    print(json.dumps(channel_info, indent=2, ensure_ascii=False))

    return pd.DataFrame(channel_info, index=[0])


def get_info_from_video(selector) -> dict[str, str | int]:
    # title
    title = selector.css(".title .ytd-video-primary-info-renderer::text").get()

    if title == None:
        title = selector.css(
            "yt-formatted-string.style-scope.ytd-watch-metadata span.style-scope.yt-formatted-string::text"
        ).get()

    print(title)

    # date
    date = selector.css("#info-strings yt-formatted-string::text").get()

    # views
    views = selector.css("span.bold.style-scope.yt-formatted-string::text").get()

    # likes
    likes = selector.css(
        "#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button::attr(aria-label)"
    ).get()

    # comments
    try:
        comments_amount = int(
            selector.css("#count .count-text span:nth-child(1)::text")
            .get()
            .replace(",", "")
        )
    except Exception as e:
        comments_amount = 0

    # keywords
    # all_script_tags = selector.css("script").getall()
    # keywords = (
    #     "".join(
    #         re.findall(r'"keywords":\[(.*)\],"channelId":".*"', str(all_script_tags))
    #     )
    #     .replace('"', "")
    #     .split(",")
    # )

    print(title, views, likes, date, comments_amount)

    try:
        likes = re.search(r"(\d+)", likes).group()
    except Exception as e:
        likes = 0
    # views = re.search(r"(\d+)", views).group()

    return pd.DataFrame.from_dict(
        {
            "title": [title],
            "views": [views],
            "likes": [likes],
            "date": [date],
            "comments_amount": [comments_amount],
            # "keywords": [keywords],
        }
    )


def parse_channel(selector) -> pd.DataFrame:
    subscribers = selector.css(
        "#subscriber-count.style-scope.ytd-c4-tabbed-header-renderer::text"
    ).get()

    # subscribers = re.search(r"(\d+)", subscribers).group()

    # get recent 5 videos
    channel_name = (
        selector.css("div#channel-header-container yt-formatted-string#text::text")
        .get()
        .strip()
    )

    videos = selector.css(
        "div.style-scope.ytd-rich-item-renderer ytd-rich-grid-media div.style-scope.ytd-rich-grid-media a#thumbnail.yt-simple-endpoint.inline-block.style-scope.ytd-thumbnail::attr(href)"
    ).getall()[:5]

    u, ind = np.unique(videos, return_index=True)
    videos = u[np.argsort(ind)]

    df = pd.DataFrame()
    for v in videos:
        print("Video: ", v)

        result = scroll_page(f"https://www.youtube.com{v}")

        info = get_info_from_video(result)
        info["channel_name"] = channel_name
        info["subscribers"] = subscribers
        # print(info)

        df = pd.concat([df, info])
        # df = df.append(info, ignore_index=True)

    print("Videos i got: ", len(videos))
    return df


def parse_top_channel(channel_link: str) -> pd.DataFrame:
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 3)

    driver.get(channel_link)
    driver.maximize_window()

    # //*[@id="chips"]/yt-chip-cloud-chip-renderer[2]
    # wait for page to load

    try:
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="chips"]/yt-chip-cloud-chip-renderer[2]')
            )
        ).click()
    except Exception as e:
        print("Nao possui aba de videos em alta")
        # return empty dataframe
        # return pd.DataFrame()

    time.sleep(3)
    selector = Selector(text=driver.page_source)
    driver.quit()

    channel_name = (
        selector.css("div#channel-header-container yt-formatted-string#text::text")
        .get()
        .strip()
    )

    videos = selector.css(
        "div.style-scope.ytd-rich-item-renderer ytd-rich-grid-media div.style-scope.ytd-rich-grid-media a#thumbnail.yt-simple-endpoint.inline-block.style-scope.ytd-thumbnail::attr(href)"
    ).getall()[:5]

    u, ind = np.unique(videos, return_index=True)
    videos = u[np.argsort(ind)]

    df = pd.DataFrame()
    for v in videos:
        # print("Video: ", v)

        result = scroll_page(f"https://www.youtube.com{v}")

        info = get_info_from_video(result)
        print(info)
        info["channel_name"] = channel_name
        # print(info)

        df = pd.concat([df, info])
        # df = df.append(info, ignore_index=True)

    print("Videos i got: ", len(videos))
    return df


# %%
with open("canais.txt", "r") as f:
    # read each line as a item in a list and remove the \n
    canais = [line.strip() for line in f.readlines()]

df = pd.DataFrame()
df_top = pd.DataFrame()
df_lifetime = pd.DataFrame()
for ch in canais:
    # recent videos
    result = scroll_page(ch + "/videos")
    df_channel = parse_channel(result)
    df = pd.concat([df, df_channel])

    # top videos
    df_top_channel = parse_top_channel(ch + "/videos")
    df_top = pd.concat([df_top, df_top_channel])

    # lifetime info
    df_lifetime_channel = get_info_from_channel(ch + "/about")
    df_lifetime = pd.concat([df_lifetime, df_lifetime_channel])


os.makedirs(f"./data/{canais[0].split('@')[-1]}", exist_ok=True)

df.to_csv(f"./data/{canais[0].split('@')[-1]}/videos.csv", index=False)
df_top.to_csv(f"./data/{canais[0].split('@')[-1]}/top_videos.csv", index=False)
df_lifetime.to_csv(f"./data/{canais[0].split('@')[-1]}/lifetime.csv", index=False)

# %% [markdown]
# # Tratamento

# %%
import locale

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

# %% [markdown]
# # Trata videos recentes


# %%
def trata_inscritos(col: pd.Series) -> pd.Series:
    col = col.split(" inscritos")[0]

    if "mil" in col:
        return int(
            float(col.replace("mil", "").replace(" ", "").replace(",", ".")) * 1000
        )

    return int(col.replace(" ", "").replace(",", "."))


def trata_visualizacoes(col: pd.Series) -> pd.Series:
    # treat the characters U+00a0

    # if its a numeric value return it
    if type(col) == int or type(col) == float:
        return col

    col = col.replace("\xa0", "")

    col = col.split(" visualizações")[0]

    if "mil" in col:
        return int(
            float(col.replace("mil", "").replace(" ", "").replace(",", ".")) * 1000
        )
    elif "mi" in col:
        # remove 'de'
        if "de" in col:
            col = col.replace("de", "")
        return int(
            float(col.replace("mi", "").replace(" ", "").replace(",", ".")) * 1000000
        )

    return int(col.replace(" ", "").replace(".", "").replace(",", "."))


def trata_data(value):
    meses = {
        "jan": "01",
        "fev": "02",
        "mar": "03",
        "abr": "04",
        "mai": "05",
        "jun": "06",
        "jul": "07",
        "ago": "08",
        "set": "09",
        "out": "10",
        "nov": "11",
        "dez": "12",
    }
    series_data = re.sub(r"\. de", "", value)
    # print(series_data)
    series_data = re.search(r"(\d{1,2} de [a-zA-Z]+ \d{4})", series_data).group(0)
    # replace month
    for k, v in meses.items():
        series_data = series_data.replace(k, v)

    # print(series_data)
    series_data = pd.to_datetime(series_data, format="%d de %m %Y", errors="coerce")
    return series_data


# %%
videos = pd.read_csv(f"./data/{canais[0].split('@')[-1]}/videos.csv")

# %%
videos.assign(
    subscribers=lambda df_: df_["subscribers"].apply(trata_inscritos),
    views=lambda df_: df_["views"].apply(trata_visualizacoes),
    date=lambda df_: df_["date"].apply(trata_data),
    category="RECENT",
).to_parquet(f"./data/{canais[0].split('@')[-1]}/videos.parquet")

# %% [markdown]
# # Trata Top videos

# %%
import pandas as pd

# %%
top_videos = pd.read_csv(f"./data/{canais[0].split('@')[-1]}/top_videos.csv")

# %%
top_videos.assign(
    date=lambda df_: df_["date"].apply(trata_data),
    views=lambda df_: df_["views"].apply(trata_visualizacoes),
    category="TOP",
).to_parquet(f"./data/{canais[0].split('@')[-1]}/top_videos.parquet")

# %%
top_videos_silver = pd.read_parquet("top_videos.parquet")

# %%
# top_videos_silver.loc[:, ['channel_name', 'title', 'date', 'views', 'likes', 'comments_amount']].to_clipboard(index=False)

# %% [markdown]
# # Trata lifetime

# %%
df_lifetime = pd.read_csv(f"./data/{canais[0].split('@')[-1]}/lifetime.csv")

# %%
df_lifetime.head()


# %%
def days_on_youtube(value) -> int:
    import datetime

    today = datetime.date.today()
    return (today - value.date()).days


# %%
(
    df_lifetime.assign(
        date_joined=lambda df_: df_["date_joined"].apply(trata_data),
        total_views=lambda df_: df_["total_views"].apply(trata_visualizacoes),
        total_subs=lambda df_: df_["total_subs"].apply(trata_inscritos),
        days_since_joined=lambda df_: df_["date_joined"].apply(days_on_youtube),
    )
).to_csv(f"./data/{canais[0].split('@')[-1]}/lifetime.csv", index=False)

# %% [markdown]
# # join

# %%
videos = pd.read_parquet("videos.parquet")
top_videos = pd.read_parquet("top_videos.parquet")

# %%
# join the two dataframes

videos = pd.concat([videos, top_videos])

# %%
videos_sorted = videos.sort_values("channel_name")

videos_sorted["subscribers"] = videos_sorted["subscribers"].fillna(method="ffill")

# %%
videos_sorted = videos_sorted.sort_values(["channel_name", "category", "date"])

# %%
videos_sorted.to_parquet(f"./data/{canais[0].split('@')[-1]}/videos_sorted.parquet")

# %%
pd.read_parquet(f"./data/{canais[0].split('@')[-1]}/videos_sorted.parquet").to_csv(
    f"./data/{canais[0].split('@')[-1]}/videos_sorted.csv", index=False
)

# %%

# read channel IDs

with open("canais.txt", "r") as f:
    canais = f.readlines()


canais = [c.strip() for c in canais]
# take only the string after the last slash
canais = [c.split("/")[-1] for c in canais]

print(canais)

base_url = "https://socialblade.com/youtube/channel/"

social_blade_data = []
for c in canais:
    response = scroll_page(base_url + c)

    # last 30 days views #socialblade-user-content > div:nth-child(23) > div:nth-child(3) > span
    views = response.css(
        "#socialblade-user-content > div:nth-child(23) > div:nth-child(3) > span::text"
    ).get()
    subs = response.css(
        "#socialblade-user-content > div:nth-child(23) > div:nth-child(2) > span::text"
    ).get()

    if views is None or subs is None:
        views = response.css(
            "#socialblade-user-content > div:nth-child(16) > div:nth-child(3) > span::text"
        ).get()
        subs = response.css(
            "#socialblade-user-content > div:nth-child(16) > div:nth-child(2) > span::text"
        ).get()

    social_blade_data.append({"Channel": c, "views": views, "subs": subs})
    last_30days = pd.DataFrame(social_blade_data)
    last_30days = last_30days.fillna("0")


# %%
def fix_views(view: pd.Series) -> pd.Series:
    view = view.str.replace("+", "").str.replace(",", "")
    print(view)

    view = view.apply(lambda x: float(x.replace("K", "")) * 1000 if "K" in x else x)
    view = view.apply(
        lambda x: float(x.replace("M", "")) * 1000000 if "M" in str(x) else x
    )

    return view


last_30days = last_30days.assign(
    views=lambda x: fix_views(x["views"]), subs=lambda x: fix_views(x["subs"])
)


last_30days.to_csv(f'data/{canais[0].split("@")[-1]}/last_30days.csv', index=False)
