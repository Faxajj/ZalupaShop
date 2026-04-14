"""
Mvideo Shop — Flask app (ES/GN + PYG/USD)
"""
import os
import uuid
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, abort, session, g
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from i18n import TRANSLATIONS, t as translate

# ----------------------------- Config ----------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mvideo-shop-secret-change-in-prod')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'mvideo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# Tasa PYG -> USD (edítalo cuando cambie)
USD_RATE = 7300.0

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ----------------------------- Models ----------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, pw): self.password_hash = generate_password_hash(pw)
    def check_password(self, pw): return check_password_hash(self.password_hash, pw)

    @property
    def is_admin(self): return self.role == 'admin'


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)          # Español
    name_gn = db.Column(db.String(200))                       # Guaraní
    description = db.Column(db.Text, default='')              # Español
    description_gn = db.Column(db.Text, default='')           # Guaraní
    price = db.Column(db.Float, nullable=False)               # PYG
    old_price = db.Column(db.Float, nullable=True)            # PYG
    category = db.Column(db.String(80), index=True)
    stock = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship('ProductImage', backref='product',
                             cascade='all, delete-orphan', lazy=True,
                             order_by='ProductImage.sort_order')
    specs = db.relationship('ProductSpec', backref='product',
                            cascade='all, delete-orphan', lazy=True)

    @property
    def main_image(self):
        return self.images[0] if self.images else None

    def localized_name(self, lang='es'):
        if lang == 'gn' and self.name_gn: return self.name_gn
        return self.name

    def localized_description(self, lang='es'):
        if lang == 'gn' and self.description_gn: return self.description_gn
        return self.description


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

    @property
    def url(self):
        if self.filename.startswith(('http://', 'https://')):
            return self.filename
        return url_for('static', filename='uploads/' + self.filename)


