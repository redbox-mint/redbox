import csv
from csv import Dialect
from AlertException import AlertException
from AlertHandler import AlertHandler
from com.googlecode.fascinator.common import JsonSimple

class LocalDialect(Dialect):
    def __init__(self, opts):  
        self.delimiter = ','
        self.quotechar = '"'
        self.escapechar = None
        self.doublequote = True
        self.skipinitialspace = False
        self.lineterminator = '\r\n'
        self.quoting = csv.QUOTE_MINIMAL

        for opt in opts:
            if hasattr(Dialect, opt):
                if type(opts[opt]) == type(bool()):
                    setattr(self, opt, opts[opt])
                else:
                    setattr(self, opt, str(opts[opt]))
                    
        Dialect.__init__(self)
    

class CSVAlertHandler(AlertHandler):
    """Processing method for a single CSV File.
    Each CSV file may contain multiple rows which should become individual ReDBox Collections
    """
    
    def __init__(self, file, config, baseline):
        AlertHandler.__init__(self, file, config, baseline)
        
        if not 'fieldMap' in config:
            raise AlertException("No FieldMap was provided for the CSVAlertHandler")
        else:
            self.fieldMap = config['fieldMap']
        
        #self.headerRow = True  
        
        self.dialect = "local"
        if 'DialectClass' in config:
            self.dialect = config['DialectClass']
        elif 'Dialect' in config:
            csv.register_dialect("local", LocalDialect(config['Dialect']))
        else:
            csv.register_dialect("local", LocalDialect({}))

        self.multiValue = False
        self.multiValueFields = None
        self.multiValueDelimiter = ";"
        
        if "multiValue" in config:
            if "fields" in config["multiValue"]:
                self.multiValueFields = config["multiValue"]["fields"]
                for field in self.multiValueFields:
                    if field not in self.fieldMap:
                        raise AlertException("The requested multiValue field [%s] was not provided in the FieldMap." % field)
            else:
                raise AlertException("The multiValue option must contain a fields key.")
            if "fieldDelimiter" in config["multiValue"]:
                self.multiValueDelimiter = config["multiValue"]["fieldDelimiter"]
            else:
                raise AlertException("The multiValue option must contain a fieldDelimiter key.")
            
            self.multiValue = True
    
    def process(self):      
        '''Parse our CSV file
        
        Return a list of JsonSimple instances
        '''
        f = None
        reader = None
        try:
            f = open(self.file, "rb")
            reader = csv.DictReader(f, dialect=self.dialect)

            if reader is None:
                raise AlertException("The requested file [%s] didn't return values" % self.file)
            
            jsonList = []
            data = None
            for row in reader:
                data = {}
                print row
                for col in self.fieldMap:
                    if col not in row:
                        raise AlertException("The requested field [%s] was not present in [%s]" % (col, self.file))
                    
                    if self.multiValue and col in self.multiValueFields:
                        val = row[col].strip()
                        values = val.split(self.multiValueDelimiter)
                        i = 1
                        for value in values:
                            #List fields look like dc:subject.vivo:keyword.0.rdf:PlainLiteral
                            #Plus the config may provide a list of target keys
                            tmpkey = self.fieldMap[col]
                            if type(tmpkey) is list:
                                for k in tmpkey:
                                    key = k.replace(".0.", ".%s." % i)
                                    data[key] = value.strip()
                            else:
                                key = tmpkey.replace(".0.", ".%s." % i)
                                data[key] = value.strip()
                            i += 1
                    else:
                        key = self.fieldMap[col]
                        if type(key) is list:
                            for k in key:
                                data[k] = row[col].strip()
                        else:
                            data[key] = row[col].strip()
                    
                objdict = self.getNewJsonObjectDict(data)
                json = JsonSimple(objdict)
                jsonList.append(json)
        except:
            raise
        finally:
            if f is not None:
                f.close()

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
