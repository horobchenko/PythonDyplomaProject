import openai
from flask_login import login_required
from sqlalchemy.sql.functions import current_user, func
from flask import render_template, request, Blueprint, session, flash, redirect, url_for, jsonify
from flask_admin.form import rules
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, Admin
from flask_mail import Message
import os
from flask_app.bat_analizer.models import *
from flask_app.battery_app import *
from sqlalchemy import insert

#blueprints registration
user = Blueprint('user', __name__)
articles = Blueprint('articles', __name__)


@app.route('/')
def index():
    return "Hello"

@app.route('/home')
def home():
    if request.headers.get("X-Requested-With") =="XMLHttpRequest":
        articles = Article.query.all()
        return jsonify({
            'count': len(articles)
        })
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
   if session.get('username'):
      flash('Your are already logged in.', 'info')
      return redirect(url_for('user.home'))
   form = RegistrationForm()
   if form.validate_on_submit():
      username = request.form.get('username')
      password = request.form.get('password')
      serial_number = request.form.get('serial_number')
      existing_username = User.query.filter(User.username.like('%' + username + '%')).first()
      if existing_username:
          flash('This username has been already taken. Tryanotherone.','warning')
          return render_template('register.html', form=form)
      user = User(username, password)
      db.session.add(user)
      db.session.flush()
      battery = Battery(serial_number = serial_number, user_id = user.id)
      db.session.add(battery)
      db.session.flush()
      if serial_number.startswith('a'):
          battery.parameters = Parameters(0, 30, 'a')
      elif serial_number.startswith('b'):
           battery.parameters = Parameters(0, 20, 'b')
      else:
           battery.parameters = Parameters(0, 50, 'c')
      mqtt.subscribe(f'{mqtt.username}/groups/{serial_number}', qos=0)
      log_reg_model.train(battery.parameters.bat_type)
      db.session.commit()
      message = Message(f"New user {user.username} is registrated",recipients=['gorobchenkotatyana16@gmail.com'])
      mail.send(message)
      flash('You are now registered. Please login.','success')
      return redirect(url_for('user_blueprint.login'))
      if form.errors:
          flash(form.errors, 'danger')
   return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
 form = LoginForm()
 if form.validate_on_submit():
     username = request.form.get('username')
     password = request.form.get('password')
     existing_user = User.query.filter_by(username=username).first()
     if not (existing_user and existing_user.check_password(password)):
      flash('Invalid username or password. Please try again.',
            'danger')
     db.session['username'] = username
     flash('You have successfully logged in.', 'success')
     return redirect(url_for('user.user_page'))
     if form.errors:
       flash(form.errors, 'danger')
     return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
 if 'username' in session:
     session.pop('username')
     flash('You have successfully logged out.', 'success')
     return redirect(url_for('app.home'))

@app.route('/user_page/<id>')
@login_required
def user_page(id):
    stmt = db.select(Battery.stop_cycle).where(Battery.user_id==id)
    result = db.execute(stmt)
    text = ''
    if result:
       messege = "Your battery must be changed"
       #img = "Battery_NO_OK"
    else:
        result = log_reg_model.predict(id)
        if result:
            messege = "Your battery must be changed"
            #img = "Battery_NO_OK"
            mqtt.unsubscribe()
        else:
            messege = "Your battery current state is OK"
            #img = "Battery_OK"
    return render_template('user_page.html',messege = messege)

@app.route('/articles/<int:page>')
def articles(page=1):
    articles = Article.query.paginate(page, 10)
    return render_template('articles.html',articles=articles)


@app.route('/articles/<id>')
def article(id):
    article = Article.query.get_or_404(id)
    article_key = 'article-%s' % article.id
    redis.set(article_key, article.title)
    redis.expire(article_key, 600)
    return 'Article - %s \n %s' % (article.title, article.text)
    #return render_template('article.html', article=article)

