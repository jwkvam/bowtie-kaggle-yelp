#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bowtie import App, command
from bowtie.visual import Plotly

from bowtie.control import Dropdown
from bowtie import cache
import numpy as np
import pandas as pd
import plotlywrapper as pw


business = pd.read_csv('yelp_business.csv.gz')
business = business[business.review_count >= 50]
checkin = pd.read_csv('yelp_checkin.csv.gz')
reviews = pd.read_pickle('reviewsub.pkl.gz')


def unique_categories():
    allcats = business.categories.str.split(';')
    cats = []
    for cat in allcats:
        cats += cat
    return list(set(cats))

categories = sorted(unique_categories())

catdd = Dropdown(values=categories, labels=categories, caption='Category')
stars = Plotly()
revdate = Plotly()
busy = Plotly()


def gen_stars(label):
    buss1 = business[business.categories.str.contains(label)]

    cache['bids'] = buss1.business_id
    chart = pw.scatter(buss1.review_count, buss1.stars, text=buss1.name)
    chart.xlabel('reviews')
    chart.ylabel('stars')
    chart.title(label)
    chart.layout['hovermode'] = 'closest'
    return chart


def gen_busy(biz_id):
    bussy = checkin[checkin.business_id == biz_id].groupby('hour').sum()
    bussy.index = [int(x[0]) for x in bussy.index.str.split(':')]
    bussy.index.name = 'hour'
    bussy = bussy.sort_index()
    chart = bussy.reindex(index=range(24)).fillna(0).plotly.bar()
    chart.xlabel('hour')
    chart.ylabel('checkins')
    return chart


def viz(cat):
    if cat:
        starchart = gen_stars(cat['label'])
        stars.do_all(starchart.dict)


def vizplace(place):
    bid = cache['bids'][place['point']]
    name = business[business.business_id == bid].name.values[0]

    chart = gen_busy(bid)
    chart.title(name)
    busy.do_all(chart.dict)
    revbid = reviews[reviews.business_id == bid]

    chart = pw.scatter(revbid.date, revbid.stars)
    chart.data[0]['marker'] = {'opacity': 1 / np.log(revbid.shape[0])}
    chart.ylabel('stars')
    chart.title(name)
    chart.layout['hovermode'] = 'closest'
    revdate.do_all(chart.dict)


@command
def main():
    app = App(rows=3, columns=2, sidebar=False, debug=True)
    app.rows[0].auto()
    app[0] = catdd
    app[1] = stars
    app[2, 0] = busy
    app[2, 1] = revdate

    app.subscribe(viz, catdd.on_change)
    app.subscribe(vizplace, stars.on_click)
    return app
