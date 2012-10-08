import csv
from AlertException import AlertException

class CSVAlertHandler(AlertHandler):
    """Processing method for a single CSV File.
    Each CSV file may contain multiple rows which should become ReDBox Collections
    
    """
    def __init__(self, file, config):
        AlertHandler.__init__(self, file, config)
        
        if not 'FieldMap' in config:
            raise AlertException("No FieldMap was provided for the CSVAlertHandler")
        else:
            self.fieldMap = config['FieldMap']
        
        self.headerRow = config.get("hasHeaderRow", true)    
        
        if 'DialectClass' in config:
            self.dialect = self.__getClass(config['DialectClass'])
        elif 'Dialect' in config:
            self.dialect = Dialect()
            for opt in config['Dialect']:
                pass

    
    def process(self):      
        ## Parse our CSV file
        with open(self.file, "rb") as f:
            try:
                reader = csv.DictReader(self.file, dialect=self.dialect)
                jsonList = []
                data = None
                for row in reader:
                    ## Process each row in turn
                    data = {}
                    for row in csvReader:
                        for col in self.fieldMap:
                            if not col in row:
                                raise AlertException("The requested field %s was not present in %s" % (col, self.file))
                            
                            if isinstance(self.fieldMap[col], list):
                                for el in self.fieldMap[col]:
                                    data[el] = self.fieldMap[col].strip()
                            else:
                                data[col] = self.fieldMap[col].strip()
    
                        json = JsonSimple(JsonObject(data))
                        jsonList.append(json)
            except:
                raise

        return jsonList
        
    
    def __getClass(self, c):
        '''Used to create an instance of a class from a string-based class name
        See http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
        '''
        parts = c.split('.')
        module = ".".join(parts[:-1])
        m = __import__( module )
        for comp in parts[1:]:
            m = getattr(m, comp)            
        return m
