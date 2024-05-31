import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

# ベースURL
base_url = "https://kabutan.jp"

# ニュースのURL（最初のページ）
initial_page_url = "https://kabutan.jp/news/marketnews/?date=20240531"


def fetch_page_content(url):
    print(f"Fetching URL: {url}")
    response = requests.get(url)
    response.raise_for_status()
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


def crawl_news(url):
    html_content = fetch_page_content(url)
    news_data, soup = parse_news_list(html_content)

    if not news_data:
        print("No news items found on this page. Stopping crawl.")
        return

    for news in news_data:
        article_text = parse_article_content(news["link"])
        news["content"] = article_text
        print(
            f"Time: {news['time']}\nCategory: {news['category']}\nTitle: {news['title']}\nLink: {news['link']}\nContent: {news['content']}\n"
        )

    # 次のページがあるか確認
    next_page_tag = soup.find("a", string="次へ＞")
    if next_page_tag:
        next_page_link = next_page_tag["href"]
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params["page"] = [str(int(query_params.get("page", [1])[0]) + 1)]
        next_page_full_link = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{urlencode(query_params, doseq=True)}"
        print(f"Next page URL: {next_page_full_link}")
        crawl_news(next_page_full_link)
    else:
        print("No more pages to crawl.")


if __name__ == "__main__":
    crawl_news(initial_page_url)
