from flask import Flask, flash, render_template, request, redirect, url_for
from sqlalchemy.orm import Session
from datetime import date,timedelta,datetime
from sqlalchemy import and_
from postgresdb import session,logincred,Profiles,Activity,ActivityTracking


app = Flask(__name__)

app.config['SECRET_KEY'] = "sarumathy-secret-key-my-project-123q43423qwe3"


user_id = 0

def get_current_date():
    return date.today()

num_person = 5
user_id_g = 1
d = { "son" :0, "mom" : 1, "dad" :2}

def set_user_id(id):
    global user_id_g
    user_id_g = id
    return user_id_g

def GetKey(val):
    for key, value in d.items():
        if val == value:
           return key
    return "son"


def get_person(person):

    print(d)
    if(person=="son"):
        print("son")
        global num_person
        num_person = d["son"]
    elif(person=="mom" ):
        num_person = d["mom"]
    elif(person=="dad"):
        num_person = d["dad"]
    return num_person



@app.route('/', methods = ["GET"])
def front_home():
    return render_template('home.html')




def update_activitytracking():
    activity_table = session.query(Activity).all()
   
    for act in activity_table:
        track = ActivityTracking(date = act.date, activity_id = act.activity_id, status = act.status)
        session.add(track)
        session.commit()


@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form.get("email")
        password = request.form.get("password")
        person = request.form.get("person")
        print(email, password, person)

        if (email,) in session.query(logincred.email).all() and password == list(session.query(logincred.password).filter(email == logincred.email))[0][0]:
            id = session.query(logincred.id).filter(email == logincred.email).first()[0]
            print(id)
            db_user = session.query(logincred).filter(email == logincred.email).first()
            now_date = date.today()
            #now_date="2023-01-20"
            try:
                prev_date = session.query(Activity.date).first()[0]
            except:
                prev_date = 0
            if(str(now_date)!= str(prev_date)):
                update_activitytracking()
                uid=session.query(Activity).all()
                for act in uid:
                    act.status = 0
                    act.date = now_date
                    session.commit()
                # print(uid)
            set_user_id(id)
            print("userid----->",id,user_id_g)
            get_person(person.lower())

            return redirect(url_for('display', id=id))
        else:
            flash("Sign in")

    profile_list = ["son","mom","dad"]
    return render_template("login.html", profile_list=profile_list)

@app.route("/loginperson/<int:id>", methods = ["GET","POST"])
def login_person(id):
    if request.method=="POST":
        person = request.form.get("person")
        get_person(person.lower())
        return redirect(url_for('display', id=id))



@app.route("/signup", methods = ["GET","POST"])
def addUser():
    if request.method=="POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user=logincred(email=email,password=password)
        session.add(user)
        session.commit()
        id = session.query(logincred.id).filter(email == logincred.email).first()[0]
        print(id)
        return redirect(url_for('display', id=id))
    return render_template("signup.html")


@app.route("/get/profiles/<int:id>",methods=["GET"])
def display(id):
    profile_list = session.query(Profiles.profiles).filter(Profiles.user_id == id).all()
    profile_ids = session.query(Profiles.id).filter(Profiles.user_id == id).all()
    l=[]
    for i in range(len(profile_list)):
        l.append((profile_ids[i][0],profile_list[i][0]))
    user_name = session.query(logincred.email).filter(logincred.id==id).first()[0].split("@")[0]
    return render_template('display.html',l=l, id=id, user_name= user_name, person= num_person, view= GetKey(num_person).title(), date=get_current_date())



@app.route("/add/profiles/<int:id>",methods=["GET","POST"])
def add_profiles(id):
    if request.method=="POST":
        profile = request.form.get("profile")
        print(profile)
        pro=Profiles(user_id=id,profiles=profile)
        session.add(pro)
        session.commit()
        return redirect(url_for('display', id=id))

@app.route("/get/activities/<int:id>", methods = ["GET", "POST"])
def get_activities(id):
    tasks = session.query(Activity.activity).filter(and_ (Activity.profile_id == id , Activity.status==0)).all()
    ids = session.query(Activity.activity_id).filter(and_(Activity.profile_id == id , Activity.status==0)).all()
    pt=[]
    for i in range(len(tasks)):
        pt.append((ids[i][0],tasks[i][0]))
    print(pt)

    ct=[]
    c_tasks=session.query(Activity.activity).filter(and_ (Activity.profile_id == id , Activity.status==1)).all()
    c_ids = session.query(Activity.activity_id).filter(and_(Activity.profile_id == id , Activity.status==1)).all()
    for i in range(len(c_tasks)):
        ct.append((c_ids[i][0],c_tasks[i][0]))
    print(ct)
    profile_name =  session.query(Profiles.profiles).filter(Profiles.id == id).first()[0]
    user_id = session.query(Profiles.user_id).filter(Profiles.id == id).first()[0]
    return render_template('tasks.html', pt = pt,ct=ct, id =id, user_id =  user_id,  name = profile_name, num_person = num_person,  date = date.today(), view = GetKey(num_person).title())    



