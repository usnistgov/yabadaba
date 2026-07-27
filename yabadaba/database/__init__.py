__all__ = ['Database', 'databasemanager', 'load_database']

# Import base Database class
from .Database import Database

# Initialize a ModuleManager for the database styles
from ..tools import ModuleManager
databasemanager = ModuleManager('Database')

# Import load_database
from .load_database import load_database

# Add the modular Database styles
databasemanager.import_style('local', '.LocalDatabase', __name__)
databasemanager.import_style('mongo', '.MongoDatabase', __name__)
databasemanager.import_style('cdcs', '.CDCSDatabase', __name__)