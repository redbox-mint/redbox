from java import util
#http://www.ibm.com/developerworks/java/tutorials/j-jython2/section7.html
#class Mapper:
def mapMapFromJava (map):
    """ Convert a Map to a Dictionary. """
    result = {}
    iter = map.keySet().iterator()
    while iter.hasNext():
        key = iter.next()
        result[mapFromJava(key)] = mapFromJava(map.get(key))
    return result

def mapCollectionFromJava (coll):
    """ Convert a Collection to a List. """
    result = []
    iter = coll.iterator();
    while iter.hasNext():
        result.append(mapFromJava(iter.next()))
    return result

def mapFromJava (object):
    """ Convert a Java type to a Jython type. """
    if object is None: return object
    if   isinstance(object, util.Map):        
        result = mapMapFromJava(object)
    elif isinstance(object, util.Collection): 
        result = mapCollectionFromJava(object)
    else:                                     
        result = object
    return result