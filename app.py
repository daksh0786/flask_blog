from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from werkzeug.utils import secure_filename
import json
import os
from datetime import datetime
import math


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER']=params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)


class Contacts(db.Model):
    SNo = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    email = db.Column(db.String(20), nullable=False)


class Posts(db.Model):
    SNo = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    # img_file = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts=Posts.query.filter_by().all()
    #for greatest integer og length
    last=math.floor(len(posts)/int(params['no_of_posts'])) 
    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    # paginatiomn logic
    #first
    page=int(page)
    posts=posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if(page==1):
        
        prev= "#"
        if(last==1):
            next= "/#"
        
        next="/?page="+ str(page+1)
    #last 
    elif(page==last):
    
        prev="/?page="+ str(page-1)
        next= "/#"
    #middle
    else:
        prev="/?page="+ str(page-1)
        next="/?page="+ str(page+1)
        
    
     
    
    
    posts=Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html', params=params,posts=posts,next=next,prev=prev)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)

@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/dashboard")


@app.route("/delete/<string:SNo>")
def delete(SNo):
    if('user' in session and session['user']==params['admin-username']):
        post=Posts.query.filter_by(SNo=SNo).first()
        db.session.delete(post)
        db.session.commit()
    return render_template('dashboard.html',params=params)

@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    
    if('user' in session and session['user']==params['admin-username']):
        
        posts=Posts.query.all()
        return render_template('dashboard.html',params=params,posts=posts)
    
    
    if(request.method=="POST"):
        username=request.form.get('username')
        password=request.form.get('password')
        
        if(username==params['admin-username'] and password==params['admin-password']):
            #get the session variables
            session['user']=username
            posts=Posts.query.all()
            return render_template('dashboard.html',params=params,posts=posts)
            
    return render_template('login.html', params=params)
        
    
@app.route("/edit/<string:SNo>", methods=['GET','POST'])
def Edit(SNo):
    if('user' in session and session['user']==params['admin-username']):
        
        if(request.method=='POST'):
           box_title=request.form.get('title')
           box_slug= request.form.get('slug')
           
           box_content=request.form.get('content')
            
           if(SNo=='0'):
               post=Posts(title=box_title,slug=box_slug,content=box_content,date= datetime.now())
               db.session.add(post)
               db.session.commit()
           else:
               post=Posts.query.filter_by(SNo=SNo).first()
               post.title= box_title
               post.slug=box_slug
               post.content=box_content
               post.date=datetime.now()
               db.session.commit()
               return redirect('/edit/'+SNo)
        post=Posts.query.filter_by(SNo=SNo).first()
        return render_template('edit.html',params=params,post=post)

@app.route("/uploader", methods = ["GET", "POST"])
def uploader():
    if('user' in session and session['user']==params['admin-username']):  
        if(request.method=='POST'):
            f=request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "uploaded successfully"
        

@app.route("/contact", methods = ["GET", "POST"])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('Phone')
        message = request.form.get('msg')
        entry = Contacts(name=name, phone_num = phone, msg = message, date= datetime.now(),email = email )
        db.session.add(entry)
        db.session.commit()
        # mail.send_message('New message from ' + name,
        #                   sender=email,
        #                   recipients = [params['gmail-user']],
        #                   body = message + "\n" + phone
        #                   )
    return render_template('contact.html', params=params)

# @app.route("/older_post",methods=['GET'])
# def OlderPost():
    
    


app.run(debug=True)

