from builtins import zip
from builtins import str
from builtins import range
from desc.sims.GCRCatSimInterface import DESCQAObject

__all__ = ["CompoundDESCQAObject"]


class CompoundDESCQAObject(DESCQAObject):
    """
    This is a class for taking several DESCQAObject daughter classes that
    query the same catalog for the same rows (but different
    columns), and combining their queries into one.

    You feed the constructor a list of DESCQAObject daughter classes.  The
    CompoundDESCQAObject verifies that they all do, indeed, query the same
    catalog.  It then constructs its own self.columns member (note
    that CompoundDESCQAObject is a daughter class of DESQAObject) which
    combines all of the requested data.

    When you call query_columns, a recarray will be returned as in a DESCQAObject.
    Note, however, that the names of the columns of the recarray will be modified.
    If the first DESCQAObject class in the list of DESCQAObject classes passed to the
    constructor asks for a column named 'col1', that will be mapped to 'catName_col1'
    where 'catName' is the DESCQAObject's objid member.  'col2' will be mapped to
    'catName_col2', etc.  In cases where the DESCQAObject does not change the name
    of the column, the column will also be returned by its original, un-mangled name.
    """

    def __init__(self, descqaObjectClassList):
        """
        @param [in] descqaObjectClassList is a list of DESCQAObject
        daughter classes (not instantiations of those classes; the classes
        themselves) that all query the same catalog

        Note: this is a list of classes, not a list of instantiations of those
        classes.  The connection to the catalog is established as soon as
        you instantiate a DESCQAObject daughter class.  To avoid creating
        unnecessary connections, CompoundDESCQAObject will
        read in classes without an active connection and establish its
        own connection in this constructor.  This means that all connection
        parameters must be specified in the class definitions of the classes
        passed into descqaObjectClassList.
        """

        self._descqaObjectClassList = descqaObjectClassList
        self._validate_input()
        self.objectTypeId = 119

        self.columnMap = dict()
        for dbc in self._descqaObjectClassList:
            sub_cat_name = dbc.objid
            dbo = dbc()
            for col_name in dbo.columnMap:
                self.columnMap[sub_cat_name+'_'+col_name] = dbo.columnMap[col_name]

        dbo = self._descqaObjectClassList[0]()
        # need to instantiate the first one because sometimes
        # idColKey is not defined until instantiation
        # (see GalaxyTileObj in sims_catUtils/../baseCatalogModels/GalaxyModels.py)

        self.idColKey = dbo.idColKey
        self.yaml_file_name = dbo.yaml_file_name
        self._cat_cache_suffix = dbo._cat_cache_suffix

        super(CompoundDESCQAObject, self).__init__()

    def _make_column_map(self):
        pass

    def _validate_input(self):
        """
        Verify that the DESCQAObjects passed to the constructor
        do, indeed, query the same table of the same catalog.
        """

        dbc0 = self._descqaObjectClassList[0]
        for dbc in self._descqaObjectClassList:
            if (dbc.yaml_file_name != dbc0.yaml_file_name or
                dbc._cat_cache_suffix != dbc0._cat_cache_suffix):

                raise RuntimeError("Not all DESCQAObject classes "
                                   "passed to CompoundDESCQAObject "
                                   "reference the same catalog")
