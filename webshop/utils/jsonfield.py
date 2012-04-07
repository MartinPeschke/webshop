from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json

class JSONField(models.TextField):
    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""

        if value == "":
            return None

        if isinstance(value, basestring):
            return json.loads(value)


        return value

    def get_db_prep_save(self, value):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)
        print value
        return super(JSONField, self).get_db_prep_save(value)
