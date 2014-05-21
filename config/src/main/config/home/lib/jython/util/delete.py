'''
This is a script to delete a record out of storage and solr
'''
from java.lang import Exception

def delete(oid, vc):
    delete(oid, vc['Services'].getStorage(), vc['Services'].getIndexer(), vc['log'])


def delete(oid, storage, indexer,log):

    # delete from storage
    try:
    	errors = False
        storage.removeObject(oid)
    except Exception, e:
        log.error('Error deleting object from storage: ', e)
        errors = True

	# Delete from Solr
    try:
        indexer.remove(oid)
    except Exception, e:
        log.error('Error deleting Solr entry: ', e)
        errors = True

    # Delete annotations
    try:
        indexer.annotateRemove(oid)
    except Exception, e:
        log.error('Error deleting annotations: ', e)
        errors = True

    # Solr commit
    try:
        indexer.commit()
    except Exception, e:
        log.error('Error during Solr commit: ', e)
        errors = True

    if errors:
        # log error return false
         return False
    else:
         return True



			