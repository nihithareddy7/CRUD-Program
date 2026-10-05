import os
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Item

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///crud_app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and login manager
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create tables on startup
with app.app_context():
    db.create_all()


# -------------------------------------------------------------
# AUTHENTICATION ROUTES
# -------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Basic validations
        if not username or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html', username=username, email=email)

        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'warning')
            return render_template('register.html', username=username, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('register.html', username=username, email=email)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', username=username, email=email)

        # Check existing user
        if User.query.filter_by(username=username).first():
            flash('Username already taken. Please choose another.', 'warning')
            return render_template('register.html', email=email)

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login instead.', 'warning')
            return render_template('register.html', username=username)

        # Create user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip() # username or email
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not identifier or not password:
            flash('Please provide both username/email and password.', 'danger')
            return render_template('login.html', identifier=identifier)

        # Find user by username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username/email or password.', 'danger')
            return render_template('login.html', identifier=identifier)

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# -------------------------------------------------------------
# CRUD APPLICATION ROUTES
# -------------------------------------------------------------

@app.route('/')
@login_required
def index():
    # Read/Search/Filter options
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    status_filter = request.args.get('status', '').strip()
    sort_by = request.args.get('sort', 'newest')

    query = Item.query.filter_by(user_id=current_user.id)

    if search_query:
        query = query.filter(
            (Item.title.ilike(f'%{search_query}%')) | 
            (Item.description.ilike(f'%{search_query}%'))
        )

    if category_filter:
        query = query.filter_by(category=category_filter)

    if status_filter:
        query = query.filter_by(status=status_filter)

    if sort_by == 'oldest':
        query = query.order_by(Item.created_at.asc())
    elif sort_by == 'title':
        query = query.order_by(Item.title.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Item.price.desc())
    elif sort_by == 'price_low':
        query = query.order_by(Item.price.asc())
    else: # newest
        query = query.order_by(Item.created_at.desc())

    items = query.all()

    # Calculate quick dashboard stats
    total_items = len(items)
    all_user_items = Item.query.filter_by(user_id=current_user.id).all()
    completed_count = sum(1 for i in all_user_items if i.status == 'Completed')
    pending_count = sum(1 for i in all_user_items if i.status in ['Pending', 'In Progress'])
    total_value = sum(i.price or 0.0 for i in all_user_items)

    # Categories list for filter dropdown
    categories = sorted(list({i.category for i in all_user_items if i.category}))

    return render_template(
        'index.html',
        items=items,
        search_query=search_query,
        category_filter=category_filter,
        status_filter=status_filter,
        sort_by=sort_by,
        categories=categories,
        total_items=len(all_user_items),
        completed_count=completed_count,
        pending_count=pending_count,
        total_value=total_value
    )


# CREATE
@app.route('/items/new', methods=['GET', 'POST'])
@login_required
def create_item():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip() or 'General'
        status = request.form.get('status', 'Pending')
        priority = request.form.get('priority', 'Medium')
        price_raw = request.form.get('price', '0')

        if not title:
            flash('Title is required.', 'danger')
            return render_template('create.html', form=request.form)

        try:
            price = float(price_raw) if price_raw else 0.0
            if price < 0:
                raise ValueError()
        except ValueError:
            flash('Please enter a valid non-negative price.', 'danger')
            return render_template('create.html', form=request.form)

        new_item = Item(
            title=title,
            description=description,
            category=category,
            status=status,
            priority=priority,
            price=price,
            user_id=current_user.id
        )

        db.session.add(new_item)
        db.session.commit()

        flash(f'Item "{title}" created successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('create.html')


# READ (Detail)
@app.route('/items/<int:item_id>')
@login_required
def view_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)
    return render_template('view.html', item=item)


# UPDATE
@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip() or 'General'
        status = request.form.get('status', 'Pending')
        priority = request.form.get('priority', 'Medium')
        price_raw = request.form.get('price', '0')

        if not title:
            flash('Title is required.', 'danger')
            return render_template('edit.html', item=item)

        try:
            price = float(price_raw) if price_raw else 0.0
            if price < 0:
                raise ValueError()
        except ValueError:
            flash('Please enter a valid non-negative price.', 'danger')
            return render_template('edit.html', item=item)

        item.title = title
        item.description = description
        item.category = category
        item.status = status
        item.priority = priority
        item.price = price

        db.session.commit()
        flash(f'Item "{item.title}" updated successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('edit.html', item=item)


# QUICK STATUS TOGGLE
@app.route('/items/<int:item_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)

    if item.status == 'Completed':
        item.status = 'Pending'
    else:
        item.status = 'Completed'

    db.session.commit()
    flash(f'Status for "{item.title}" updated to {item.status}.', 'success')
    return redirect(request.referrer or url_for('index'))


# DELETE
@app.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        abort(403)

    title = item.title
    db.session.delete(item)
    db.session.commit()

    flash(f'Item "{title}" has been deleted.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
