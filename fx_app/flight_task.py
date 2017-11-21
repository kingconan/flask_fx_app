# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json
import base64
from Crypto.Cipher import AES


def umetrip(flight_number="DL582", flight_date="2017-10-21"):
    '''
    获得城市信息，目前携程无法获得城市信息
    :param flight_number:
    :param flight_date:
    :return:
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
        'Host': 'www.umetrip.com'
    }
    url = "http://www.umetrip.com/mskyweb/fs/fc.do?flightNo=%s&date=%s&channel=" % (flight_number, flight_date)
    content = requests.get(url, headers=headers)
    soup = BeautifulSoup(content.text, 'html.parser')

    cities = soup.select('li[class="city"]')
    arr = []
    for city in cities:
        city_arr = city.span.text.split("-")
        arr.append(city_arr)
    return arr


def ctrip(flight_number="DL582", flight_date="2017-10-21"):
    '''
    :param flight_number:
    :param flight_date:
    :return: [
            {
                airline,arrCity,arrDate,arrDay,arrTerminal,
                depCity,depDate,depDay,depTerminal,depTime,
                duration,flightNumber,stopDuration
            }
        ]
    special case:
        19:10-1天
        09:10+1天
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
        'Host': 'flights.ctrip.com'
    }
    url = "http://flights.ctrip.com/actualtime/fno--%s-%s.html" % (flight_number, flight_date.replace("-", ""))
    print url
    content = requests.get(url, headers=headers)
    soup = BeautifulSoup(content.text, 'html.parser')

    detail_info = soup.select('div[class="detail-info"]')
    arr = []
    fly_header = []
    for detail in detail_info:
        tmp = {

        }

        if not fly_header:
            fly_header = detail.select_one('div[class="detail-t"]')

        if fly_header:
            airline = fly_header.select_one('span[class="ml5"]')
            date = fly_header.select_one('span[class="ml10"]')
            number = fly_header.select_one('strong[class="ml5"]')
            print airline.text
            print number.text
            print date.text
            tmp['airline'] = airline.text
            tmp['flight_number'] = number.text
            tmp['date'] = date.text

        m = detail.select_one('div[class="detail-m"]')
        fly = m.select_one('div[class="detail-fly"]')

        departure = fly.select_one('div[class="inl departure"]')
        arrive = fly.select_one('div[class="inl arrive"]')
        departure_time = departure.select_one('p[class="time"]')
        arrive_time = arrive.select_one('p[class="time"]')
        print departure_time.text
        print arrive_time.text

        tmp['departure_time'] = departure_time.text[:5]
        tmp['departure_days'] = departure_time.text[5:]
        tmp['arrive_time'] = arrive_time.text[:5]
        tmp['arrive_days'] = arrive_time.text[5:]

        fly_route = m.select_one('div[class="detail-fly detail-route"]')
        departure = fly_route.select_one('div[class="inl departure"]')
        arrive = fly_route.select_one('div[class="inl arrive"]')
        duration = fly_route.select_one('div[class="inl between"]')
        duration_text = duration.p.text.strip().replace(u'飞行时长','')
        departure_arr = departure.p.text.splitlines()
        arrive_arr = arrive.p.text.splitlines()
        print departure_arr[0].strip()
        print departure_arr[1].strip()
        print arrive_arr[0].strip()
        print arrive_arr[1].strip()
        print duration_text

        tmp['departure_city'] = departure_arr[0].strip()
        tmp['arrive_city'] = arrive_arr[0].strip()
        tmp['departure_terminal'] = departure_arr[1].strip()
        tmp['arrive_terminal'] = arrive_arr[1].strip()
        tmp['duration'] = duration_text

        through_line = m.select_one('div[class="through-line"]')
        if through_line:
            stop_duration = through_line.span.text.replace(u"经停", "").strip()
            print stop_duration
            tmp['stop_duration'] = stop_duration

        arr.append(tmp)
    return arr


def get_flight(flight_number="DL582", flight_date="2017-10-21"):
    flight_arr = ctrip(flight_number, flight_date)
    city_arr = umetrip(flight_number, flight_date)
    if len(flight_arr) == len(city_arr):
        for i in range(len(flight_arr)):
            flight_arr[i]["departure_city"] = city_arr[i][0]
            flight_arr[i]["arrive_city"] = city_arr[i][1]

    print json.dumps(flight_arr)
    return flight_arr

# get_flight()
umetrip_key = "Ume2012Trip0309\0"
json_text = '{"rpver":"1.0","netType":"1","rcid":"131541348","rcver":"IOS_i03_04.36.1010","rcuuid":"m4be1ad5a2352464a8c54a44369c4db24","rsid":"104847$$a624db45cbbc4c4781e39588e5726767pgvlCYJeqLG","rkey":"2017-10-21 05:28:37 +0000","rchannel":"00000000","rname":"GetFlightStatusByNo","rpversion":"1.0","lastTransactionID":"m4be110600381508563671317","transactionID":"m4be0106002915085637","MD5digest":"jp22cFDm0A0","lastReqTime":"463","rparams":{"flightNo":"DL58","deptFlightDate":"2017-10-22"},"rpid":"1060029"}'

def aes_encode(raw, key):
    # ref: http://stackoverflow.com/a/12525165
    BS = 16
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    raw = pad(raw)
    cipher = AES.new((key), AES.MODE_ECB)
    res = base64.b64encode(cipher.encrypt(raw))
    return res


def aes_decode(raw, key):
    BS = 16
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    raw = base64.b64decode(raw)
    cipher = AES.new((key), AES.MODE_ECB)
    res = cipher.decrypt(raw)
    return res

import hashlib

if __name__ == '__main__':
    encode_str = aes_encode(json_text, umetrip_key)
    decode_str = aes_decode(encode_str, umetrip_key)
    print encode_str
    print decode_str
    # str0 = "m4be110600291508563717960"
    # str1 = "1.0"
    # str2 = "IOS_i03_04.36.1010"
    # str3 = "00000000"
    str0 = "DL58"
    str1 = ""
    str2 = ""
    str3 = "2017-10-22"
    digest = "jp22cFDm0A0"
    m = hashlib.md5()
    m.update(str0)
    m.update(str1)
    m.update(str2)
    m.update(str3)
    print base64.b64encode(m.digest())