@app.route('/recent-articles')
def recent_articles():
    keys_alive = redis.keys('article-*')
    articles = [redis.get(k).decode('utf-8') for k in keys_alive]
    return jsonify({'articles': articles})


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
  if request.method == 'POST':
      msg = request.form.get('msg')
      openai.api_key = ''
      messages = [{"role": "system",
                   "content": "You are a helpful chat assistant for a electric car managment app"},
                  {"role": "user","content": msg}]
      response = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messages)
      return jsonify(message=response['choices'][0]['message']['content'])
  return render_template('chat.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
       return current_user.is_authenticated and current_user.is_admin()

class UserAdminView(ModelView):
    form_edit_rules = (
        'username', 'admin',
        rules.Header('Reset Password'),
        'new_password', 'confirm'
    )
    form_create_rules = (
        'username', 'admin', 'notes', 'password'
    )
    column_searchable_list = ('username',)
    column_sortable_list = ('username', 'admin')
    column_exclude_list = ('password',)
    form_excluded_columns = ('password',)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def scaffold_form(self):
        form_class = super(UserAdminView, self).scaffold_form()
        form_class.password = PasswordField('Password')
        form_class.new_password = PasswordField('New Password')
        form_class.confirm = PasswordField('Confirm New Password')
        return form_class

    def create_model(self, form):
        model = self.model(form.username.data, form.password.data,form.admin.data)
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()

    def update_model(self, form, model):
        form.populate_obj(model)
        if form.new_password.data:
            if form.new_password.data != form.confirm.data:
                 flash('Passwords must match')
                 return
            model.password = generate_password_hash(form.new_password.data)
        self.session.add(model)
        self._on_model_change(form, model, False)
        self.session.commit()

# admin object creation
admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(UserAdminView(User, db.session))

##########mqtt##########3
@socketio.on('unsubscribe')
def handle_unsubscribe():
    mqtt.unsubscribe()
    print('Unsubscribe!')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    cycle = 0
    time = 0
    data = dict(topic=message.topic, payload=message.payload.decode())
    socketio.emit('mqtt_message', data=data)
    print(f'Data {data.items()}')
    serial_number = data.get("topic")
    serial_number = serial_number.rsplit('/')
    serial_number = serial_number[2]
    payload = data.get("payload")
    payload = payload.rsplit('"')
    for word in payload:
        if word == 'time':
            if (str.isdigit(payload)):
                time = int(word)
                print(time)
        elif word == 'cycle':
            if (str.isdigit(payload)):
                cycle = int(word)
                print(cycle)
        else:
            print("No data")
    stmt = db.select(Battery.id).where(Battery.serial_number==serial_number)
    bat_id = db.session.execute(stmt)
    db.session.execute(
        insert(Data).values(timestamp=func.now()).execution_options(render_nulls=True),
        {"time": time, "cycle": cycle, "bat_id": bat_id},
    )
    db.session.flush()
    db.session.commit()


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)
#############################app run###########33
#app factory
def create_app(alt_config={}):
    app = Flask(__name__, template_folder=alt_config.get('TEMPLATE_FOLDER', 'templates'))
    app.config['UPLOAD_FOLDER'] = os.path.realpath('') + '/battery_app/static/uploads'
    app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:////tmp/test.db'
    app.config['WTF_CSRF_SECRET_KEY'] = 'random key for form'
    app.config['LOG_FILE'] = 'application.log'
    app.config.update(alt_config)
    app.register_blueprint(user)
    app.register_blueprint (articles)
    if not app.debug:
        import logging
        from logging import FileHandler, Formatter
        from logging.handlers import SMTPHandler
        file_handler = FileHandler(app.config['LOG_FILE'])
        app.logger.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s:%(message)s ''[in %(pathname)s:%(lineno)d]'))
        app.secret_key = 'some_random_key'
    return app

def create_db(app):
    db.init_app(app)
    with app.app_context():
       db.create_all()
       return db






