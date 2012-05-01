

simple_role = {'F':'E', 'E':'E', 'X':'E', 'K':'K', 'P':'K'}
ANONYMOUS_ROLE = 'F'
LEAST_ROLE = 'E'
NORM_ROLE = 'K'
NO_RIGHTS = [ANONYMOUS_ROLE, 'E', 'X']
REQUIRES_APPROVAL = HAS_RIGHTS = ['K', 'P', 'M']

#    role : roleName
USER_GROUPS = [
    ('E', 'Retail'),
    ('K', 'Wholesale'),
    ('P', 'Partner'),
    ('M', 'Content Manager'),
]
USER_ROLES = [(ANONYMOUS_ROLE, 'Anonymous')] + USER_GROUPS + [('X', 'Disabled')]
userRoles = dict(USER_ROLES)