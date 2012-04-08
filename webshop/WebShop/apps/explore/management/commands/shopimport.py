from django.core.management.base import BaseCommand
from WebShop.utils.etl import importTabDelimted

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        importTabDelimted(args[0], args[1])