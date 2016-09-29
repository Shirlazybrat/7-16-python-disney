from flask import Flask, render_template, request, redirect, session #include flask class, render and request module
from flaskext.mysql import MySQL

app = Flask('sqlConn')
#create an instance of the mysql class
mysql = MySQL()
#add to the app (Flack object) som config data for our connection
app.config['MYSQL_DATABASE_USER'] = 'x' #username is x
app.config['MYSQL_DATABASE_PASSWORD'] = 'x' # password is x
app.config['MYSQL_DATABASE_DB'] = 'disney'
#where the mysql database is located
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
#use the mysql method, init_app, and pass it the flask object
mysql.init_app(app)

#Make one connection and use it over, and over, and over...
conn = mysql.connect()
# set up a cursor object whihc is what the sql object uses to connect and run queries
cursor = conn.cursor()

app.secret_key = "navlksnlakjwa8924hr8qoarhfvpui34"


@app.route("/")
def index():
	# set upa cursor object which is what sequel 
	cursor = mysql.connect().cursor()
	# execute cursor
	cursor.execute("SELECT * FROM page_content WHERE page = 'home' AND status = 1")
	header_text = cursor.fetchall()

	# Write a query that will pull the three main fields for all rows that have page as home, and left_block as location. Alsp, make sure they are publisehd (status = 1)
	left_block_query = "SELECT header_text,content,image_link, id FROM page_content WHERE page = 'home' AND location = 'left_block' AND status = 1 ORDER BY priority asc"
	# Run the query
	cursor.execute(left_block_query)
	# Turn the query into something Python can use via fetchall
	data = cursor.fetchall()
	# print header_text
	return render_template('index.html',
		header = header_text,
		left_data = data
	)



@app.route('/admin')
def admin():
	# return render_template('admin.html')
	if request.args.get('message'):
		return render_template('admin.html',
			message = "Login Failed"
			#add an if statement for message based on user action
		)
	else:
		return render_template('admin.html')

@app.route('/logout')
def logout():
	#nuke the session vars. This will end the session which is what we use to let the user in
	session.clear()
	return redirect('/admin?message=LoggedOut')



# make a new route
@app.route('/admin_submit', methods=['GET', 'POST']) #add method POST so from can get here
# define the method for the new route admin_submit
def admin_submit():
	print request
	# get the variable message out of the query string
	if request.form['username'] == 'admin' and request.form['password'] == 'admin': #if it exists, return template with the var
		#you may proceed, but b4 you do, you get aticket
		session['username'] = request.form['username']
		return redirect('/admin_portal')
	else: #else, failed
		return redirect('/admin?message=login_failed')
	#return request.form['username'] + '----- ' + request.form['password'] 

@app.route('/admin_portal')
def admin_portal():
	#session:variable username exists, proceed
	#make sure to check to see if it's in the dictionary rather than just "if"
	if 'username' in session:
		# return render_template('admin_portal.html')
		home_page_query = "SELECT header_text, content, image_link, location, id FROM page_content WHERE page = 'home' AND status = 1"
		cursor.execute(home_page_query)
		data = cursor.fetchall()
		return render_template('admin_portal.html',
			home_page_content = data
			)
	#you have no ticket, BYE
	else:
		return redirect('/admin?message=YouMustLogIn')


@app.route('/admin_update',methods=['POST'])
def admin_update():
	#First, do you belong here?
	if 'username' in session:
		#ok, youre logged in, I will insert your stuff
		body = request.form['body_text']
		header = request.form['header']
		image = request.files['image']
		image.save('static/images/'+ image.filename)
		image_path = image.filename
 		# execute our query
		query = "INSERT INTO page_content VALUES (DEFAULT, 'home', '"+body+"', 1,1,'left_block', NULL, '"+header+"', '"+image_path+"')"
		# print query
		cursor.execute(query)
		conn.commit()
		return redirect('/admin_portal?success=Added')

	#you have no ticket, BYE
	else:
		return redirect('/admin?message=YouMustLogin')


@app.route('/edit/<id>', methods=['GET','POST'])
def edit(id):
	if request.method == 'GET':
		#write a query for the row with the matching id
		query = "SELECT header_text, content, image_link, id, status, priority FROM page_content WHERE id = %s" % id
		print query
		cursor.execute(query)
		data = cursor.fetchone()
		return render_template('/edit.html',
			data = data
		)
	else:
		#do the post stuff
		request.method == 'POST'
		content = request.form['body_text']
		header = request.form['header']
		image = request.form['image']
		status = request.form['status']
		priority = request.form['priority']
 		# execute our query
		query = "UPDATE page_content SET content = %s, image_link = %s, header_text = %s, status = %s, priority = %s WHERE id = %s" 
		# print query
		cursor.execute(query,(content, image, header, status, priority, id))
		conn.commit()
		return redirect('/admin_portal?success=ContentUpdated')

@app.route('/delete/<id>')
def delete(id):
	#nuke the session vars. This will end the session which is what we use to let the user in
	query = "DELETE FROM page_content WHERE id = %s"
	cursor.execute(query, id)
	conn.commit()
	return redirect('/admin_portal?message=ItemDeleted')


@app.route('/link_page/<path:id>')
def link_page(id):
	query = "SELECT header_text, content, image_page, id, status, priority FROM page_content WHERE id = %s" % id
	print query
	cursor.execute(query)
	data = cursor.fetchone()
	return render_template('link_page.html',
		data = data
	)

if __name__== "__main__":
	app.run(debug = True)