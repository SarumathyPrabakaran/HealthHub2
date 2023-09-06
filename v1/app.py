from flask import Flask, flash, render_template, request, redirect, url_for, session
from sqlalchemy.orm import Session
from datetime import date,timedelta,datetime
from sqlalchemy import and_
from postgresdb import session1,logincred,Profiles,Activity,ActivityTracking,Forum
import requests
import openai
import dotenv
import os
import logging
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

dotenv.load_dotenv()

app.config['SECRET_KEY'] = "wishlistpage"

openai.api_key = os.environ.get("API_KEY")

# user_id = 0

def get_current_date():
    return date.today()

# num_person = 5
# user_id_g = 1
d = { "son" :0, "mom" : 1, "dad" :2}

# def get_num_person_int(person):
#     return d.get(person.lower(), 0)

# def set_user_id(id):
#     global user_id_g
#     user_id_g = id
#     return user_id_g

# def GetKey(val):
#     for key, value in d.items():
#         if val == value:
#            return key
#     return "son"


# def get_person(person):
#     # d = {"son": 0}
#     # prof = session1.query(Profiles).all()
#     # for pro in prof:
#     #     d[(pro.profiles).lower()] = pro.id
    
#     print(d)
#     if(person=="son"):
#         print("son")
#         global num_person
#         num_person = d["son"]
#     elif(person=="mom" ):
#         num_person = d["mom"]
#     elif(person=="dad"):
#         num_person = d["dad"]
#     return num_person



@app.route('/', methods = ["GET"])
def front_home():
    return render_template('home.html')



# @app.route("/login", methods= ["GET"])
# def home():
#     profile_list = ["son","mom","dad"]
#     return render_template("login.html", profile_list=profile_list)


def update_activitytracking():
    # session = get_db()
    activity_table = session1.query(Activity).all()
   
    for act in activity_table:
        track = ActivityTracking(date = act.date, activity_id = act.activity_id, status = act.status)
        session1.add(track)
        session1.commit()


@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")
        person = request.form.get("person")
        print(email, password, person)
        print(session1.query(logincred.email).all(), list(session1.query(logincred.password).filter(email == logincred.email)))
        if (email,) in session1.query(logincred.email).all() and password == list(session1.query(logincred.password).filter(email == logincred.email))[0][0]:
            id = session1.query(logincred.id).filter(email == logincred.email).first()[0]
            print(id)
            db_user = session1.query(logincred).filter(email == logincred.email).first()
            now_date = date.today()
            #now_date="2023-01-20"

            try:
                prev_date = session1.query(Activity.date).first()[0]
            except:
                prev_date = 0
            if(str(now_date)!= str(prev_date)):
                update_activitytracking()
                uid=session1.query(Activity).all()
                for act in uid:
                    act.status = 0
                    act.date = now_date
                    session1.commit()
                # print(uid)
            # set_user_id(id)
            #print("userid----->",id,user_id_g)
            
            session["user_id"] = id 
            session["num_person"] = person
            session["num_person_int"] = d.get(person.lower(), 0)
            session["username"] = email.split("@")[0]
            return redirect(url_for('display', id=id))
        else:
            return {"Message" : "Auth"}
            flash("Sign in")

    profile_list = ["son","mom","dad"]
    return render_template("login.html", profile_list=profile_list)

@app.route("/loginperson/<int:id>", methods = ["GET","POST"])
def login_person(id):
    if request.method=="POST":
        person = request.form.get("person")
        session["user_id"] = id 
        session["num_person"] = person
        session["num_person_int"] = d.get(person.lower(), 0)
        


        return redirect(url_for('display', id=id))



@app.route("/signup", methods = ["GET","POST"])
def addUser():
    if request.method=="POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user=logincred(email=email,password=password)
        session1.add(user)
        session1.commit()
        id = session1.query(logincred.id).filter(email == logincred.email).first()[0]
        print(id)
        session["user_id"] = id
        session["num_person"] = "Son"
        session["num_person_int"] = d.get("son", 0)
        session["username"] = email.split("@")[0]

        return redirect(url_for('display', id=id))
    return render_template("signup.html")


