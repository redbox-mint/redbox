/*
 * The Fascinator - Plugin - Transformer - MARC Author Records
 * Copyright (C) 2010 University of Southern Queensland
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
package au.edu.usq.fascinator.transformer.marc;

import java.io.File;
import java.io.IOException;
import java.util.Properties;

import org.apache.commons.codec.digest.DigestUtils;
import org.apache.commons.io.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import au.edu.usq.fascinator.HarvestClient;
import au.edu.usq.fascinator.api.PluginDescription;
import au.edu.usq.fascinator.api.PluginException;
import au.edu.usq.fascinator.api.PluginManager;
import au.edu.usq.fascinator.api.harvester.HarvesterException;
import au.edu.usq.fascinator.api.storage.DigitalObject;
import au.edu.usq.fascinator.api.storage.Payload;
import au.edu.usq.fascinator.api.storage.Storage;
import au.edu.usq.fascinator.api.storage.StorageException;
import au.edu.usq.fascinator.api.transformer.Transformer;
import au.edu.usq.fascinator.api.transformer.TransformerException;
import au.edu.usq.fascinator.common.JsonConfig;
import au.edu.usq.fascinator.common.JsonConfigHelper;
import au.edu.usq.fascinator.common.storage.StorageUtils;

/**
 * Creates author record objects.
 * 
 * @author Oliver Lucido
 */
public class MarcAuthorsTransformer implements Transformer {

    /** PID for metadata input payload **/
    private static String METADATA_PAYLOAD = "metadata.json";

    /** PID for harvest config payload **/
    private static String HARVEST_PAYLOAD = "harvest.json";

    /** Logging **/
    private static Logger log = LoggerFactory
            .getLogger(MarcAuthorsTransformer.class);

    /** Json config file **/
    private JsonConfigHelper config;

    /** Harvest client */
    private HarvestClient harvestClient;

    /** Storage layer */
    private Storage storage;

    /**
     * Constructor
     */
    public MarcAuthorsTransformer() {
    }

    /**
     * Init method from file
     * 
     * @param jsonFile
     * @throws IOException
     * @throws PluginException
     */
    @Override
    public void init(File jsonFile) throws PluginException {
        try {
            config = new JsonConfigHelper(jsonFile);
            reset();
        } catch (IOException e) {
            throw new PluginException("Error reading config: ", e);
        }
    }

    /**
     * Init method from String
     * 
     * @param jsonString
     * @throws IOException
     * @throws PluginException
     */
    @Override
    public void init(String jsonString) throws PluginException {
        try {
            config = new JsonConfigHelper(jsonString);
            reset();
        } catch (IOException e) {
            throw new PluginException("Error reading config: ", e);
        }
    }

    /**
     * Reset the transformer in preparation for a new object
     */
    private void reset() throws TransformerException {
        if (harvestClient == null) {
            try {
                harvestClient = new HarvestClient();
            } catch (HarvesterException he) {
                throw new TransformerException(he);
            }
        }
        if (storage == null) {
            try {
                JsonConfig sysConfig = new JsonConfig();
                String storageType = sysConfig.get("storage/type");
                storage = PluginManager.getStorage(storageType);
                storage.init(JsonConfig.getSystemFile());
            } catch (IOException ioe) {
            } catch (PluginException pe) {
                throw new TransformerException(pe);
            }
        }
    }

    /**
     * Transform method
     * 
     * @param object : DigitalObject to be transformed
     * @param jsonConfig : String containing configuration for this item
     * @return DigitalObject The object after being transformed
     * @throws TransformerException
     */
    @Override
    public DigitalObject transform(DigitalObject in, String jsonConfig)
            throws TransformerException {

        // Get the payload to transform
        Payload payload = null;
        try {
            payload = in.getPayload(METADATA_PAYLOAD);
            JsonConfigHelper json = new JsonConfigHelper(payload.open());
            String title = json.get("title");
            String author100 = json.get("author_100");
            if (author100 != null) {
                createAuthorRecord(in, title, author100);
            }
            String author700 = json.get("author_700");
            if (author700 != null) {
                createAuthorRecord(in, title, author700);
            }
        } catch (StorageException se) {
            log.error("No metadata found to transform.");
            return in;
        } catch (IOException ioe) {
            log.error("Failed to parse JSON metadata!", ioe);
        } finally {
            if (payload != null) {
                try {
                    payload.close();
                } catch (StorageException se) {
                    log.error("Failed to close the payload!", se);
                }
            }
        }

        return in;
    }

    private void createAuthorRecord(DigitalObject object, String title,
            String author) throws TransformerException {
        try {
            Properties objectMeta = object.getMetadata();

            // Generate OID using author name + title
            String fullTitle = author + " : " + title;
            String oid = DigestUtils.md5Hex(fullTitle);
            log.debug("Creating author record: {} ({})", fullTitle, oid);

            // Signal a reharvest on the author object to index them
            DigitalObject authorObj = StorageUtils.getDigitalObject(storage,
                    oid);

            // Add a harvesting config payload to the current object
            JsonConfigHelper harvestJson = new JsonConfigHelper();
            harvestJson.set("indexer/params/title", title);
            harvestJson.set("indexer/params/author", author);
            harvestJson.set("indexer/params/repository.name",
                    objectMeta.getProperty("repository.name"));
            harvestJson.set("indexer/params/repository.type",
                    objectMeta.getProperty("repository.type"));
            //log.debug(harvestJson.toString());
            StorageUtils.createOrUpdatePayload(authorObj, HARVEST_PAYLOAD,
                    IOUtils.toInputStream(harvestJson.toString(), "UTF-8"));

            Properties authorObjMeta = authorObj.getMetadata();
            for (Object keyObject : objectMeta.keySet()) {
                String key = keyObject.toString();
                String value = objectMeta.getProperty(key);
                authorObjMeta.setProperty(key, value);
            }
            authorObjMeta.setProperty("jsonConfigOid", oid);
            authorObjMeta.setProperty("jsonConfigPid", HARVEST_PAYLOAD); // doesn't get used...
            authorObjMeta.setProperty("title", title);
            authorObjMeta.setProperty("author", author);
            authorObjMeta.setProperty("recordType", "marc-author");

            authorObj.close();

            harvestClient.reharvest(oid);
        } catch (Exception e) {
            throw new TransformerException(e);
        }
    }

    /**
     * Get Transformer ID
     * 
     * @return id
     */
    @Override
    public String getId() {
        return "marc-authors";
    }

    /**
     * Get Transformer Name
     * 
     * @return name
     */
    @Override
    public String getName() {
        return "MARC Author Records Transformer";
    }

    /**
     * Gets a PluginDescription object relating to this plugin.
     * 
     * @return a PluginDescription
     */
    @Override
    public PluginDescription getPluginDetails() {
        return new PluginDescription(this);
    }

    /**
     * Shut down the transformer plugin
     */
    @Override
    public void shutdown() throws PluginException {
        if (storage != null) {
            storage.shutdown();
        }
        if (harvestClient != null) {
            harvestClient.shutdown();
        }
    }
}
