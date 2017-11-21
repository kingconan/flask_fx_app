# coding=utf-8

import requests
import json

from bs4 import BeautifulSoup


def parse_booking(url):
    r = requests.get(url)
    content = r.text
    soup = BeautifulSoup(content, "lxml")

    name = soup.find("h2", class_="hp__hotel-name")
    address = soup.find("span", {"class": "hp_address_subtitle"})
    summary = soup.find("div", {"id": "summary"})
    policies = soup.find("div", {"class": "hp-policies-block"})
    breadcrumb = soup.find("div", {"id": "breadcrumb"})

    hotel = {
        "refer": "booking"
    }

    name = name.text.strip()
    left = name.find(u"（")
    right = name.find(u"）")
    name_en = name[:left]
    name_cn = name[left + 1:right]

    hotel["name"] = name_cn
    hotel["name_en"] = name_en
    hotel["address"] = address.text.strip()
    hotel["description"] = summary.text.strip()

    location_arr = breadcrumb.findAll("div", {"property": "itemListElement"})
    print "location parsing"
    for item in location_arr:
        if not item.has_key("data-google-track"):
            continue
        str = item["data-google-track"]
        if str.find("city") > -1:
            city = item.find("a").text.strip()
            hotel["city"] = city.replace(u"的酒店","").strip()
        elif str.find("district") > -1:
            district = item.find("a").text.strip()
            hotel["district"] = district.replace(u"的酒店", "").strip()

    des_arr = policies.findAll("div", {"class": "description"})
    for des in des_arr:
        policy_name = des.find("p", {"class": "policy_name"}).text.strip()
        value = des.text.strip()
        if policy_name == u"入住时间":
            hotel["checkin"] = value.replace(policy_name, "").strip()
        elif policy_name == u"退房时间":
            hotel["checkout"] = value.replace(policy_name, "").strip()
        elif policy_name == u"儿童和加床":
            hotel["children"] = value.replace(policy_name, "").strip()
        elif policy_name == u"宠物":
            hotel["pet"] = value.replace(policy_name, "").strip()
        elif policy_name == u"酒店接受的银行卡类型":
            buttons = des.findAll("button", {"class": "payment_methods_readability"})
            res = ""
            for btn in buttons:
                res = res + btn["aria-label"] + " "
            hotel["payment"] = res + value.replace(policy_name, "").strip()

        elif policy_name.find(u"预订取消") > -1:
            hotel["cancellation"] = value.replace(u"预订取消/", "").strip().replace(u"预付政策", "").strip()

    facilities = soup.findAll("div", {"class": "facilitiesChecklistSection"})

    f_arr = []

    for f in facilities:
        title = f.find("h5").text.strip()
        li_arr = f.findAll("li")
        content = []
        for li in li_arr:
            content.append(li.text.strip())
        f_arr.append([title, content])

    hotel["facilities"] = f_arr

    print json.dumps(hotel, indent=4, sort_keys=True)

    return hotel


def parse_aman(url):
    """
        only parse the rooms info from synxis of aman
        ProductsHeaderDiv Chain=16840
    """
    r = requests.get(url)
    content = r.text
    soup = BeautifulSoup(content, "lxml")

    arr = soup.find("div", {"class": "ProductsHeaderDiv"})
    res_arr = []
    print arr
    if arr:
        for item in arr:
            info = item.find("div", {"class": "HeaderInfo"})
            title = ""
            if info:
                title = info.find("h3").text().strip()
            d = item.find("div", {"class": "HeaderLongDesc"})
            des = d.find("p").text().strip()
            highlight = d.find("ul").text().strip()
            if not title:
                continue

            res_arr.append({
                "title": title,
                "description" : des,
                "highlight": highlight
            })
            pass
    return res_arr













