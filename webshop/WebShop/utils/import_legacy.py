from WebShop.apps.user.models import *
from django.contrib.auth.models import *

import MySQLdb
import md5

HOST = 'localhost'
DATABASE = 't'
USER = 'root'
PASSWORD = 'Me-2-B'

SQL = '''
select u.username, u.email, u.password, p.compname, p.taxregnu, p.openhours,
pp.firstname, pp.phone, pp.fax, pp.street, pp.zip, pp.country, pp.city
from auth_user u
join apps_profile p on u.id = p.user_id
join apps_person pp on u.id = pp.user_id
where pp.role = 'billing'
'''

def _create_user(username, email, password):
    '''
    Create user object
    '''
    # user = User.objects.create_user(_make_username(email), email, password)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User()
        user.is_active = True
        user.is_staff = False
    user.username = username
    user.email = email
    user.password = password
    user.save()
    return user

def main():
    connect = MySQLdb.connect(host=HOST, db=DATABASE, user=USER, passwd=PASSWORD, charset='utf8')
    cursor = connect.cursor()
    cursor.execute('set names utf8')
    # cursor.execute('select u.username, u.email, u.password, p.compname, p.taxregnu, p.openhours from auth_user u join apps_profile p on u.id = p.user_id')
    cursor.execute(SQL)
    '''
    row[0] - username
    row[1] - email
    row[2] - password hash
    row[3] - company name = Profile.company_name
    row[4] - taxregnu = Profile.vat_id
    row[5] - openhours = Profile.opening_hours
    row[6] - firstname = Profile.first_name
    row[7] - phone = Address.tel
    row[8] - fax = Address.fax
    row[9] - street = Address.street
    row[10] - zip = Address.zip
    row[11] - country = Address.country
    row[12] - city = Address.city
    '''
    for row in cursor.fetchall():
        # print row
        # Save user
        user = _create_user(row[0], row[1], row[2])
        # Save profile
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            profile = Profile()
            profile.user = user
        profile.title = 'MR'
        profile.first_name = row[6] 
        profile.company_name = row[3]
        profile.vat_id = row[4]
        profile.opening_hours = row[5][:32]
        profile.same_address = True
        if row[3]:
            profile.role = 'K'
        else:
            profile.role = 'E'
        try:
            profile.save()
        except:
            print 'Save Profile Error ', row
            continue
        # Save Address
        try:
            address = Address.objects.get(user=user, type='billing')
        except Address.DoesNotExist:
            address = Address()
            address.user = user
        address.type = 'billing'
        address.language = ''
        address.tel = row[7]
        address.fax = row[8]
        address.country = row[11]
        address.city = row[12]
        try:
            address.save()
        except:
            print 'Save Address bError ', row
    cursor.close()

if __name__ == '__main__':
    main()