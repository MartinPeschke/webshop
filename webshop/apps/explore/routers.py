
class ArticleDBRouter(object):
    def db_for_read(self, model, **hints):
        if getattr(model, 'is_articleDB', False):
            return 'articledb'
        else:
            return None
    def db_for_write(self, model, **hints):
        if getattr(model, 'is_articleDB', False):
            return 'articledb'
        else:
            return None
    def allow_relation(self, obj1, obj2, **hints):
        return None
    def allow_syncdb(self, db, model):
        return None