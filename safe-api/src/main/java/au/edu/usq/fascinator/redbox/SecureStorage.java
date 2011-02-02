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
package au.edu.usq.fascinator.redbox;

import au.edu.usq.fascinator.api.PluginDescription;
import au.edu.usq.fascinator.api.PluginException;
import au.edu.usq.fascinator.api.authentication.User;
import au.edu.usq.fascinator.api.indexer.Indexer;
import au.edu.usq.fascinator.api.indexer.SearchRequest;
import au.edu.usq.fascinator.api.storage.DigitalObject;
import au.edu.usq.fascinator.api.storage.Storage;
import au.edu.usq.fascinator.api.storage.StorageException;
import au.edu.usq.fascinator.common.JsonConfigHelper;
import au.edu.usq.fascinator.portal.JsonSessionState;
import au.edu.usq.fascinator.portal.services.PortalSecurityManager;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.apache.commons.lang.StringUtils;

/**
 * Wraps a storage plugin for secure access through the Solr index.
 *
 * @author Oliver Lucido
 */
public class SecureStorage implements Storage {

    private Logger log = LoggerFactory.getLogger(SecureStorage.class);
    private Storage storage;
    private Indexer indexer;
    private PortalSecurityManager securityManager;
    private JsonSessionState state;
    private static Map<String, CacheEntry> accessCache = new HashMap<String, CacheEntry>();

    public SecureStorage(Storage storage, Indexer indexer, PortalSecurityManager securityManager, JsonSessionState state) {
        this.storage = storage;
        this.indexer = indexer;
        this.securityManager = securityManager;
        this.state = state;
    }

    @Override
    public DigitalObject createObject(String oid) throws StorageException {
        return storage.createObject(oid);
    }

    @Override
    public DigitalObject getObject(String oid) throws StorageException {
        if (isAccessAllowed(oid)) {
            return storage.getObject(oid);
        }
        throw new StorageException("Access denied");
    }

    @Override
    public void removeObject(String oid) throws StorageException {
        storage.removeObject(oid);
    }

    @Override
    public Set<String> getObjectIdList() {
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

    private boolean isAccessAllowed(String oid) {
        try {
            if (state.containsKey("username")) {
                String username = state.get("username").toString();
                //log.debug("username: {}", username);
                String key = oid + ":" + username;
                CacheEntry entry = accessCache.get(key);
                if (entry == null) {
                    entry = new CacheEntry();
                    accessCache.put(key, entry);
                } else {
                    long lastUpdated = entry.getLastUpdated();
                    long now = System.currentTimeMillis();
                    if (now - lastUpdated > 300000L) {
                        // 5 minute cache expiry
                        log.debug("Cache entry {} expired!", key);
                        entry = new CacheEntry();
                    } else {
                        // use cached value
                        log.debug("Cached entry {}={}", key, entry.isAllowed());
                        return entry.isAllowed();
                    }
                }
                User user = securityManager.getUser(state, username, "storage");
                String[] rolesList = securityManager.getRolesList(state, user);
                log.debug("roles: {}", rolesList);
                String query = "storage_id:" + oid;
                SearchRequest req = new SearchRequest(query);
                req.setParam("fq", "owner:" + username);
                req.addParam("fq", "security_filter:(" + StringUtils.join(rolesList, " OR ") + ")");
                ByteArrayOutputStream out = new ByteArrayOutputStream();
                indexer.search(req, out);
                JsonConfigHelper json = new JsonConfigHelper(new ByteArrayInputStream(out.toByteArray()));
                List<JsonConfigHelper> docs = json.getJsonList("response/docs");
                entry.setAllowed(!docs.isEmpty());
                return entry.isAllowed();
            }
        } catch (Exception e) {
            log.error("Failed to get access details", e);
        }
        return false;
    }
}
