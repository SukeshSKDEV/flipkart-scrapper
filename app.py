from flask import Flask, render_template, request,jsonify,redirect
import requests
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pandas as pd
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/review",methods=["GET","POST"])
def review_items():
    search_query=request.form.get('query').replace(" ","")
    flipkart_url='https://www.flipkart.com/search?q='
    base_url='https://www.flipkart.com'
    response=requests.get(flipkart_url+search_query)
    flipkart_html=bs(response.content,'html.parser')
    flipkart_items=flipkart_html.find_all('a',{'class':'_1fQZEK'})
    
    # Reviewing the first product of query
    reviews=[]
    product_link=base_url+flipkart_items[0]['href']
    prodRes=requests.get(product_link)
    prodRes.encoding='utf-8'
    prod_html=bs(prodRes.content,'html.parser')

    customer_names=prod_html.find_all('div',{'class':'_2sc7ZR _2V5EHH'})
    ratings=prod_html.find_all('div',{'class':'_3LWZlK _1BLPMq'})
    comment_headings=prod_html.find_all('p',{'class':'_2-N8zT'})
    comments=prod_html.find_all('div',{'class':'t-ZTKy'})

    for i in range(len(customer_names)):
        try:
            #name.encode(encoding='utf-8')
            name = customer_names[i].text
        except:
            logging.info("name")

        try:
            #rating.encode(encoding='utf-8')
            rating = ratings[i].text
        except:
            rating = 'No Rating'
            logging.info("rating")
        
        try:
            #comment_heading.encode(encoding='utf-8')
            comment_heading = comment_headings[i].text
        except:
            comment_heading = 'No Comment Heading'
            logging.info(comment_heading)

        try:
            #comment.encode(encoding='utf-8')
            comment = comments[i].text
        except Exception as e:
            logging.info(e)
        
        myDict={'Product':search_query,'Rating':rating,'CommentHead':comment_heading,'Comment':comment}
        reviews.append(myDict)
        flipkart_reviews=pd.DataFrame.from_dict(myDict)
        flipkart_reviews.to_csv("sk.csv")
    
    return render_template("results.html")

        
        


    return product_link

if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True,port=8080)
