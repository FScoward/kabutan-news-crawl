from time import sleep
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# ベースURL
base_url = "https://kabutan.jp"

# ニュースのURL（最初のページ）
initial_page_url = "https://kabutan.jp/news/marketnews/?date=20240531"

# ニュースデータを格納するリスト
all_news_data = []

# 最大ページ数の制限を設定
max_pages = 50
current_page = 1


def fetch_page_content(url):
    print(f"Fetching URL: {url}")
    sleep(0.5)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except:
        print()

    return response.text


def parse_news_list(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    news_items = soup.find_all("tr")
    print(f"Found {len(news_items)} news items in the page.")

    news_data = []
    for item in news_items:
        news_time_tag = item.find("time")
        if news_time_tag:
            news_time = news_time_tag.get_text(strip=True)
        else:
            continue

        category_tag = item.find("div", class_="newslist_ctg")
        if category_tag:
            category = category_tag.get_text(strip=True)
        else:
            continue

        link_tag = item.find("a")
        if link_tag:
            title = link_tag.get_text(strip=True)
            link = link_tag["href"]
            full_link = urljoin(base_url, link)

            news_data.append(
                {
                    "time": news_time,
                    "category": category,
                    "title": title,
                    "link": full_link,
                }
            )

    print(f"Parsed {len(news_data)} news items.")
    return news_data, soup


def parse_article_content(article_url):
    print(f"Fetching article URL: {article_url}")
    article_html = fetch_page_content(article_url)
    print("Fetch complete")
    article_soup = BeautifulSoup(article_html, "html.parser")

    # 記事の内容を抽出する部分を修正
    article_body = article_soup.find("div", class_="body")
    if article_body:
        print(f"Article body found: {article_body.prettify()}")  # デバッグ用ログ
        # すべての子要素を取得してテキストを抽出
        content = article_body.get_text(separator="\n", strip=True)
        return content
    else:
        print("Article body not found.")  # デバッグ用ログ
        return "記事の内容を取得できませんでした。"


def crawl_news(url, page):
    global all_news_data, max_pages, current_page

    if page > max_pages:
        print("Reached maximum page limit. Stopping crawl.")
        return

    print(f"Crawling page {page} with URL: {url}")
    html_content = fetch_page_content(url)
    print(f"Complete Crawling page {page} with URL: {url}")
    news_data, soup = parse_news_list(html_content)

    if not news_data:
        print("No news items found on this page. Stopping crawl.")
        return

    print("")
    for news in news_data:
        article_text = parse_article_content(news["link"])
        news["content"] = article_text
        all_news_data.append(news)
        # print(
        #     f"Time: {news['time']}\nCategory: {news['category']}\nTitle: {news['title']}\nLink: {news['link']}\nContent: {news['content']}\n"
        # )

    # 次のページがあるか確認
    next_page_tag = soup.find("a", string="次へ＞")
    if next_page_tag:
        next_page_link = next_page_tag["href"]
        next_page_full_link = urljoin(initial_page_url, next_page_link)
        print(f"Next page URL: {next_page_full_link}")
        current_page += 1
        crawl_news(next_page_full_link, current_page)
    else:
        print("No more pages to crawl.")


def save_news_to_json(file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_news_data, f, ensure_ascii=False, indent=4)
    print(f"News data saved to {file_path}")


if __name__ == "__main__":
    crawl_news(initial_page_url, current_page)
    save_news_to_json("news_data.json")
