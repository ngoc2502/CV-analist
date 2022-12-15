from PyPDF2 import PdfFileReader
import os
import pandas as pd
from spacy.pipeline import EntityRuler
from spacy import displacy
import jsonlines
import spacy
import re 
from sympy import true
from spacy.matcher import Matcher
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

json_path="skill_paterns.jsonl"
with jsonlines.open(json_path) as f:
    entities=[line["label"].upper() for line in f.iter()]
# spacy model
nlp=spacy.load("en_core_web_lg")

ruler = nlp.add_pipe("entity_ruler")
ruler.from_disk(json_path)

def extract_pdf(path):
    pdf=PdfFileReader(path)
    number_pages=pdf.getNumPages()
    content=''
    for i in range(number_pages):
        content+=pdf.getPage(i).extractText()    
    content=content.replace('\n','. ').replace('\n\n','. ')
    content=content.replace('\t',' ')   
    return content

def get_path_pdf(path_folder):
    path_pdf=[]
    for dirname,_,filenames in os.walk(path_folder):
        for filename in filenames:
            path_pdf.append(os.path.join(dirname,filename))
    return path_pdf

def get_skill(content_CV):
    doc=nlp(content_CV)
    skill_list=[]
    for ent in doc.ents:
        if ent.label_=='SKILL':
            skill_list.append(ent.text)
    skill_list=list(set(skill_list))
    return skill_list

def get_GPA(content_CV):
    doc=nlp(content_CV)
    sent=list(doc.sents)
    gpa=''
    for s in sent:
        s=s.text
        if s.find('GPA') !=-1 :
            gba_pos= s.find('GPA') 
            for i in range (gba_pos+3,gba_pos+8):
                if (s[i] >'0' and s[i]<'9' or s[i]=='.'):
                    gpa+=s[i]
    if gpa=='':
        return None
    else:
        return gpa

def get_experience(content_CV):
    '''
    Return\n
        None if no experience\n
        List of experience if exist
    '''
    doc=nlp(content_CV)
    sent=list(doc.sents)
    final_res=''
    ex=[]
    for s in sent:
        s_text=s.text.split(' ')
        flag=False
        for i in s_text:
            i=i.lower()
            if i=='experience':
                flag=True
        if flag==True:
            ex.append([s.text])
    if (len(ex)==0):
        final_res=None
    else:
        final_res=ex
    return final_res

def get_education(content_CV):
    doc=nlp(content_CV)
    sent=list(doc.sents)
    edu=''
    pos_edu=-1
    pos_edu_end=-1
    edu_key=['university','academic','college','institute','bachelor','education']
    for s in sent:
        s_text=s.text.lower()
        for key in edu_key:
            if s_text.find(key) != -1:
                edu=s.text
                if key=='educaiton ':
                    pos_edu+=9
                pos_edu=s_text.find(key)

                pos_edu_end=s_text.find('. ',pos_edu)
                edu=edu[pos_edu:pos_edu_end]
                print(edu)
                break
    if edu=='':
        return None
    else:
        return edu

def get_phone(content_CV):
    '''
    Format for Phone-Numbers:
    134567890
    123-456-7890
    (123)(456)(7890)
    123.456.7890
    (123)(456-7890)
    '''
    phone= re.compile(r'''
        (\d{3}|\(\d{3}\))    
        (\s|-|\.)?           
        (\d{3}|\(\d{3}\))    
        (\s|-|\.)?           
        (\d{4}|\(\d{4}\))    
    ''', re.VERBOSE) 
    matchs=phone.finditer(content_CV)
    res = ''
    for match in matchs:
        res+=match.group(0)
        break

    if res=='':
        return None
    else:
        return res

def get_link(link,content_CV):
    matchs=link.finditer(content_CV)
    res=''
    for match in matchs:
        res+=match.group(0)
    if res=='':
        return None
    else:
        return res

def extract_name(content_CV):
    matcher = Matcher(nlp.vocab)
    doc=nlp(content_CV)
    error_key=['city','school','university','freelancer','building']
    warning_key=['curriculum vita']
    cut_pos=-1
    for ent in doc.ents:
        if ent.label_=='PERSON':
            txt=ent.text
            txt_lower=txt.lower()
            flag=True
            for i in error_key:
                if i in txt_lower:
                    flag=False
            for j in warning_key:
                if j in txt_lower:
                    cut_pos=txt_lower.find(j)
                    txt=txt[:cut_pos]
            if flag==True:
                return txt
            else:
                break
    # First name and Last name are always Proper Nouns
    pattern = [
        {'POS': 'PROPN'},{'POS': 'PROPN'},
        ]
    matcher.add('NAME',[pattern])
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text
        
    return None

def name_acc(train_data):
    list_an=[]
    list_txt=[]
    name=[]

    for text,annotation in train_data:
        list_an.append(list(annotation.values()))
        list_txt.append(text)

    target_name=[]
    predic_name=[]

    similar=0
    for i in range(len(list_an)):
        t=''
        p=''
        p=extract_name(list_txt[i])
        predic_name.append(p)
        for j in range(len(list_an[i][0])):
            if list_an[i][0][j][2]=='Name':
                t=list_txt[i][list_an[i][0][j][0]:list_an[i][0][j][1]]
                target_name.append(t)
        if t==p:
            similar+=1
    return (similar/len(list_an)*100)

def extract_all_data(list_content_CV,content_JD):
    df_match=cosine_similar(list_content_CV,content_JD)
    extract_df_match=df_match["Percent_Match_JD"]

    label=['ID','Name','Email','Phone_Number','Related_Link','Skill','Experience','Education','GPA']

    df_information = pd.DataFrame(columns=label) 
    # bitbucket
    mail = re.compile(r'[a-zA-Z0-9-\.]+@[a-zA-Z-\.]*\.(com|edu|net)')
    git = re.compile(r'(gitlab.com/|github.com/)+[a-zA-Z0-9-\.]*')
    web = re.compile(r'(http://|https:// )+[a-zA-Z0-9-"/"-\.]*')
    linkedin = re.compile(r'linkedin.com/+[a-zA-Z0-9-"/"-\.]*')

    for i in range(len(list_content_CV)):
        content=list_content_CV[i]
        link=[]
        link.append(get_link(git,content))
        link.append(get_link(web,content))
        link.append(get_link(linkedin,content))
        row={
                'ID':i,
                'Name':extract_name(content),
                'Email':get_link(mail,content),
                'Phone_Number':get_phone(content),
                'Related_Link':link,
                'Skill':get_skill(content),
                'Experience':get_experience(content),
                'Education':get_education(content),
                'GPA':get_GPA(content)
            }
        new_df=pd.DataFrame([row])
        df_information=pd.concat([df_information,new_df],axis=0,ignore_index=True)
    df_information=df_information.join(extract_df_match)
    df_information=df_information.sort_values(by='Percent_Match_JD', ascending=False)
    return df_information

def cosine_similar(list_CV,JD):
    df_rank_match=pd.DataFrame(columns=['ID','Percent_Match_JD'])
    
    for i in range(len(list_CV)):
        test=[list_CV[i],JD]
        cv = CountVectorizer()
        count_matrix= cv.fit_transform(test)
        match= cosine_similarity(count_matrix)
        
        row = {
            'ID':i,
            'Percent_Match_JD':round(match[0][1]*100,2)
        }

        new_df=pd.DataFrame([row])
        df_rank_match=pd.concat([df_rank_match,new_df],axis=0,ignore_index=True)      

    return df_rank_match 

