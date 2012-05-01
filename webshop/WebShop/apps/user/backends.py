from WebShop.apps.user.models.password_token import PasswordToken
from django.contrib.auth.models import User

class ModelBackend:
    """
    Authenticate against User
    """
    # TODO: Model, login attribute name and password attribute name should be
    # configurable.
    def authenticate(self, username = None, email=None, password=None, token=None, role = None):
        if email and password:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None  
        elif(token and role):
            try:
                p = PasswordToken.objects.get(value=token, role = role)
                user = p.user
                return user
            except PasswordToken.DoesNotExist:
                return None
        elif(username and password):
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                try:
                    user = User.objects.get(username=username.lstrip('K'))
                    if user.check_password(password):
                        return user
                except User.DoesNotExist:
                    users = User.objects.filter(profile__bo_customer_no=username.lstrip('K'), address__zip = password).distinct()
                    try:
                        return users[0]
                    except IndexError:
                        return None
        return None
        
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
