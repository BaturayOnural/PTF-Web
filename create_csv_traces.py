from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

from datetime import time
from datetime import date
from collections import namedtuple

import os
import csv
import csv
import sys





app2 = Flask(__name__)
app2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///MCPBase_TL.db'

db = SQLAlchemy(app2)


class MCP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)


f = open('filters.csv', 'r')

with f:

    reader = csv.reader(f)

    count = 0
    for row in reader:
        for e in row:
        	if count == 0:
        		start_date1 = e
        		count = count + 1
        	elif count == 1:
        		end_date1 = e
        		count = count + 1
        	elif count== 2:
        		start_hour = e
        		count = count + 1
        	elif count ==3:
        		end_hour = e
        		count = count + 1
        	else:
        		print("Filtering error!")
            

print(start_hour)
print(end_hour)

year = int(start_date1[:4])
month = int(start_date1[5:7])
day = int(start_date1[8:])

year2 = int(end_date1[:4])
month2 = int(end_date1[5:7])
day2 = int(end_date1[8:])


start_date2 = datetime.datetime(year, month, day)
end_date2 = datetime.datetime(year2, month2, day2)

rows = db.session.query(MCP).filter(MCP.date.between(start_date2, end_date2))

#################################  TL
fp = open('trace_tl.csv', 'w')
myFile = csv.writer(fp)
header = ["Date", "TL"]
myFile.writerow(header)

for row in rows:
    date = row.date
    price = row.price
    data = [date, price]
    myFile.writerow(data)
fp.close()



