from flask import Flask, render_template, request, redirect, session, flash
import re
import md5 
password = 'password'
from mysqlconnection import MySQLConnector
app = Flask(__name__)
app.secret_key = "ThisIsSecret!"
mysql = MySQLConnector(app,'reddit')

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html') 

# after click LOG IN 
@app.route('/login', methods=['post'])
def longinprocess():
	email = request.form['email']
	password = md5.new(request.form['password']).hexdigest()
	user_query = "SELECT * FROM users where users.email = :email"
	query_data = { 'email': email}
	user = mysql.query_db(user_query, query_data)
	print user
	EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
	# invalid email
	if len(request.form['email'])<1:
		flash("Valid Email format!")
		return redirect('/')
	# email doesn't exists
	elif len(request.form['password']) <1:
		flash("no password")
		return redirect('/')
	# invalid user
	elif  not user:
		flash("Wrong email")
		return redirect('/')
	# invalid password
	elif user[0]['password'] != password:
		flash("Wrong password")
		return redirect('/')
	# correct info
	else:
		session['id'] = user[0]['id']
		session['loggedName'] = user[0]['first_name']
		return redirect ('/mainpage')


# after click REGISTER 
@app.route('/register', methods=['POST'])
def takeResults():
	fname = request.form['first_name']
	lname = request.form['last_name']
	email = request.form['email']
	password = request.form['password']
	confirmpw = request.form['confirm']
	regex = re.compile(r'^[^\W_]+(-[^\W_]+)?$', re.U)
	EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
	# invalid first name
	if len(fname)<2 or fname.isalpha() == False:
		flash("First name has to have at least two alphabetic characters ")
		return redirect('/')
	# invalid last name
	elif len(lname)<2 or not regex.match(lname):
		flash("Last name has to have at least two alphabetic characters ")
		return redirect('/')
	# invail email
	elif len(request.form['email']) < 1 or not EMAIL_REGEX.match(request.form['email']):
		flash("Inalid Email format!")
		return redirect('/')
	# invalid password
	elif len(password) <1:
		flash("blank")
	elif password != confirmpw:
            flash("Passwords are not matching!")
            return redirect('/')
	# correct info 
	else:
            flash("Time to log in :)")
            password = md5.new(request.form['password']).hexdigest()
            # we want to insert into our query.
            query = "INSERT INTO users (first_name, last_name, email, password) VALUES (:first_name, :last_name, :email, :password)"
            # We'll then create a dictionary of data from the POST data received.
            data = {
                    'first_name': request.form['first_name'],
                    'last_name': request.form['last_name'],
                    'email': request.form['email'],
                    'password': password,
                }
            # Run query, with dictionary values injected into the query.
            mysql.query_db(query, data)
            return redirect('/')

# test
@app.route('/register', methods=['POST'])
def test():
	from jinja2 import Environment, FileSystemLoader
	env = Environment(loader=FileSystemLoader('templates'))
	template = env.get_template('test.html')
	output_from_parsed_template = template.render(foo='Hello World!')
	print output_from_parsed_template

# mainpage
@app.route('/mainpage')
def mainpage():
	# if 'id' in session:
	# 	message_query = "SELECT messages.id, messages.user_id, CONCAT(users.first_name, ' ', users.last_name) AS name,  DATE_FORMAT(messages.created_at, '%M %D %Y') AS date, messages.message FROM messages JOIN users ON users.id = messages.user_id"
	# 	# SELECT * FROM messages JOIN users ON users.id = messages.user_id LEFT JOIN messages ON comments.message_id = message.id"
	# 	message = mysql.query_db(message_query) 

	# 	comment_query = "SELECT * FROM comments LEFT JOIN messages ON messages.id = comments.message_id JOIN users ON users.id = messages.user_id"
	# 	comment = mysql.query_db(comment_query)
	# 	return render_template("mainpage.html", all_message=message, all_comment=comment) #all means whole table with messages = table
	# else:
	# 	return redirect('/')
    return render_template("mainpage.html")

# after click POST MESSAGE
# @app.route('/messages', methods=['post'])
# def messageprocess():
#     # created_at = request.form['message'].DateTimeField(auto_now_add=True)
#     userid = session['id'] 
#     query = "INSERT INTO messages (message, user_id, updated_at, created_at) VALUES (:message, :userid, NOW(),NOW())"
#     data={
#         'userid': userid,
#         'message': request.form['message'],
#     }
#     mysql.query_db(query, data)
#     return redirect('/xxxxxxx')



# after click POST COMMENT
# @app.route('/comment', methods=['post'])
# def commentprocess():
# 	userid = session['id'] 
# 	query = "INSERT INTO comments (comment, created_at, updated_at, user_id, message_id) VALUES (:comment, NOW(),NOW(),:userid, :message_id)"
#     # ths is going to db when I create the comment
# 	data={
#         'userid': userid,
#         'message_id': request.form['hiddenmessageid'],
# 		'comment': request.form['comment'],
#     }
# 	mysql.query_db(query, data)
# 	return redirect('/xxxxx')

# delete message
# @app.route('/delete', methods=['post'])
# def deletemessage():
# 	print"delete"
# 	userid = session['id'] 
# 	query = "DELETE FROM messages WHERE messages.id = :message_id"
# 	# ths is happening to db when I delete the message
# 	print "message number: ",request.form['hiddenmessageidDEL']
# 	data={
# 		'userid': userid,
# 		'message_id': request.form['hiddenmessageidDEL'],
# 	}
# 	mysql.query_db(query, data)
# 	return redirect('/xxxxxxx')

# add subreddit
@app.route('/add', methods=['POST'])
def addsubreddit():
    return render_template("addsubreddit.html")

# my page
@app.route('/mypage', methods=['POST'])
def mypage():
    return render_template("mypage.html")




#add subreddit
@app.route('/addedsub', methods=['GET', 'POST'])
def addedSubreddit():
	userid = session['id']
	url = request.form['url']
	title = request.form['title']
	subreddit = request.form['subreddit']
	comment = request.form['comment'] 
	image = request.form['image']
	#add subreddit to db
	query = "INSERT INTO subreddits (url, created_at, updated_at, title, subreddit, comment, image) VALUES (:url, NOW(), NOW(), :title, :subreddit, :comment, :image)"
	data={
		'userid': userid,
		'url' : url,
		'title': title,
        'subreddit': request.form['subreddit'],
        'comment': request.form['comment'],
		'image': request.form['image']
    }
	mysql.query_db(query, data)
    # display in terminal
	print title, url, image, subreddit, comment
	return render_template("addedsub.html", title=title, url=url, image=image, subreddit=subreddit, comment=comment)










#log off
@app.route('/logof', methods=['GET'])
def logoff():
	return render_template('index.html') 	

app.run(debug=True)