@app.route("/get/profiles/<int:id>",methods=["GET"])
def display(id):
    if "user_id" in session:
        profile_list = session1.query(Profiles.profiles).filter(Profiles.user_id == id).all()
        profile_ids = session1.query(Profiles.id).filter(Profiles.user_id == id).all()
        l=[]
        for i in range(len(profile_list)):
            l.append((profile_ids[i][0],profile_list[i][0]))
        user_name = session1.query(logincred.email).filter(logincred.id==id).first()[0].split("@")[0]
        return render_template('display.html',l=l, id=id, user_name= user_name, view= session["num_person"].title(), date=get_current_date())
    else:
        return render_template('404.html')


@app.route("/add/profiles/<int:id>",methods=["GET","POST"])
def add_profiles(id):
    if "user_id" in session:
        if request.method=="POST":
            profile = request.form.get("profile")
            print(profile)
            pro=Profiles(user_id=id,profiles=profile)
            session1.add(pro)
            session1.commit()
            return redirect(url_for('display', id=id))
    else:
        return render_template('404.html')
    

@app.route("/get/activities/<int:id>", methods = ["GET", "POST"])
def get_activities(id):
    if "user_id" in session:
        tasks = session1.query(Activity.activity).filter(and_ (Activity.profile_id == id , Activity.status==0)).all()
        ids = session1.query(Activity.activity_id).filter(and_(Activity.profile_id == id , Activity.status==0)).all()
        pt=[]
        for i in range(len(tasks)):
            pt.append((ids[i][0],tasks[i][0]))
        print(pt)

        ct=[]
        c_tasks=session1.query(Activity.activity).filter(and_ (Activity.profile_id == id , Activity.status==1)).all()
        c_ids = session1.query(Activity.activity_id).filter(and_(Activity.profile_id == id , Activity.status==1)).all()
        for i in range(len(c_tasks)):
            ct.append((c_ids[i][0],c_tasks[i][0]))
        print(ct)
        profile_name =  session1.query(Profiles.profiles).filter(Profiles.id == id).first()[0]
        user_id = session1.query(Profiles.user_id).filter(Profiles.id == id).first()[0]
        return render_template('tasks.html', pt = pt,ct=ct, id =id, user_id =  user_id,  name = profile_name, num_person = session["num_person_int"],  date = date.today(), view = session["num_person"].title())    

    else:
        return render_template('404.html')

@app.route("/add/activities/<int:id>", methods = ["POST"])
def add_activities(id):
    
    if "user_id" in session:
        if request.method == "POST":

            task = request.form.get("task")
            task=Activity(profile_id=id,activity=task,date = get_current_date())
            session1.add(task)
            session1.commit()
            return redirect(url_for('get_activities', id=id))

    else:
        return render_template('404.html')

@app.route("/update/task/<int:id>", methods = ["GET"])
def update_status(id):
    if "user_id" in session:
        task = session1.query(Activity).filter(Activity.activity_id==id).first()
        uid=session1.query(Activity.profile_id).filter(Activity.activity_id==id).first()
        task.status = 1
        session1.commit()
        return redirect(url_for('get_activities', id=uid[0]))

    else:
        return render_template('404.html')

@app.route("/history/<int:id>", methods = ["GET"])
def history(id):
    if "user_id" in session:
        statuses=[]
        date = session1.query(ActivityTracking.date).filter(ActivityTracking.activity_id==id).all()
        status = session1.query(ActivityTracking.status).filter(ActivityTracking.activity_id==id).all()
        task = session1.query(Activity.activity).filter(Activity.activity_id==id).first()[0]

        pro_id = session1.query(Activity.profile_id).filter(Activity.activity_id==id).first()[0]
        profile = session1.query(Profiles.profiles).filter(Profiles.id==pro_id).first()[0]

        d={0:"incomplete",1:"completed"}

        for i in range(len(date)):

            statuses.append((str(date[i][0]),d[status[i][0]]))
        user_id = session1.query()
        return render_template('history.html',status=statuses,task=task,profile=profile,date=get_current_date(), view=  session["num_person"].title(), act_id=pro_id, user_id= session["user_id"])
    else:
        return render_template('404.html')