class ProductSpec(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(500), nullable=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total = db.Column(db.Float, nullable=False, default=0)    # PYG
    status = db.Column(db.String(30), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order',
                            cascade='all, delete-orphan', lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    name = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)


# ----------------------------- Helpers ---------------------------------------
@login_manager.user_loader
def load_user(uid): return User.query.get(int(uid))


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def allowed_file(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in ALLOWED_EXT


# ----------------------------- i18n / currency -------------------------------
@app.before_request
def set_locale():
    g.lang = session.get('lang', 'es')
    if g.lang not in ('es', 'gn'): g.lang = 'es'
    g.currency = session.get('currency', 'PYG')
    if g.currency not in ('PYG', 'USD'): g.currency = 'PYG'


@app.route('/set-lang/<lang>')
def set_lang(lang):
    if lang in ('es', 'gn'): session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


@app.route('/set-currency/<cur>')
def set_currency(cur):
    if cur in ('PYG', 'USD'): session['currency'] = cur
    return redirect(request.referrer or url_for('index'))


def fmt_pyg(pyg):
    return "₲ " + "{:,.0f}".format(pyg).replace(",", ".")

def fmt_usd(pyg):
    return "US$ " + "{:,.2f}".format(pyg / USD_RATE)

def fmt_primary(pyg):
    return fmt_usd(pyg) if g.currency == 'USD' else fmt_pyg(pyg)

def fmt_secondary(pyg):
    return fmt_pyg(pyg) if g.currency == 'USD' else fmt_usd(pyg)


@app.context_processor
def inject_globals():
    return {
        'site_name': 'Mvideo Shop',
        'current_year': datetime.utcnow().year,
        't': lambda key: translate(key, g.lang),
        'lang': g.lang,
        'currency': g.currency,
        'fmt_primary': fmt_primary,
        'fmt_secondary': fmt_secondary,
        'fmt_pyg': fmt_pyg,
        'fmt_usd': fmt_usd,
        'loc_name': lambda p: p.localized_name(g.lang),
        'loc_desc': lambda p: p.localized_description(g.lang),
    }


# ----------------------------- Public routes ---------------------------------
@app.route('/')
def index():
    q = request.args.get('q', '').strip()
    cat = request.args.get('cat', '').strip()
    query = Product.query
    if q:
        query = query.filter(db.or_(
            Product.name.ilike(f'%{q}%'),
            Product.name_gn.ilike(f'%{q}%')
        ))
    if cat:
        query = query.filter_by(category=cat)
    products = query.order_by(Product.created_at.desc()).all()
    categories = [c[0] for c in
                  db.session.query(Product.category).distinct().all() if c[0]]
    return render_template('index.html',
                           products=products, categories=categories,
                           q=q, cat=cat)


@app.route('/product/<int:pid>')
def product_page(pid):
    product = Product.query.get_or_404(pid)
    return render_template('product.html', product=product)


# ----------------------------- Auth ------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not username or not email or len(password) < 6:
            flash(translate('err_fill_all', g.lang), 'error')
            return redirect(url_for('register'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash(translate('err_exists', g.lang), 'error')
            return redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(translate('ok_registered', g.lang), 'success')
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        ident = request.form.get('username', '').strip()
        pw = request.form.get('password', '')
        user = User.query.filter(
            (User.username == ident) | (User.email == ident.lower())
        ).first()
        if user and user.check_password(pw):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        flash(translate('err_bad_credentials', g.lang), 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    orders = Order.query.filter_by(user_id=current_user.id)\
                        .order_by(Order.created_at.desc()).all()
    return render_template('profile.html', orders=orders)


@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    data = request.get_json() or {}
    items = data.get('items', [])
    if not items:
        return jsonify({'error': 'empty'}), 400

    order = Order(user_id=current_user.id, total=0)
    db.session.add(order)
    db.session.flush()

    total = 0.0
    for it in items:
        p = Product.query.get(it.get('id'))
        if not p: continue
        qty = max(1, int(it.get('qty', 1)))
        total += p.price * qty
        db.session.add(OrderItem(
            order_id=order.id, product_id=p.id,
            name=p.name, price=p.price, qty=qty
        ))
    order.total = total
    db.session.commit()
    return jsonify({'ok': True, 'order_id': order.id, 'total': total})


# ----------------------------- Admin -----------------------------------------
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'products': Product.query.count(),
        'users': User.query.count(),
        'orders': Order.query.count(),
        'total_revenue': db.session.query(db.func.sum(Order.total)).scalar() or 0,
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           stats=stats, recent_orders=recent_orders)


@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template('admin/products.html', products=products)


@app.route('/admin/products/new', methods=['GET', 'POST'])
@app.route('/admin/products/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_product_form(pid=None):
    product = Product.query.get(pid) if pid else None

    if request.method == 'POST':
        is_new = product is None
        if is_new:
            product = Product(
                sku=request.form.get('sku', '').strip(),
                name=request.form.get('name', '').strip(),
                price=float(request.form.get('price') or 0),
            )
            db.session.add(product)

        product.sku = request.form.get('sku', '').strip()
        product.name = request.form.get('name', '').strip()
        product.name_gn = request.form.get('name_gn', '').strip() or None
        product.description = request.form.get('description', '')
        product.description_gn = request.form.get('description_gn', '')
        product.price = float(request.form.get('price') or 0)
        op = request.form.get('old_price', '').strip()
        product.old_price = float(op) if op else None
        product.category = request.form.get('category', '').strip()
        product.stock = int(request.form.get('stock') or 0)
        db.session.flush()

        ProductSpec.query.filter_by(product_id=product.id).delete()
        keys = request.form.getlist('spec_key[]')
        vals = request.form.getlist('spec_value[]')
        for k, v in zip(keys, vals):
            if k.strip() and v.strip():
                db.session.add(ProductSpec(product_id=product.id,
                                           key=k.strip(), value=v.strip()))

        for url in request.form.getlist('image_url[]'):
            url = url.strip()
            if url.startswith(('http://', 'https://')):
                db.session.add(ProductImage(product_id=product.id, filename=url))

        files = request.files.getlist('images')
        for f in files:
            if f and f.filename and allowed_file(f.filename):
                ext = f.filename.rsplit('.', 1)[1].lower()
                fn = f"{uuid.uuid4().hex}.{ext}"
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
                db.session.add(ProductImage(product_id=product.id, filename=fn))

        db.session.commit()
        flash(translate('product_saved', g.lang), 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', product=product)


@app.route('/admin/products/<int:pid>/delete', methods=['POST'])
@login_required
@admin_required
def admin_product_delete(pid):
    p = Product.query.get_or_404(pid)
    for img in p.images:
        if not img.filename.startswith(('http://', 'https://')):
            try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
            except OSError: pass
    db.session.delete(p)
    db.session.commit()
    flash(translate('product_deleted', g.lang), 'success')
    return redirect(url_for('admin_products'))


@app.route('/admin/image/<int:img_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_image_delete(img_id):
    img = ProductImage.query.get_or_404(img_id)
    pid = img.product_id
    if not img.filename.startswith(('http://', 'https://')):
        try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], img.filename))
        except OSError: pass
    db.session.delete(img)
    db.session.commit()
    return redirect(url_for('admin_product_form', pid=pid))


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.id.desc()).all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/users/<int:uid>/toggle', methods=['POST'])
@login_required
@admin_required
def admin_user_toggle(uid):
    u = User.query.get_or_404(uid)
    if u.id == current_user.id:
        flash(translate('cannot_change_self', g.lang), 'error')
    else:
        u.role = 'admin' if u.role == 'user' else 'user'
        db.session.commit()
    return redirect(url_for('admin_users'))


# ----------------------------- Errors ----------------------------------------
@app.errorhandler(403)
def e403(e):
    return render_template('error.html', code=403,
                           msg=translate('err_403', g.lang)), 403

@app.errorhandler(404)
def e404(e):
    return render_template('error.html', code=404,
                           msg=translate('err_404', g.lang)), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000, host='0.0.0.0')
