/*
 * The Fascinator - Callista Harvester Plugin
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
package au.edu.usq.fascinator.harvester.callista;

import au.edu.usq.fascinator.api.harvester.HarvesterException;
import au.edu.usq.fascinator.api.storage.DigitalObject;
import au.edu.usq.fascinator.api.storage.Payload;
import au.edu.usq.fascinator.api.storage.StorageException;
import au.edu.usq.fascinator.common.JsonConfigHelper;
import au.edu.usq.fascinator.common.harvester.impl.GenericHarvester;

import com.Ostermiller.util.CSVParser;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.StringReader;
import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;

import org.apache.commons.codec.digest.DigestUtils;
import org.apache.commons.lang.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 *
 * @author Greg Pendlebury
 */
public class CallistaHarvester extends GenericHarvester {

    /** Package payload */
    private static String PACKAGE_PAYLOAD = "authority.tfpackage";

    /** Workflow payload */
    private static String WORKFLOW_PAYLOAD = "workflow.metadata";

    /** logging */
    private Logger log = LoggerFactory.getLogger(CallistaHarvester.class);

    /** whether or not there are more files to harvest */
    private boolean hasMore;

    /** Data file */
    private File csvData;

    /** Data structure to hold parsed data */
    private Map<String, List<String[]>> parsedData;

    /** Debugging limit */
    private int limit;

    /**
     * File System Harvester Constructor
     */
    public CallistaHarvester() {
        super("callista", "Callista Harvester");
    }

    /**
     * Initialisation of harvester plugin
     *
     * @throws HarvesterException if fails to initialise
     */
    @Override
    public void init() throws HarvesterException {
        JsonConfigHelper config;

        // Read config
        try {
            config = new JsonConfigHelper(getJsonConfig().toString());
        } catch (IOException ex) {
            throw new HarvesterException("Failed reading configuration", ex);
        }

        String filePath = config.get("harvester/callista/fileLocation");
        if (filePath == null) {
            throw new HarvesterException("No Callista data file provided!");
        }

        String limitString = config.get("harvester/callista/limit", "-1");
        limit = Integer.parseInt(limitString);

        csvData = new File(filePath);
        if (csvData == null || !csvData.exists()) {
            throw new HarvesterException(
                    "Could not find Callista data file: '" + filePath + "'");
        }

        parsedData = new HashMap();

        hasMore = false;
    }

    /**
     * Shutdown the plugin
     *
     * @throws HarvesterException is there are errors
     */
    @Override
    public void shutdown() throws HarvesterException {
    }

