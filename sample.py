# type: ignore
from flask import Flask,render_template,url_for,request
import sqlite3
import pandas as pd
conn = sqlite3.connect('data/world.sqlite',check_same_thread=False)
c = conn.cursor()

#func to execute a query
def sql_executor(raw_query):
    c.execute(raw_query)
    data = c.fetchall()
    return data

#init app
app = Flask(__name__)

#routes
@app.route('/')
def index():
    results = pd.DataFrame([])
    return render_template('index.html',results = results)

@app.route('/process_query',methods=['GET','POST'])
def process_query():
    if request.method == 'POST':
        raw_query = request.form['raw_query']
        initial_results = sql_executor(raw_query)
        results = pd.DataFrame(initial_results)
    return render_template('index.html',raw_query=raw_query,results = results)

if __name__ == '__main__':
    app.run(debug=True,use_reloader=True)