# @app.route("/yesterday/<int:id>", methods = ["GET"])
# def yesterday(id):
#     task_ids = session1.query(Activity.activity_id).filter(Activity.profile_id==id).all()
#     task_ids1=[]
#     for i in task_ids:
#         task_ids1.append(i[0])
#     statuses=[]
#     d={0:"incomplete",1:"completed"}
#     today = get_current_date()
#     yesterday = today - timedelta(days = 1)
#     #yesterday = "2023-01-19"
#     for i in task_ids1:
#         s = session1.query(ActivityTracking.status).filter(and_ ((ActivityTracking.date) == (yesterday) , ActivityTracking.activity_id==i)).first()[0]
#         t= session1.query(Activity.activity).filter(Activity.activity_id==i).first()[0]
#         statuses.append((t,str(yesterday),d[s]))
#         print(statuses[-1])
#     pro_id = session1.query(Activity.profile_id).filter(Activity.activity_id==id).first()[0]
#     profile = session1.query(Profiles.profiles).filter(Profiles.id==pro_id).first()[0]
    
#     return render_template('yesterday.html',status=statuses,profile=profile, date= yesterday, id =  id, view= session["num_person"].title(), y_date = yesterday, user_id = session["user_id"])



@app.route("/yesterday/<int:id>", methods = ["GET","POST"])
def yesterday(id):
    if "user_id" in session:
        if request.method=="POST":
            yesterday_not_found = False
            date_format = "%Y-%m-%d"
            try:
                now_date = datetime.strptime(request.form.get("now_date"),date_format)  #convert to date
            except:
                yesterday_not_found = True
                #return render_template('yesterday.html', status = statuses, profile = profile, id =  id, y_date = yesterday, back_exists =  True, view  =  session["num_person"].title(), no_tasks =  no_tasks, pro_id = pro_id, user_id = session["user_id"])

                now_date = ''
            number = request.form.get("number")
            pro_id = session1.query(Activity.profile_id).filter(Activity.activity_id==id).first()[0]
            profile = session1.query(Profiles.profiles).filter(Profiles.id==pro_id).first()[0]
            
            task_ids = session1.query(Activity.activity_id).filter(Activity.profile_id==id).all()
            task_ids1=[]
            for i in task_ids:
                task_ids1.append(i[0])
            statuses=[]
            if(now_date == (date.today()- timedelta(days = 1)) and number==0):
                
                return redirect(url_for('get_activities', id = id))
            d={0:"incomplete",1:"completed"}
            if(number==1):
                today = now_date
                yesterday = today - timedelta(days = 1)
                
            else:
                today = now_date
                yesterday = today + timedelta(days = 1)
                
            #yesterday = "2023-01-19"
            try:
                for i in task_ids1:
                    s = session1.query(ActivityTracking.status).filter(and_ ((ActivityTracking.date) == (yesterday) , ActivityTracking.activity_id==i)).first()[0]
                    t= session1.query(Activity.activity).filter(Activity.activity_id==i).first()[0]
                    statuses.append((t,str(yesterday),d[s]))
                    print(statuses[-1])

            except:
                pass

            no_tasks = False
            if(len(statuses)==0 or now_date==''):
                no_tasks = True
            
            return render_template('yesterday.html', status = statuses, profile = profile, id =  id, y_date = yesterday, back_exists =  True, view  =  session["num_person"].title(), no_tasks =  no_tasks, pro_id = pro_id, user_id = session["user_id"], yesterday_not_found=True)
        task_ids = session1.query(Activity.activity_id).filter(Activity.profile_id==id).all()
        task_ids1=[]
        for i in task_ids:
            task_ids1.append(i[0])
        statuses=[]
        d={0:"incomplete",1:"completed"}
        today = get_current_date()
        yesterday = today - timedelta(days = 1)
        #yesterday = "2023-01-19"
        for i in task_ids1:
            s = session1.query(ActivityTracking.status).filter(and_ ((ActivityTracking.date) == (yesterday) , ActivityTracking.activity_id==i)).first()[0]
            t= session1.query(Activity.activity).filter(Activity.activity_id==i).first()[0]
            statuses.append((t,str(yesterday),d[s]))
            print(statuses[-1])
        pro_id = session1.query(Activity.profile_id).filter(Activity.activity_id==id).first()[0]
        profile = session1.query(Profiles.profiles).filter(Profiles.id==pro_id).first()[0]
        
        return render_template('yesterday.html',status=statuses,profile=profile, date= yesterday, id =  id, view= session["num_person"].title(), y_date = yesterday, user_id = session["user_id"])
    else:
        return render_template('404.html')