    /**
     * Harvest the next set of files, and return their Object IDs
     *
     * @return Set<String> The set of object IDs just harvested
     * @throws HarvesterException is there are errors
     */
    @Override
    public Set<String> getObjectIdList() throws HarvesterException {
        Set<String> fileObjectIdList = new HashSet<String>();

        // Data streams - get CSV data
        FileInputStream fstream;
        try {
            fstream = new FileInputStream(csvData);
        } catch (FileNotFoundException ex) {
            // We tested for this earlier
            throw new HarvesterException("Could not find file", ex);
        }
        DataInputStream in = new DataInputStream(fstream);
        BufferedReader br = new BufferedReader(new InputStreamReader(in));

        int i = 0;
        int j = 0;
        boolean stop = false;
        // Line by line from buffered reader
        String line;
        try {
            while ((line = br.readLine()) != null && !stop) {
                // Parse the CSV for this line
                String[][] values;
                try {
                    values = CSVParser.parse(new StringReader(line));
                } catch (IOException ex) {
                    log.error("Error parsing CSV file", ex);
                    throw new HarvesterException("Error parsing CSV file", ex);
                }

                for (String[] columns : values) {
                    // Ignore the header row
                    if (columns[0].equals("RESEARCHER_ID")) {
                        for (String column : columns) {
                            // Print if debugging
                            //log.debug("HEADING {}: '{}'", j, column);
                            j++;
                        }
                        j = 0;

                    // Store normal data rows
                    } else {
                        i++;
                        if (i % 500 == 0) {
                            log.info("Parsing row {}", i);
                        }
                        String rId = columns[0];
                        if (!parsedData.containsKey(rId)) {
                            // New researcher, add an empty list
                            parsedData.put(rId, new ArrayList());
                        }
                        parsedData.get(rId).add(columns);
                    }
                }

                // Check our record limit if debugging
                if (limit != -1 && i >= limit) {
                    stop = true;
                    log.debug("Stopping at debugging limit");
                }
            }
            in.close();
        } catch (IOException ex) {
            log.error("Error reading from CSV file", ex);
            throw new HarvesterException("Error reading from CSV file", ex);
        }
        log.info("Parse complete: {} rows", i);

        // Process parsed data
        i = 0;
        for (String key : parsedData.keySet()) {
            // Create the new record
            JsonConfigHelper json = new JsonConfigHelper();
            JsonConfigHelper packageJson = new JsonConfigHelper();
            packageJson.set("viewId", "default");
            packageJson.set("packageType", "name-authority");
            json.set("id", key);
            json.set("step", "pending");

            List<JsonConfigHelper> authors = new ArrayList();
            for (String[] columns : parsedData.get(key)) {
                try {
                    // IDS
                    store("studentId", columns[1], json);
                    store("employeeId", columns[2], json);
                    // Preferred Name exists
                    String pName = null;
                    if (columns[5] != null && !columns[5].equals("")) {
                        pName = columns[3] + " " + columns[5] + " " +
                                columns[7];
                    }
                    store("preferedName", pName, json);
                    // Full name
                    String fName = null;
                    if (columns[6] != null) {
                        // We have a middle name
                        fName = columns[3] + " " + columns[4] + " " + columns[6]
                                + " " + columns[7];
                    } else {
                        fName = columns[3] + " " + columns[4] + " " +
                                columns[7];
                    }
                    store("fullName", fName, json);
                    store("title", fName, json);
                    store("description", "Authority record for '" +
                            fName + "'", json);
                    packageJson.set("title", fName);
                    packageJson.set("description", "Authority record for '" +
                            fName + "'");
                    // Email
                    store("email", columns[8], json);

                    // Author data used in publication
                    JsonConfigHelper auth = new JsonConfigHelper();
                    auth.set("author", columns[9]);
                    auth.set("orgUnitId", columns[11]);
                    auth.set("orgUnit", columns[12]);
                    auth.set("expiry", columns[13]);
                    authors.add(auth);

                // Catch any data mismatches during storage
                } catch(Exception ex) {
                    log.error("Error parsing record '{}'", key, ex);
                }
            }

            // Add author data
            if (!authors.isEmpty()) {
                // TODO: Work-around for #656
                json.set("authors", "===REPLACE=ME===");
                String list = "[" + StringUtils.join(authors, ",") + "]";
                String jsonString = json.toString();
                jsonString = jsonString.replace("\"===REPLACE=ME===\"", list);
                try {
                    json = new JsonConfigHelper(jsonString);
                } catch (IOException ex) {
                    json = null;
                    log.error("Error parsing json '{}': ", jsonString);
                }
            }

            // Add an empty package manifest
            // TODO: Work-around for #656
            packageJson.set("manifest", "===REPLACE=ME===");
            String jsonString = packageJson.toString();
            jsonString = jsonString.replace("\"===REPLACE=ME===\"", "{}");
            try {
                packageJson = new JsonConfigHelper(jsonString);
            } catch (IOException ex) {
                packageJson = null;
                log.error("Error parsing json '{}': ", jsonString);
            }

            i++;
            if (i % 500 == 0) {
                log.info("Object count: {}", i);
            }
            if (json != null && packageJson != null) {
                try {
                    String oid = storeJson(
                            json.toString(), packageJson.toString(), key);
                    fileObjectIdList.add(oid);
                } catch (StorageException ex) {
                    log.error("Error during storage: ", ex);
                }
            }
        }
        log.info("Object creation complete: {} objects", i);

        return fileObjectIdList;
    }

