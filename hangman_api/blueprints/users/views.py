from flask import Blueprint , make_response,jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import *

users_api_blueprint = Blueprint('users_api', __name__,)

def get_user_id():
    #get current user
    auth_header = request.headers.get('Authorization')
    # breakpoint()

    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        responseObject = {
            'status': 'failed',
            'message': 'No authorization header found'
        }
        return make_response(jsonify(responseObject)), 400
    # breakpoint()
    user_id = User.decode_auth_token(auth_token)
    return user_id

@users_api_blueprint.route('/', methods=['GET'])
# get all users data
def index():
    users = User.select()
    # users = [(user.__dict__['__data__'] for user in users] # returns a full user object incl password!! (think of how you can exclude sensetive data from the returned JSON if you want to use this)
    users = [{"id": int(user.id), "username": user.username, "email": user.email} for user in users]
    return jsonify(users)

@users_api_blueprint.route('/read', methods=['GET'])
# # get 1 user data
def read():
    user_id = get_user_id()
    user = User.select().where(User.id == user_id)
    # breakpoint()
    user1 = {"id":int(user[0].id),"username": user[0].username, "email": user[0].email}
    return jsonify(user1)

@users_api_blueprint.route('/new', methods=['POST'])
def create():
    # get the post data
    post_data = request.get_json()
    # breakpoint()
    try:
        new_user = User(
            username=post_data['username'],
            email=post_data['email'].lower(),
            password=generate_password_hash(post_data['password'])
        )
    except:
        responseObject={
            'status':'failed',
            'message':['username or password is not unique']
        }
        return make_response(jsonify(responseObject)),400

    else: 
        if new_user.save():
            auth_token = new_user.encode_auth_token(new_user.id)
            responseObject = {
                'status': 'success',
                'message': 'Successfully created a user and signed in.',
                'auth_token': auth_token.decode(),
                'user': {"id": int(new_user.id), "username": new_user.username}
            }
            return make_response(jsonify(responseObject)), 201

        else:
            responseObject = {
                'status': 'failed',
                'message': new_user.errors
            }
            return make_response(jsonify(responseObject)), 400

@users_api_blueprint.route('/update', methods=['POST'])
def update():
    user_id = get_user_id()
    # breakpoint()
    post_data=request.get_json()
    # breakpoint()
    user_username=post_data['username']
    user_email=post_data['email'].lower()
    user_password=generate_password_hash(post_data['password'])

    responseObject = []
    
    if user_username:
        a = User.update(username=user_username).where(User.id == user_id )
        if a.execute():
            responseObjectUsername={
                'status':'success',
                'message' : 'Successfully updated username'
            }
            responseObject.append(responseObjectUsername)
    if user_email:
        b = User.update(email=user_email).where(User.id == user_id )
        if b.execute():
            responseObjectEmail={
                'status':'success',
                'message' : 'Successfully updated email'
            }
            responseObject.append(responseObjectEmail)
    if user_password: 
        c = User.update(password=user_password).where(User.id == user_id )
        if c.execute():
            responseObjectPassword={
                'status':'success',
                'message' : 'Successfully updated password'
            }
            responseObject.append(responseObjectPassword)
    return make_response(jsonify(responseObject)), 201

@users_api_blueprint.route('/delete', methods=['POST'])
def delete():
    # delete user
    user_id = get_user_id()
    # breakpoint()
    q = User.delete().where(User.id == user_id)
    if q.execute():
        responseObject={
            'status':'success',
            'message' : 'Successfully deleted account'
        }
        return make_response(jsonify(responseObject), 201)
    else:
        responseObject={
            'status':'fail',
            'message' : 'Some error occured, please try again later'
        }
        return make_response(jsonify(responseObject), 400)


@users_api_blueprint.route('/login', methods=['POST'])
def sign_in():
    # get the post data
    post_data = request.get_json()
    # check if user already exists
    user = User.get_or_none(username=post_data.get('username'))
    if user and check_password_hash(user.password, post_data.get('password')):
        auth_token = user.encode_auth_token(user.id)

        responseObject = {
            'status': 'success',
            'message': 'Successfully signed in.',
            'auth_token': auth_token.decode(),
            'user': {"id": int(user.id), "username": user.username}
        }
        return make_response(jsonify(responseObject)), 201

    else:
        responseObject = {
            'status': 'fail',
            'message': 'Hey, username or password is incorrect. Please try again'
        }
        return make_response(jsonify(responseObject)), 401