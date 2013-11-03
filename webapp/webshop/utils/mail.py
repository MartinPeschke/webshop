# Use this module for e-mailing.

from django.conf import settings
from django.template import loader, Context, TemplateDoesNotExist
from django.core.mail import EmailMultiAlternatives

from email.Header import Header
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib, rfc822

def create_mail(subject, from_mail, to_mail, template, context=None):
    '''
    Refactored Version, Using Django EmailMessage support. Throws Mail Server Exceptions
    '''
    text_template = loader.get_template('email/%s.txt' % template)
    html_template = loader.get_template('email/%s.html' % template)
    order_html = html_template.render(context)
    bcc = []
    if(settings.SERVER_EMAIL not in to_mail):
        bcc = [settings.SERVER_EMAIL]
    msg = EmailMultiAlternatives(subject, text_template.render(context), from_mail, [to_mail], bcc = bcc)
    msg.attach_alternative(order_html, "text/html")
    msg.send()

def createEmail(templateName, context=None):
    htmlTemplate, txtTemplate = None, None
    htmlMsg, txtMsg = None, None
    msg = SafeMIMEMultipart('alternative', charset="utf-8") 
    try:
        txtTemplate = loader.get_template('email/%s.txt' % templateName)
        txtMsg = SafeMIMEText(txtTemplate.render(context), "text")
        msg.attach(txtMsg)
    except TemplateDoesNotExist, e:
        pass
    try:
        htmlTemplate = loader.get_template('email/%s.html' % templateName)
        htmlMsg = SafeMIMEText(htmlTemplate.render(context), "html")
        msg.attach(htmlMsg)
    except TemplateDoesNotExist, e:
        if(txtMsg): msg = txtMsg

    if(txtMsg == None):
        txtMsg = SafeMIMEText("No Text Mail available!","text");
        msg.attach(txtMsg)
        if(htmlMsg == None):
            raise TemplateDoesNotExist, """Neither Text nor HTML Template found! Please make sure 
                        'webshop/templates/email/' contains %s.txt or %s.html!"""  % (templateName, templateName)
    return msg

class BadHeaderError(ValueError):
    pass        

class SafeMIMEMultipart(MIMEMultipart): 
    def __setitem__(self, name, val): 
        "Forbids multi-line headers, to prevent header injection." 
        if '\n' in val or '\r' in val: 
            raise BadHeaderError, "Header values can't contain newlines (got %r for header %r)" % (val, name) 
        MIMEMultipart.__setitem__(self, name, val) 

class SafeMIMEText(MIMEText):
    def __setitem__(self, name, val):
        "Forbids multi-line headers, to prevent header injection."
        if '\n' in val or '\r' in val:
            raise BadHeaderError, "Header values can't contain newlines (got %r for header %r)" % (val, name)
        if name == "Subject":
            val = Header(val, settings.DEFAULT_CHARSET)
        MIMEText.__setitem__(self, name, val)

def send_mail(subject, message, from_email, recipient_list, fail_silently=False, auth_user=settings.EMAIL_HOST_USER, auth_password=settings.EMAIL_HOST_PASSWORD):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.
    """
    return send_mass_mail([[subject, message, from_email, recipient_list]], fail_silently, auth_user, auth_password)

def send_mass_mail(datatuple, fail_silently=False, auth_user=settings.EMAIL_HOST_USER, auth_password=settings.EMAIL_HOST_PASSWORD):
    """
    Given a datatuple of (subject, message, from_email, recipient_list), sends
    each message to each recipient list. Returns the number of e-mails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    """
    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        if auth_user and auth_password:
            server.login(auth_user, auth_password)
    except:
        if fail_silently:
            return
        raise
    num_sent = 0
    for subject, message, from_email, recipient_list in datatuple:
        if not recipient_list:
            continue
        from_email = from_email or settings.DEFAULT_FROM_EMAIL

        if isinstance(message, SafeMIMEText) or isinstance(message, SafeMIMEMultipart): 
                msg = message 
        else: 
                msg = SafeMIMEText(message, 'plain', settings.DEFAULT_CHARSET)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ', '.join(recipient_list)
        msg['Date'] = rfc822.formatdate()
        try:
            server.sendmail(from_email, recipient_list, msg.as_string())
            num_sent += 1
        except:
            if not fail_silently:
                raise
    try:
        server.quit()
    except:
        if fail_silently:
            return
        raise
    return num_sent

def mail_admins(subject, message, fail_silently=False):
    "Sends a message to the admins, as defined by the ADMINS setting."
    send_mail(settings.EMAIL_SUBJECT_PREFIX + subject, message, settings.SERVER_EMAIL, [a[1] for a in settings.ADMINS], fail_silently)

def mail_managers(subject, message, fail_silently=False):
    "Sends a message to the managers, as defined by the MANAGERS setting."
    send_mail(settings.EMAIL_SUBJECT_PREFIX + subject, message, settings.SERVER_EMAIL, [a[1] for a in settings.MANAGERS], fail_silently)
