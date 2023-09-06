'''
Created on Dec 29, 2022
Course work: Fastapi
@author: Mukesh, Santhosh, Chaaya, Sarumathy

'''



from fastapi import FastAPI, Request, Form ,responses, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
import starlette.status as status
from fastapi.responses import HTMLResponse ,RedirectResponse
from fastapi.templating import Jinja2Templates

from postgresdb import session,logincred,Profiles,Activity,ActivityTracking
from sqlalchemy import and_
import uvicorn
from datetime import date,timedelta,datetime
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
app = FastAPI()





templates = Jinja2Templates(directory="templates")
security = HTTPBearer()

app.mount("/static", StaticFiles(directory="static"), name="static")

JWT_SECRET_KEY = "your-secret-key"  # Change this to your secret key
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 30

class User(BaseModel):
    email: str
    password: str

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
      
# def get_db():
#     session = get_session()
    
#     yield session

     
def get_person(person):
    # d = {"son": 0}
    # prof = session.query(Profiles).all()
    # for pro in prof:
    #     d[(pro.profiles).lower()] = pro.id
    
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

@app.get("/", response_class=HTMLResponse)
async def front_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def home(request: Request):
    profile_list = ["son","mom","dad"]
    return templates.TemplateResponse("login.html", {"request": request,"profile_list": profile_list})

def update_activitytracking():
    # session = get_db()
    activity_table = session.query(Activity).all()
   
    for act in activity_table:
        track = ActivityTracking(date = act.date, activity_id = act.activity_id, status = act.status)
        session.add(track)
        session.commit()
    
        

@app.post("/login",response_class=RedirectResponse, status_code=302)
async def login(request: Request, email: str = Form(...), password: str = Form(...), person: str = Form(...)):

    if (email,) in session.query(logincred.email).all() and password == list(session.query(logincred.password).filter(email == logincred.email))[0][0]:
        id = session.query(logincred.id).filter(email == logincred.email).first()[0]
        # print(id)
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
        token = generate_token(db_user)

        redirect_url = request.url_for('display',**{'id': id})
        response = RedirectResponse(url=redirect_url)
        # response.set_cookie(key="Authorization", value=f"Bearer {token}", httponly=True)
        return response
        # return (redirect_url)
        # prof_list = session.query(Profiles.profiles).all()
        # return templates.TemplateResponse('login.html',context={"request":request ,"login_person" : True, "user_id":id, "profile_list" : prof_list})


@app.post("/loginperson/{id}",response_class=RedirectResponse, status_code=302)
async def login_person(request: Request, id: int, person : str = Form(...)):

    get_person(person.lower())
    redirect_url = request.url_for('display',**{'id': id})
    return (redirect_url)

@app.get("/signup",response_class=HTMLResponse)
async def signup(request:Request):
    return templates.TemplateResponse("signup.html",context={"request":request})

    

@app.post("/signup",response_class=RedirectResponse)
async def addUser(request: Request, email: str = Form(...), password: str = Form(...)):
    user=logincred(email=email,password=password)
    session.add(user)
    session.commit()
    id = session.query(logincred.id).filter(email == logincred.email).first()[0]
    print(id)
    redirect_url = request.url_for('display',**{'id': id})
    return responses.RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)



@app.get("/get/profiles/{id}",response_class=HTMLResponse)
async def display(request: Request, id: int):
    profile_list = session.query(Profiles.profiles).filter(Profiles.user_id == id).all()
    profile_ids = session.query(Profiles.id).filter(Profiles.user_id == id).all()
    l=[]
    for i in range(len(profile_list)):
        l.append((profile_ids[i][0],profile_list[i][0]))
    user_name = session.query(logincred.email).filter(logincred.id==id).first()[0].split("@")[0]
    return templates.TemplateResponse('display.html',context={"request":request , "l":l, "id":id, "user_name": user_name, "person": num_person, "view" : GetKey(num_person).title(), "date":get_current_date()})



@app.post("/add/profiles/{id}",response_class=RedirectResponse)
async def add_profiles(request: Request, id, profile : str = Form(...)):
    print(profile)
    pro=Profiles(user_id=id,profiles=profile)
    session.add(pro)
    session.commit()
    redirect_url = request.url_for('display',**{'id': id})
    return responses.RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)



@app.get("/get/activities/{id}")
async def get_activities(request : Request , id :int):
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
    return templates.TemplateResponse('tasks.html',context={"request":request , "pt":pt,"ct":ct, "id":id, "user_id": user_id, "name":profile_name,"num_person":num_person, "date":date.today(),"view" : GetKey(num_person).title()})    



@app.post("/add/activities/{id}",response_class=RedirectResponse)
async def add_profiles(request: Request, id, task : str = Form(...)):
    task=Activity(profile_id=id,activity=task,date = get_current_date())
    session.add(task)
    session.commit()
    redirect_url = request.url_for('get_activities',**{'id': id})
    return responses.RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)



@app.get("/update/task/{id}",response_class=RedirectResponse)
async def update_status(request : Request , id :int):
    task = session.query(Activity).filter(Activity.activity_id==id).first()
    uid=session.query(Activity.profile_id).filter(Activity.activity_id==id).first()
    task.status = 1
    session.commit()
    redirect_url = request.url_for('get_activities',**{'id': uid[0]})
    return responses.RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)




@app.get("/history/{id}",response_class=HTMLResponse)
async def history(request : Request , id :int):
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
    return templates.TemplateResponse('history.html',context={"request":request ,"status":statuses,"task":task,"profile":profile,"date":get_current_date(), "view" : GetKey(num_person).title(), "act_id":pro_id, "user_id": user_id_g})

@app.get("/yesterday/{id}",response_class=HTMLResponse)
async def yesterday(request : Request , id :int):
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
    
    return templates.TemplateResponse('yesterday.html',context={"request":request ,"status":statuses,"profile":profile, "date": yesterday, "id" : id, "view" : GetKey(num_person).title(), "y_date":yesterday, "user_id": user_id_g})
    
@app.post("/yesterday/{id}",response_class=RedirectResponse)
async def yesterday(request : Request , id :int, now_date : date = Form(...), number : int = Form(...)):
    pro_id = session.query(Activity.profile_id).filter(Activity.activity_id==id).first()[0]
    profile = session.query(Profiles.profiles).filter(Profiles.id==pro_id).first()[0]
    
    task_ids = session.query(Activity.activity_id).filter(Activity.profile_id==id).all()
    task_ids1=[]
    for i in task_ids:
        task_ids1.append(i[0])
    statuses=[]
    if(now_date == (date.today()- timedelta(days = 1)) and number==0):
        redirect_url = request.url_for('get_activities',**{'id': id})
        return responses.RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
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
    if(len(statuses)==0):
        no_tasks = True
    
    return templates.TemplateResponse('yesterday.html',context={"request":request ,"status":statuses,"profile":profile, "id" : id, "y_date":yesterday, "back_exists" : True, "view" : GetKey(num_person).title(), "no_tasks": no_tasks, "pro_id":pro_id, "user_id":user_id_g})

def generate_token(user: logincred) -> str:
    expires_delta = timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": str(user.id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    print(encoded_jwt)
    return encoded_jwt

@app.get("/logout", response_class=RedirectResponse)
async def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    redirect_url = str(request.url_for('login')) + '?error=' + exc.detail.replace(' ', '+')
    return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)

if __name__ == "__main__":
    
    uvicorn.run(
        "main:app",
        host    = "0.0.0.0",
        port    = 8036, 
        reload  = True
    )