# type: ignore
from flask import Flask,render_template,url_for,request
import sqlite3
import pandas as pd
import re
conn = sqlite3.connect('data/world.sqlite',check_same_thread=False)
c = conn.cursor()

#func to execute a query
# def sql_executor(raw_query):
#     c.execute(raw_query)
#     data = c.fetchall()
#     return data

def sql_executor(queries):
    results = []
    errors = []
    try:
        for query in queries:
            c.execute(query)
            data = c.fetchall()
            results.append(data)
    except Exception as e:
        # Handle the exception here
        error_message = f"Error executing SQL query: {e}"
        errors.append({'error': error_message})

    return {'results': results, 'errors': errors}



def remove_comments(sql):
    # Remove SQL comments (both single-line and multi-line)
    sql = re.sub(r'(--[^\n]*)|(/\*.*?\*/)', '', sql, flags=re.DOTALL)
    return sql.strip()


#init app
app = Flask(__name__)

#routes
@app.route('/')
def index():
    results = pd.DataFrame([])
    errors = pd.DataFrame([])
    return render_template('index.html',results = results,errors = errors)

@app.route('/process_query',methods=['GET','POST'])
def process_query():
    if request.method == 'POST':
        raw_query = request.form['raw_query']
        raw_query = remove_comments(raw_query)
        queries = [query.strip() for query in raw_query.split(';') if query.strip()]
        initial_results = sql_executor(queries)
        num_columns = [len(item) for sublist in initial_results['results'] for item in sublist]
        num_columns = num_columns[0] if num_columns else None
        print("Required Length is : ",num_columns)
        # Generate column names with numbers
        results1 = initial_results['results']
        results = pd.DataFrame(initial_results['results'])
        print("initial data",initial_results['results'])
        print(results)
        newResults = []
        for i in results1:
            if(len(i)>0):
                newResults.append(i)

        

        styled_html = results.style.set_table_styles([
    {'selector': 'th', 'props': [('border', '1px solid black')]},
    {'selector': 'td, th', 'props': [('border-collapse', 'collapse'), ('border', '1px solid black'), ('padding', '8px')]},
    {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
])
       
        print("Results are : ",newResults)
        errors = pd.DataFrame(initial_results['errors'])
        print("Errors are: ", errors)
    return render_template('index.html',raw_query = raw_query,results = styled_html,queries = queries,errors = errors)


if __name__ == '__main__':
    app.run(debug=True,use_reloader=True)