import requests
import csv
import json
import time
from enum import Enum
from datetime import datetime

from tldextract import update


# 定义枚举类
class WriteToType(Enum):
    CSV = 1
    JSON = 2

payload = {}
headers = {
  'Accept': 'application/json, text/plain, */*',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Cache-Control': 'no-cache, no-store',
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Referer': 'https://wenku.baidu.com/ndcore/browse/ainote?notePage=ai_note_square&_wkts_=1777946025838',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36',
  'sec-ch-ua': '"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'Cookie': 'BAIDUID=0BD6688B63397918668B3EAF51ED31E5:FG=1; BIDUPSID=0BD6688B63397918668B3EAF51ED31E5; PSTM=1768446363; MCITY=-257%3A; H_WISE_SIDS_BFESS=63144_67499_67758_67833_67861_67884_67886_67895_67942_67915_67952_67954_67955_67975_67877_67991_68044_68035_68077_68086_68099_67986_68003_68129_68148_68147_68153_68166_68192_68208_68210; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BAIDUID_BFESS=0BD6688B63397918668B3EAF51ED31E5:FG=1; H_PS_PSSID=63144_67861_68166_68297_68450_68739_69001_69168_69194_69245_69229_69239_69232_69237_69293_69294_69251_69353_69378_69386_69399_69401_69397_69420_69416_69422_69441_69430_69451_69459_69343_69338_69347_69344_69349_69350_69340_69498_69500_69503_69559_69553_69575_69586_69613_69665_69660_69684; BA_HECTOR=0lal00818h00200h80ak8l042k202g1kvg04u27; ZFY=0Kyk1zksMJXP9hoGzSUbJWOx:AlXTcuenOmgKFcDyEeA:C; H_WISE_SIDS=63144_67861_68166_68297_68450_68739_69001_69168_69194_69245_69229_69239_69232_69237_69293_69294_69251_69353_69378_69386_69399_69401_69397_69420_69416_69422_69441_69430_69451_69459_69343_69338_69347_69344_69349_69350_69340_69498_69500_69503_69559_69553_69575_69586_69613_69665_69660_69684; Hm_lvt_4fbbee5fb2fd1d3e6c51ad50dd936eb3=1777945997; HMACCOUNT=75B04076D32E32A2; __bid_n=194d864ae44460851f0c5b; ab_sr=1.0.1_NjA5OGE3ZDA1ZGI3ZDczNTlhNWYwODAzMWI2MWRmNjA5YmY3MDA4OGVlMWExOWE1OWViYTM5YTRmNzAyODMxYjA1YzQ0OWNlYTZiZjZjMGVjYzIzZDU4ZWM1MjI2ZGQwMDFhMjU0Mjk2NWVhOTc4ZWUxY2MzZDdhYmZkN2RiZjQzMDVmNmJmYjAzNGZiOGQ5Mzg3NmRkZDBjZjk0YzEzYjU5ZjgxNjY4ZjkzODYzYjA0NjljODg4NzQxMTJkYmIxNmZjNWM2ZDI3ODUyYzliMjFhNDRkZGM5MWJmNzQ2ZDM=; Hm_lpvt_4fbbee5fb2fd1d3e6c51ad50dd936eb3=1777946385; BAIDUID=346A95F72C1516C0986D2948A9ED8DE6:FG=1'
}

# ==================== 文件保存 ====================
# 保存到 CSV
def write_note_to_csv(notes):
    with open('baidu_wenku.csv', 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ["标题", "分享人", "上传时间", "内容详情列表"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(notes)
    print("✅ 数据已保存到 CSV")

# 保存到 JSON
def write_note_to_json(notes):
    with open('baidu_wenku.json', 'a', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    print("✅ 数据已保存到 JSON")

# ==================== 处理单页 ====================
def process_note_items(data_list, notes, write_to):
    for data in data_list:
        notes_list = []

        title = data["title"]
        note_list = data["noteList"]
        sharer = data["sharerUname"]
        raw_update_time = data["utime"]
        update_time = datetime.fromtimestamp(raw_update_time).strftime("%Y-%m-%d %H:%M:%S")

        print(f"标题：{title}")
        print(f"分享人：{sharer}")
        print(f"上传时间：{update_time}")
        print("内容详情：")
        for note in note_list:
            note_title = note["title"]
            print(f"{note_title}")
            notes_list.append(note_title)
        #print("\n")
        #print("-" * 50)

        # 创建储存字典
        note = {
            "标题": title,
            "分享人": sharer,
            "上传时间": update_time,
            "内容详情列表": notes_list
        }

        notes.append(note)
        print(notes)
        print(f"✅ 已抓取：{title}")
        print("-" * 50)
        time.sleep(1)

    return notes

# ==================== 主爬虫 ====================
def scrape_notes(start_page, end_page, write_to):
    notes = []

    try:
        for page in range(start_page, end_page + 1):
            print(f"\n===== 正在爬取第 {page} 页 =====")
            url = f"https://wenku.baidu.com/gdoc/square/squarecardlist?pn={page}&rn=10&category=0"
            # 发送请求
            response = requests.request("GET", url, headers=headers, data=payload)

            json_data = response.json()
            json_data = json_data["data"]
            data_list = json_data["data"]
            data_list = data_list["list"]
            # 遍历文库
            notes = process_note_items(data_list, notes, write_to)

        # 统一保存
        if write_to == WriteToType.CSV:
            write_note_to_csv(notes)
        elif write_to == WriteToType.JSON:
            write_note_to_json(notes)
        print(f"\n🎉 全部爬取完成！共抓取 {len(notes)} 条文库信息")

    except Exception as e:
        print(f"❌ 第{page}页失败：{e}")
    time.sleep(2)

if __name__ == "__main__":
    scrape_notes(1, 1, WriteToType.CSV)