from flask import Flask, render_template, request,jsonify,redirect
import requests
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pandas as pd
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
import pymongo

app = Flask(__name__)


@app.route("/")
@cross_origin()
def home():
    return render_template('index.html')

@app.route("/review",methods=["GET","POST"])
@cross_origin()
def review_items():
    if request.method=='POST':
        try:
            # Getting items to be search from index page
            search_query=request.form.get('query').replace(" ","")
            mobile_model=request.form.get('query')
    
            flipkart_url='https://www.flipkart.com/search?q='
    
            base_url='https://www.flipkart.com'

            # parsing query link using BeautifulSoup
    
            response=requests.get(flipkart_url+search_query)
            flipkart_html=bs(response.content,'html.parser')


            flipkart_items=flipkart_html.find_all('a',{'class':'_1fQZEK'})
            
            reviews=[] # collection of all records

            # Reviewing the first product of query
            product_link=base_url+flipkart_items[0]['href']
            prodRes=requests.get(product_link)
            prodRes.encoding='utf-8'
            prod_html=bs(prodRes.content,'html.parser')

            # Scraping customer names
            customer_names=prod_html.find_all('p',{'class':'_2sc7ZR _2V5EHH'})

            # Scraping rating of products
            ratings=prod_html.find_all('div',{'class':'_3LWZlK _1BLPMq'})

            # Scraping comment heading of products
            comment_headings=prod_html.find_all('p',{'class':'_2-N8zT'})
            
            # Scraping comment of products
            comments=prod_html.find_all('div',{'class':'t-ZTKy'})


            # scraping review of each customer into myDict object
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
                
                myDict={'Product':mobile_model,'Customer_Name':name,'Rating':rating,'CommentHead':comment_heading,'Comment':comment}
                
                # scraping review of all customers into review list
                reviews.append(myDict)
                
                # Converting data into Data Frames and then into csv file using pandas library
                flipkart_reviews=pd.DataFrame.from_dict(reviews)
                flipkart_reviews.to_csv(f"{search_query}.csv",index=None)

            # 1. Establishing connection
            client = pymongo.MongoClient("mongodb+srv://pwskills:pwskills@cluster0.nj6x4ec.mongodb.net/?retryWrites=true&w=majority")
            # 2. Creating database
            db = client['flipkart_scraping']
            # 3. Create collection
            flipkart_review_coll=db['flipkart_review']
            # 4. Insert records
            flipkart_review_coll.insert_many(reviews)
            # 5. Close connection
            client.close()

            return render_template('results.html',reviews=reviews)
        except Exception as e:
            logging.info(e)
            return f"something is wrong."
    else:
        return render_template('index.html')

    

if __name__=="__main__":
    app.run(host="0.0.0.0",debug=True)
