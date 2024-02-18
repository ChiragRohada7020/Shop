from flask import Flask, render_template, request, redirect, url_for,jsonify
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from waitress import serve


app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb+srv://ChiragRohada:s54icYoW4045LhAW@atlascluster.t7vxr4g.mongodb.net/test')
db = client['shop']  # Replace 'your_database_name' with your database name
user_collection = db['users']  # Replace 'users' with the name of your user collection

@app.route('/')
def index():
    # Fetch all users from the collection
    users = user_collection.find()
    return render_template("index.html")

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        # Get user details from the form
        name = request.form['name']
        address = request.form['address']
        mobile = request.form['mobile']
        balance=0


        # Insert the new user into the 'users' collection with an empty transactions list
        user_id = user_collection.insert_one({'name': name, 'address': address, 'mobile': mobile,'balance':balance}).inserted_id

        # Redirect to the user transactions page
        return redirect(url_for('user_transactions', user_id=user_id))

    return render_template('add_user.html')


@app.route('/search_users')
def search_users():
    query = request.args.get('query', '').lower()
    print(query)

    if query:
        users = user_collection.find({
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'mobile': {'$regex': query, '$options': 'i'}},
                {'address': {'$regex': query, '$options': 'i'}}
            ]
        })
    else:
         # Fetch users from the database based on the search query
        users = user_collection.find({})

   
        # Convert MongoDB objects to a list of dictionaries
    users_data = [
        {'_id': str(user['_id']), 'name': user['name'],'mobile':user['mobile'],'balance':user['balance']}
        for user in users
    ]

    print(users_data)

    return jsonify(users_data)


@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user_transactions(user_id):
    # Fetch user details
    user_id = ObjectId(user_id)
    user = user_collection.find_one({'_id': user_id})
    transactions = user.get('transactions', [])[::-1]


    if request.method == 'POST':
        # Get transaction details from the form
        transaction_type = request.form['transaction_type']
        amount = float(request.form['amount'])
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description=request.form['description']

        if transaction_type == 'deposit':
            user_collection.update_one(
                {'_id': user_id},
                {'$inc': {'balance': amount},
                 '$push': {'transactions': {'type': 'deposit', 'amount': amount, 'date': date,'description':description}}}
            )
        elif transaction_type == 'withdraw':
            user_collection.update_one(
                    {'_id': user_id},
                    {'$inc': {'balance': -amount},
                     '$push': {'transactions': {'type': 'withdraw', 'amount': amount, 'date': date,'description':description}}}
                )
        user = user_collection.find_one({'_id': user_id})
        transactions = user.get('transactions', [])[::-1]


    return render_template('user_transactions.html', user=user,transactions=transactions)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
