import requests
from lxml import etree
import csv
import json
import time
from enum import Enum
import time
from concurrent.futures import ThreadPoolExecutor

# 定义枚举类
class WriteToType(Enum):
    CSV = 1
    JSON = 2

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'
}

# ==================== 文件保存 ====================
# 保存到 CSV
def write_book_to_csv(books):
    with open('douban_reading.csv', 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["书名", "作者", "出版社", "出版日期", "页数", "装帧", "定价", "评分", "评价人数", "短评数"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)
    print("✅ 数据已保存到 CSV")

# 保存到 JSON
def write_book_to_json(books):
    with open('douban_reading.json', 'a', encoding='utf-8') as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print("✅ 数据已保存到 JSON")

# ==================== 数据提取 ====================
# 提取书本详情链接
def get_book_detail(item):
    book_url = item.xpath(".//h2/a[@class='fleft']/@href")
    return book_url[0].strip() if book_url else None

# 提取书名
def get_book_title(tree):
    book_title = tree.xpath("//h1/span/text()")
    return book_title[0].strip() if book_title else '未知书名'

# 提取作者
def get_book_author(tree):
    author = tree.xpath("//div[@id='info']/span/a/text()")
    return author[0].strip() if author else '未知作者'

# 提取出版社
def get_published_house(tree):
    pub = tree.xpath("//div[@id='info']/a[1]/text()")
    return pub[0].strip() if pub else '未知出版社'

# 提取出版日期
def get_published_date(tree):
    date = tree.xpath("//div[@id='info']/span[contains(., '出版年')]/following-sibling::text()")
    return date[0].strip() if date else '未知日期'

# 提取页数
def get_page_num(tree):
    num = tree.xpath("//div[@id='info']/span[contains(., '页数')]/following-sibling::text()")
    return num[0].strip() if num else '未知页数'

# 提取装帧信息
def get_binding(tree):
    binding = tree.xpath("//div[@id='info']/span[contains(., '装帧')]/following-sibling::text()")
    return binding[0].strip() if binding else '装帧信息未知'

# 提取定价
def get_price(tree):
    price = tree.xpath("//div[@id='info']/span[contains(., '定价')]/following-sibling::text()")
    return price[0].strip() if price else '未知定价'

# 提取评分
def get_rating(tree):
    rating = tree.xpath("//div[@class='rating_self clearfix']/strong[@class='ll rating_num ']/text()")
    return rating[0].strip() if rating else '未知评分'

# 提取评价人数
def get_rating_num(tree):
    rating_num = tree.xpath("//div[@class='rating_sum']/span/a[@class='rating_people']/span/text()")
    return rating_num[0].strip() if rating_num else '未知评价人数'

# 提取短评数
def get_comment_num(tree):
    comment_num = tree.xpath("//div[@class='mod-hd']/h2/span[@class='pl']/a/text()")
    return comment_num[0].strip() if comment_num else '未知短评数'

# ==================== 处理单页书单 ====================
def process_book_items(book_item_list, books,write_to):
    for book in book_item_list:
        book_url = get_book_detail(book)
        if not book_url:
            continue

        # 请求详情页
        detail_resp = requests.get(book_url, headers=headers, timeout=10)
        detail_resp.raise_for_status()
        book_tree = etree.HTML(detail_resp.text)

        # 提取信息
        title = get_book_title(book_tree)
        author = get_book_author(book_tree)
        pub_house = get_published_house(book_tree)
        pub_date = get_published_date(book_tree)
        page_num = get_page_num(book_tree)
        binding = get_binding(book_tree)
        price = get_price(book_tree)
        rating = get_rating_num(book_tree)
        rating_num = get_rating_num(book_tree)
        comment_num = get_comment_num(book_tree)

        print(f"书名：{title}")
        print(f"作者：{author}")
        print(f"出版社：{pub_house}")
        print(f"出版日期：{pub_date}")
        print(f"页数：{page_num}")
        print(f"装帧：{binding}")
        print(f"定价：{price}")
        print(f"评分：{rating}")
        print(f"评价人数：{rating_num}")
        print(f"短评数：{comment_num}")
        print("\n")

        # 创建储存字典
        book = {
            "书名": title,
            "作者": author,
            "出版社": pub_house,
            "出版日期": pub_date,
            "页数": page_num,
            "装帧": binding,
            "定价": price,
            "评分": rating,
            "评价人数": rating_num,
            "短评数": comment_num,
        }

        books.append(book)
        print(f"✅ 已抓取：{title}")
        print("-" * 50)
        time.sleep(1)
    return books

# ==================== 主爬虫 ====================
def scrape_books(start_page, end_page, write_to):
    books = []

    try:
        for page in range(start_page, end_page + 1):
            print(f"\n===== 正在爬取第 {page} 页 =====")
            url = f"https://book.douban.com/chart?subcat=all&p={page}"

            # 发送请求
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            # 解析HTML
            tree = etree.HTML(response.text)
            book_item_list = tree.xpath("//ul[contains(@class, 'chart-dashed-list')]/li")
            print(f"本页获取到书籍数量：{len(book_item_list)}\n")
            # 遍历书籍
            books = process_book_items(book_item_list, books, write_to)

        # 统一保存
        if write_to == WriteToType.CSV:
            write_book_to_csv(books)
        elif write_to == WriteToType.JSON:
            write_book_to_json(books)
        print(f"\n🎉 全部爬取完成！共抓取 {len(books)} 本书籍信息")

    except Exception as e:
        print(f"❌ 第{page}页失败：{e}")
    time.sleep(2)


# ==================== 执行 ====================
if __name__ == "__main__":
    scrape_books(1, 2, WriteToType.CSV)
