import requests
import csv
import json
import time
from enum import Enum

# 定义枚举类
class WriteToType(Enum):
    CSV = 1
    JSON = 2

# 请求头
payload = {}
headers = {
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'cache-control': 'no-cache',
  'pragma': 'no-cache',
  'priority': 'u=1, i',
  'referer': 'https://wenku.cnki.net/reader/article/articleList?categoryCode=A000435',
  'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
  'Cookie': 'Ecp_ClientId=6285274ef806c2d812bd9d611ba9bc6d0VISVO7n6b; UM_distinctid=19de697166dd52-0d7e10ef6c2ad3-26061e51-1bcab9-19de697166e2f02; Ecp_IpLoginFail=260504112.94.77.114; SID_wenku=017044; Hm_lvt_ce1d986bcc5006d82686e9864343c93a=1777690155,1777861012; HMACCOUNT=75B04076D32E32A2; CNZZDATA1281326790=206625648-1777690155-%7C1777861074; Hm_lpvt_ce1d986bcc5006d82686e9864343c93a=1777861074'
}

# ==================== 文件保存 ====================
# 保存到 CSV
def write_essay_to_csv(essays):
    with open('cnki_wneku.csv', 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["标题", "作者", "发布日期", "关键字", "简介", "浏览数"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(essays)
    print("✅ 数据已保存到 CSV")

# 保存到 JSON
def write_essay_to_json(essays):
    with open('cnki_wenku.json', 'a', encoding='utf-8') as f:
        json.dump(essays, f, ensure_ascii=False, indent=2)
    print("✅ 数据已保存到 JSON")

# ==================== 处理单页 ====================
def process_research_items(essay_list, essays, write_to):
    for item in essay_list:
        title = item["title"]
        author = item["author"]
        published_date = item["publishedAt"]
        keywords = item["keywords"]
        summary = item["summary"]
        read_count = item["readCount"]

        print(f"标题：{title}")
        print(f"作者：{author}")
        print(f"发布日期：{published_date}")
        print(f"关键字：{keywords}")
        print(f"简介：{summary}")
        print(f"浏览数：{read_count}")

        # 创建储存字典
        essay = {
            "标题": title,
            "作者": author,
            "发布日期": published_date,
            "关键字": keywords,
            "简介": summary,
            "浏览数": read_count
        }

        essays.append(essay)
        print(f"✅ 已抓取：{title}")
        print("-" * 50)
        time.sleep(1)

    return essays

# ==================== 主爬虫 ====================
def scrape_essays(start_page, end_page, write_to):
    essays = []

    try:
        for page in range(start_page, end_page + 1):
            print(f"\n===== 正在爬取第 {page} 页 =====")
            url = f"https://wenku.cnki.net/egret-reader/library/list?pageNumber={page}&pageSize=10&order=0&fileType=&categoryCode=A000435&clientType=1"

            # 发送请求
            response = requests.request("GET", url, headers=headers, data=payload)

            json_data = response.json()
            items = json_data["data"]
            items_list = items["ugcContentDtoPageDto"]
            essay_list = items_list["data"]
            # 遍历书籍
            essays = process_research_items(essay_list, essays, write_to)

        # 统一保存
        if write_to == WriteToType.CSV:
            write_essay_to_csv(essays)
        elif write_to == WriteToType.JSON:
            write_essay_to_json(essays)
        print(f"\n🎉 全部爬取完成！共抓取 {len(essays)} 条论文信息")

    except Exception as e:
        print(f"❌ 第{page}页失败：{e}")
    time.sleep(2)

if __name__ == "__main__":
    scrape_essays(1, 1, WriteToType.JSON)