# @app.get("/logout", response_class=RedirectResponse)
# def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
#     response = RedirectResponse(url="/")
#     response.delete_cookie("Authorization")
#     return response

@app.route('/dictionary',methods = ["GET","POST"])
def dictionary():
    if request.method=="POST":
            
        word = request.form.get('word', None)
        dict_url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
        try:
            response = requests.get(dict_url)
            if response.status_code == 200:
                data = response.json()
                meaning = data[0]['meanings'][0]['definitions'][0]['definition']

            else:
                meaning = "No definition found for the word."
                
        except requests.exceptions.RequestException:
            meaning =  "An error occurred while connecting to the dictionary service."
        print(meaning)
        return render_template('dict.html',meaning = meaning)
        
    return render_template('dict.html')   

@app.route('/medicine', methods=['POST','GET'])
def get_medical_term_explanation():
    # Extract the medical term from the POST request
    if request.method=="POST":
        medical_term = request.form.get('term')
        print(medical_term)
    # Define the prompt for GPT-3
        prompt = f"Explain the medicine named '{medical_term}' in simple words and tell whether the medicine causes sleep or not."

    # Use GPT-3 to generate an explanation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
        {"role": "system", "content": "You are a helpful assistant that explains medical terms and medicine. "},
        {"role": "user", "content": prompt},
        ],
        max_tokens=150  # Adjust as needed
    )

    # Extract and return the explanation from the GPT-3 response
        explanation = response["choices"][0]["message"]["content"]
        
        return render_template('explain.html', med_term = medical_term, explanation = explanation)
    
    return render_template('explain.html')


@app.route('/forum', methods = ["GET","POST"])
def forum():
    if "user_id" in session:
        if request.method=="POST":
            content = request.form.get('content')
            if content!= '':
                data_to_add = Forum(user_id = session["user_id"], date=get_current_date(), content=content)
                session1.add(data_to_add)
                session1.commit()
                data = session1.query(Forum).all()
                user_names = []
                for post in data:
                    name = session1.query(logincred.email).filter(logincred.id==post.user_id).first()[0].split("@")[0]
                    print(name)
                    user_names.append(name)
                return render_template("forum.html", data=data, user_names = user_names,user_id = session["user_id"])
            
        data = session1.query(Forum).all()
        user_names = []
        for post in data:
            name = session1.query(logincred.email).filter(logincred.id==post.user_id).first()[0].split("@")[0]
            print(name)
            user_names.append(name)
        return render_template("forum.html", data=data, user_names=user_names, user_id = session["user_id"])
    else:
        return render_template('404.html')
    




@app.route('/upload', methods= ["GET","POST"])
def s3_upload():
    s3_client = boto3.client('s3', aws_access_key_id='', aws_secret_access_key='')
    if "user_id" in session:
        if request.method=="POST":
            if 'file' in request.files:
                file = request.files['file']
                filename = secure_filename(file.filename)
                if file:
                
                    
                    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[-1]
                    bucket_name = session['username']
                    
                    if not check_s3_bucket_exists(s3_client, bucket_name):
                        create_s3_bucket(s3_client,bucket_name)
                    
                    upload_file_to_s3(s3_client, file, bucket_name, filename)
                    return render_template('upload.html', files=list_s3_files(s3_client, session["username"]))

        return render_template('upload.html', files=list_s3_files(s3_client, session["username"]))
    else:
        return render_template('404.html')


def check_s3_bucket_exists(s3,bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except Exception as e:
        return False

def create_s3_bucket(s3,bucket_name):
    s3.create_bucket(Bucket=bucket_name)

def list_s3_files(s3,bucket_name):
    response = s3.list_objects(Bucket=bucket_name)
    return [obj['Key'] for obj in response.get('Contents', [])]

def upload_file_to_s3(s3,file, bucket_name, filename):
    s3.upload_fileobj(file, bucket_name, filename)



@app.route('/logout', methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for('front_home'))




if __name__=="__main__":
    app.run(debug=True, port=8036, host="0.0.0.0")