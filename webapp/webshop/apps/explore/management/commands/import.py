from django.core.management.base import BaseCommand
from webshop.utils.etl import process

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        process(args[0])