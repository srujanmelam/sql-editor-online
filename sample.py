# type: ignore
from flask import Flask,render_template,url_for,request,jsonify
import sqlite3
import pandas as pd
import re
import boto3
import os

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
    success_queries = []
    for query in queries:
        try:
            c.execute(query)
            success_queries.append(query)
        except Exception as e:
            # Handle the exception here
            error_message = f"Error executing SQL query: {e}"
            errors.append({'error': error_message})
        data = c.fetchall()
        results.append(data)
    

    return {'results': results, 'errors': errors, 'success_queries':success_queries}



def remove_comments(sql):
    # Remove SQL comments (both single-line and multi-line)
    sql = re.sub(r'(--[^\n]*)|(/\*.*?\*/)', '', sql, flags=re.DOTALL)
    return sql.strip()


#init app
app = Flask(__name__)

AWS_ACCESS_KEY = 'your_access_key'
AWS_SECRET_KEY = 'your_secret_key'
AWS_REGION = 'your_aws_region'
S3_BUCKET_NAME = 'your_s3_bucket_name'


# Get the filepath of the currently executing Python script
current_file_path = os.path.abspath(__file__)

print(f"The current file path is: {current_file_path}")


def deleteFileWithTimeOut(timeout,file_path):
    try:
        time.sleep(timeout)

        # Delete the file
        os.remove(file_path)
        print(f"File deleted successfully.")
    except Exception as e:
        print(f"Error: {str(e)}")
    return


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
        success_queries = initial_results['success_queries']
        results = pd.DataFrame(initial_results['results'])
        print("initial data",initial_results['results'])
        print(results)
        res_final = []
        for res in results1:
            res_final.append(pd.DataFrame(res))
        styled_html = []
        for res in res_final:
            styled_html.append(res.style.set_table_styles([{'selector': 'th', 'props': [('border', '1px solid black')]},
            {'selector': 'td, th', 'props': [('border-collapse', 'collapse'), ('border', '1px solid black'), ('padding', '8px')]},
            {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
            ]))
#         styled_html = res_final.style.set_table_styles([
#     {'selector': 'th', 'props': [('border', '1px solid black')]},
#     {'selector': 'td, th', 'props': [('border-collapse', 'collapse'), ('border', '1px solid black'), ('padding', '8px')]},
#     {'selector': 'table', 'props': [('border-collapse', 'collapse'), ('width', '100%')]},
# ])
       
        errors = pd.DataFrame(initial_results['errors'])
        print("Errors are: ", errors)
        #,results = styled_html
    return render_template('index.html',results=styled_html,raw_query = raw_query,success_queries = success_queries,errors = errors)


#checking if a specific .sqlite file is present or not
@app.route('/check_file', methods=['POST'])
def check_file():
    file_name = request.form.get('file_name')
    print(file_name)

    # Assuming SQLite files are in the same directory as app.py
    #file_path = os.path.join(os.path.dirname(__file__), f'{file_name}.sqlite')
    file_path = os.path.join(os.path.dirname(__file__), 'data', f'{file_name}.sqlite')
    print("file path is :",file_path)
    print("root path is :",os.path.dirname(__file__))
    if os.path.exists(file_path):
        response = {'status': 'success', 'message': 'File exists!'}
    else:
        response = {'status': 'error', 'message': 'File does not exist.'}

    return render_template('result.html', result_file=response)


@app.route('/awsPutFile', methods=['POST'])
def awsPutFile():
    try:
        # Get parameters from the request
        # userId = request.args.get('luid')
        uuid = request.args.get('attachment_uuid')
        dbName = request.args.get('attachment_name')

        # Initialize S3 client
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)

        # Specify the file path on the server
        local_file_path = current_file_path + '/data/'+dbName+'.sqlite'  # Change this to your local file path

        try:
            with open(local_file_path, 'x') as file:
                # file.write("Hello, this is a new file!")
                print(f"File created successfully at path: {local_file_path}")
                        # Add a delay before deleting the file (e.g., 5 seconds)
                delete_timeout = 4*60*60 #4hrs
                print(f"Waiting for {delete_timeout} seconds before deleting the file...")
                deleteFileWithTimeOut(delete_timeout,local_file_path)

        except FileExistsError:
            print(f"File already exists at path: {local_file_path}")
        except Exception as e:
            print(f"Error: {str(e)}")

        # Specify S3 key (object name in S3)
        s3_key = uuid  # You can adjust the key structure as needed

        # Specify additional metadata
        metadata = {
            'ContentType': 'application/sqlite',
            'ContentDisposition': 'attachment;filename='+dbName
        }

        # Upload file to S3 with metadata
        s3.upload_file(local_file_path, S3_BUCKET_NAME, s3_key, ExtraArgs={'Metadata': metadata})

        return "File uploaded successfully!"

    except Exception as e:
        return f"Error: {str(e)}"




@app.route('/awsGetFile', methods=['GET'])
def awsGetFile():
    try:

                # Get parameters from the request
        # userId = request.args.get('luid')
        s3_key = request.args.get('attachment_uuid')
        # dbName = request.args.get('attachment_name')

        # Initialize S3 client
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)

        # Specify the local file path to save the downloaded file
        local_file_path = current_file_path + '/data/sample.sqlite'  # Change this to your desired local file path

        # Download the file from S3 along with metadata
        s3.download_file(S3_BUCKET_NAME, s3_key, local_file_path)

        # Get metadata for the S3 object
        metadata = s3.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)['Metadata']

        contentType = metadata.ContentType;
        contentDisposition = metadata.ContentDisposition;
        contDispArr = contentDisposition.split("=");
        contTypeArr = contentType.split("/");
        new_file_path = current_file_path + '/data/' + contDispArr[1]+"."+contTypeArr[1];

        try:
            # Rename the file
            os.rename(local_file_path, new_file_path)
            delete_timeout = 5 #5 sec
            print(f"Waiting for {delete_timeout} seconds before deleting the file...")
            deleteFileWithTimeOut(delete_timeout,local_file_path)
            delete_timeout = 4*60*60 #4hrs
            deleteFileWithTimeOut(delete_timeout,new_file_path)

            print(f"File renamed successfully from {current_file_path} to {new_file_path}")
        except FileNotFoundError:
            print(f"The file {current_file_path} does not exist.")
        except FileExistsError:
            print(f"The file {new_file_path} already exists.")
        except Exception as e:
            print(f"Error: {str(e)}")


        # Return the file and metadata in the response
        return send_file(local_file_path, as_attachment=True, download_name=f'{s3_key.split("/")[-1]}', attachment_filename=f'{s3_key.split("/")[-1]}', add_etags=False, cache_timeout=0, conditional=True, metadata=metadata)

    except Exception as e:
        return f"Error: {str(e)}"



if __name__ == '__main__':
    app.run(debug=True,use_reloader=True)
