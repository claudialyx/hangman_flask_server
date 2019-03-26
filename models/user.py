from app import app
import peewee as pw
from models.base_model import *
from playhouse.hybrid import hybrid_property
from flask import flash
import datetime
import jwt

class User(BaseModel):
    username = pw.CharField(unique=True)
    email = pw.CharField(unique=True)
    password = pw.CharField()

    def validate(self):
        duplicate_username = User.get_or_none(User.username == self.username)

        if duplicate_username and duplicate_username.id != self.id:
            self.errors.append('username not unique')

        duplicate_email = User.get_or_none(User.email == self.email)

        if duplicate_email and duplicate_email.id != self.id:
            self.errors.append('email not unique')


    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 0
        except jwt.InvalidTokenError:
            return 0