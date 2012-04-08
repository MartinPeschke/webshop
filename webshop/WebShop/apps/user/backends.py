from WebShop.apps.user.models import PasswordToken, Profile, Address

from django.contrib.auth.models import User

class ModelBackend:
    """
    Authenticate against django.contrib.auth.models.User
    """
    # TODO: Model, login attribute name and password attribute name should be
    # configurable.
    def authenticate(self, username = None, email=None, password=None, token=None, role = None, cu_no = None, zip = None):
        #print username, email, password, token, role, cu_no, zip
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
                p.delete() # each token is one time use only
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
                    users = User.objects.filter(profile__bo_customer_no=username.lstrip('K'), address__zip = '95615').distinct()
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
