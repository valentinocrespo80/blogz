from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Brockman80!@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "1815augusta"

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id= db.Column(db.Integer, db.ForeignKey('user.id'))
    

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner 
        

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")




@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]   
        user= User.query.filter_by(username=username).first()
        if user and user.password == password:
            #remember the user has logged in    
            session['username'] = username
            return redirect("/newpost")
        else:
            flash('User password incorrect, or user does not exist','error')
           
    return render_template("login.html")
            

@app.route("/signup", methods=["POST", "GET"])
def signup():

    
    if request.method == "POST":
        username= request.form['username']
        password= request.form['password']
        verify= request.form['verify']
        #Validate the user's data
 
        existing_user= User.query.filter_by(username=username).first()

        user_error = ""
        password_error = ""
        verify_error = ""

        if existing_user and username:
            flash("username already exists")
            username =''

       
        if ' ' in username:
            flash("That's not a valid username") 
            user_error = True
            user_name = ''
        else:
            if len(username) < 3 or len(username) > 20:
                flash("That's not a valid username") 
                user_error = True
                user_name = ''


        if ' ' in password:
            flash("That's not a valid password") 
            password_error = True
            password = ''
        else:
            if len(password) < 3 or len(password) > 20:
                flash("That's not a valid password") 
                password_error = True
                password = ''

        #if not verify:
            #flash("Passwords don't match") 
            #verify = ''

        if not password == verify:
            flash("Passwords don't match") 
            verify_error = True
            password = ''
            verify = ''
  
        else:
            if not existing_user and not user_error and not password_error and not verify_error:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                #remember the User
                session['username'] = username
                return redirect("/newpost")    
            
               
    return render_template("signup.html")

    

@app.route("/logout")
def logout():
    del session['username']
    return redirect ("/blog")


@app.route("/newpost", methods=["POST", "GET"])
def newpost():

    
    blog_title_error= ""
    blog_body_error= ""
    newpost_error = ""
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == "POST":
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        if not blog_title:
             blog_title_error = ("Please enter a title entry")
             newpost_error = True
            

        if not blog_body:
            blog_body_error = ("Please enter a blog entry")
            newpost_error = True

        if newpost_error:
            return render_template("newpost.html",blog_title_error=blog_title_error,blog_body_error=blog_body_error)

        
        if not blog_title_error and not blog_body_error:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            # get the blog id
            the_blog = new_blog.id
            return redirect ("/blog?id=" + str(the_blog))         
   
    return render_template("newpost.html")

    
    
         

@app.route("/blog", methods=["GET"])
def blog():
    
    
    user_id = request.args.get("user")
    blog_id = request.args.get("id")
   
    if blog_id:
        blog=Blog.query.get(blog_id)
        return render_template("single-blog.html", blog=blog, title="Build A Blog")      
    elif user_id:
        blogz=Blog.query.filter_by(owner_id=user_id).all()
        return render_template("singleUser.html", blogs=blogz, title="Something")
    else:
        #display all blogs
        blogs=Blog.query.all()
        return render_template("blog.html", title="Build A Blog", blogs=blogs, User=User)
        
# get the blog by the id that you have
        #query result

@app.route("/", methods=["POST", "GET"])
def index():

    blog_id = request.args.get("id")
    
    if blog_id==None:
        user_name = User.query.all()
        return render_template("index.html", title="Blog Users!", user_name=user_name)
    else:
        blog = Blog.query.get(blog_id)
        #user = User.query.get(blog.owner_id)
        return render_template("single-blog.html", blog=blog, title="Build A Blog")
    
    #if request.method == "POST":
        #blog_title = request.form['blog_title']
        #blog_body = request.form['blog_body']
        #new_blog = Blog(blog_title, blog_body)
        #db.session.add(new_blog)
        #db.session.commit()

    #blogs = Blog.query.all()

    #return render_template('add_blog.html', title="Add a Blog Entry", blogs=blogs)

if __name__ == '__main__':
    app.run()

