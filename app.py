from ctypes.wintypes import MSG
from flask import Flask, render_template, request
import os
from extract import extract_all_data,extract_pdf,get_path_pdf,cosine_similar
import json

app = Flask(__name__)

app.config['UPLOAD_FOLDER_CV'] = 'static/files_CV'
app.config['UPLOAD_FOLDER_JD'] = 'static/files_JD'

def get_result():  
    path_CV=[]
    path_JD=[]
    path_CV=get_path_pdf('./static/files_CV')
    path_JD=get_path_pdf('./static/files_JD')
    list_CV=[]
    for p in path_CV:
        list_CV.append(extract_pdf(p))
    content_JD=''
    for p in path_JD:
        content_JD=extract_pdf(p)
        break
    df_infor=extract_all_data(list_CV,content_JD)
    return df_infor


@app.route('/', methods=['GET',"POST"])
def index():
    return render_template('index.html',msg="Select files to uploads")

@app.route('/home', methods=['GET',"POST"])
def home():
    if request.method=='POST' :
        for f_cv in request.files.getlist('file_name_cv'):
            f_cv.save(os.path.join(app.config['UPLOAD_FOLDER_CV'],f_cv.filename))
        
        if (request.files.get('file_name_jd')):
            f_jd=request.files.get('file_name_jd')
            f_jd.save(os.path.join(app.config['UPLOAD_FOLDER_JD'],f_jd.filename))

        return render_template('index.html',msg="Files has been uploaded successfully")
    else:
        df_infor = get_result()
        json_infor=df_infor.to_json(orient="records")
        parsed_infor=json.loads(json_infor)
        final_infor =json.dumps(parsed_infor)
        return final_infor


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)