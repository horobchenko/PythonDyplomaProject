import openai
from flask_login import login_required
from sqlalchemy.sql.functions import current_user
from werkzeug.security import generate_password_hash
from battery_app import app, mqtt, redis, socketio, db
from battery_app.bat_analizer.models import User, Data, Article, Battery, RegistrationForm, Parameters, LoginForm
from flask import render_template, request, Blueprint, session, flash, redirect, url_for, jsonify
from flask_admin.form import rules
from wtforms import PasswordField
from flask_admin.contrib.sqla import ModelView
from machine_learning.classes import log_reg_model
from flask_admin import AdminIndexView, Admin
from battery_app import mail
from flask_mail import Message

user = Blueprint('user', __name__)
articles = Blueprint('articles', __name__)

@app.route('/')
@app.route('/home')
def home():
    if request.headers.get("X-Requested-With") =="XMLHttpRequest":
        articles = Article.query.all()
        return jsonify({
            'count': len(articles)
        })
    return render_template('home.html')

@user.route('/register', methods=['GET', 'POST'])
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

@user.route('/login', methods=['GET', 'POST'])
def login():
 form = LoginForm()
 if form.validate_on_submit():
     username = request.form.get('username')
     password = request.form.get('password')
     existing_user = User.query.filter_by(username=username).first()
     if not (existing_user and existing_user.check_password(password)):
      flash('Invalid username or password. Please try again.',
            'danger')
     return render_template('login.html', form=form)
     db.session['username'] = username
     flash('You have successfully logged in.', 'success')
     return redirect(url_for('user.user_page'))
     if form.errors:
      flash(form.errors, 'danger')
     return render_template('login.html', form=form)


@user.route('/logout')
@login_required
def logout():
 if 'username' in session:
     session.pop('username')
     flash('You have successfully logged out.', 'success')
     return redirect(url_for('app.home'))

@user.route('/user_page/<id>')
@login_required
def user_page(id):
    stmt = db.select(Battery.stop_cycle).where(Battery.user_id==id)
    result = db.execute(stmt)
    if result:
       messege = "Your battery must be changed"
       img = "Battery_NO_OK"
    else:
        last_cycle_data = log_reg_model.predict(id)
        text = (f"The last cycle number: {last_cycle_data[0]}."
                f"The last cycle date: {last_cycle_data[1]}")
        result = last_cycle_data[2]
        if result:
            messege = "Your battery must be changed"
            img = "Battery_NO_OK"
            mqtt.unsubscribe()
        else:
            messege = "Your battery current state is OK"
            img = "Battery_OK"
    return render_template('user_page.html', text=text,
                           messege = messege,img = img)

@articles.route('/articles')
@articles.route('/articles/<int:page>')
def articles(page=1):
    articles = Article.query.paginate(page, 10)
    return render_template('articles.html',articles=articles)


@articles.route('/articles/<id>')
def articles(id):
    article = Article.query.get_or_404(id)
    article_key = 'article-%s' % article.id
    redis.set(article_key, article.title)
    redis.expire(article_key, 600)
    #return 'Article - %s \n %s' % (article.title, article.text)
    return render_template('article.html', article=article)

@articles.route('/recent-articles')
def recent_articles():
    keys_alive = redis.keys('article-*')
    articles = [redis.get(k).decode('utf-8') for k in keys_alive]
    return jsonify({'articles': articles})


@user.route('/chat', methods=['GET', 'POST'])
@login_required
def chat_gpt():
  if request.method == 'POST':
      msg = request.form.get('msg')
      openai.api_key = app.config['OPENAI_KEY']
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

if __name__ == '__main__':
    socketio.app.run(debug=True,allow_unsafe_werkzeug=True)

