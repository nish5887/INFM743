import flask,flask.views
import os,json
import functools
import sqlite3
from contextlib import closing
import pygal



app = flask.Flask(__name__)
# Don't do this!
app.secret_key = "development key"

# configuration
DATABASE = '/Users/nishitarao/Desktop/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# Getting Environment variables
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


#Initialize the DB
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

init_db()

@app.before_request
def before_request():
    flask.g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(flask.g, 'db', None)
    if db is not None:
        db.close()


def login_required(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if 'username' in flask.session:
            return method(*args, **kwargs)
        else:
            flask.flash("A login is required to see the page!")
            return flask.redirect('/index')
    return wrapper


# RETURNS USER DASHBOARD
@app.route('/user_dashboard')
@login_required
def userdashboard():
    return flask.render_template('user_dashboard.html')


#RETURNS CONTENT OF MESSAGES
@app.route('/get_messages')
@login_required
def get_messages():
    username = flask.session['username']
    cur = flask.g.db.execute('select * from requests where receiver_user_id=? and request_status="pending" and event_id=0', [username])
    flask.g.db.commit()
    p_messages = {}
    for row in cur.fetchall():
        p_messages[row[0]] = {}
        p_messages[row[0]]['requester'] = row[2]
        p_messages[row[0]]['sport'] = row[6]
        p_messages[row[0]]['location'] = row[4]
        p_messages[row[0]]['gender'] = row[5]
    cur = flask.g.db.execute('select * from requests where receiver_user_id=? and request_status="pending" and event_id!=0', [username])
    flask.g.db.commit()
    b_messages = {}
    for row in cur.fetchall():
        b_messages[row[0]]={}
        b_messages[row[0]]['requester']=row[2]
        b_messages[row[0]]['sport']=row[6]
        b_messages[row[0]]['location']=row[4]
        b_messages[row[0]]['gender']=row[5]
    cur = flask.g.db.execute('select * from requests where receiver_user_id=? and request_status="accepted"', [username])
    flask.g.db.commit()
    accepted_messages = {}
    for row in cur.fetchall():
        accepted_messages[row[0]]={}
        accepted_messages[row[0]]['requester']=row[2]
        accepted_messages[row[0]]['sport']=row[6]
        accepted_messages[row[0]]['location']=row[4]
        accepted_messages[row[0]]['gender']=row[5]
    cur = flask.g.db.execute('select * from requests where request_status!="cancelled" and requester_user_id=?', [username])
    flask.g.db.commit()
    s_messages = {}
    for row in cur.fetchall():
        s_messages[row[0]] = {}
        s_messages[row[0]]['sent_to'] = row[3]
        s_messages[row[0]]['sport'] = row[6]
        s_messages[row[0]]['location'] = row[4]
        s_messages[row[0]]['gender'] = row[5]
        s_messages[row[0]]['status'] = row[7]
    messages = {}
    messages['p_messages'] = p_messages
    messages['b_messages'] = b_messages
    messages['accepted_messages'] = accepted_messages
    messages['s_messages'] = s_messages
    print messages
    return flask.jsonify(messages)


#HANDLES PRIVATE MESSAGES
@app.route('/handleprivatemessages', methods=['POST'])
@login_required
def handlingprivatemessages():
        print "Taking action on private messages"
        if 'acceptmessage' in flask.request.form:
            message_id = flask.request.form.getlist('message_number')
            print message_id
            for message in message_id:
                print "Setting message to accepted:"+message
                flask.g.db.execute('update requests set request_status="accepted" where request_id=?', [message])
                flask.g.db.commit()
            return flask.redirect('/user_dashboard')
        if 'denymessage' in flask.request.form:
            print "Trying to deny private message"
            message_id = flask.request.form.getlist('message_number')
            for message in message_id:
                print "Setting message to denied:"+message
                flask.g.db.execute('update requests set request_status="denied" where request_id=?', [message])
                flask.g.db.commit()
            return flask.redirect('/user_dashboard')


#HANDLES BROADCASTED MESSAGES
@app.route('/handlebroadcastedmessages', methods=['POST'])
@login_required
def handlingbroadcastedmessages():
        print "Taking action on broadcasted messages"
        if 'acceptmessage' in flask.request.form:
            message_id = flask.request.form.getlist('message_number')
            print message_id
            for message in message_id:
                print "Setting message to accepted:"+message
                flask.g.db.execute('update requests set request_status="accepted" where request_id=?', [message])
                flask.g.db.commit()
            return flask.redirect('/user_dashboard')
        if 'denymessage' in flask.request.form:
            print "Trying to deny broadcasted message"
            message_id = flask.request.form.getlist('message_number')
            for message in message_id:
                print "Setting message to denied:"+message
                flask.g.db.execute('update requests set request_status="denied" where request_id=?', [message])
                flask.g.db.commit()
            return flask.redirect('/user_dashboard')


#HANDLES ACCEPTED MESSAGES
@app.route('/handleacceptedmessages', methods=['POST'])
@login_required
def handlingacceptedmessages():
        print "Taking action on accepted messages"
        if 'denymessage' in flask.request.form:
            print "Trying to deny accepted message"
            message_id = flask.request.form.getlist('message_number')
            for message in message_id:
                print "Setting message to denied:"+message
                flask.g.db.execute('update requests set request_status="denied" where request_id=?', [message])
                flask.g.db.commit()
            return flask.redirect('/user_dashboard')


#HANDLES SENT MESSAGES
@app.route('/handlesentmessages', methods=['POST'])
@login_required
def handlingsentmessages():
        print "Taking action on sent messages"
        if 'cancelmessage' in flask.request.form:
            print "Trying to cancel event"
            message_id = flask.request.form.getlist('message_number')
            for message in message_id:
                print "Setting message to cancelled:"+message
                flask.g.db.execute('update requests set request_status="cancelled" where request_id=?', [message])
                flask.g.db.commit()
            return flask.redirect('/user_dashboard')


# TO LOG OUT
@app.route('/logout',methods=['POST'])
@login_required
def logout():
    print "Logging out"
    if 'logout' in flask.request.form:
        username = flask.session['username']
        flask.session.pop('username', None)
        print "logged out"
        return flask.redirect('/index')

# SIGN IN PAGE
@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def notSignedIn_index():
    print "Entered sign in"
    if flask.request.method == 'POST':
        print "Entered sign in-POST"
        username = flask.request.form['username']
        password = flask.request.form['password']
        cur = flask.g.db.execute('select * from user_details where username=?', [username])
        flask.g.db.commit()
        if not cur.fetchall():
            print "User does not exist"
            flask.flash("User does not exist, please check the user ID")
        print "Going through rows"
        cur = flask.g.db.execute('select * from user_details where username=?', [username])
        flask.g.db.commit()
        for row in cur.fetchall():
            print row
            if row[1] == password:
                print "Password matched"
                flask.session['username'] = username
                print "User in session: " +username
            else:
                print "Incorrect Password"
                flask.flash("Incorrect password")
        return flask.redirect('/user_dashboard')
    if flask.request.method == 'GET':
        print "Entered sign in- GET"
        return flask.render_template('index.html')


#ROUTE TO SIGN UP PAGE
@app.route('/signup')
def signup():
    return flask.render_template('signup.html')


#ROUTE TO MANAGE PROFILE
@app.route('/manageprofile')
@login_required
def managingprofile():
    user = flask.session['username']
    cur = flask.g.db.execute('select * from user_details where username=?', [user])
    flask.g.db.commit()
    for row in cur:
        password = row[1]
        location = row[2]
        gender = row[3]
        football = row[4]
        basketball = row[5]
        tennis = row[6]
        badminton = row[7]
        cricket = row[8]
    return flask.render_template('manage_profile.html',user=user,password=password,location=location,gender=gender,football=football,basketball=basketball,tennis=tennis, badminton=badminton,cricket=cricket)


@app.route('/changeprofile', methods=['POST'])
@login_required
def changingprofile():
    if 'submit' in flask.request.form:
        print "Trying to change form"
        username = flask.request.form['username']
        password = flask.request.form['password']
        gender = flask.request.form['gender']
        sports = flask.request.form.getlist('sport')
        location = flask.request.form['location']
        flask.g.db.execute('update user_details set password="'+password+'" ,location="'+location+'" ,gender="'+gender+'" where username=?',[username])
        flask.g.db.commit()
        for sport in sports:
            flask.g.db.execute('update user_details set ' + sport + '="true" where username=?', [username])
            flask.g.db.commit()
        flask.session['username'] = username
        print "Updated database for "+username
    if 'cancel' in flask.request.form:
        print "Canceling the change"
    return flask.redirect('/user_dashboard')


#SIGNING UP PAGE
@app.route('/signingup', methods=['POST'])
def signingup():
    if 'submit' in flask.request.form:
        print "Trying to submit form"
        username = flask.request.form['username']
        password = flask.request.form['password']
        gender = flask.request.form['gender']
        sports = flask.request.form.getlist('sport')
        location = flask.request.form['location']
        flask.g.db.execute('insert into user_details (username,password,location,gender) '
                       'values (?,?,?,?)', [username,password,location,gender])
        flask.g.db.commit()
        for sport in sports:
            flask.g.db.execute('update user_details set ' + sport + '="true" where username=?', [username])
            flask.g.db.commit()
        flask.session['username'] = username
        print "Updated database for "+username
    if 'cancel' in flask.request.form:
        print "Canceling the submission"
        return flask.redirect('/index')
    return flask.redirect('/user_dashboard')


#ROUTES TO SEARCH PAGE
@app.route('/searching')
@login_required
def searching():
    user = flask.session['username']
    return flask.render_template('search.html', username=user)


#WHEN SEARCH IS PRESSED
@app.route('/search')
@login_required
def Search():
    sport = flask.request.args.get('sport')
    gender = flask.request.args.get('gender')
    location = flask.request.args.get('location')
    print sport,gender,location
    print "Searching"
    construct_query="select * from user_details where location=\'"+location+"\' and "+sport+"='true'"
    if gender == "male" or gender == "female":
        construct_query=construct_query+" and gender=\'"+gender+"\'"
    cur = flask.g.db.execute(construct_query)
    flask.g.db.commit()
    player_dict={}
    for row in cur:
        player_dict[row[0]]={}
        player_dict[row[0]]['gender']=row[3]
        player_dict[row[0]]['location']=row[2]
    return json.dumps({"answer": player_dict})


#WHEN BROADCAST IS PRESSED
@app.route('/broadcast')
@login_required
def Broadcast():
    cur = flask.g.db.execute('select event_id from requests')
    flask.g.db.commit()
    for row in cur.fetchall():
        print row
    sport = flask.request.args.get('sport')
    gender = flask.request.args.get('gender')
    location = flask.request.args.get('location')
    event_id = flask.request.args.get('event_id')
    print sport,gender,location
    print "Broadcasting"
    user = flask.session['username']
    cur = flask.g.db.execute('select * from user_details where username !=?', [user])
    flask.g.db.commit()
    for row in cur.fetchall():
        flask.g.db.execute('insert into requests (event_id,requester_user_id,receiver_user_id,location,gender,sport,request_status) values (?,?,?,?,?,?,?)',[event_id,user,row[0],location,gender,sport,"pending"])
        flask.g.db.commit()
    return json.dumps({"answer": "Message broadcasted"})


#SENDING MESSAGES TO SELECTED USERS
@app.route('/sendmessagetoselectedusers', methods=['POST'])
@login_required
def sendmessagetoselectedusers():
    print "Reached send message"
    if 'sendmessage' in flask.request.form:
        print "Trying to send message"
        sender=flask.session['username']
        receiver = flask.request.form.getlist('user')
        sport = flask.request.form['sport_for_invite']
        location = flask.request.form['location_for_invite']
        for person in receiver:
            print "Sending message to "+person
            flask.g.db.execute('insert into requests (event_id,requester_user_id,receiver_user_id,location,sport,request_status) values (?,?,?,?,?,?)',[0,sender,person,location,sport,"pending"])
            flask.g.db.commit()
        return flask.redirect('/user_dashboard')
    if 'cancelmessage' in flask.request.form:
        return flask.redirect('/user_dashboard')


#WHEN ANALYTICS IS PRESSED
@app.route('/graph')
@login_required
def Graph():
    fav_sport =[]
    football_query = flask.g.db.execute('select count(*) from user_details where football ="true"')
    flask.g.db.commit()
    for row in football_query:
        football = row[0]
    fav_sport.append(football)
    basketball_query = flask.g.db.execute('select count(*) from user_details where basketball ="true"')
    flask.g.db.commit()
    for row in basketball_query:
        basketball = row[0]
    fav_sport.append(basketball)
    tennis_query = flask.g.db.execute('select count(*) from user_details where tennis ="true"')
    flask.g.db.commit()
    for row in tennis_query:
        tennis = row[0]
    fav_sport.append(tennis)
    badminton_query = flask.g.db.execute('select count(*) from user_details where badminton ="true"')
    flask.g.db.commit()
    for row in badminton_query:
        badminton = row[0]
    fav_sport.append(badminton)
    cricket_query = flask.g.db.execute('select count(*) from user_details where cricket ="true"')
    flask.g.db.commit()
    for row in cricket_query:
        cricket = row[0]
    fav_sport.append(cricket)
    bar_chart = pygal.Bar()
    bar_chart.x_labels=['Football','Basketball','Tennis','Badminton','Cricket']# Then create a bar graph object
    bar_chart.add('Popular sports', fav_sport)  # Add some values
    bar_chart.render_to_file('static/img/fav_sport.svg')
    return flask.render_template('graph.html')


app.debug = True
app.run()