    private String storeJson(String workflowData, String packageData,
            String recordId) throws HarvesterException, StorageException {
        String oid = DigestUtils.md5Hex(recordId);
        DigitalObject object = null;

        // Check if the object is already in storage
        boolean inStorage = true;
        try {
            object = getStorage().getObject(oid);
        } catch (StorageException ex) {
            inStorage = false;
        }

        // New items
        if (!inStorage) {
            try {
                object = getStorage().createObject(oid);
            } catch (StorageException ex) {
                throw new HarvesterException("Error creating new object: ", ex);
            }
            storePayload(object, PACKAGE_PAYLOAD, getStream(packageData));
            storePayload(object, WORKFLOW_PAYLOAD, getStream(workflowData));

        // Update an existing item
        } else {
            updateOrCreate(PACKAGE_PAYLOAD, object, packageData);
            updateOrCreate(WORKFLOW_PAYLOAD, object, workflowData);
        }

        // Update object metadata
        Properties props = object.getMetadata();
        props.setProperty("render-pending", "true");
        object.close();

        return object.getId();
    }

    /**
     * Update a payload in the object, or create if it doesn't exist
     *
     * @param pid The Payload id to update/create
     * @param object The object to hold the payload
     * @param data The data to store
     * @throws HarvesterException If unable to do update or create payload
     */
    private void updateOrCreate(String pid, DigitalObject object,
            String data) throws HarvesterException {
        try {
            // Confirm it exists
            object.getPayload(pid);
            object.updatePayload(pid, getStream(data));
        } catch (StorageException ex) {
            log.error("Existing object '{}' has no payload '{}', adding",
                    object.getId(), pid);
            storePayload(object, pid, getStream(data));
        }
    }

    /**
     * Turn the String into an inputstream
     *
     * @param data The data to read
     * @return InputStream of the data
     */
    private InputStream getStream(String data) {
        try {
            return new ByteArrayInputStream(data.getBytes("utf-8"));
        } catch (UnsupportedEncodingException ex) {
            log.error("Error parsing metadata, invalid UTF-8");
            return null;
        }
    }

    /**
     * Simple wrapper for storing strings in json to avoid excessive null
     * testing. Duplicate testing is performed to ensure only like values
     * exist in the data stream and no mismatches exist.
     *
     * @param field : Field name to use
     * @param value : Data to store, possibly null
     * @param json : The JSON object to store in
     * @return boolean : <code>true</code> the value is appropriate for storage,
     * <code>false</code> if there is a clash
     */
    private void store(String field, String value, JsonConfigHelper json)
            throws Exception {
        if (value != null) {
            String existing = json.get("formData/" + field);
            if (existing != null) {
                if (existing.equals(value)) {
                    // Match is good
                } else {
                    // Data mismatch, we have two or more different values
                    // in a field that should be the same.
                    throw new Exception("Duplicate in field '" + field +"'!");
                }
            } else {
                // First time we've seen this field
                json.set("formData/" + field, value);
            }
        }
    }

    /**
     * Check if there are more objects to harvest
     *
     * @return <code>true</code> if there are more, <code>false</code> otherwise
     */
    @Override
    public boolean hasMoreObjects() {
        return hasMore;
    }

    /**
     * Delete cached references to files which no longer exist and return the
     * set of IDs to delete from the system.
     *
     * @return Set<String> The set of object IDs deleted
     * @throws HarvesterException is there are errors
     */
    @Override
    public Set<String> getDeletedObjectIdList() throws HarvesterException {
        return new HashSet<String>();
    }

    /**
     * Check if there are more objects to delete
     *
     * @return <code>true</code> if there are more, <code>false</code> otherwise
     */
    @Override
    public boolean hasMoreDeletedObjects() {
        return false;
    }

    /**
     * Store an inputstream as a payload for the given object.
     *
     * @param object The object to store the payload in
     * @param pid The payload ID to use when storing
     * @param in The inputstream to store data from
     * @return Payload The resulting payload stored
     * @throws HarvesterException on storage errors
     */
    private Payload storePayload(DigitalObject object, String pid,
            InputStream in) throws HarvesterException {
        try {
            return object.createStoredPayload(pid, in);
        } catch (StorageException ex) {
            throw new HarvesterException("Error storing payload: ", ex);
        }
    }
}
