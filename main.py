import news_resources
from data import db_session, news_api
from flask import Flask, render_template, redirect, request, make_response, session, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.news import News
from forms.user import RegisterForm, LoginForm
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

# для списка объектов
api.add_resource(news_resources.NewsListResource, '/api/v2/news')

# для одного объекта
api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(news_api.blueprint)

    # db_sess = db_session.create_session()
    # user = db_sess.query(User).filter(User.id == 1).first()
    # news = News(title="Личная запись", content="Эта запись личная",
    #            is_private=True)
    # user.news.append(news)
    # db_sess.commit()
    @app.route("/")
    def index():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.is_private != True)
        if current_user.is_authenticated:
            news = db_sess.query(News).filter(
                (News.user == current_user) | (News.is_private != True))
        else:
            news = db_sess.query(News).filter(News.is_private != True)
        return render_template("index.html", news=news)

    @app.route('/register', methods=['GET', 'POST'])
    def reqister():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Пароли не совпадают")
            db_sess = db_session.create_session()
            if db_sess.query(User).filter(User.email == form.email.data).first():
                return render_template('register.html', title='Регистрация',
                                       form=form,
                                       message="Такой пользователь уже есть")
            user = User(
                name=form.name.data,
                email=form.email.data,
                about=form.about.data
            )
            user.set_password(form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    @app.route("/session_test")
    def session_test():
        visits_count = session.get('visits_count', 0)
        session['visits_count'] = visits_count + 1
        return make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")

    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(user_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect("/")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    @app.errorhandler(400)
    def bad_request(_):
        return make_response(jsonify({'error': 'Bad Request'}), 400)

    app.run()


if __name__ == '__main__':
    main()