@app.route("/add/activities/<int:id>", methods = ["POST"])
def add_activities(id):
    if request.method == "POST":

        task = request.form.get("task")
        task=Activity(profile_id=id,activity=task,date = get_current_date())
        session.add(task)
        session.commit()
        return redirect(url_for('get_activities', id=id))



@app.route("/update/task/<int:id>", methods = ["GET"])
def update_status(id):
    task = session.query(Activity).filter(Activity.activity_id==id).first()
    uid=session.query(Activity.profile_id).filter(Activity.activity_id==id).first()
    task.status = 1
    session.commit()
    return redirect(url_for('get_activities', id=uid[0]))



@app.route("/history/<int:id>", methods = ["GET"])
def history(id):
    statuses=[]
    date = session.query(ActivityTracking.date).filter(ActivityTracking.activity_id==id).all()
    status = session.query(ActivityTracking.status).filter(ActivityTracking.activity_id==id).all()
    task = session.query(Activity.activity).filter(Activity.activity_id==id).first()[0]

    pro_id = session.query(Activity.profile_id).filter(Activity.activity_id==id).first()[0]
    profile = session.query(Profiles.profiles).filter(Profiles.id==pro_id).first()[0]

    d={0:"incomplete",1:"completed"}

    for i in range(len(date)):

        statuses.append((str(date[i][0]),d[status[i][0]]))
    user_id = session.query()
    return render_template('history.html',status=statuses,task=task,profile=profile,date=get_current_date(), view=  GetKey(num_person).title(), act_id=pro_id, user_id= user_id_g)




@app.route("/yesterday/<int:id>", methods = ["GET","POST"])
def yesterday(id):
    if request.method=="POST":
        yesterday_not_found = False
        date_format = "%Y-%m-%d"
        try:
            now_date = datetime.strptime(request.form.get("now_date"),date_format)  #convert to date
        except:
            yesterday_not_found = True
            #return render_template('yesterday.html', status = statuses, profile = profile, id =  id, y_date = yesterday, back_exists =  True, view  =  GetKey(num_person).title(), no_tasks =  no_tasks, pro_id = pro_id, user_id = user_id_g)

            now_date = ''
        number = request.form.get("number")
        pro_id = session.query(Activity.profile_id).filter(Activity.activity_id==id).first()[0]
        profile = session.query(Profiles.profiles).filter(Profiles.id==pro_id).first()[0]
        
        task_ids = session.query(Activity.activity_id).filter(Activity.profile_id==id).all()
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
                s = session.query(ActivityTracking.status).filter(and_ ((ActivityTracking.date) == (yesterday) , ActivityTracking.activity_id==i)).first()[0]
                t= session.query(Activity.activity).filter(Activity.activity_id==i).first()[0]
                statuses.append((t,str(yesterday),d[s]))
                print(statuses[-1])

        except:
            pass

        no_tasks = False
        if(len(statuses)==0 or now_date==''):
            no_tasks = True
        
        return render_template('yesterday.html', status = statuses, profile = profile, id =  id, y_date = yesterday, back_exists =  True, view  =  GetKey(num_person).title(), no_tasks =  no_tasks, pro_id = pro_id, user_id = user_id_g, yesterday_not_found=True)
    task_ids = session.query(Activity.activity_id).filter(Activity.profile_id==id).all()
    task_ids1=[]
    for i in task_ids:
        task_ids1.append(i[0])
    statuses=[]
    d={0:"incomplete",1:"completed"}
    today = get_current_date()
    yesterday = today - timedelta(days = 1)
    #yesterday = "2023-01-19"
    for i in task_ids1:
        s = session.query(ActivityTracking.status).filter(and_ ((ActivityTracking.date) == (yesterday) , ActivityTracking.activity_id==i)).first()[0]
        t= session.query(Activity.activity).filter(Activity.activity_id==i).first()[0]
        statuses.append((t,str(yesterday),d[s]))
        print(statuses[-1])
    pro_id = session.query(Activity.profile_id).filter(Activity.activity_id==id).first()[0]
    profile = session.query(Profiles.profiles).filter(Profiles.id==pro_id).first()[0]
    
    return render_template('yesterday.html',status=statuses,profile=profile, date= yesterday, id =  id, view= GetKey(num_person).title(), y_date = yesterday, user_id = user_id_g)




if __name__=="__main__":
    app.run(debug=True, port=8036)