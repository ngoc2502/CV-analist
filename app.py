from ctypes.wintypes import MSG
from flask import Flask, render_template, request
import os
import extract as e
# from extract import extract_all_data,extract_pdf,get_path_pdf,cosine_similarity
# from extract import get_path_pdf
# from extract import extract_all_data
# from extract import cosine_similarity


app = Flask(__name__)

app.config['UPLOAD_FOLDER_CV'] = 'static/files_CV'
app.config['UPLOAD_FOLDER_JD'] = 'static/files_JD'

path_CV=e.get_path_pdf('./static/files_CV')
path_JD=e.get_path_pdf('./static/files_JD')

def get_result():
    path_CV=e.get_path_pdf('./static/files_CV')
    path_JD=e.get_path_pdf('./static/files_JD')

    list_CV=[]
    for p in path_CV:
        list_CV.append(e.extract_pdf(p))

    content_JD=e.extract_pdf(path_JD)
    df_infor=e.extract_all_data(list_CV)
    df_match=e.cosine_similarity(list_CV,content_JD)

    return df_infor.to_html,df_match.to_html


@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    if request.method=='POST':
        for f_cv in request.files.getlist('file_name_cv'):
            f_cv.save(os.path.join(app.config['UPLOAD_FOLDER_CV'],f_cv.filename))
            return render_template('index.html',msg="Files has been uploaded successfully")

        f_jd=request.files.get('file_name_jd')
        f_jd.save(os.path.join(app.config['UPLOAD_FOLDER_JD'],f_jd.filename))
        return render_template('index.html',msg="Files has been uploaded successfully")

    df_info,df_match=get_result()
    text_file = open("index.html", "w")
    text_file.write(df_info)
    text_file.write(df_match)
    text_file.close()    

    return render_template("index.html",msg="Result")

if __name__ == '__main__':
    app.run(debug=True)
