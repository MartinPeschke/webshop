from WebShop.apps.user.models import PasswordToken
import md5, datetime


def _attach_token(user, role):
    try:
        token = PasswordToken.objects.get(user=user, role = role)
        token.delete()
    except PasswordToken.DoesNotExist:
        pass
    token = _create_token(user, role)
    token.save()
    return token

def _create_token(user, role):
    token = PasswordToken(user=user, role=role)
    token.value = md5.new(str(datetime.datetime.now())+user.password).hexdigest()
        # added the hash of password so knowing time of creation is not enough to guess token value
    return token