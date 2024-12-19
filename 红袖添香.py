import requests
from bs4 import BeautifulSoup
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor

# 目标网站列表及其适配规则
novel_sites = {
    "hongxiu": {
        "url": "https://www.hongxiu.com/",
        "search_url": "https://www.hongxiu.com/search?kw={}",
        "list_selector": ".book-list a",
        "chapter_selector": ".volume-list a",
        "content_selector": ".read-content"
    },
    "zongheng": {
        "url": "http://www.zongheng.com/",
        "search_url": "http://search.zongheng.com/s?keyword={}",
        "list_selector": ".search-tab a",
        "chapter_selector": ".chapter-list a",
        "content_selector": ".content"
    }
    # 添加其他目标网站的适配规则
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def fetch_url(url):
    """请求 URL 并返回内容"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"请求失败：{url}, 错误：{e}")
        return None

def parse_search_results(site, novel_name):
    """搜索小说并返回小说链接列表"""
    search_url = site["search_url"].format(novel_name)
    html = fetch_url(search_url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    links = soup.select(site["list_selector"])
    return [(link.text.strip(), link["href"]) for link in links]

def fetch_chapters(site, novel_url):
    """获取小说章节列表"""
    html = fetch_url(novel_url)
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    chapters = soup.select(site["chapter_selector"])
    return [(chapter.text.strip(), chapter["href"]) for chapter in chapters]

def fetch_chapter_content(site, chapter_url):
    """获取单章内容"""
    html = fetch_url(chapter_url)
    if not html:
        return None, None
    soup = BeautifulSoup(html, "html.parser")
    try:
        title = soup.select_one("h1").text.strip()  # 标题
        content = "\n".join([p.text.strip() for p in soup.select(site["content_selector"])])
        return title, content
    except Exception as e:
        print(f"解析章节失败：{chapter_url}, 错误：{e}")
        return None, None

def save_novel(novel_name, chapters):
    """保存小说到文件"""
    filename = f"{novel_name}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        for title, content in chapters:
            file.write(f"{title}\n\n{content}\n\n")
    print(f"小说已保存：{filename}")

def crawl_novel(site, novel_name):
    """爬取单本小说"""
    print(f"开始爬取小说：{novel_name}")
    results = parse_search_results(site, novel_name)
    if not results:
        print(f"未找到小说：{novel_name}")
        return
    novel_title, novel_url = results[0]  # 获取第一个搜索结果
    chapters = fetch_chapters(site, novel_url)
    novel_content = []
    for title, url in chapters:
        chapter_title, chapter_content = fetch_chapter_content(site, url)
        if chapter_title and chapter_content:
            novel_content.append((chapter_title, chapter_content))
        time.sleep(random.uniform(1, 3))  # 避免被封
    if novel_content:
        save_novel(novel_title, novel_content)
    else:
        print(f"未能爬取任何章节：{novel_name}")

def main():
    novel_name = input("请输入要爬取的小说名称：")
    print("支持以下网站：")
    for site_name in novel_sites.keys():
        print(f"- {site_name}")
    site_choice = input("选择目标网站（如 hongxiu）：").strip()
    if site_choice not in novel_sites:
        print("不支持该网站")
        return
    site = novel_sites[site_choice]
    crawl_novel(site, novel_name)

if __name__ == "__main__":
    main()