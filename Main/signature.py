from itsdangerous import URLSafeTimedSerializer
from django.conf import settings
import base64

class Token:
    def __init__(self,security_key):
        self.security_key=security_key
        self.salt=base64.encodebytes(bytes(self.security_key,encoding='utf-8'))
        self.serializer=URLSafeTimedSerializer(security_key)
    def generate_validate_token(self,username):
        return self.serializer.dumps(username,self.salt)
    def confirm_validate_token(self,token,expiration=3600):
        return self.serializer.loads(token,max_age=expiration,salt=self.salt)
    def remove_validate_token(self,token):
        return self.serializer.loads(token,salt=self.salt)

token_confirm=Token(settings.SECRET_KEY)
