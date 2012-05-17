from django.utils.translation import ugettext_lazy

simple_role = {'F':'E', 'E':'E', 'G':'E',  'X':'E', 'K':'K', 'P':'K'}
ANONYMOUS_ROLE = 'F'
LEAST_ROLE = 'E'
AWAITING_APPROVAL_ROLE = "G"
NORM_ROLE = 'K'



NO_RIGHTS = [ANONYMOUS_ROLE, LEAST_ROLE, 'X', AWAITING_APPROVAL_ROLE]
HAS_RIGHTS = [NORM_ROLE, 'P']
REQUIRES_APPROVAL = [AWAITING_APPROVAL_ROLE, NORM_ROLE, 'P']





#    role : roleName
USER_GROUPS = [
    (LEAST_ROLE, ugettext_lazy('Endkunde')),
    (AWAITING_APPROVAL_ROLE, ugettext_lazy('Studio')),
    (NORM_ROLE, ugettext_lazy('Studio')),
    ('P', ugettext_lazy('Partner')),
    ('M', ugettext_lazy('Content Manager')),
]





USER_ROLES = [(ANONYMOUS_ROLE, 'Anonymous')] + USER_GROUPS + [('X', 'Disabled')]
userRoles = dict(USER_ROLES)