# coding: utf-8
# Standard Python libraries
from pathlib import Path
import ast
import shutil
import tarfile
from typing import Optional, Tuple, Union

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# iprPy imports
from ..tools import aslist, iaslist
from . import Database
from ..record import recordmanager, load_record, Record

class LocalDatabase(Database):

    def __init__(self,
                 host: str,
                 format: str = 'json',
                 indent: Optional[int] = None):
        """
        Initializes a connection to a local database of JSON/XML records
        stored in a local directory.
        
        Parameters
        ----------
        host : str
            The host name (local directory path) for the database.
        format : str, optional
            The format that the model records are saved as.  Can be either
            JSON or XML.  Default value is JSON.
        indent : int or None, optional
            The indentation used when saving the records.  If None (default)
            then the saved records are compact.  Otherwise, the lines in the
            file will be indented by multiples of this value based on the
            model's element recursion.
        """
        # Make the path if needed
        host = Path(host)
        if not host.is_dir():
            host.mkdir(parents=True)

        # Get absolute path to host
        host = host.resolve()

        # Pass host to Database initializer
        Database.__init__(self, host)

        # Set default format and indent values
        self.__format = format
        self.__indent = indent

    @property
    def style(self) -> str:
        """str: The database style"""
        return 'local'

    @property
    def format(self) -> str:
        """str: The format that records are saved as: 'json' or 'xml'"""
        return self.__format

    @property
    def indent(self) -> Optional[int]:
        """int or None: The record indentation setting to use when saving records."""
        return self.__indent

    def cache(self,
              style: str,
              refresh: bool = False,
              addnew: bool = True) -> pd.DataFrame:
        """
        Loads/generates the metadata cache csv file for a given record style.

        Parameters
        ----------
        style : str 
            The record style to retrieve the metadata content for.
        refresh : bool, optional
            If True, then the metadata content will be rebuilt by loading every
            record of the given style.  If False (default), the stored metadata
            for records will be used rather than loading from the files.
        addnew : bool, optional
            If True (default), then the metadata for new records will be
            appended to the stored metadata cache.  If False, then the stored
            metadata is returned as is.

        Returns
        -------
        pandas.DataFrame
            The contents of the cache csv file.
        """
        recordmanager.assert_style(style)
        cachefile = Path(self.host, f'{style}.csv')

        if cachefile.is_file() and refresh is False:

            # Load cache file
            cache = pd.read_csv(cachefile)

            def interpret(series, key):
                """Safely convert dict, list and tuple elements from str"""
                try:
                    assert series[key][0] in '{[('
                    return ast.literal_eval(series[key])
                except:
                    return series[key]

            def toint(column):
                """Convert int columns as needed"""
                try:
                    assert column.dtype == float
                    newcolumn = column.astype(int)
                    assert np.allclose(column, newcolumn, atol=0.0)
                except:
                    return column
                else:
                    return newcolumn

            # Interpret int, dict and list elements
            if len(cache) > 0:
                cache = cache.apply(toint, axis=0)
                for key in cache.keys():
                    cache[key] = cache.apply(interpret, axis=1, args=[key])
            else:
                r = load_record(style)
                cache = pd.DataFrame(columns=r.metadatakeys)

        else:
            # Initialize new cache
            r = load_record(style)
            cache = pd.DataFrame(columns=r.metadatakeys)

        if addnew is True:

            # Compare names in the cache to file names in the directory
            cachenames = set(cache.name)
            filenames = set([fname.stem for fname in Path(self.host, style).glob(f'*.{self.format}')])
            newnames = filenames.difference(cachenames)
            deletednames = cachenames.difference(filenames)

            # Load new entries
            if len(newnames) > 0:
                newrecords = []
                for name in newnames:
                    fname = Path(self.host, style, f'{name}.{self.format}')
                    record = load_record(style, model=fname, name=name)
                    newrecords.append(record.metadata())
                newrecords = pd.DataFrame(newrecords)
                if not cache.empty:
                    cache = pd.concat([cache, newrecords], sort=False).sort_values('name')
                else:
                    cache = newrecords.sort_values('name')
                refresh = True

            # Delete missing entries
            if len(deletednames) > 0:
                cache = cache[~cache.name.isin(deletednames)]
                refresh = True

        # Refresh cache file
        if refresh:
            cache.to_csv(cachefile, index=False)

        return cache

    def get_records(self, 
                    style: Optional[str] = None,
                    return_df: bool = False,
                    refresh_cache: bool = False,
                    **kwargs) -> Union[list, Tuple[list, pd.DataFrame]]:
        """
        Produces a list of all matching records in the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to search.
        refresh_cache : bool, optional
            Indicates if the metadata cache file is to be refreshed.  If False,
            metadata for new records will be added but the old record metadata
            fields will not be updated.  If True, then the metadata for all
            records will be regenerated, which is needed to update the metadata
            for modified records.
        return_df : bool, optional
            If True, then the corresponding pandas.Dataframe of metadata
            will also be returned
        **kwargs : any, optional
            Any of the record-specific metadata keywords that can be searched
            for.

        Returns
        ------
        records : numpy.NDArray
            All records from the database matching the given parameters.
        records_df : pandas.DataFrame
            The corresponding metadata values for the records.  Only returned
            if return_df is True.
        """
        # Set default search parameters
        if style is None:
            style = self.select_record_style()

        # Get df
        df = self.get_records_df(style, refresh_cache=refresh_cache, **kwargs)

        # Load only the matching records
        records = []
        if len(df) > 0:
            for name in df.name:
                fname = Path(self.host, style, f'{name}.{self.format}')
                records.append(load_record(style, model=fname, database=self))

        records = np.array(records)

        if return_df:
            return records, df
        else:
            return records

    def get_records_df(self, 
                       style: Optional[str] = None,
                       refresh_cache: bool = False,
                       **kwargs) -> pd.DataFrame:
        """
        Produces a table of metadata for matching records in the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to limit the search by.
        refresh_cache : bool, optional
            Indicates if the metadata cache file is to be refreshed.  If False,
            metadata for new records will be added but the old record metadata
            fields will not be updated.  If True, then the metadata for all
            records will be regenerated, which is needed to update the metadata
            for modified records.
        **kwargs : any, optional
            Any of the record-specific metadata keywords that can be searched
            for.
        
        Returns
        ------
        records_df : pandas.DataFrame
            The corresponding metadata values for the records.
        """

        # Set default search parameters
        if style is None:
            style = self.select_record_style()

        if 'name' in kwargs and kwargs['name'] is not None:
            # Load named records
            cache = []
            for name in aslist(kwargs['name']):
                fname = Path(self.host, style, f'{name}.{self.format}')
                if fname.exists():
                    record = load_record(style, model=fname)
                    cache.append(record.metadata())

            # Build cache DataFrame
            if len(cache) == 0:
                # Initialize new cache
                r = load_record(style)
                cache = pd.DataFrame(columns=r.metadatakeys)
            else:
                cache = pd.DataFrame(cache)

        else:
            # Load cache file
            cache = self.cache(style, refresh=refresh_cache)

        # Filter based on the record's pandasfilter method
        mask = load_record(style).pandasfilter(cache, **kwargs)
        df = cache[mask].reset_index(drop=True)

        return df

    def get_record(self,
                   style: Optional[str] = None,
                   refresh_cache: bool = False,
                   **kwargs) -> Record:
        """
        Returns a single matching record from the database.
        
        Parameters
        ----------
        style : str, optional
            The record style to limit the search by.
        refresh_cache : bool, optional
            Indicates if the metadata cache file is to be refreshed.  If False,
            metadata for new records will be added but the old record metadata
            fields will not be updated.  If True, then the metadata for all
            records will be regenerated, which is needed to update the metadata
            for modified records.
        **kwargs : any, optional
            Any of the record-specific metadata keywords that can be searched
            for.
        
        Returns
        -------
        Record
            The single record from the database matching the given parameters.
        
        Raises
        ------
        ValueError
            If multiple or no matching records found.
        """

        if style is None:
            styles = recordmanager.loaded_style_names
        else:
            styles = aslist(style)

        # Get records
        records = []
        for style in styles:
            records.append(self.get_records(style, refresh_cache=refresh_cache, **kwargs))
        records = np.hstack(records)

        # Verify that there is only one matching record
        if len(records) == 1:
            return records[0]
        elif len(records) == 0:
            raise ValueError('No matching records found')
        else:
            raise ValueError('Multiple matching records found')

    def count_records(self,
                      style: Optional[str] = None,
                      **kwargs) -> int:
        """
        Retrieves a count of matching records from the database.  Fast if you
        only want the total number of records of a given style. 
        
        Parameters
        ----------
        style : str, optional
            The record style to search.
        **kwargs : any, optional
            Any of the record-specific metadata keywords that can be searched
            for, or other kwargs supported by get_records_df.  Note that if
            you give kwargs the method will be much slower as it is effectively
            calling len(get_records_df).
            
        Returns
        ------
        int
            The count of records in the database matching the given parameters.
        """
        # Set default search parameters
        if style is None:
            style = self.select_record_style()

        # Fast count of all records of a given style
        if len(kwargs) == 0:
            count = len([i for i in Path(self.host, style).glob(f'*.{self.format}')])

        # Use get_records_df for delimited searches    
        else:
            count = len(self.get_records_df(style, **kwargs))

        return count

    def add_record(self,
                   record: Optional[Record] = None,
                   style: Optional[str] = None,
                   name: Optional[str] = None,
                   model: Union[str, DM, None] = None,
                   build: bool = False,
                   verbose: bool = False) -> Record:
        """
        Adds a new record to the database.
        
        Parameters
        ----------
        record : Record, optional
            The new record to add to the database.  If not given, then name,
            style and model are required.
        style : str, optional
            The record style for the new record.  Required if record is not
            given.
        name : str, optional
            The name to assign to the new record.  Required if record is not
            given.
        model : str or DataModelDict, optional
            The model contents of the new record.  Required if record is not
            given.
        build : bool, optional
            If True, then the uploaded content will be (re)built based on the
            record's attributes.  If False (default), then record's existing
            content will be loaded if it exists, or built if it doesn't exist.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.

        Returns
        ------
        Record
            Either the given record or a record composed of the name, style,
            and model.
        
        Raises
        ------
        ValueError
            If style, name and/or model given with record, or a matching record
            already exists.
        """
        # Create Record object if not given
        if record is None:
            if style is None:
                style = self.find_record_style(name)
            record = load_record(style, model=model, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None or model is not None:
            raise ValueError('kwargs style, name, and model cannot be given with kwarg record')

        # Verify that there isn't already a record with a matching name
        style_dir = Path(self.host, record.style)
        fname = Path(style_dir, f'{record.name}.{self.format}')
        if fname.is_file():
            raise ValueError(f'Record {record.name} already exists')

        # Make record style directory if needed
        if not style_dir.is_dir():
            style_dir.mkdir()

        # Retrieve/build model contents
        try:
            assert build is False
            model = record.model
            assert model is not None
        except:
            model = record.build_model()

        # Save record
        with open(fname, 'w', encoding='UTF-8') as f:
            if self.format == 'json':
                model.json(fp=f, indent=self.indent, ensure_ascii=False)
            elif self.format == 'xml':
                model.xml(fp=f, indent=self.indent)

        if verbose:
            print(f'{record} added to {self.host}')

        return record

    def update_record(self,
                      record: Optional[Record] = None,
                      style: Optional[str] = None,
                      name: Optional[str] = None,
                      model: Union[str, DM, None] = None,
                      build: bool = False,
                      verbose: bool = False) -> Record:
        """
        Replaces an existing record with a new record of matching name and
        style, but new content.
        
        Parameters
        ----------
        record : Record, optional
            The record with new content to update in the database.  If not
            given, content is required along with name and/or style to
            uniquely define a record to update.
        style : str, optional
            The style of the record to update.
        name : str, optional
            The name to uniquely identify the record to update.
        model : str or DataModelDict, optional
            The model contents of the new record.  Required if record is not
            given.
        build : bool, optional
            If True, then the uploaded content will be (re)built based on the
            record's attributes.  If False (default), then record's existing
            content will be loaded if it exists, or built if it doesn't exist.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.

        Returns
        ------
        Record
            Either the given record or a record composed of the name, style,
            and content.
        
        Raises
        ------
        TypeError
            If no new content is given.
        ValueError
            If style and/or name content given with record.
        """
        # Create Record object if not given
        if record is None:
            if model is None:
                raise TypeError('no new model given')
            if style is None:
                style = self.find_record_style(name)

            record = load_record(style, model=model, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')

        # Replace content in record object
        elif model is not None:
            record = load_record(record.style, model=model, name=record.name)

        # Check if record already exists
        style_dir = Path(self.host, record.style)
        fname = Path(style_dir, f'{record.name}.{self.format}')
        if not fname.is_file():
            raise ValueError(f'No existing {record.style} record {record.name} found')

        # Retrieve/build model contents
        try:
            assert build is False
            model = record.model
            assert model is not None
        except:
            model = record.build_model()

        # Save record
        with open(fname, 'w', encoding='UTF-8') as f:
            if self.format == 'json':
                model.json(fp=f, indent=self.indent, ensure_ascii=False)
            elif self.format == 'xml':
                model.xml(fp=f, indent=self.indent)

        if verbose:
            print(f'{record} updated in {self.host}')

        return record

    def delete_record(self,
                      record: Optional[Record] = None,
                      style: Optional[str] = None,
                      name: Optional[str] = None,
                      verbose: bool = False):
        """
        Permanently deletes a record from the database.
        
        Parameters
        ----------
        record : Record, optional
            The record to delete from the database.  If not given, name and/or
            style are needed to uniquely define the record to delete.
        name : str, optional
            The name of the record to delete.
        style : str, optional
            The style of the record to delete.
        verbose : bool, optional
            If True, info messages will be printed during operations.  Default
            value is False.
            
        Raises
        ------
        ValueError
            If style and/or name given with record.
        """
        # Create Record object if not given
        if record is None:
            if style is None:
                style = self.find_record_style(name)
            record = load_record(style, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')

         # Delete record file
        fname = Path(self.host, record.style, f'{record.name}.{self.format}')
        if fname.is_file():
            fname.unlink()
        else:
            raise ValueError(f'No existing {record.style} record {record.name} found')

        if verbose:
            print(f'{record} deleted from {self.host}')

    def add_tar(self, 
                record: Optional[Record] = None,
                style: Optional[str] = None,
                name: Optional[str] = None,
                tar: Optional[bytes] = None,
                root_dir: Optional[Path] = None):
        """
        Archives and stores a folder associated with a record.
        
        Parameters
        ----------
        record : Record, optional
            The record to associate the tar archive with.  If not given, then
            name and/or style necessary to uniquely identify the record are
            needed.
        name : str, optional
            The name to use in uniquely identifying the record.
        style : str, optional
            The style to use in uniquely identifying the record.
        tar : bytes, optional
            The bytes content of a tar file to save.  tar cannot be given
            with root_dir.
        root_dir : str, optional
            Specifies the root directory for finding the directory to archive.
            The directory to archive is at <root_dir>/<name>.  (Default is to
            set root_dir to the current working directory.)  tar cannot be given
            with root_dir.
        
        Raises
        ------
        ValueError
            If style and/or name content given with record or the record already
            has a folder or a tar archive.
        """

        # Create Record object if not given
        if record is None:
            if style is None:
                style = self.find_record_style(name)
            record = load_record(style, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')

        # Verify that record exists
        style_dir = Path(self.host, record.style)
        fname = Path(style_dir, f'{record.name}.{self.format}')
        if not fname.is_file():
            raise ValueError(f'No existing {record.style} record {record.name} found')

        # Build path to record
        dir_path = Path(style_dir, record.name)
        tar_path = Path(style_dir, f'{record.name}.tar.gz')

        # Check if an archive or folder already exists
        if tar_path.exists():
            raise ValueError('Record already has an archive')
        elif dir_path.exists():
            raise ValueError('Record already has a folder')

        # Make archive
        if tar is None:
            if root_dir is None:
                root_dir = '.'
            target = Path(root_dir, record.name)

            tar = tarfile.open(tar_path, 'w:gz')
            tar.add(target, target.name)
            tar.close()

        elif root_dir is None:
            with open(tar_path, 'wb') as f:
                f.write(tar)
        else:
            raise ValueError('tar and root_dir cannot both be given')

    def get_tar(self,
                record: Optional[Record] = None,
                style: Optional[str] = None,
                name: Optional[str] = None,
                raw: bool = False) -> Union[tarfile.TarFile, bytes]:
        """
        Retrieves the tar archive associated with a record in the database.
        
        Parameters
        ----------
        record : Record, optional
            The record to retrieve the associated tar archive for.
        name : str, optional
            The name to use in uniquely identifying the record.
        style : str, optional
            The style to use in uniquely identifying the record.
        raw : bool, optional
            If True, return the archive as raw binary content. If 
            False, return as an open tarfile. (Default is False)
        
        Returns
        -------
        tarfile or bytes
            The tar archive as an open tarfile if raw=False, or as a binary str if
            raw=True.
        
        Raises
        ------
        ValueError
            If style and/or name content given with record.
        """

        # Build path to record from name (and style)
        if record is None:
            if style is None:
                style = self.find_record_style(name)
            record = load_record(style, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')

        # Build path to record
        tar_path = Path(self.host, record.style, record.name+'.tar.gz')
        if not tar_path.is_file():
            raise ValueError(f'No existing tar found for {record.style} record {record.name}')

        # Return content
        if raw is True:
            with open(tar_path, 'rb') as f:
                return f.read()
        else:
            tar = tarfile.open(tar_path)
            if record is not None:
                record.tar = tar
            return tar

    def delete_tar(self, 
                   record: Optional[Record] = None,
                   style: Optional[str] = None,
                   name: Optional[str] = None):
        """
        Deletes a tar file from the database.
        
        Parameters
        ----------
        record : Record, optional
            The record associated with the tar archive to delete.  If not
            given, then name and/or style necessary to uniquely identify
            the record are needed.
        name : str, optional
            The name to use in uniquely identifying the record.
        style : str, optional
            The style to use in uniquely identifying the record.
        
        Raises
        ------
        ValueError
            If style and/or name content given with record.
        """

        # Create Record object if not given
        if record is None:
            if style is None:
                style = self.find_record_style(name)
            record = load_record(style, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')

        # Build path to tar file
        tar_path = Path(self.host, record.style, record.name+'.tar.gz')

        # Delete record if it exists
        if tar_path.is_file():
            tar_path.unlink()

    def update_tar(self,
                   record: Optional[Record] = None,
                   style: Optional[str] = None,
                   name: Optional[str] = None,
                   tar: Optional[bytes] = None,
                   root_dir: Optional[Path] = None):
        """
        Replaces an existing tar archive for a record with a new one.
        
        Parameters
        ----------
        record : Record, optional
            The record to associate the tar archive with.  If not given, then 
            name and/or style necessary to uniquely identify the record are 
            needed.
        name : str, optional
            The name to use in uniquely identifying the record.
        style : str, optional
            The style to use in uniquely identifying the record.
        tar : bytes, optional
            The bytes content of a tar file to save.  tar cannot be given
            with root_dir.
        root_dir : str, optional
            Specifies the root directory for finding the directory to archive.
            The directory to archive is at <root_dir>/<name>.  (Default is to
            set root_dir to the current working directory.)  tar cannot be given
            with root_dir.
        """

        # Delete the existing tar archive stored in the database
        self.delete_tar(record=record, style=style, name=name)

        # Add the new tar archive
        self.add_tar(record=record, name=name, style=style, tar=tar,
                     root_dir=root_dir)

    def add_folder(self,
                   record: Optional[Record] = None,
                   style: Optional[str] = None,
                   name: Optional[str] = None,
                   filenames: Union[str, Path, list, None] = None,
                   root_dir: Optional[Path] = None):
        """
        Stores a folder associated with a record.
        
        Parameters
        ----------
        record : Record, optional
            The record to associate the folder with.  If not given, then
            name and/or style necessary to uniquely identify the record are
            needed.
        style : str, optional
            The style to use in uniquely identifying the record.
        name : str, optional
            The name to use in uniquely identifying the record.
        filenames : str or list, optional
            The paths to files that are to be added to the record's folder.
            Cannot be given with root_dir.
        root_dir : str, optional
            Specifies the root directory for finding the folder to add.
            The directory to add is at <root_dir>/<name>.  (Default is to
            set root_dir to the current working directory.)  Cannot be given
            with filenames.
        
        Raises
        ------
        ValueError
            If style and/or name content given with record or the record already
            has a folder or a tar archive.
        """

        # Create Record object if not given
        if record is None:
            if style is None:
                style = self.find_record_style(name)
            record = load_record(style, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')

        # Verify that record exists
        style_dir = Path(self.host, record.style)
        fname = Path(style_dir, f'{record.name}.{self.format}')
        if not fname.is_file():
            raise ValueError(f'No existing {record.style} record {record.name} found')

        # Build database paths
        dir_path = Path(style_dir, record.name)
        tar_path = Path(style_dir, f'{record.name}.tar.gz')

        # Check if an archive or folder already exists
        if tar_path.exists():
            raise ValueError('Record already has an archive')
        elif dir_path.exists():
            raise ValueError('Record already has a folder')

        # Copy folder
        if filenames is None:
            if root_dir is None:
                root_dir = '.'
            source = Path(root_dir, record.name)
            shutil.copytree(source, dir_path)

        # Copy files
        elif root_dir is None:
            dir_path.mkdir(parents=True)
            for filename in iaslist(filenames):
                shutil.copy2(filename, Path(dir_path, Path(filename).name))

        else:
            raise ValueError('filenames and root_dir cannot both be given')

    def get_folder(self,
                   record: Optional[Record] = None,
                   style: Optional[str] = None,
                   name: Optional[str] = None) -> Path:
        """
        Retrives the location of the folder associated with a record in the
        database. 
        
        Parameters
        ----------
        record : Record, optional
            The record to retrieve the associated folder location for.
        style : str, optional
            The style to use in uniquely identifying the record.
        name : str, optional
            The name to use in uniquely identifying the record.
        
        Returns
        -------
        pathlib.Path
            The path to the record's folder
        
        Raises
        ------
        ValueError
            If style and/or name content given with record.
        NotADirectoryError
            If the record's folder doesn't exist.
        """

        # Create Record object if not given
        if record is None:
            if style is None:
                style = self.find_record_style(name)
            record = load_record(style, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')

        # Build path to folder
        dir_path = Path(self.host, record.style, record.name)

        # Return path
        if dir_path.exists():
            return dir_path
        else:
            raise NotADirectoryError('No folder saved for the record')

    def delete_folder(self,
                      record: Optional[Record] = None,
                      style: Optional[str] = None,
                      name: Optional[str] = None):
        """
        Deletes a folder from the database.
        
        Parameters
        ----------
        record : Record, optional
            The record associated with the folder to delete.  If not
            given, then name and/or style necessary to uniquely identify
            the record are needed.
        style : str, optional
            The style to use in uniquely identifying the record.
        name : str, optional
            The name to use in uniquely identifying the record.
        
        Raises
        ------
        ValueError
            If style and/or name content given with record.
        """

        # Create Record object if not given
        if record is None:
            if style is None:
                style = self.find_record_style(name)
            record = load_record(style, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')

        # Build path to tar file
        dir_path = Path(self.host, record.style, record.name)

        # Delete record if it exists
        if dir_path.exists():
            shutil.rmtree(dir_path)

    def update_folder(self,
                      record: Optional[Record] = None,
                      style: Optional[str] = None,
                      name: Optional[str] = None,
                      filenames: Union[str, Path, list, None] = None,
                      root_dir: Optional[Path] = None,
                      clear: bool = True):
        """
        Updates an existing folder for a record.
        
        Parameters
        ----------
        record : Record, optional
            The record to associate the folder with.  If not given, then 
            name and/or style necessary to uniquely identify the record are 
            needed.
        style : str, optional
            The style to use in uniquely identifying the record.
        name : str, optional
            The name to use in uniquely identifying the record.
        filenames : str or list, optional
            The paths to files that are to be added to the record's folder.
            Cannot be given with root_dir.
        root_dir : str, optional
            Specifies the root directory for finding the folder to add.
            The directory to add is at <root_dir>/<name>.  (Default is to
            set root_dir to the current working directory.)  Cannot be given
            with filenames.
        clear : bool, optional
            If True (default), then the current folder contents will be deleted
            before the new contents are added.  If False, existing files may
            remain if the new content does not overwrite it.
        """
        # Check competing parameters
        if filenames is not None and root_dir is not None:
            raise ValueError('filenames and root_dir cannot both be given')

        # Create Record object if not given
        if record is None:
            if style is None:
                style = self.find_record_style(name)
            record = load_record(style, name=name)

        # Issue a ValueError for competing kwargs
        elif style is not None or name is not None:
            raise ValueError('kwargs style and name cannot be given with kwarg record')

        # Build database paths
        dir_path = Path(self.host, record.style, record.name)

        # Delete existing folder
        if clear is True:
            if dir_path.exists():
                shutil.rmtree(dir_path)

        # Copy folder
        if filenames is None:
            if root_dir is None:
                root_dir = '.'
            source = Path(root_dir, record.name)
            shutil.copytree(source, dir_path)

        # Copy files
        elif root_dir is None:
            dir_path.mkdir(parents=True)
            for filename in iaslist(filenames):
                shutil.copy2(filename, Path(dir_path, Path(filename).name))


    def find_record_style(self, name):
        """
        Uses path globs to search for a record by name to identify its style.

        Parameters
        ----------
        name : str
            The record name to search for.
        """
        # Glob search for record if style is unknown
        paths = [path for path in Path(self.host).glob(f'*/{name}.{self.format}')]
        if len(paths) == 0:
            raise ValueError(f'no existing record {name} found')
        elif len(paths) > 1:
            raise ValueError(f'multiple existing records called {name} found: style must be specified!')
        
        # Return style field
        return paths[0].parent.name