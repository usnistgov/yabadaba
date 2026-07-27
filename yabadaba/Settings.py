# Standard Python libraries
from pathlib import Path
import json
from copy import deepcopy
from typing import Union, Optional

# Relative imports
from yabadaba.tools import screen_input

class Settings():
    """
    Class for handling saved settings.
    """
    def __init__(self,
                 directoryname: str = '.NIST',
                 filename: str = 'settings.json'):
        """
        Class initializer. Calls load.
        
        Parameters
        ----------
        directoryname : str, optional
            The default directory where the settings file is expected will be
            in a directory of this name within the user's home directory.
            Default value is ".NIST".
        filename, str, optional
            The name to use for the settings file.  This will be saved in the
            directory path and should have a ".json" extension.  Default value
            is "settings.json".
        """
        self.__directoryname = directoryname
        self.__filename = filename
        self.__content = {}
        self.__defaultcontent = {}

        self.load()

    ######################## Basic settings operations ########################

    @property
    def defaultdirectory(self) -> Path:
        """pathlib.Path : Path to the default settings directory"""
        return Path(Path.home(), self.__directoryname)

    @property
    def defaultfilename(self) -> Path:
        """pathlib.Path : Path to the default settings file"""
        return Path(self.defaultdirectory, self.__filename)

    @property
    def directory(self) -> Path:
        """pathlib.Path : Path to the settings directory"""
        return self.__directory

    @property
    def filename(self) -> Path:
        """pathlib.Path : Path to the settings file"""
        return Path(self.directory, self.__filename)

    @property
    def content(self) -> dict:
        """dict : The contents of the settings file"""
        return self.__content
    
    @property
    def defaultcontent(self) -> dict:
        """dict : The contents of the default settings file"""
        return self.__defaultcontent
    
    def load(self):
        """Loads the settings file."""
        
        # Load settings.json from the default location
        if self.defaultfilename.is_file():
            with open(self.defaultfilename, 'r') as f:
                self.__defaultcontent = json.load(fp=f)
        else:
            self.__defaultcontent = {}
            
        # Check if forwarding_directory has been set
        if 'forwarding_directory' in self.__defaultcontent:
            self.__directory = Path(self.__defaultcontent['forwarding_directory'])
            
            # Load content from the forwarded location
            if self.filename.is_file():
                with open(self.filename, 'r') as f:
                    self.__content = json.load(fp=f)
            else:
                self.__content = {}

            # Check for recursive forwarding
            if 'forwarding_directory' in self.__content:
                raise ValueError('Multi-level forwarding not allowed.')
        
        # If no forwarding, default is current content
        else:
            self.__content = self.__defaultcontent
            self.__directory = self.defaultdirectory

    def save(self):
        """Saves content to settings.json."""
        if not self.directory.is_dir():
            self.directory.mkdir(parents=True)

        with open(self.filename, 'w') as f:
            json.dump(self.content, fp=f, indent=4)
        
        # Reload
        self.load()

    def set_directory(self,
                      directory: Union[str, Path] = None,
                      move: bool = True,
                      prompt: bool = True):
        """
        Changes the settings directory to a different location.

        Parameters
        ----------
        directory : str or Path
            The path to the new settings directory where settings.json (and the
            default library directory) are to be located.
        move : bool, optional
            If True (default), will attempt to move the exiting settings file to the new
            location.  If False, only the directory path is updated and any settings in the
            old and new locations are left alone.
        prompt : bool, optional
            The default behavior is to prompt for missing details and confirmation of
            changes being made.  Setting prompt = False will skip confirmations and
            throw errors if required inputs are not given to the function.

        Raises
        ------
        TypeError
            If prompt is False and directory is not given.
        ValueError
            If an invalid response is given to the confirmation prompt or if move is True
            and a non-empty settings file already exists in the new location.
        """
        # Manage directory values
        if directory is None:
            if prompt:
                directory = screen_input("Enter the path for the new settings directory:")
            else:
                raise TypeError('directory must be specified if prompt is False')
        directory = Path(directory).resolve()
        
        # Check if given directory path is the current set value
        if self.directory == directory:
            print(f'Settings directory is already set to "{self.directory}"')
            return None
        
        # Prompt confirmation
        if prompt:
            print(f'Current settings directory is "{self.directory}"')
            option = screen_input(f'Update to "{directory}"? (yes or no):')
            if option.lower() in ['yes', 'y']:
                pass
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
        
        # Move existing settings
        if move:
            
            # Check for file in the new location
            filename = Path(directory, self.__filename)
            if filename.is_file():
                with open(filename, 'r') as f:
                    test_content = f.read()
                if test_content.strip() not in ['', '{}']:
                    raise ValueError(f'cannot move directory as "{filename}" exists and contains content')

            # Move the settings file
            self.filename.replace(filename)
            
            # Clear defaultcontent if previous directory was the default
            if self.directory == self.defaultdirectory:
                self.__defaultcontent = {}
            
        # Update forwarding_directory value in default content
        self.defaultcontent['forwarding_directory'] = directory.as_posix()
        
        # Save the updated default settings file
        if not self.defaultdirectory.is_dir():
            self.defaultdirectory.mkdir(parents=True)
        with open(self.defaultfilename, 'w') as f:
            json.dump(self.defaultcontent, fp=f, indent=4)
        
        # Reload settings
        self.load()
        
    def unset_directory(self,
                        move: bool = True,
                        prompt: bool = True):
        """
        Changes the settings directory back to the default location.
        
        Parameters
        ----------
        move : bool
            If True (default), will attempt to move the contents of the existing settings file
            to the default location.  If False, only the directory path is updated and any settings
            in the old and new locations are left alone.
        prompt : bool, optional
            The default behavior is to prompt for missing details and confirmation of
            changes being made.  Setting prompt = False will skip confirmations and
            throw errors if required inputs are not given to the function.

        Raises
        ------
        ValueError
            If an invalid response is given to the confirmation prompt or if move is True
            and a non-empty settings file already exists in the new location.
        """
        
        # Check if directory already is the default value
        if self.directory == self.defaultdirectory:
            print(f'Settings directory is already set to "{self.defaultdirectory}"')
            return None
        
        # Prompt confirmation
        if prompt:
            print(f'Current settings directory is "{self.directory}"')
            option = screen_input(f'Update to "{self.defaultdirectory}"? (yes or no):')
            if option.lower() in ['yes', 'y']:
                pass
            elif option.lower() in ['no', 'n']: 
                return None
            else: 
                raise ValueError('Invalid choice')
        
        # Move existing settings
        if move:
            # Check if default content contains other settings
            for key in self.defaultcontent:
                if key != 'forwarding_directory':
                    raise ValueError(f'cannot move directory as "{self.defaultfilename}" contains content')

            # Move the settings file to the default location
            self.filename.replace(self.defaultfilename)
        
        # Unset without moving
        else:       
            
            # Remove forwarding_directory pointer
            del self.defaultcontent['forwarding_directory']
            
            # Save the updated default settings file
            if not self.defaultdirectory.is_dir():
                self.defaultdirectory.mkdir(parents=True)
            with open(self.defaultfilename, 'w') as f:
                json.dump(self.defaultcontent, fp=f, indent=4)
        
        # Reload settings
        self.load()
    
    ############################ database settings ############################

    @property
    def databases(self) -> dict:
        """dict: Any defined database settings organized by name"""
        if 'database' in self.content:
            return deepcopy(self.content['database'])
        else:
            return {}

    @property
    def list_databases(self) -> list:
        """list: The names associated with the defined databases"""
        return list(self.databases.keys())

    def set_database(self,
                     name: Optional[str] = None,
                     style: Optional[str] = None,
                     host: Optional[str] = None,
                     prompt: bool = True,
                     **kwargs):
        """
        Allows for database information to be defined in the settings file. Screen
        prompts will be given to allow any necessary database parameters to be
        entered.

        Parameters
        ----------
        name : str, optional
            The name to assign to the database. If not given, the user will be
            prompted to enter one.
        style : str, optional
            The database style associated with the database. If not given, the
            user will be prompted to enter one.
        host : str, optional
            The database host (directory path or url) where the database is
            located. If not given, the user will be prompted to enter one.
        prompt : bool, optional
            The default behavior is to prompt for missing details and confirmation of
            changes being made.  Setting prompt = False will skip confirmations and
            throw errors if required inputs are not given to the function.
        **kwargs : any, optional
            Any other database style-specific parameter settings required to
            properly access the database.

        Raises
        ------
        ValueError
            If the answer to the overwrite question is invalid.
        """
        # Ask for name if not given
        if name is None:
            if prompt:
                name = screen_input('Enter a name for the database:')
            else:
                raise TypeError('name must be specified if prompt is False')

        # Load database if it exists
        if name in self.list_databases:
            
           # Ask if existing database should be overwritten
            if prompt:
                print(f'Database {name} already defined.')
                option = screen_input('Overwrite? (yes or no):')
                if option.lower() in ['yes', 'y']:
                    pass
                elif option.lower() in ['no', 'n']: 
                    return None
                else: 
                    raise ValueError('Invalid choice')

        # Ask for style if not given
        if style is None: 
            if prompt:
                style = screen_input("Enter the database's style:")
            else:
                raise TypeError('style must be specified if prompt is False')
        
        # Ask for host if not given
        if host is None: 
            if prompt:
                host = screen_input("Enter the database's host:")
            else:
                raise TypeError('host must be specified if prompt is False')
        
        if len(kwargs) == 0 and prompt:
            print('Enter any other database parameters as key, value')
            print('Exit by leaving key blank')
            while True:
                key = screen_input('key:')
                if key == '': 
                    break
                kwargs[key] = screen_input('value:')

        # Create database entry
        if 'database' not in self.content:
            self.content['database'] = {}
        self.content['database'][name] = entry = {}
        entry['style'] = style
        entry['host'] = str(host)
        for key, value in kwargs.items():
            entry[key] = value

        # Save changes
        self.save()
    
    def unset_database(self,
                       name: Optional[str] = None,
                       prompt: bool = True):
        """
        Deletes the settings for a pre-defined database from the settings file.

        Parameters
        ----------
        name : str, optional
            The name assigned to a pre-defined database.
        prompt : bool, optional
            The default behavior is to prompt for missing details and confirmation of
            changes being made.  Setting prompt = False will skip confirmations and
            throw errors if required inputs are not given to the function.

        Raises
        ------
        TypeError
            If prompt is False and name is not given.
        ValueError
            If the database name is not found
        """
        database_names = self.list_databases
                  
        # Ask for name if not given
        if name is None:
            if len(database_names) > 0:
                if prompt:
                    print('Select a database:')
                    for i, database in enumerate(database_names):
                        print(i+1, database)
                    choice = screen_input(':')
                    try:
                        choice = int(choice)
                    except:
                        name = choice
                    else:
                        name = database_names[choice-1]
                else:
                    raise TypeError('name must be specified if prompt is False')
            else:
                print('No databases currently set')
                return None

        # Verify listed name exists 
        try:
            i = database_names.index(name)
        except:
            raise ValueError(f'Database {name} not found')

        # Confirmation prompt
        if prompt:
            print(f'Database {name} found')
            test = screen_input('Delete settings? (must type yes):').lower()
            if test != 'yes':
                return None

        # Delete database and save
        del(self.content['database'][name])
        if len(self.content['database']) == 0:
            del(self.content['database'])
        self.save()

# Initialize settings
settings = Settings()