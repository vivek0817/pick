from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

# Initialize variables for data storage
use_dynamodb = False
dynamodb = None
users_table = None
products_table = None

# In-memory data storage for local development
users = {}
products = [
    {
        'id': 1,
        'name': 'Mango Pickle',
        'price': 150,
        'category': 'veg',
        'image': 'mango.jpg',
        'description': 'Spicy and tangy mango pickle'
    },
    {
        'id': 2,
        'name': 'Lemon Pickle',
        'price': 120,
        'category': 'veg',
        'image': 'lemon.jpg',
        'description': 'Sour and spicy lemon pickle'
    },
    {
        'id': 3,
        'name': 'Chicken Pickle',
        'price': 250,
        'category': 'non_veg',
        'image': 'chicken.jpg',
        'description': 'Spicy chicken pickle'
    },
    {
        'id': 4,
        'name': 'Fish Pickle',
        'price': 300,
        'category': 'non_veg',
        'image': 'fish.jpg',
        'description': 'Traditional fish pickle'
    },
    {
        'id': 5,
        'name': 'Mixed Snacks',
        'price': 180,
        'category': 'snacks',
        'image': 'mixed.jpg',
        'description': 'Assorted traditional snacks'
    },
    {
        'id': 6,
        'name': 'Murukku',
        'price': 100,
        'category': 'snacks',
        'image': 'murukku.jpg',
        'description': 'Crispy rice flour snack'
    }
]

# Try to initialize DynamoDB, fallback to in-memory if credentials are invalid
try:
    # Set AWS credentials and region
    os.environ['AWS_ACCESS_KEY_ID'] = 'your_access_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'your_secret_key'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    # Initialize DynamoDB resource and tables
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    if dynamodb is not None:
        users_table = dynamodb.Table('users')
        products_table = dynamodb.Table('products')
        
        # Test the connection
        products_table.scan(Limit=1)
        use_dynamodb = True
        print("Successfully connected to DynamoDB")
    else:
        use_dynamodb = False
    
except (ClientError, NoCredentialsError) as e:
    print(f"DynamoDB connection failed: {e}")
    print("Falling back to in-memory data storage for local development")
    use_dynamodb = False

def get_products():
    """Get products from DynamoDB or in-memory storage"""
    if use_dynamodb and products_table is not None:
        try:
            response = products_table.scan()
            return response.get('Items', [])
        except ClientError:
            print("DynamoDB error, falling back to in-memory data")
            return products
    else:
        return products

def get_user(username):
    """Get user from DynamoDB or in-memory storage"""
    if use_dynamodb and users_table is not None:
        try:
            response = users_table.get_item(Key={'username': username})
            return response.get('Item')
        except ClientError:
            print("DynamoDB error, falling back to in-memory data")
            return users.get(username)
    else:
        return users.get(username)

def save_user(username, password):
    """Save user to DynamoDB or in-memory storage"""
    if use_dynamodb and users_table is not None:
        try:
            users_table.put_item(Item={'username': username, 'password': password})
            return True
        except ClientError:
            print("DynamoDB error, falling back to in-memory data")
            users[username] = {'username': username, 'password': password}
            return True
    else:
        users[username] = {'username': username, 'password': password}
        return True

def get_product_by_id(product_id):
    """Get product by ID from DynamoDB or in-memory storage"""
    if use_dynamodb and products_table is not None:
        try:
            response = products_table.get_item(Key={'id': int(product_id)})
            return response.get('Item')
        except ClientError:
            print("DynamoDB error, falling back to in-memory data")
            return next((p for p in products if p['id'] == product_id), None)
    else:
        return next((p for p in products if p['id'] == product_id), None)

@app.route('/')
def index():
    products_list = get_products()
    return render_template('index.html', products=products_list)

@app.route('/home')
def home():
    products_list = get_products()
    return render_template('home.html', products=products_list)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user(username)
        if user:
            flash('Username already exists', 'danger')
        else:
            hashed_pw = generate_password_hash(password)
            save_user(username, hashed_pw)
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = get_product_by_id(int(pid))
        if product:
            item_total = product['price'] * qty
            total += item_total
            cart_items.append({'product': product, 'qty': qty, 'item_total': item_total})
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    session['cart'] = cart
    flash('Added to cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        cart.pop(str(product_id))
        session['cart'] = cart
        flash('Removed from cart!', 'success')
    return redirect(url_for('cart'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact_us.html')

@app.route('/veg_pickles')
def veg_pickles():
    products_list = get_products()
    vegs = [p for p in products_list if p['category'] == 'veg']
    return render_template('veg_pickles.html', products=vegs)

@app.route('/non_veg_pickles')
def non_veg_pickles():
    products_list = get_products()
    nonvegs = [p for p in products_list if p['category'] == 'non_veg']
    return render_template('non_veg_pickles.html', products=nonvegs)

@app.route('/snacks')
def snacks():
    products_list = get_products()
    snack_items = [p for p in products_list if p['category'] == 'snacks']
    return render_template('snacks.html', products=snack_items)

@app.route('/checkout')
def checkout():
    return render_template('checkout.html')

@app.route('/order')
def order():
    return render_template('order.html')

@app.route('/success')
def success():
    session.pop('cart', None)
    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)