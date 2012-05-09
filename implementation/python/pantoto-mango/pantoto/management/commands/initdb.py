from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from pantoto import Pantoto

class Command(BaseCommand):
    args = ''
    help = 'Resets the database and initializes the database with default data'

    option_list = BaseCommand.option_list + (
        make_option('--only-reset',
            action='store_true',
            dest='reset_only',
            default=False,
            help='Only Resets the database without storing any default data'),
    )

    def handle(self, *args, **options):
        confirm = raw_input("""
You have requested to initialize database which will IRREVERSIBLY DESTROY any data
Are you sure you want to do this?
Type 'yes' to continue, or 'no/anything' to cancel:""")
        if confirm == "yes":
            Pantoto().init_db(reset_only=options['reset_only'])
            if options['reset_only']:
                print 'Reset Successfully!'
            else:
                print 'Database Initialization successfull!'
        return
            


    
