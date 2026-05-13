import requests
import os
import csv
import json
import time
from enum import Enum
from PIL import Image
from io import BytesIO

# 定义枚举类
class WriteToType(Enum):
    CSV = 1
    JSON = 2

# 请求头
payload = {}
headers = {
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Referer': 'https://www.iresearch.com.cn/report.shtml?type=4',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'Cookie': 'refCookie=www.iresearch.com.cn; Hm_lvt_342cc290125ac01f1d96b15a01b47e94=1777361519,1777427333,1777622257; HMACCOUNT=75B04076D32E32A2; Hm_lpvt_342cc290125ac01f1d96b15a01b47e94=1777622381'
}

# ==================== 文件保存 ====================
# 保存到 CSV
def write_research_to_csv(researches):
    with open('iresearch.csv', 'a', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["标题", "分类", "日期"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(researches)
    print("✅ 数据已保存到 CSV")

# 保存到 JSON
def write_research_to_json(researches):
    with open('iresearch.json', 'a', encoding='utf-8') as f:
        json.dump(researches, f, ensure_ascii=False, indent=2)
    print("✅ 数据已保存到 JSON")

# 从URL获取到图片对象
def get_image_obj_by_url(img_url):
    response = requests.get(img_url)
    bytes_img = BytesIO(response.content)
    image_obj = Image.open(bytes_img)
    return image_obj

# 保存图片文件
def save_image(img_url, save_dir, file_name):
    print(f"{file_name} 的 URL 为: {img_url}")

    img_obj = get_image_obj_by_url(img_url)

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"创建了图片目录：{save_dir}")
    save_path = os.path.join(save_dir, file_name)
    img_obj.save(save_path)
    print(f"成功下载图片：{file_name}")

# ==================== 处理单页 ====================
def process_research_items(data_list, researches, write_to):
    for data in data_list:
        title = data['Title']
        industry = data['industry']
        date = data['Uptime']
        id = data['Id']
        img_url = data['SmallImg']

        print(f"标题：{title}")
        print(f"分类：{industry}")
        print(f"日期：{date}")
        print(f"研究ID：{id}")

        # 下载并保存图片
        img = save_image(img_url, './iresearch_image', f'{id}.png')

        # 创建储存字典
        research = {
            "标题": title,
            "分类": industry,
            "日期": date
        }

        researches.append(research)
        print(f"✅ 已抓取：{title}")
        print("-" * 50)
        time.sleep(1)

    return researches

# ==================== 主爬虫 ====================
def scrape_researches(page_num, page_size, ID, write_to):
    researches = []

    try:
        #page_size = 20
        lastId = ID  # 第一页为空
        page = 1

        while page <= page_num:
            print(f"-----正在爬取第{page}页-----")
            url = f"https://www.iresearch.com.cn/api/products/getdatasapi?rootId=14&channelId=&userId=&lastId={lastId}&pageSize={page_size}"

            response = requests.request("GET", url, headers=headers, data=payload)

            # print(response.text)

            json_data = response.json()
            data_list = json_data['List']
            print(len(data_list))

            researches = process_research_items(data_list, researches, write_to)

            page += 1

        # 统一保存
        if write_to == WriteToType.CSV:
            write_research_to_csv(researches)
        elif write_to == WriteToType.JSON:
            write_research_to_json(researches)
        print(f"\n🎉 全部爬取完成！共抓取 {len(researches)} 条研究图表信息")

    except Exception as e:
        print(f"❌ 第{page}页失败：{e}")
    time.sleep(2)

# ==================== 执行 ====================
if __name__ == "__main__":
    scrape_researches(100, 20, "chart.45875", WriteToType.CSV)
    # 第1个20，结尾ID：chart.45875
    # 第2个20，结尾ID：chart.45855