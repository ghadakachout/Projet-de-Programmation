#!/usr/bin/env python3
# coding: utf8
import os
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, url_for, flash, redirect, request, abort
from sqlalchemy import or_
import base64
from db_config import bcrypt, db, app
from appforms import RegistrationForm, sForm, Inputs, LoginForm, ClothesForm, MessageSeller
from db_handling import Achat, User, Garment, Message
from flask_bcrypt import generate_password_hash, check_password_hash


@app.route("/")
def index():
    return render_template('index.html', title='index')
@app.route("/home")
def home(garments=None, *args):
    form = sForm()
    mSeller = MessageSeller()
    iform = Inputs()
    if garments is None:
        garments = Garment.query.all()
    return render_template('home.html', garments=garments, form=form, iform=iform, mSeller=mSeller)



@app.route("/about")
def about():
    return render_template('about.html', title='About')



@app.route("/register", methods=['GET', 'POST'])
def register():
    users = User.query
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if db.session.query(User).filter_by(email=form.email.data).count() < 1:
            user = User(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data,type="user")
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        else:
            flash('email is already registered', 'success')

    return render_template('register.html', title='Register', form=form)



@app.route("/garment/newAdmin", methods=['GET', 'POST'])
def registerAdmin():
    users = User.query
    form = RegistrationForm()
    if form.validate_on_submit():
        if db.session.query(User).filter_by(email=form.email.data).count() < 1:
            user = User(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data,type="admin")
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('New Admin has been created!', 'success')
            return redirect(url_for('account'))
        else:
            flash('email is already registered', 'success')

    return render_template('registerAdmin.html', title='Register', form=form)





@app.route("/home/<int:garment_id>/message", methods=['GET', 'POST'])
def message(garment_id):

    mSeller = MessageSeller()
    garments = Garment.query
    users = User.query
    if mSeller.validate_on_submit():
        if current_user.is_authenticated:
            if current_user.type=="user":
                gar = garments.filter_by(id=garment_id).first()
                userid = gar.user_id
                user = users.filter_by(id=userid).first()
                message = Message(gar_name= gar.title, msg=mSeller.msg.data, sender=user, )
                db.session.add(message)
                db.session.commit()
                flash('Your message have been successfully sent!', 'success')
                return redirect(url_for('home'))
            
    return render_template('message.html', title='Message seller',
                           mSeller=mSeller, legend='Message seller')


