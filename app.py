from flask import Flask, request, jsonify, render_template
import sqlite3 as sql
import os,json,requests
import pandas as pd

app = Flask(__name__)


@app.route('/')
def home():
   return render_template("index.html")

@app.route('/getProducts',methods=['POST'])
def getProducts():
    url = request.form['url']
    r = requests.get(url)
    data = r.json()
    rows = data['products']
    return render_template("allProducts.html",rows = rows)

@app.route('/getFilters',methods=['POST'])
def getFilters():

   url = request.form['url']
   r = requests.get(url)
   filters = r.json()

   df = pd.DataFrame.from_dict(filters["products"])
   filters = {}
   gender = df['gender'].unique().tolist()

   df['sizes'] = df['sizes'].str.split(',')
   sizes = list(set([x for y in df['sizes'] for x in y]))

   category = df['category'].unique().tolist()

   filters["gender"] = gender
   filters["sizes"] = sizes
   filters["category"] = category

   return filters

@app.route('/filterPage',methods=['GET','POST'])
def filterPage():

    return render_template("filterPage.html")

@app.route('/filterProducts',methods=['GET','POST'])
def filterProducts():

        filter = request.form["filters"]
        keyword = request.form["keyword"]
        url = request.form["url"]

        r = requests.get(url)
        data = r.json()
        df = pd.DataFrame.from_dict(data["products"])
        df = df[['productId', 'productName','gender','searchImage','mrp', 'price','sizes','category','rating']]


        if filter == 'gender':

            mask = (df['gender'].str.len() == len(keyword)) & (df['gender'].str.contains(keyword, case = False))
            df = df.loc[mask]
            df = df.to_dict('records')

        elif filter == 'category':
            df = df[df.category.str.contains(keyword, case = False) ]
            df = df.to_dict('records')

        elif filter == 'sizes':
            df = df[df.sizes.str.contains(keyword, case = False) ]
            df = df.to_dict('records')

        elif filter == 'all':

            df['filters'] = df['gender'] +' '+ df['sizes'] +' '+ df['category']
            filterList = keyword.split(' ')
            print(filterList)
            filterString = '|'.join(filterList)
            print(filterString)
            df= df[df['filters'].str.contains(filterString, case = False)]
            df= df.to_dict('records')

        return render_template("filterList.html",rows = df)

@app.route('/searchPage',methods=['GET','POST'])
def searchPage():

   return render_template("searchPage.html")

@app.route('/searchProducts',methods=['GET','POST'])
def searchProducts():

    keyword = request.form["keyword"]
    url = request.form["url"]

    r = requests.get(url)
    data = r.json()
    df = pd.DataFrame.from_dict(data["products"])
    df = df[['productId', 'productName','gender','searchImage','mrp', 'price','sizes','category','rating']]
    df['keyword'] = df['productName'] +' '+ df['category']
    df = df[df.keyword.str.contains(keyword, case = False) ]
    df= df.to_dict('records')
    return render_template("searchList.html",rows = df)
