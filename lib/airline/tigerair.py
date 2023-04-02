import requests
import json
from datetime import datetime, timedelta


class TigerAir:
    def __init__(self):
        self.name = "TigerAir"
        self.airports = {
            "台灣": {
                "台北": "TPE",
                "台中": "RMQ",
                "高雄": "KHH", 
            },
            "日本": {
                    "東京成田": "NRT",
                    "東京羽田": "HND",
                    "茨城": "IBR",   
                    "大阪": "KIX",
                    "岡山": "OKJ",
                    "沖繩": "OKA",
                    "福岡": "FUK",
                    "名古屋": "NGO",
                    "小松": "KMQ",
                    "新潟": "KIJ",
                    "仙台": "SDJ",
                    "花卷": "HNA",
                    "函館": "HKD",
                    "新千歲": "CTS",
                    "旭川": "AKJ",
            },
            "南韓": {
                "首爾仁川": "ICN",
                "大邱": "TAE",
                "釜山": "PUS",
                "濟州": "CJU",
            },
            "澳門": {
                "澳門": "MFM",
            },
            "泰國": {
                "曼谷": "DMK",
            },
            "菲律賓": {
                "巴拉望公主港": "PPS",
                "卡里博長灘島": "KLO",
            },
            "越南": {
                "峴港": "DAD",
            },
        }  
   
    def get_ticket_price_list(self, origin, destination, since, until, get_price_num=10):
        url = 'https://api-book.tigerairtw.com/graphql'
        data = {
            "operationName": "appLiveDailyPrices",
            "variables": {
                "input": {
                    "origin": f"{self.airports[destination[0]][destination[1]]}",
                    "destination": f"{self.airports[origin[0]][origin[1]]}",
                    "userCurrency": "TWD",
                    "pricingCurrency": "TWD",
                    "since": f"{since}",
                    "until": f"{until}",
                    "source": "resultPagePriceBrick"
                }
            },
            "query": "query appLiveDailyPrices($input: QueryDailyPricesInput!) {\n  appLiveDailyPrices(input: $input) {\n    origin\n    destination\n    date\n    currency\n    amount\n    fareLabels {\n      id\n    }\n  }\n}\n"
        }

        headers = {
            "Host": "api-book.tigerairtw.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "content-type": "application/json",
            "accept": "*/*",
            "Content-Length": str(len(json.dumps(data))),
        }

        res = requests.post(url, data=json.dumps(data), headers=headers)

        if res.status_code != 200:
            print('Error: ', res.status_code, res.text, sep='\t', end='\n\n')

        # 將 JSON 字符串轉換為 Python 對象
        data = json.loads(res.text)

        # 從 Python 對象中提取所需的數據
        prices = data['data']['appLiveDailyPrices']

        # 使用列表推導式移除 amount 等於 0 的數據
        filtered_prices = [p for p in prices if p['amount'] != 0]

        # 對價格列表按 amount 鍵進行排序
        sorted_prices = sorted(filtered_prices, key=lambda p: p['amount'])

        # 提取前十個價格
        cheapest_prices = sorted_prices[:get_price_num]

        # 返回前十個最便宜的價格和日期
        return cheapest_prices

    def find_best_op_and_rp(self, out_prices_set, in_prices_set, date_range=7, least_days=4, out_tax=500, in_tax=937):
        print(f"Date Range Setting: {date_range} days")
        for i, out_price in enumerate(out_prices_set):
            for j, in_price in enumerate(in_prices_set):
                # Check if the total duration is less than 10 days and inbound date is later than outbound date
                if (datetime.strptime(in_price['date'], '%Y-%m-%d') - datetime.strptime(out_price['date'], '%Y-%m-%d')).days <= date_range and datetime.strptime(in_price['date'], '%Y-%m-%d') > datetime.strptime(out_price['date'], '%Y-%m-%d') and (datetime.strptime(in_price['date'], '%Y-%m-%d') - datetime.strptime(out_price['date'], '%Y-%m-%d')).days >= least_days:
                    print(f"Out/In: {out_price['origin']} <-> {out_price['destination']}")
                    print(f"Arri/Dep: {out_price['date']} -> {in_price['date']}")
                    print(f"Duration: {(datetime.strptime(in_price['date'], '%Y-%m-%d') - datetime.strptime(out_price['date'], '%Y-%m-%d')).days} days")
                    print(f"OutPrice: ${out_price['amount']}, InPrice: ${in_price['amount']}")
                    print(f"OutTax: ${out_tax}, InTax: ${in_tax}")
                    print(f"Total: TWD${out_price['amount'] + in_price['amount'] + out_tax + in_tax}\n")          

###### Input Data ######

origin = ['台灣', '台北']
destination = ['日本', '福岡']
since = '2023-04-15'
until = '2023-07-01'
get_price_num = 20

##### Main ######
t = TigerAir()
# 爬取去程的
out_prices = t.get_ticket_price_list(destination, origin, since, until, get_price_num)

print("==== The Outbound Cheapest Prices of ====")
for index, price in enumerate(out_prices):
    if index == 0:
        print(f"==== Origin: {price['origin']}, Dest.: {price['destination']} ====")
    print(f"{index+1}. Date: {price['date']}, Amount: {price['amount']}")

print("\n")

# 爬取回程的價格
in_prices = t.get_ticket_price_list(origin, destination, since, until, get_price_num)
print("==== The Inbround Cheapest Prices of ====")
for index, price in enumerate(in_prices):
    if index == 0:
        print(f"==== Origin: {price['origin']}, Dest.: {price['destination']} ====")
    print(f"{index+1}. Date: {price['date']}, Amount: {price['amount']}")

# 爬取不超過指定天數的最便宜的往返價格與日期
print("\n")
print("==== The Best Price of Trip ====")
t.find_best_op_and_rp(out_prices, in_prices)

    
