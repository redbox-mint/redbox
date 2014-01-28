/* 
 * The Fascinator - ReDBox
 * Copyright (C) 2011 University of Southern Queensland
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */
package com.googlecode.fascinator.redbox;

import com.googlecode.fascinator.api.PluginDescription;
import com.googlecode.fascinator.api.PluginException;
import com.googlecode.fascinator.api.authentication.AuthenticationException;
import com.googlecode.fascinator.api.authentication.User;
import com.googlecode.fascinator.api.indexer.Indexer;
import com.googlecode.fascinator.api.indexer.SearchRequest;
import com.googlecode.fascinator.api.storage.DigitalObject;
import com.googlecode.fascinator.api.storage.Storage;
import com.googlecode.fascinator.api.storage.StorageException;
import com.googlecode.fascinator.common.JsonSimple;
import com.googlecode.fascinator.portal.JsonSessionState;
import com.googlecode.fascinator.portal.services.PortalSecurityManager;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;

import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Wraps a storage plugin for secure access through the Solr index.
 *
 * @author Oliver Lucido
 */
public class SecureStorage implements Storage {

    private final static long DEFAULT_EXPIRY = 30000;
    private static Map<String, CacheEntry> accessCache = new HashMap<String, CacheEntry>();
    private Logger log = LoggerFactory.getLogger(SecureStorage.class);
    private Storage storage;
    private Indexer indexer;
    private PortalSecurityManager securityManager;
    private JsonSessionState state;
    private String username;
    private List<String> rolesList;

    public SecureStorage(Storage storage, Indexer indexer, PortalSecurityManager securityManager, JsonSessionState state) {
        this.storage = storage;
        this.indexer = indexer;
        this.securityManager = securityManager;
        this.state = state;
        setGuestAccess();
    }

    @Override
    public DigitalObject createObject(String oid) throws StorageException {
        // everyone can create objects
        return storage.createObject(oid);
    }

    @Override
    public DigitalObject getObject(String oid) throws StorageException {
        DigitalObject obj = storage.getObject(oid);
        if (isAccessAllowed(obj)) {
            return obj;
        }
        throw new StorageException("Access denied");
    }

    @Override
    public void removeObject(String oid) throws StorageException {
        DigitalObject tempObj = getObject(oid);
        log.debug("Closing temp object.");
        tempObj.close();
        log.debug("Temp object closed.");
        storage.removeObject(oid);
    }

    @Override
    public Set<String> getObjectIdList() {
        // TODO Filter list depending on access
        return storage.getObjectIdList();
    }

    @Override
    public String getId() {
        return storage.getId();
    }

    @Override
    public String getName() {
        return storage.getName() + " (secure)";
    }

    @Override
    public PluginDescription getPluginDetails() {
        return storage.getPluginDetails();
    }

    @Override
    public void init(File jsonFile) throws PluginException {
        storage.init(jsonFile);
    }

    @Override
    public void init(String jsonString) throws PluginException {
        storage.init(jsonString);
    }

    @Override
    public void shutdown() throws PluginException {
        storage.shutdown();
    }

    private void updateCredentials() {
        if (state.containsKey("username")) {
            username = state.get("username").toString();
            String source = state.containsKey("source") ? state.get("source").toString() : "system";
            try {
                User user = securityManager.getUser(state, username, source);
                rolesList = Arrays.asList(securityManager.getRolesList(state, user));
            } catch (AuthenticationException ae) {
                log.error("Failed to get user access, assuming guest access", ae);
                setGuestAccess();
            }
        } else {
            setGuestAccess();
        }
    }

    private void setGuestAccess() {
        username = "guest";
        rolesList = new ArrayList<String>();
        rolesList.add("guest");
    }

    /**
     * This calls the Solr indexer to check if the current user is allowed to
     * access the specified object. This access is based on the following rules:
     *
     * 1. If the object is indexed check the ownership and security
     *    filters against the current user.
     * 2. If the object is not indexed, check the storage directly since we
     *    may be waiting on a commit from a workflow for example, or the
     *    requested object is a harvest config or rules script.
     * 
     * @param oid an object identifier
     * @return true if access is allowed, false otherwise
     */
    private boolean isAccessAllowed(DigitalObject obj) throws StorageException {
        if (obj != null) {
            updateCredentials();
            String oid = obj.getId();
            try {
                // check the cache
                String key = oid + ":" + username;
                CacheEntry entry = accessCache.get(key);
                if (entry == null) {
                    entry = new CacheEntry();
                    accessCache.put(key, entry);
                } else {
                    long lastUpdated = entry.getLastUpdated();
                    long now = System.currentTimeMillis();
                    log.debug("Elapsed time: {}", now - lastUpdated);
                    if (now - lastUpdated > DEFAULT_EXPIRY) {
                        log.debug("Cache entry {} expired!", key);
                        entry = new CacheEntry();
                        accessCache.put(key, entry);
                    } else {
                        log.debug("Cached entry {}={}", key, entry.isAllowed());
                        return entry.isAllowed();
                    }
                }

                // check the index if the object exists (or is referenced)
                String query = "storage_id:" + oid;
                SearchRequest req = new SearchRequest(query);
                req.setParam("fl", "id");
                req.addParam("fq", "owner:\"" + username
                        + "\" OR security_filter:("
                        + StringUtils.join(rolesList, " OR ") + ")"
                        + " OR security_exception:(\"" + username + "\")");
                ByteArrayOutputStream out = new ByteArrayOutputStream();
                indexer.search(req, out);
                JsonSimple json = new JsonSimple(
                        new ByteArrayInputStream(out.toByteArray()));
                List<JsonSimple> docs = json.getJsonSimpleList(
                        "response", "docs");
                if (docs.isEmpty()) {
                    entry.setAllowed(false);
                    Properties props = obj.getMetadata();
                    props.store(out, "");
                    if (props.containsKey("fileHash")) {
                        // this is a harvest config or rules script
                        entry.setAllowed(true);
                    } else if (props.containsKey("owner")) {
                        // current user owns this object, most likely a new
                        // workflow object, or index has not completed yet
                        if (props.getProperty("owner").equals(username)) {
                            entry.setAllowed(true);
                        }
                    }
                    obj.close();
                } else {
                    // query returned result(s), allow access
                    entry.setAllowed(true);
                }
                return entry.isAllowed();
            } catch (StorageException se) {
                throw se;
            } catch (Exception e) {
                log.error("Failed to get access details", e);
            }
        }
        return false;
    }
}
