import requests
import json
from datetime import datetime, timedelta

  
def select_departure_stations():
    url = 'https://sec.jejuair.net/zh-tw/ibe/booking/selectDepartureStations.json'
    data = {
        'bookType': 'Common',
        'cultureCode': 'zh-tw',
        'pageId': '0000000127',
    }
    
    headers = {
        "Host": "sec.jejuair.net",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(json.dumps(data))),
    }
    
    res = requests.post(url, data=data, headers=headers)  
    print(res.text)


def set_booking_info():
    url = 'https://sec.jejuair.net/zh-tw/ibe/booking/selectArrivalStations.json'
    data = {
        'bookType': 'Common',
        'cultureCode': 'zh-tw',
        'originAirport': 'TPE',
        'pageId': '0000000127',    
    }
    
    headers = {
        "Host": "sec.jejuair.net",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(json.dumps(data))),
    }
    
    res = requests.post(url, data=data, headers=headers)
    print(res.text)

def find_best_op_and_rp(out_prices_set, in_prices_set, date_range=10, least_days=3, out_tax=1500, in_tax=1500):
    print(f"Date Range Setting: {date_range} days")
    for i, out_price in enumerate(out_prices_set):
        for j, in_price in enumerate(in_prices_set):
            # Check if the total duration is less than 10 days and inbound date is later than outbound date
            if (datetime.strptime(in_price['Date'], '%Y-%m-%d') - datetime.strptime(out_price['Date'], '%Y-%m-%d')).days <= date_range and datetime.strptime(in_price['Date'], '%Y-%m-%d') > datetime.strptime(out_price['Date'], '%Y-%m-%d') and (datetime.strptime(in_price['Date'], '%Y-%m-%d') - datetime.strptime(out_price['Date'], '%Y-%m-%d')).days >= least_days:
                print(f"Out/In: {out_price['Out/In']}")
                print(f"Arri/Dep: {out_price['Date']} -> {in_price['Date']}")
                print(f"Duration: {(datetime.strptime(in_price['Date'], '%Y-%m-%d') - datetime.strptime(out_price['Date'], '%Y-%m-%d')).days} days")
                print(f"OutPrice: ${out_price['Price']}, InPrice: ${in_price['Price']}")
                print(f"OutTax: ${out_tax}, InTax: ${in_tax}")
                print(f"Total: TWD${out_price['Price'] + in_price['Price'] + out_tax + in_tax}\n")

def get_prices(origin, destination, since, until, passenger_type="ADT", count="1", obtain_num=10):
    url = 'https://sec.jejuair.net/zh-tw/ibe/booking/searchlowestFareCalendar.json'
    data = f'lowestFareCalendar=%7B%22tripRoute%22%3A%5B%7B%22searchStartDate%22%3A%22{since}%22%2C%22originAirport%22%3A%22{origin}%22%2C%22destinationAirport%22%3A%22{destination}%22%7D%2C%7B%22searchStartDate%22%3A%22{since}%22%2C%22originAirport%22%3A%22{destination}%22%2C%22destinationAirport%22%3A%22{origin}%22%7D%5D%2C%22passengers%22%3A%5B%7B%22type%22%3A%22{passenger_type}%22%2C%22count%22%3A%22{count}%22%7D%5D%7D&pageId=0000000127'

    headers = {
        "Host": "sec.jejuair.net",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "accept": "application/json, text/javascript, */*",
        "Content-Length": str(len(json.dumps(data))),
    }

    res = requests.post(url, data=data, headers=headers)

    if res.status_code != 200:
        print('Error: ', res.status_code, res.text, sep='\t', end='\n\n')

    # 將 JSON 字符串轉換為 Python 對象
    data = json.loads(res.text)
    
    price_list = data['data']['lowfares']['lowFareDateMarkets']
    
    outbound_flight = []
    inbound_flight = []
    
    for date in price_list:
        if "lowestFareAmount" in date:
            # Format the date
            
            date_object = datetime.strptime(date['departureDate'], '%Y-%m-%dT%H:%M:%S')
            formatted_date = date_object.strftime('%Y-%m-%d')
            
            temp = {
                    "Out/In": f"{date['origin']} -> {date['destination']}",
                    "Date": formatted_date,
                    "Price": int(date['lowestFareAmount']['fareAmount']),
                }
            if date['destination'] != destination:
                # It's a inbound flight
                inbound_flight.append(temp)
            else:
                # It's a outbound flight
                outbound_flight.append(temp)
    
    sorted_out_prices = sorted(outbound_flight, key=lambda p: p['Price'])
    sorted_in_prices = sorted(inbound_flight, key=lambda p: p['Price'])
    
    # 提取前十個價格
    cheapest_out_prices = sorted_out_prices[:obtain_num]
    cheapest_in_prices = sorted_in_prices[:obtain_num]
    
    return cheapest_out_prices, cheapest_in_prices

###### Airlines ######

airports = {
    "台灣": "TPE",
    "東京成田": "NRT",
    "大阪": "KIX",
    "福岡": "FUK",
    "名古屋": "NGO",
    "札幌": "CTS",
    "沖繩": "OKA",
    "松山": "MYJ",
    "靜岡": "FSZ",
    "威海": "WEH",
    "煙台": "YNT",
    "哈爾濱": "HRB",
    "延吉": "YNJ",
    "仁川": "ICN",
    "金浦": "GMP",
    "釜山": "PUS",
    "濟州": "CJU",
    "光州": "KWJ",
    "清洲": "CJJ",
    "大邱": "TAE",
    "河內": "HAN",
    "胡志明": "SGN",
    "峴港": "DAD",
    "芽莊": "CXR",
    "曼谷": "BKK",
    "清邁": "CNX",
    "馬尼拉": "MNL",
    "宿霧": "CEB",
    "保和島": "TAG",
    "克拉克": "CRK",
    "新加坡": "SIN",
    "永珍/萬象": "VTE",
    "亞庇": "BKI",
    "關島": "GUM",
    "塞班": "SPN",
}

###### Input Data ######

origin = airports['台灣']
destination = airports['峴港']
since = '2023-02-16'
until = '2023-07-28'

##### Main ######

out_prices, in_prices = get_prices(origin, destination, since, until)

print("==== The 10 Cheapest Prices of Outbound ====")
for index, date in enumerate(out_prices):
    if index == 0:
        print(f"==== Dest./Origin: {date['Out/In']} ====")
    print(f"{index+1}. Date: {date['Date']}", f"Amount: ${date['Price']}")

print("\n")

print("==== The 10 Cheapest Prices of Inbround ====")
for index, date in enumerate(in_prices):
    if index == 0:
        print(f"==== Dest./Origin: {date['Out/In']} ====")
    print(f"{index+1}. Date: {date['Date']}", f"Amount: ${int(date['Price'])}")

print("\n")

print("==== The Best Price of Trip ====")
find_best_op_and_rp(out_prices, in_prices)