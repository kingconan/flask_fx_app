# -*- coding: utf-8 -*-

import sys
import pyexcel as pe
from decimal import Decimal
import pprint


def parse_fx_excel(filepath):
    print "working..."
    book = pe.get_book(file_name=filepath)
    cnt = 0
    tc = 0
    all_data = {}
    for sheet in book:
        name = sheet.name
        cnt = cnt + 1
        if cnt > 1:
            sheet.name_columns_by_row(0)
            # print sheet.colnames
            records = sheet.to_records()
            sum_volume = Decimal("0.00")
            sum_commission = Decimal("0.00")
            data = {}
            for record in records:
                if record["Login"]:
                    tc += 1
                    sum_volume += Decimal(str(record["Volume"]))
                    sum_commission += Decimal(str(record["Commission"]))
                    if not data.has_key(record["Symbol"]):
                        data[record["Symbol"]] = {"volume": Decimal("0.00"), "commission": Decimal("0.00")}

                    data_volume = data[record["Symbol"]].get("volume")
                    data_commission = data[record["Symbol"]].get("commission")

                    data_volume = data_volume + Decimal(str(record["Volume"]))
                    data_commission = data_commission + Decimal(str(record["Commission"]))

                    data[record["Symbol"]]["volume"] = data_volume
                    data[record["Symbol"]]["commission"] = data_commission

                    # print "%s   %s  %s  %s" % (record["Login"], record["Symbol"], record["Commission"], record["Volume"])
            print "user %s, volume=%s, commission=%s" % (name, sum_volume, sum_commission)
            all_data[name] = {
                "volumes": sum_volume,
                "commission": sum_commission,
                "group": data,
                "details": []
                # all details
            }
    print "%d rows processed" % tc
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(all_data)
    print "ok"
    return all_data