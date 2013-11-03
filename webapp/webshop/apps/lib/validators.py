"""
    Provides functions & Fields for validating credit card numbers
    Thanks to David Shaw for the Luhn Checksum code 
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/172845)
"""


import re
from django import forms
import datetime

def ValidateLuhnChecksum(number_as_string):
    """ checks to make sure that the card passes a luhn mod-10 checksum """

    sum = 0
    num_digits = len(number_as_string)
    oddeven = num_digits & 1

    for i in range(0, num_digits):
        digit = int(number_as_string[i])

        if not (( i & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit

    return ( (sum % 10) == 0 )

# Regex for valid card numbers
CC_PATTERNS = {
    'mastercard':   '^5[12345]([0-9]{14})$',
    'visa':         '^4([0-9]{12,15})$',
    }

def ValidateCharacters(number):
    """ Checks to make sure string only contains valid characters """
    return re.compile('^[0-9 ]*$').match(number) != None

def StripToNumbers(number):
    """ remove spaces from the number """
    if ValidateCharacters(number):
        result = ''
        rx = re.compile('^[0-9]$')
        for d in number:
            if rx.match(d):
                result += d
        return result
    else:
        raise Exception('Number has invalid digits')

def ValidateDigits(type, number):
    """ Checks to make sure that the Digits match the CC pattern """
    regex = CC_PATTERNS.get(type.lower(), False)
    if regex:
        return re.compile(regex).match(number) != None
    else:
        return False

def ValidateCreditCard(clean, number):
    """ Check that a credit card number matches the type and validates the Luhn Checksum """
    clean = clean.strip().lower()
    if ValidateCharacters(number):
        number = StripToNumbers(number)
        if CC_PATTERNS.has_key(clean):
            return ValidateDigits(clean, number)
            return ValidateLuhnChecksum(number)
    return False

class CreditCardNumberField(forms.CharField):
    """ A newforms field for a creditcard number """
    def clean(self, value):

        value = forms.CharField.clean(self, value)
        if not ValidateCharacters(value):
            raise forms.ValidationError('Can only contain numbers and spaces.')
        value = StripToNumbers(value)
        if not ValidateLuhnChecksum(value):
            raise forms.ValidationError('Not a valid credit card number.')

        return value


class CreditCardExpiryField(forms.CharField):
    """ A newforms field for a creditcard expiry date """
    def clean(self, value):
        value = forms.CharField.clean(self, value.strip())

        # Just check MM/YY Pattern
        r = re.compile('^([0-9][0-9])/([0-9][0-9][0-9][0-9])$')
        m = r.match(value)
        if m == None:
            raise forms.ValidationError('Must be in the format MM/YY. i.e. "11/10" for Nov 2010.')

        # Check that the month is 1-12
        month = int(m.groups()[0])
        if month < 1 or month > 12:
            raise forms.ValidationError('Month must be in the range 1 - 12.')

        # Check that the year is not too far into the future
        year = int(m.groups()[1])
        curr_year = datetime.datetime.now().year
        max_year = curr_year + 10
        if year > max_year or year < curr_year:
            raise forms.ValidationError('Year must be in the range %s - %s.' % (str(curr_year).zfill(2), str(max_year).zfill(2),))
        return value
