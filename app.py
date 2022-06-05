# Source:
# https://python.plainenglish.io/keywords-research-in-5-minutes-using-google-suggest-and-python-cc21cffe5625

import base64
from collections import Counter
from flask import Flask,jsonify,redirect,render_template,request,Response,session,url_for
from flask_cors import CORS, cross_origin   # pip install -U flask-cors
from flask_session import Session           # pip install -U flask-session
from io import BytesIO
import json
import logging
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')
import pandas as pd
import requests
import time
from wordcloud import WordCloud

lang='en'
max_letters=1
max_words=50

# Rotate Headers - YouTube Comments


#
# Logging
#
logging.basicConfig(
  filename='TweetGraphs.log',
  # encoding='utf-8', 
  format='%(asctime)s %(levelname)s:%(message)s', 
  level=logging.DEBUG
)

app = Flask(__name__)

#
# Cross Origin to be able to call the API from another machine or port
#
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Use Flask server session to avoid a "Confirm Form Resubmission" pop-up:
# Redirect and pass form values from post to get method
app.config['SECRET_KEY'] = "your_secret_key" 
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_PERMANENT']= False
app.config.from_object(__name__)
Session(app)

@app.route('/getgooglesuggest', methods=['POST'])
@cross_origin()
def api():
  logging.debug(f"/getgooglesuggest - got request: {request.method}")
  data = json.loads(request.data)
  
  # Get and process tweets
  extract(data['keyword'],data['letters'])
  
  if 'results' in session:
    res={
      'results': session['results'],
      'word_graph': session['word_graph']
    }
  else:
    res={
      'results': [],
      'word_graph': ''
    }
  return jsonify(res)
# api

@app.route('/', methods=['GET','POST'])
@cross_origin()
def slash():
  print(f"slash - got request: {request.method}")
  logging.debug(f"slash - got request: {request.method}")
  logging.debug(f"r.f: {request.form}")
  print(request.form)

  # The 'extract' button was pressed
  if 'extract' in request.form:
    logging.debug("extract")    
    data=request.form
    extract(data['keyword'],data['letters'])
  # extract
  
  # Download Option
  elif 'download' in request.form:
    if 'results' not in session:
      print("results not in session")
    else:
      csv = 'Common Word,Google Suggestion\n'
      for row in session['results']:
        csv+=row[0]+","+row[1]+"\n"
      return Response(
        csv,
        mimetype="text/csv",
        headers={'Content-Disposition': 'attachment; filename=thomasmoor.org.csv'}
      ) 
  # download
    
  # Redirect
  if request.method=='POST':
    logging.debug("GoogleSuggest - branch: redirect")
    return redirect(url_for('slash'))

  # Render
  else:
    logging.debug("GoogleSuggest - branch: render index.html")
    if 'results' in session:
        results=session['results']
    else:
      results=[]
    logging.debug("GoogleSuggest - Rendered results:")
    logging.debug(results)

    if 'word_graph' in session:
        word_graph=session['word_graph']
    else:
      word_graph=None

    return render_template("index.html",results=results,word_graph=word_graph)
# slash

def extract(keyword,s_letters):

  # To lower case
  keyword=keyword.lower()
  
  # Split the list of selected letters
  letters=s_letters.split(',')

  # Initiate the list of suggestions done by Google
  suggestions=[]
  
  # Append the search letter by letter
  i=0
  for letter in letters:

    # Restrict the number of letters that can be used
    i+=1
    if i > max_letters:
      break
      
    q=keyword+" "+letter
    print(f"Search {q}")
    logging.debug(f"Search {q}")
    # Call Google Suggest
    URL="http://suggestqueries.google.com/complete/search?client=firefox&hl="+str(lang)+"&q="+q
    headers = {'User-agent':'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    data = json.loads(response.content.decode('utf-8'))
    # print(f"data {letter}:")
    # print(data)
    
	# Subset of suggestions
    # tmp=[keyword,letter]
    for suggestion in data[1]:
      # print(f"for suggestion: {suggestion}")
      if(suggestion!=keyword):
        # tmp.append(suggestion)
        suggestions.append(suggestion)
    # suggestions.append(tmp)
    
    # print(f"suggestions: {suggestions}")
    
    # Temporize
    time.sleep(1)
    
  # for letter

  # Collect the words
  words=[]
  for suggestion in suggestions:
    tmp_words = nltk.word_tokenize(str(suggestion))
    for word in tmp_words:
      if(word not in stop_words and len(word)>1):
        words.append(word)
        
  # print(f"words: {words}")

  # Identify the most used words
  most_common_words= [word for word, word_count in Counter(words).most_common(max_words)]
  # print(f"most_common_words: {most_common_words}")
  
  # Create a Word Cloud graph
  word_cloud(700,1000,5,10,most_common_words,"")
  word_graph=get_graph()
  session['word_graph']=word_graph
  
  # Suggestions per most common word
  results=[]
  for common_word in most_common_words:
    for suggestion in suggestions:
      if(common_word in str(suggestion)):
        results.append([common_word,suggestion])
  session['results']=results
  
# extract

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0) # Go to the beginning of the buffer
    image_png=buffer.getvalue()
    graph=base64.b64encode(image_png)
    graph=graph.decode('utf-8')
    buffer.close()
    return graph
# get_graph
	
def word_cloud(cloud_height,cloud_width,fig_height,fig_width,suggestions,title):
  allWords=' '.join( [t for t in suggestions])
  # print(allWords)
  cloud=WordCloud(width=cloud_width,height=cloud_height,random_state=21,max_font_size=119,stopwords=stop_words).generate(allWords)
  plt.imshow(cloud,interpolation="bilinear")
  plt.title(title)
  plt.axis('off')
  plt.margins(x=0, y=0)
  # plt.show()
# word_cloud

if __name__ == '__main__':
  stop_words = set(stopwords.words('english'))
  app.run(debug=True,host='0.0.0.0',port=5004)