@app.route("/login", methods=['GET', 'POST'])
def login():
    """
     A web page that allows an end-user with login credentials to login
    :return:
    """
    if current_user.is_authenticated:
        if current_user.type=="user":

            return redirect(url_for('home'))
        else:
            return redirect(url_for('account'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if user.type=="admin":
                return redirect(url_for('account'))
            else:
                return redirect(url_for('home'))    
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    garments = Garment.query.all()
    messages = Message.query.all()
    return render_template('account.html', title='Account', garments=garments, messages=messages)


@app.route("/garment/<int:garment_id>/update", methods=['GET', 'POST'])
@login_required
def update_garment(garment_id):

    garment = Garment.query.get_or_404(garment_id)
    if garment.seller != current_user:
        abort(403)
    form = ClothesForm()
    if form.validate_on_submit():
        garment.title = form.title.data
        garment.gender = form.gender.data
        garment.size = form.size.data
        garment.price = form.price.data
        garment.des = form.des.data
        garment.pic = f'{base64.b64encode(form.pic.data.read()).decode("utf-8")}'
        db.session.commit()
        flash('Your garment has been updated!', 'success')
        #return redirect(url_for('garment', garment_id=garment.id))
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.title.data = garment.title
        form.des.data = garment.des
    return render_template('create_garment.html', title='Update Garment',
                           form=form, legend='Update Garment')
    #return render_template('home.html')


@app.route("/garment/<int:garment_id>/delete", methods=['POST'])
@login_required
def delete_garment(garment_id):

    garment = Garment.query.get_or_404(garment_id)
    db.session.delete(garment)
    db.session.commit()
    flash('Your clothes have been successfully deleted!', 'success')
    return redirect(url_for('account'))


@app.route("/garment/new", methods=['GET', 'POST'])
@login_required
def new_garment():

    form = ClothesForm()
    if form.validate_on_submit():
        gender = str(form.gender.data)
        size = str(form.size.data)
        pic = f'{base64.b64encode(form.pic.data.read()).decode("utf-8")}'
        garment = Garment(title=form.title.data,  gender=gender, size=size, price=form.price.data,  des=form.des.data, seller=current_user, pic=pic)
        db.session.add(garment)
        db.session.commit()
        flash('Your clothes have been successfully added!', 'success')
        return redirect(url_for('account'))
    return render_template('create_garment.html', title='New Post',
                           form=form, legend='New Post')





@app.route('/search', methods=['GET', 'POST'])
def search():
    mSeller = MessageSeller()
    form = sForm()
    iform = Inputs()
    garments = Garment.query
    if form.validate_on_submit():
        search_term = form.gare.data
        #garments = garments.filter( Garment.des.like('%' +search_term +'%'))
        garments = garments.filter(or_(Garment.des.like('%' + search_term + '%'), Garment.title.like('%' + search_term + '%'),
                                       Garment.price.like('%' + search_term + '%'), Garment.size.like('%' + search_term + '%'),
                                       Garment.gender.like('%' + search_term + '%')
                                       ))
        garments = garments.order_by(Garment.des).all()
       # return render_template('search.html', form=form, results=results)
        return render_template('home.html', garments=garments, form=form, iform=iform)

    return render_template('search.html', form=form)


@app.route('/sort', methods=['GET', 'POST'])
def sort():
    form = sForm()
    iform = Inputs()
    mSeller = MessageSeller()
    garments = Garment.query
    if  iform.validate_on_submit():
        sort_value = iform.myField.data
        if sort_value == "price":
            garments = Garment.query.order_by(Garment.price.desc())
        elif sort_value == "date":
            garments = Garment.query.order_by(Garment.date_posted.desc())
        elif sort_value == "gender":
            garments = Garment.query.order_by(Garment.gender.desc())
        elif sort_value == "size":
            garments = Garment.query.order_by(Garment.size.desc())

        return render_template('home.html', garments=garments, form=form, iform=iform, mSeller=mSeller)

    return render_template('sort.html', iform=iform)


@app.route("/garmentDetails/<int:garment_id>")
def garment(garment_id):
    garment=Garment.query.get(garment_id)
    return render_template('garment.html',garment=garment)


"""@app.route("/add/<id>", methods=['POST'])
def add_to_cart(id):
	if not current_user.is_authenticated:
		flash(f'You must login first!<br> <a href={url_for("login")}>Login now!</a>', 'error')
		return redirect(url_for('login'))

	garment = Garment.query.get(id)
	if request.method == "POST":
		current_user.add_to_cart(id)
		flash(f'''{garment.name} successfully added to the <a href=cart>cart</a>.<br> <a href={url_for("cart")}>view cart!</a>''','success')
		return redirect(url_for('cart'))"""




@app.route("/cart")
@login_required
def cart():
    garments = Garment.query.all()
    messages = Message.query.all()
    return render_template('account.html', title='Account', garments=garments, messages=messages)  








@app.route("/addToCart/<int:garment_id>/<int:user_id>")
def add_to_cart(garment_id,user_id):
    new_achat = Achat(uid=user_id,gid=garment_id)
    db.session.add(new_achat)
    db.session.commit()
    flash('Your clothes have been successfully added in your Cart!', 'success')
    achats=Achat.query.filter_by(uid=user_id)
    garments=[]
    for achat in achats:
        garment=Garment.query.filter_by(id=achat.gid).first()
        garments.append(garment)
    return render_template('cart.html',current_user=current_user,garments=garments)    



@app.route("/ViewCart/<int:user_id>")
def ViewCart(user_id):
    achats=Achat.query.filter_by(uid=user_id)
    garments=[]
    for achat in achats:
        garment=Garment.query.filter_by(id=achat.gid).first()
        garments.append(garment)

    return render_template('ViewCart.html',current_user=current_user,garments=garments)  


@app.route('/shop')
def shop():
        garments = Garment.query.all()
        return render_template('shop.html',garments=garments)



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port,debug=True)
    
