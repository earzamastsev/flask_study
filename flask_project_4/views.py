from flask import session, render_template, abort, flash, redirect
from models import MealModel, CategoryModel, UserModel, OrderModel
from sqlalchemy.sql.expression import func
from app import app, db
from forms import RegisterForm, OrderForm, LoginForm
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

admin = Admin(app)

admin.add_view(ModelView(MealModel, db.session))
admin.add_view(ModelView(CategoryModel, db.session))
admin.add_view(ModelView(UserModel, db.session))
admin.add_view((ModelView(OrderModel, db.session)))


@app.route('/')
def index():
    categories = db.session.query(CategoryModel).all()
    cat_meals_dict = {}

    # формируем список их 3х товаров по каждой из категорий
    for category in categories:
        meals = db.session.query(MealModel) \
            .filter(MealModel.category == category) \
            .order_by(func.random()) \
            .limit(3) \
            .all()
        cat_meals_dict[category] = meals
    return render_template('main.html', meals=cat_meals_dict, session=session)


@app.route('/cart/', methods=['GET', 'POST'])
def cart():
    # Проверяем наличие товаров в корзине
    if not session.get('cart_id'):
        error = "Ваша корзина пуста. Для оформления заказа необхоимо выбрать блюда."
        return render_template('error.html', error=error)

    form = OrderForm()
    # проверяем правильно заполнена ли форма (запрос POST)
    if form.validate_on_submit():
        order = OrderModel()
        user = session.get('user_id')
        # проверяем авторизирован ли пользователь, если нет - добавляем его в базу но без пароля и роль=guest
        if not user:
            user = UserModel(name=form.name.data,
                             email=form.email.data,
                             address=form.address.data,
                             phone=form.phone.data,
                             role='guest')
            db.session.add(user)
            db.session.commit()
        # пользователь авторизирован, можно из базы подгрузить его данные сразу в форму заказа
        else:
            user = db.session.query(UserModel).get(session.get('user_id'))
        # проверяем есть ли выбранные для заказа блюда, если да - делаем заказ
        if session.get('cart_id'):
            order.users = user
            order.summa = sum(list(map(int, session.get('cart_price'))))
            meals = list(map(int, session.get('cart_id')))
            for meal in meals:
                meal = db.session.query(MealModel).get(meal)
                order.meals.append(meal)
            db.session.add(order)
            db.session.commit()
            session['cart_id'] = []
            session['cart_price'] = []
            return redirect('/ordered/')
        else:
            flash('У вас нет блюд в корзине. Дбавьте блюдо и повторите оформление заказа.')
            return redirect('/')

    # Проверяем прошел ли пользователь аутентификацию
    if session.get('user_id'):
        user = db.session.query(UserModel).get(session['user_id'])
        form.name.data = user.name
        form.email.data = user.email
        form.address.data = user.address
        form.phone.data = user.phone
    meals = []
    for meal in session.get('cart_id'):
        meal = db.session.query(MealModel).get(meal)
        meals.append(meal)
    return render_template('cart.html', meals=meals, form=form)


# добавляем товар в корзину
@app.route('/addtocart/<int:meal>/')
def addtochart(meal):
    price = db.session.query(MealModel).get(meal).price
    session['cart_id'] = session.get('cart_id', [])
    session['cart_price'] = session.get('cart_price', [])
    session['cart_id'].append(str(meal))
    session['cart_price'].append(price)
    return redirect('/cart/')


# удаляем товар из корзины
@app.route('/delfromcart/<meal>/')
def delfromcart(meal):
    # проверка есть ли блюдо в списке выбранных
    if meal in session['cart_id']:
        print(session['cart_id'])
        idx = session['cart_id'].index(meal)
        session['cart_id'].pop(idx)
        session['cart_price'].pop(idx)
        flash('Блюдо удалено из корзины')
        return redirect('/cart/')
    else:
        return abort(404, 'Блюдо не может быть удалено, т.к. оно не было добавлено в корзину')


# подтверждение заказа
@app.route('/ordered/')
def ordered():
    return render_template('ordered.html')


# личный кабинет зарегистрированного пользователя
@app.route('/account/')
def account():
    if session.get('user_id'):
        user = db.session.query(UserModel).get(session['user_id'])
        return render_template('account.html', orders=user.orders)
    return abort(404,
                 'Вы не авторизированы для доступа к этой странице. Необходимо пройти регистрацию и войти в личный кабинет.')


# регистрация пользователя
@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(email=form.email.data).first()
        # Если такой пользователь существует и это не guest
        if user and user.role in ['authorized_user', 'admin']:
            # Не можем зарегистрировать, так как пользователь уже существует
            error_msg = "Пользователь с указанным e-mail уже существует"
            return render_template("register.html", error_msg=error_msg, form=form)
        # если этот польователь уже ранее делал заказы, но не был зарегистрирован (роль guest)
        elif user and user.role == 'guest':
            try:
                form.populate_obj(user)
                user.role = 'authorized_user'
                db.session.add(user)
                db.session.commit()
            except BaseException as er:
                error_msg = "Что-то пошло не так при добавлении пользователя. Попробуйте еще раз."
                return render_template('register.html', form=form, error_msg=error_msg)
            flash(
                'С возвращением! Теперь вы имеете статус зарегистрированного пользователя. Ваша история заказов доступа в личном кабинете.')
            session['user_id'] = user.id
            return redirect('/account/')
        # это новый пользователь
        user = UserModel()
        try:
            form.populate_obj(user)
            user.role = 'authorized_user'
            db.session.add(user)
            db.session.commit()
        except BaseException as er:
            error_msg = "Что-то пошло не так при добавлении пользователя. Попробуйте еще раз."
            return render_template('register.html', form=form, error_msg=error_msg)
        flash('Поздравляем, вы успешно зарегистровались! Добро пожаловать в личный кабинет пользователя.')
        session['user_id'] = user.id
        return redirect('/account/')
    return render_template('register.html', form=form)


# выход пользователя из системы
@app.route('/logout/')
def logout():
    session['user_id'] = None
    session['cart_id'] = []
    session['cart_price'] = []
    return render_template('logout.html')


# вход пользователя в систему
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(UserModel).filter(UserModel.email == form.email.data).first()
        if user and user.password_valid(form.password.data):
            flash('И снова здравствуйте! Добро пожаловать в личный кабинет для заказа блюд.')
            session['user_id'] = user.id
            return redirect('/account/')
        form.email.errors.append("Неверный email или пароль.")
    return render_template('auth.html', form=form)


# страница для отображения ошибок и несуществующих страниц
@app.errorhandler(404)
def no_auth(error):
    return (render_template('error.html', error=error))


# админка
@app.route('/admin/')
def admin():
    return "This is admin view"
