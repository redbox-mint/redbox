/*
 * ReDBox - VITAL Subscriber
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
import au.edu.usq.fascinator.api.PluginManager;
import au.edu.usq.fascinator.api.indexer.Indexer;
import au.edu.usq.fascinator.api.indexer.SearchRequest;
import au.edu.usq.fascinator.api.storage.DigitalObject;
import au.edu.usq.fascinator.api.storage.Payload;
import au.edu.usq.fascinator.api.storage.Storage;
import au.edu.usq.fascinator.api.storage.StorageException;
import au.edu.usq.fascinator.api.subscriber.Subscriber;
import au.edu.usq.fascinator.api.subscriber.SubscriberException;
import au.edu.usq.fascinator.common.JsonConfig;
import au.edu.usq.fascinator.common.JsonConfigHelper;
import au.edu.usq.fascinator.common.JsonObject;
import au.edu.usq.fascinator.common.JsonSimple;
import au.edu.usq.fascinator.common.MessagingServices;
import au.edu.usq.fascinator.common.solr.SolrDoc;
import au.edu.usq.fascinator.common.solr.SolrResult;

import fedora.client.FedoraClient;
import fedora.server.management.FedoraAPIM;
import fedora.server.types.gen.Datastream;
import fedora.server.types.gen.DatastreamDef;
import fedora.server.types.gen.UserInfo;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.Closeable;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.io.StringWriter;

import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.jms.JMSException;

import org.apache.commons.io.IOUtils;
import org.apache.commons.lang.StringUtils;
import org.json.simple.JSONArray;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A subscriber to notify VITAL of completed objects in ReDBox.
 *
 * @author Greg Pendlebury
 */

public class VitalSubscriber implements Subscriber {

    private static String DEFAULT_EMAIL_SUBJECT = "VITAL Subscriber error";
    private static String DEFAULT_EMAIL_TEMPLATE =
            "VITAL Subscriber error: [[MESSAGE]]\n\n====\n\n[[ERROR]]";
    private static String DEFAULT_VITAL_MESSAGE =
            "Datastream update from ReDBox '[[OID]]' => '[[PID]]'";
    private static String VITAL_PROPERTY_KEY = "vitalPid";

    /** Logging */
    private final Logger log = LoggerFactory
            .getLogger(VitalSubscriber.class);

    /** Messaging */
    private MessagingServices messaging;
    private String emailQueue;
    private List<String> emailAddresses;
    private String emailSubject;
    private String emailTemplate;

    /** Fascinator plugins */
    private Storage storage;
    private Indexer indexer;

    /** Fedora */
    private String fedoraUrl;
    private String fedoraUsername;
    private String fedoraPassword;
    private String fedoraNamespace;
    // Template for log entries
    private String fedoraMessageTemplate;
    private int fedoraTimeout;

    /** Valid instantiation */
    boolean valid = false;

    /** VITAL integration config */
    private Map<String, JsonConfigHelper> pids;
    private String attachDs;
    private String attachStatusField;
    private Map<String, String> attachStatuses;
    private String attachLabelField;
    private Map<String, String> attachLabels;
    private String attachControlGroup;
    private boolean attachVersionable;
    private boolean attachRetainIds;
    private Map<String, List<String>> attachAltIds;
    private File foxmlTemplate;

    /** Temp directory */
    private File tmpDir;

    /**
     * Gets an identifier for this type of plugin. This should be a simple name
     * such as "file-system" for a storage plugin, for example.
     *
     * @return the plugin type id
     */
    @Override
    public String getId() {
        return "vital";
    }

    /**
     * Gets a name for this plugin. This should be a descriptive name.
     *
     * @return the plugin name
     */
    @Override
    public String getName() {
        return "VITAL Subscriber";
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
     * Initializes the plugin using the specified JSON String
     *
     * @param jsonString JSON configuration string
     * @throws SubscriberException if there was an error in initialization
     */
    @Override
    public void init(String jsonString) throws SubscriberException {
        try {
            setConfig(new JsonConfigHelper(jsonString));
        } catch (IOException e) {
            throw new SubscriberException(e);
        }
    }

    /**
     * Initializes the plugin using the specified JSON configuration
     *
     * @param jsonFile JSON configuration file
     * @throws SubscriberException if there was an error in initialization
     */
    @Override
    public void init(File jsonFile) throws SubscriberException {
        try {
            setConfig(new JsonConfigHelper(jsonFile));
        } catch (IOException ioe) {
            throw new SubscriberException(ioe);
        }
    }

    /**
     * Initialization of plugin
     *
     * @param config The configuration to use
     * @throws SubscriberException if fails to initialize
     */
    private void setConfig(JsonConfigHelper config) throws SubscriberException {
        // Test our Fedora connection... things are kind of useless without it
        fedoraUrl = config.get("subscriber/vital/server/url");
        fedoraNamespace = config.get("subscriber/vital/server/namespace");
        fedoraUsername = config.get("subscriber/vital/server/username");
        fedoraPassword = config.get("subscriber/vital/server/password");
        String timeout = config.get("subscriber/vital/server/timeout", "15");
        fedoraTimeout = Integer.parseInt(timeout);
        if (fedoraUrl == null || fedoraNamespace == null ||
                fedoraUsername == null || fedoraPassword == null) {
            throw new SubscriberException("VITAL Subscriber:" +
                    " Valid fedora configuration is mising!");
        }
        // This will throw the SubscriberException for
        //  us if there's something wrong
        fedoraConnect(true);
        fedoraMessageTemplate = config.get("subscriber/vital/server/message",
                DEFAULT_VITAL_MESSAGE);

        // Temp space
        boolean success = false;
        String tempPath = config.get("subscriber/vital/tempDir",
                System.getProperty("java.io.tmpdir"));
        if (tempPath != null) {
            tmpDir = new File(tempPath);

            // Make sure it exists
            if (!tmpDir.exists()) {
                success = tmpDir.mkdirs();
            // And it's a directory
            } else {
                success = tmpDir.isDirectory();
            }
            // Now make sure it's writable
            if (success) {
                File file = new File(tmpDir, "creation.test");
                try {
                    file.createNewFile();
                    file.delete();
                    success = !file.exists();
                } catch (IOException ex) {
                    success = false;
                }

            }
        }
        if (tmpDir == null || !success) {
            throw new SubscriberException("VITAL Subscriber:" +
                    " Cannot find a valid (and writable) TEMP directory!");
        }

        // Get the list of pids we are sending to VITAL
        pids = config.getJsonMap("subscriber/vital/dataStreams");
        if (pids == null || pids.isEmpty()) {
            throw new SubscriberException("VITAL Subscriber:" +
                    " No datastreams configured to export!");
        }
        // And attachment handling
        String path = "subscriber/vital/attachments/";
        attachDs = config.get(path + "dsID", "ATTACHMENT%02d");
        Pattern p = Pattern.compile("%\\d*d");
        Matcher m = p.matcher(attachDs);
        if (!m.find()) {
            throw new SubscriberException("VITAL Subscriber: " +
                    "'*/attachments/dsId' must have a format placeholder for " +
                    "incrementing integer, eg. '%d' or '%02d'. The value " +
                    "provided ('" + attachDs + "') is invalid");
        }
        attachStatusField = config.get(path + "statusField");
        attachStatuses = getStringMap(config, path + "status");
        attachLabelField = config.get(path + "labelField");
        attachLabels = getStringMap(config, path + "label");
        attachControlGroup = config.get(path + "controlGroup");
        String versionable = config.get(path + "versionable");
        attachVersionable = Boolean.parseBoolean(versionable);
        String retainIds = config.get(path + "retainIds", "true");
        attachRetainIds = Boolean.parseBoolean(retainIds);
        // To make life easier we're going to use the new JSON Library here
        attachAltIds = new LinkedHashMap();
        JsonSimple json;
        try {
            json = new JsonSimple(config.toString());
        } catch (IOException ex) {
            throw new SubscriberException("VITAL Subscriber:" +
                    " Error parsing attachment JSON", ex);
        }
        // Use the base object for iteration
        JsonObject objAltIds = json.getObject(
                "subscriber", "vital", "attachments", "altIds");
        // And the library for access methods
        JsonSimple altIds = new JsonSimple(objAltIds);
        for (Object oKey : objAltIds.keySet()) {
            String key = (String) oKey;
            List<String> ids = altIds.getStringList(key);
            if (ids.isEmpty()) {
                log.warn("WARNING: '{}' has no altIds configured.", key);
            } else {
                attachAltIds.put(key, ids);
            }
        }
        // Make sure 'default' exists, even if empty
        if (!attachAltIds.containsKey("default")) {
            attachAltIds.put("default", new ArrayList());
        }

        // Are we sending emails on errors?
        emailQueue = config.get("subscriber/vital/failure/emailQueue");
        if (emailQueue != null) {
            List<Object> emails = config.getList(
                    "subscriber/vital/failure/emailAddress");
            emailAddresses = new ArrayList();
            for (Object email : emails) {
                if (email instanceof String) {
                    emailAddresses.add((String) email);
                }
            }
            if (emailQueue != null) {
                emailSubject = config.get(
                        "subscriber/vital/failure/emailSubject",
                        DEFAULT_EMAIL_SUBJECT);
                emailTemplate = config.get(
                        "subscriber/vital/failure/emailTemplate",
                        DEFAULT_EMAIL_TEMPLATE);
            } else {
                log.error("No email address provided!" +
                        " Reverting to errors using log files");
                emailQueue = null;
            }
        } else {
            log.warn("No email queue provided. Errors will only be logged");
        }

        // Ensure we have access to messaging services
        if (emailQueue != null) {
            try {
                messaging = MessagingServices.getInstance();
            } catch (JMSException ex) {
                throw new SubscriberException("VITAL Subscriber:" +
                        " Error starting Messaging Services", ex);
            }
        }

        // Need our config file to instantiate plugins
        File sysFile = null;
        try {
            sysFile = JsonConfig.getSystemFile();
        } catch (IOException ioe) {
            log.error("Failed to read configuration: {}", ioe.getMessage());
            throw new SubscriberException("VITAL Subscriber:" +
                    " Failed to read configuration", ioe);
        }

        // Start our storage layer
        try {
            storage = PluginManager.getStorage(
                    config.get("storage/type", "file-system"));
            storage.init(sysFile);
        } catch (PluginException pe) {
            log.error("Failed to initialise plugin: {}", pe.getMessage());
            throw new SubscriberException("VITAL Subscriber:" +
                    " Failed to initialise storage", pe);
        }

        // Instantiate an indexer for searching
        try {
            indexer = PluginManager.getIndexer(
                    config.get("indexer/type", "solr"));
            indexer.init(sysFile);
        } catch (PluginException pe) {
            log.error("Failed to initialise plugin: {}", pe.getMessage());
            throw new SubscriberException("VITAL Subscriber:" +
                    " Failed to initialise indexer", pe);
        }

        // Do we have a template?
        String templatePath = config.get("vital/foxmlTemplate");
        if (templatePath != null) {
            foxmlTemplate = new File(templatePath);
            if (!foxmlTemplate.exists()) {
                foxmlTemplate = null;
                throw new SubscriberException("VITAL Subscriber:" +
                        " The new object template provided does not exist: '" +
                        templatePath + "'");
            }
        }

        valid = true;
    }

    /**
     * Trivial wrapper on the JsonConfigHelper getMap() method to cast all map
     * entries to strings if appropriate and return.
     *
     * @param json : The json object to query.
     * @param path : The path on which the map is found.
     * @return Map<String, String>: The object map cast to Strings
     */
    private Map<String, String> getStringMap(JsonConfigHelper json,
            String path) {
        Map<String, String> response = new HashMap();
        Map<String, Object> objects = json.getMap(path);
        for (String key : objects.keySet()) {
            Object value = objects.get(key);
            if (value instanceof String) {
                response.put(key, (String) value);
            }
        }
        return response;
    }

    /**
     * Establish a connection to Fedora's management API (API-M) to confirm
     * credentials, then return the instantiated fedora client used to connect.
     *
     * @param firstConnection : If this is the first connection (ie. from the
     * Constructor), set this flag. Some logging will occur, and a basic API
     * call will be triggered to test genuine connectivity with regards to the
     * network and the credentials supplied.
     * @return FedoraClient : The client used to connect to the API
     * @throws SubscriberException if there was an error
     */
    private FedoraClient fedoraConnect() throws SubscriberException {
        return fedoraConnect(false);
    }
    private FedoraClient fedoraConnect(boolean firstConnection)
            throws SubscriberException {
        FedoraClient fedora = null;
        try {
            // Connect to the server
            fedora = new FedoraClient(fedoraUrl, fedoraUsername, fedoraPassword);
            fedora.SOCKET_TIMEOUT_SECONDS = fedoraTimeout;
            if (firstConnection) {
                log.info("Connected to FEDORA : '{}'", fedoraUrl);
            }
            // Make sure we can get the server version
            String version = fedora.getServerVersion();
            if (firstConnection) {
                log.info("FEDORA version: '{}'", version);
            }
            // And that we have appropriate access to the management API
            FedoraAPIM apim = fedora.getAPIM();
            if (firstConnection) {
                log.info("API-M access testing... {} second timeout",
                        fedoraTimeout);
                UserInfo user = apim.describeUser(fedoraUsername);
                log.info("API-M access confirmed: User '{}', ID: '{}'",
                        fedoraUsername, user.getId());
            }
        } catch (MalformedURLException ex) {
            throw new SubscriberException("VITAL Subscriber:" +
                    " Server URL is Invalid (?) : ", ex);
        } catch (IOException ex) {
            throw new SubscriberException("VITAL Subscriber:" +
                    " Error connecting to VITAL! : ", ex);
        } catch (Exception ex) {
            throw new SubscriberException("VITAL Subscriber:" +
                    " Error accesing management API! : ", ex);
        }
        return fedora;
    }

    /**
     * Shuts down the plugin
     *
     * @throws SubscriberException if there was an error during shutdown
     */
    @Override
    public void shutdown() throws SubscriberException {
        if (storage != null) {
            try {
                storage.shutdown();
            } catch (PluginException pe) {
                log.error("Failed to shutdown storage: {}", pe.getMessage());
                throw new SubscriberException("VITAL Subscriber:" +
                        " Failed to shutdown storage", pe);
            }
        }
        if (indexer != null) {
            try {
                indexer.shutdown();
            } catch (PluginException pe) {
                log.error("Failed to shutdown indexer: {}", pe.getMessage());
                throw new SubscriberException("VITAL Subscriber:" +
                        " Failed to shutdown indexer", pe);
            }
        }
    }

    /**
     * Method to fire for incoming events
     *
     * @param param : Map of key/value pairs to add to the index
     * @throws SubscriberException if there was an error
     */
    @Override
    public void onEvent(Map<String, String> param) throws SubscriberException {
        if (!valid) {
            error("VITAL Subscriber: Instantiation did not complete.");
        }

        // We only want workflow events
        String context = param.get("context");
        if (context == null || !context.equals("Workflow")) {
            return;
        }

        // What type of event is it?
        String type = param.get("eventType");
        if (type == null) {
            return;
        }

        // ReIndex events need special attention,
        // check if we have to send VITAL an update
        if (type.equals("ReIndex")) {
            process(param);
            return;
        }

        // If it's a new workflow step, we
        // are looking for the last step
        if (type.startsWith("NewStep")) {
            String[] parts = StringUtils.split(type, " : ");
            if (parts.length != 2) {
                error("Invalid event type received, expected " +
                        "'NewStep : {step}', received: '" + type + "'!");
            }
            String step = parts[1];
            if (step.equals("live")) {
                process(param);
                return;
            }
        }
    }

    /**
     * Top level wrapping method for a processing an object.
     *
     * This method first performs all the basic checks whether
     * this Object is technically ready to go to VITAL
     * (no matter what the workflow says).
     *
     * @param param : Map of key/value pairs to add to the index
     */
    private void process(Map<String, String> param) {
        // What object is this about?
        String oid = param.get("oid");
        if (oid == null) {
            error("No Object Identifier received with message!");
        }

        // Get the object
        DigitalObject object;
        try {
            object = storage.getObject(oid);
        } catch (StorageException ex) {
            error("Error whilst accessing Object in storage!\nOID: '"
                    + oid + "'", ex);
            return;
        }

        // Workflow payload
        JsonConfigHelper workflow;
        try {
            Payload workflowPayload = object.getPayload("workflow.metadata");
            workflow = new JsonConfigHelper(workflowPayload.open());
            workflowPayload.close();
        } catch (StorageException ex) {
            error("Error accessing workflow data from Object!\nOID: '"
                    + oid + "'", ex);
            return;
        } catch (IOException ex) {
            error("Error parsing workflow data from Object!\nOID: '"
                    + oid + "'", ex);
            return;
        }

        // And for reindex calls... make sure it's live
        String type = param.get("eventType");
        if (type.equals("ReIndex")) {
            String step = workflow.get("step");
            if (step == null || !step.equals("live")) {
                // This is a 'quiet' fail, it's just not live
                return;
            }
        }

        // Make sure we have a title
        String title = workflow.get("formData/title");
        if (title == null) {
            error("No title provided in Object form data!\nOID: '" +
                    object.getId() + "'");
            return;
        }

        // Object metadata
        Properties metadata;
        try {
            metadata = object.getMetadata();
        } catch (StorageException ex) {
            error("Error reading Object metadata!\nOID: '" + oid + "'", ex);
            return;
        }

        // Now that we have all the data we need, go do the real work
        processObject(object, workflow, metadata);
    }

    /**
     * Middle level wrapping method for processing objects. Now we are looking
     * at what actually needs to be done. Has the object already been put in
     * VITAL, or is it new.
     *
     * @param object : The Object in question
     * @param workflow : The workflow data for the object
     * @param metadata : The Object's metadata
     */
    private void processObject(DigitalObject object, JsonConfigHelper workflow,
            Properties metadata) {
        String oid = object.getId();
        String title = workflow.get("formData/title");
        FedoraClient fedora;

        try {
            fedora = fedoraConnect();
        } catch (SubscriberException ex) {
            error("Error connecting to VITAL", ex, oid, title);
            return;
        }

        // Find out if we've sent it to VITAL before
        String vitalPid = metadata.getProperty(VITAL_PROPERTY_KEY);
        if (vitalPid != null) {
            log.debug("Existing VITAL object: '{}'", vitalPid);
            // Make sure it exists, we'll test the DC datastream
            if (!datastreamExists(fedora, vitalPid, "DC")) {
                // How did this happen? Better let someone know
                String message = " !!! WARNING !!! The expected VITAL object '"
                        + vitalPid + "' was not found. A new object will be" +
                        " created instead!";
                error(message, null, oid, title);
                vitalPid = null;
            }
        }

        // A new VITAL object
        if (vitalPid == null) {
            try {
                vitalPid = createNewObject(fedora, object.getId());
                log.debug("New VITAL object created: '{}'", vitalPid);
                metadata.setProperty(VITAL_PROPERTY_KEY, vitalPid);
                // Trigger a save on the object's metadata
                object.close();
            } catch (Exception ex) {
                error("Failed to create object in VITAL", ex, oid, title);
                return;
            }
        }

        // Submit all the payloads to VITAL now
        try {
            processDatastreams(fedora, object, vitalPid);
        } catch (Exception ex) {
            error("Failed to send object to VITAL", ex, oid, title);
            return;
        }
    }

    /**
     * Create a new VITAL object and return the PID.
     *
     * @param fedora : An instantiated fedora client
     * @param oid : The ID of the ReDBox object we will store here. For logging
     * @return String : The new VITAL PID that was just created
     */
    private String createNewObject(FedoraClient fedora, String oid)
            throws Exception {
        InputStream in = null;
        byte[] template = null;
        if (foxmlTemplate != null) {
            // We have a user provided template
            in = new FileInputStream(foxmlTemplate);
            template = IOUtils.toByteArray(in);
            in.close();
        } else {
            // Use the built in template
            in = getClass().getResourceAsStream("/foxml_template.xml");
            template = IOUtils.toByteArray(in);
            in.close();
        }
        String vitalPid = fedora.getAPIM().ingest(template, "foxml1.0",
                "ReDBox creating new object: '" + oid + "'");
        log.info("New VITAL PID: '{}'", vitalPid);
        return vitalPid;
    }

    /**
     * Method responsible for arranging submissions to VITAL to
     * store our datastreams.
     *
     * @param fedora : An instantiated fedora client
     * @param object : The Object to submit
     * @param vitalPid : The VITAL PID to use
     * @throws Exception on any errors
     */
    private void processDatastreams(FedoraClient fedora, DigitalObject object,
            String vitalPid) throws Exception {
        int sent = 0;

        // Each payload we care about needs to be sent
        for (String ourPid : pids.keySet()) {
            // Fascinator packages have unpredictable names,
            //  so we just use the extension
            // eg. 'e6e174fe-3508-4c8a-8530-1d6bb644d10a.tfpackage'
            String realPid = ourPid;
            if (ourPid.equals(".tfpackage")) {
                realPid = getPackagePid(object);
                if (realPid == null) {
                    String message = partialUploadErrorMessage(
                            ourPid, sent, pids.size(), vitalPid);
                    throw new Exception(message +
                            "\n\nPackage not found.");
                }
            }
            log.info("Processing PID to send to VITAL: '{}'", ourPid);

            // Get our configuration
            JsonConfigHelper thisPid = pids.get(ourPid);
            String dsId = thisPid.get("dsID", realPid);
            String label = thisPid.get("label", dsId);
            String status = thisPid.get("status", "A");
            String controlGroup = thisPid.get("controlGroup", "X");
            String strVersionable = thisPid.get("versionable", "true");
            boolean versionable = Boolean.parseBoolean(strVersionable);
            String strRetainIds = thisPid.get("retainIds", "true");
            boolean retainIds = Boolean.parseBoolean(strRetainIds);
            String[] altIds = {};
            if (retainIds && datastreamExists(fedora, vitalPid, dsId)) {
                altIds = getAltIds(fedora, vitalPid, dsId);
                for (String altId : altIds) {
                    log.debug("Retaining alt ID: '{}' => {}'", dsId, altId);
                }
            }

            // MIME Type
            Payload payload = null;
            String mimeType = null;
            try {
                payload = object.getPayload(realPid);
            } catch (StorageException ex) {
                String message = partialUploadErrorMessage(
                        realPid, sent, pids.size(), vitalPid);
                throw new Exception(message + "\n\nError accessing payload '" +
                        realPid + "' : ", ex);
            }
            mimeType = payload.getContentType();
            // Default to binary data
            if (mimeType == null) {
                mimeType = "application/octet-stream";
            }

            try {
                sendToVital(fedora, object, realPid, vitalPid, dsId, altIds,
                        label, mimeType, controlGroup, status, versionable);
            } catch (Exception ex) {
                String message = partialUploadErrorMessage(
                        realPid, sent, pids.size(), vitalPid);
                throw new Exception(message, ex);
            }

            // Increase our counter
            sent++;
        } // End for loop

        // Datastreams are taken care of, now handle attachments
        try {
            processAttachments(fedora, object, vitalPid);
        } catch (Exception ex) {
            throw new Exception("Error processing attachments: ", ex);
        }
    }

    /**
     * Similar to sendToVital(), but this method is specifically looking for
     * attachments distributed throughout the system.
     *
     * @param fedora : An instantiated fedora client
     * @param object : The Object to submit
     * @param vitalPid : The VITAL PID to use
     * @throws Exception on any errors
     */
    private void processAttachments(FedoraClient fedora, DigitalObject object,
            String vitalPid) throws Exception {
        ByteArrayOutputStream out = null;
        ByteArrayInputStream in = null;
        SolrResult result;

        // Search for attachments to this object
        String oid = object.getId();
        SearchRequest req = new SearchRequest("attached_to:\"" + oid + "\"");
        req.setParam("rows", "1000");

        // Get our search results
        try {
            out = new ByteArrayOutputStream();
            indexer.search(req, out);
            in = new ByteArrayInputStream(out.toByteArray());
            result = new SolrResult(in);
        } catch (Exception ex) {
            throw new Exception("Error searching for attachments : ", ex);
        } finally {
            close(out);
            close(in);
        }

        // Make sure there were even results
        if (result.getNumFound() == 0) {
            log.info("No attachments found for '{}'", oid);
            return;
        }

        // Do a *first* pre-pass establishing which IDs to use
        Map<String, Map<String, String>> idMap = new HashMap();
        List<String> usedIds = new ArrayList();
        for (SolrDoc item : result.getResults()) {
            // Has it been to VITAL before?
            String aOid = item.getFirst("id");
            DigitalObject attachment = storage.getObject(aOid);
            Properties metadata = attachment.getMetadata();
            String vitalDsId = metadata.getProperty("vitalDsId");
            String vitalOrder = metadata.getProperty("vitalOrder");

            // Record what we know
            Map<String, String> map = new HashMap();
            if (vitalDsId != null) {
                map.put("hasId", "true");
                map.put("vitalDsId", vitalDsId);
                map.put("vitalOrder", vitalOrder);
                usedIds.add(vitalDsId);
            } else {
                map.put("hasId", "false");
            }
            idMap.put(aOid, map);
        }

        // Another pass, now that we know all the used IDs
        int dsIdSuffix = 1;
        for (SolrDoc item : result.getResults()) {
            String aOid = item.getFirst("id");
            boolean hasId = Boolean.parseBoolean(idMap.get(aOid).get("hasId"));
            // This record needs a new ID
            if (!hasId) {
                String newId = String.format(attachDs, dsIdSuffix);
                // Make sure it's not in use already
                       // either by us
                while (usedIds.contains(newId) ||
                       // or by VITAL
                        datastreamExists(fedora, vitalPid, newId))
                {
                    dsIdSuffix++;
                    newId = String.format(attachDs, dsIdSuffix);
                }
                // 'Use' it
                idMap.get(aOid).put("vitalDsId", newId);
                idMap.get(aOid).put("vitalOrder", String.valueOf(dsIdSuffix));
                usedIds.add(newId);
                dsIdSuffix++;
            }
        }

        // Now, the real work. Loop through each attachment
        for (SolrDoc item : result.getResults()) {
            String aOid = item.getFirst("id");
            log.info("Processing Attachment: '{}'", aOid);

            // Get the object from storage
            DigitalObject attachment = storage.getObject(aOid);

            // Find our workflow/form data
            Payload wfPayload = attachment.getPayload("workflow.metadata");
            JsonConfigHelper workflow = null;
            try {
                workflow = new JsonConfigHelper(wfPayload.open());
            } catch (Exception ex) {
                throw ex;
            } finally {
                wfPayload.close();
            }

            // Find our payload
            String pid = workflow.get("formData/filename",
                    attachment.getSourceId());
            log.info(" === Attachment PID: '{}'", pid);
            Payload payload = attachment.getPayload(pid);

            // MIME Type - Default to binary data
            String mimeType = payload.getContentType();
            if (mimeType == null) {
                mimeType = "application/octet-stream";
            }

            // Get our VITAL config
            String dsId = idMap.get(aOid).get("vitalDsId");
            String vitalOrder = idMap.get(aOid).get("vitalOrder");
            String label = dsId; // Default
            String labelData = workflow.get("formData/" + attachLabelField);
            if (attachLabels.containsKey(labelData)) {
                // We found a real value
                label = attachLabels.get(labelData);
            }
            String status = "A"; // Default
            String statusData = workflow.get("formData/" + attachStatusField);
            if (attachStatuses.containsKey(statusData)) {
                // We found a real value
                status = attachStatuses.get(statusData);
            }
            // Check for Alt IDs that already exist... if configured to
            String[] altIds = {};
            if (attachRetainIds && datastreamExists(fedora, vitalPid, dsId)) {
                altIds = getAltIds(fedora, vitalPid, dsId);
                for (String altId : altIds) {
                    log.debug("Retaining alt ID: '{}' => {}'", dsId, altId);
                }
            }
            altIds = resolveAltIds(altIds, mimeType,
                    Integer.valueOf(vitalOrder));

            try {
                sendToVital(fedora, attachment, pid, vitalPid, dsId, altIds,
                      label, mimeType, attachControlGroup, status,
                      attachVersionable);
            } catch (Exception ex) {
                // Throw error
                throw new Exception("Error uploading attachment '" +
                        aOid + "' : ", ex);
            }

            // The submission was successful, store the dsId if not already
            boolean hasId = Boolean.parseBoolean(idMap.get(aOid).get("hasId"));
            if (!hasId) {
                Properties metadata = attachment.getMetadata();
                metadata.setProperty("vitalDsId", dsId);
                metadata.setProperty("vitalOrder", vitalOrder);
                attachment.close();
            }
        } // End for loop
    }

    /**
     * For the given digital object, find the Fascinator package inside.
     *
     * @param object : The object with a package
     * @return String : The payload ID of the package, NULL if not found
     * @throws Exception if any errors occur
     */
    private String getPackagePid(DigitalObject object) throws Exception {
        for (String pid : object.getPayloadIdList()) {
            if (pid.endsWith(".tfpackage")) {
                return pid;
            }
        }
        return null;
    }

    /**
     * For the given mime type, ensure that the array of alternate identifiers
     * is correct. If identifiers are missing they will be added to the array.
     *
     * @param oldArray : The old array of identifiers
     * @param mimeType : The mime type of the datastream
     * @param count : The attachment count, to use in the format call
     * @return String[] : An array containing all of the old IDs with any that
     * were missing for the mime type
     */
    private String[] resolveAltIds(String[] oldArray, String mimeType,
            int count) {
        // First, find the valid list we want
        String key = null;
        for (String mimeTest : attachAltIds.keySet()) {
            // Ignore 'default'
            if (mimeTest.equals("default")) {
                continue;
            }
            // Is it a broad group?
            if (mimeTest.endsWith("/")) {
                if (mimeType.startsWith(mimeTest)) {
                    key = mimeTest;
                }
            // Or a specific mime type?
            } else {
                if (mimeType.equals(mimeTest)) {
                    key = mimeTest;
                }
            }
        }
        // Use default if not found
        if (key == null) {
            key = "default";
        }
        // Loop through the ids we're going to use
        for (String newId : attachAltIds.get(key)) {
            // If there is a format requirement, use it
            String formatted = String.format(newId, count);
            // Modify our arrray (if we it's not there)
            oldArray = growArray(oldArray, formatted);
        }
        return oldArray;
    }

    /**
     * Check the array for the new element, and if not found, generate a new
     * array containing all of the old elements plus the new.
     *
     * @param oldArray : The old array of data
     * @param newElement : The new element we want
     * @return String[] : An array containing all of the old data
     */
    private String[] growArray(String[] oldArray, String newElement) {
        // Look for the element first
        for (String element : oldArray) {
            if (element.equals(newElement)) {
                // If it's already there, we're done
                return oldArray;
            }
        }
        log.debug("Adding ID: '{}'", newElement);

        // Ok, we know we need a new array
        int length = oldArray.length + 1;
        String[] newArray = new String[length];
        // Copy the old array contents
        System.arraycopy(oldArray, 0, newArray, 0, oldArray.length);
        // And the new element, and return
        newArray[length - 1] = newElement;
        return newArray;
    }

    /**
     * Take care of the actual transmission to VITAL. This method will select
     * the appropriate transmission method based on:
     *
     *  1) If VITAL has already seen the datastream before
     *  2) If the data is XML or not
     *
     * @param fedora : The fedora client to use in transmission
     * @param ourObject : The DigitalObject in storage
     * @param ourPid : The payload in the object to send
     * @param vitalPid : The object in fedora we are targeting
     * @param dsId : The datastream ID in fedora to create or overwrite
     * @param label : The label to use
     * @param mimeType : The mime type of the content we are sending
     * @param controlGroup : The control group value to use if the object is new
     * @param status : The status to use in fedora if the object is new
     * @throws Exception if any errors occur
     */
    private void sendToVital(FedoraClient fedora, DigitalObject ourObject,
            String ourPid, String vitalPid, String dsId, String[] altIds,
            String label, String mimeType, String controlGroup, String status,
            boolean versionable) throws Exception {
        // We might need to cleanup a file upload if things go wrong
        File tempFile = null;
        String tempURI = null;

        try {
            // Find out if it has been sent before
            if (datastreamExists(fedora, vitalPid, dsId)) {
                log.info("Updating existing datastream: '{}'", dsId);
                log.debug("LABEL: '" + label + "', STATUS: '" + status +
                        "', GROUP: '" + controlGroup + "'");

    /**********************************
     * 1) Submission to overwrite EXISTING datastreams in VITAL
     * 2) Can only be used for XML uploads
     */
                if (mimeType.equals("text/xml")) {
                    // Updates on inline XML must be by value
                    byte[] data = getBytes(ourObject, ourPid);
                    // Modify the existing datastream
                    fedora.getAPIM().modifyDatastreamByValue(
                        vitalPid,          // Object PID in VITAL
                        dsId,              // The dsID we have configured
                        altIds,            // Alt IDs... not using
                        label,             // Label
                        mimeType,          // MIME type
                        null,              // Format URI
                        data,              // Our XML data
                        null,              // ChecksumType
                        null,              // Checksum
                        fedoraLogEntry(ourObject, ourPid), // Log message
                        true);             // Force update

    /**********************************
     * 1) Submission to overwrite EXISTING datastreams in VITAL
     * 2) Must be performed by reference if not XML
     */
                } else {
                    // Get our data
                    try {
                        tempFile = getTempFile(ourObject, ourPid);
                    } catch (Exception ex) {
                        throw new Exception("Error caching file to disk '" +
                                ourObject.getId() + "' : ", ex);
                    }

                    // Upload out data first
                    tempURI = fedora.uploadFile(tempFile);

                    // Modify the existing datastream
                    fedora.getAPIM().modifyDatastreamByReference(
                        vitalPid,          // Object PID in VITAL
                        dsId,              // The dsID we have configured
                        altIds,            // Alt IDs... not using
                        label,             // Label
                        mimeType,          // MIME type
                        null,              // Format URI
                        tempURI,           // Datastream Location
                        null,              // ChecksumType
                        null,              // Checksum
                        fedoraLogEntry(ourObject, ourPid), // Log message
                        true);             // Force update
                }

    /**********************************
     * 1) Submission for NEW datastreams in VITAL
     */
            } else {
                log.info("Creating new datastream: '{}'", dsId);
                log.debug("LABEL: '" + label + "', STATUS: '" + status +
                        "', GROUP: '" + controlGroup + "'");

                // Get our data
                try {
                    tempFile = getTempFile(ourObject, ourPid);
                } catch (Exception ex) {
                    throw new Exception("Error caching file to disk '" +
                            ourObject.getId() + "' : ", ex);
                }

                // Upload out data first
                tempURI = fedora.uploadFile(tempFile);

                // A new datastream
                fedora.getAPIM().addDatastream(
                    vitalPid,          // Object PID in VITAL
                    dsId,              // The dsID we have configured
                    altIds,            // Alt IDs... not using
                    label,             // Label
                    versionable,       // Versionable
                    mimeType,          // MIME type
                    null,              // Format URI
                    tempURI,           // Datastream Location
                    controlGroup,      // Control Group
                    status,            // State
                    null,              // ChecksumType
                    null,              // Checksum
                    fedoraLogEntry(ourObject, ourPid)); // Log message
            }

        } catch (Exception ex) {
            // Throw error
            throw new Exception("Error submitting datastream '" +
                    ourObject.getId() + "' : ", ex);
        } finally {
            if (tempFile != null && tempFile.exists()) {
                tempFile.delete();
            }
        }
    }

    /**
     * Trivial wrapper to close Closeable objects with an awareness that they
     * may not have been instantiated, or may have already been closed.
     *
     * Typically this would be a Stream, either in or out.
     *
     * @param toClose : The object to close
     */
    private void close(Closeable toClose) {
        if (toClose != null) {
            try {
                toClose.close();
            } catch (Exception ex) {
                // Already closed
            }
        }
    }

    /**
     * Test for the existence of a given datastream in VITAL.
     *
     * @param fedora : An instantiated fedora client
     * @param vitalPid : The VITAL PID to use
     * @param dsPid : The datastream ID on the object
     * @returns boolean : True is found, False if not found or there are errors
     */
    private boolean datastreamExists(FedoraClient fedora, String vitalPid,
            String dsPid) {
        try {
             // Some options:
             //  * getAPIA().listDatastreams... seems best
             //  * getAPIM().getDatastream... causes Exceptions against new IDs
             //  * getAPIM().getDatastreams... is limited to a single state
            DatastreamDef[] streams = fedora.getAPIA().listDatastreams(
                    vitalPid, null);
            for (DatastreamDef stream : streams) {
                if (stream.getID().equals(dsPid)) {
                    return true;
                }
            }
        } catch (Exception ex) {
            log.error("API Query error: ", ex);
        }
        return false;
    }

    /**
     * Find and return any alternate identifiers already in use in fedora for
     * the given datastream.
     *
     * @param fedora : An instantiated fedora client
     * @param vitalPid : The VITAL PID to use
     * @param dsPid : The datastream ID on the object
     * @returns String[] : An array or String identifiers, will be empty if
     * datastream does not exist.
     */
    private String[] getAltIds(FedoraClient fedora, String vitalPid,
            String dsPid) {
        Datastream ds = getDatastream(fedora, vitalPid, dsPid);
        if (ds != null) {
            return ds.getAltIDs();
        }
        return new String[] {};
    }

    /**
     * Get the indicated datastream from VITAL. This method pre-supposes that
     * the datastream does in fact exist. Call datastreamExists() first to
     * confirm.
     *
     * @param fedora : An instantiated fedora client
     * @param vitalPid : The VITAL PID to use
     * @param dsPid : The datastream ID on the object
     * @returns Datastream : The datastream requested, null if not found
     */
    private Datastream getDatastream(FedoraClient fedora, String vitalPid,
            String dsPid) {
        try {
            return fedora.getAPIM().getDatastream(vitalPid, dsPid, null);
        } catch (Exception ex) {
            log.error("API Query error: ", ex);
            return null;
        }
    }

    /**
     * Build a Log entry to use in Fedora. Replace all the template placeholders
     *
     * @param object : The Object being submitted
     * @param pid : The PID in our system
     */
    private String fedoraLogEntry(DigitalObject object, String pid) {
        String message = fedoraMessageTemplate.replace("[[PID]]", pid);
        return message.replace("[[OID]]", object.getId());
    }

    /**
     * Build an error message detailing an interrupted upload. Some (or none)
     * of the intended list of payloads did not transfer to VITAL correctly.
     *
     * @param pid : The PID in our system for which the failure occurred.
     * @param count : The number of successful PIDs sent before the failure.
     * @param total : The total number of PIDs that were intended to be sent.
     * @param vitalPid : The PID for the entire object in VITAL.
     */
    private String partialUploadErrorMessage(String pid, int count, int total,
            String vitalPid) {
        String message = "Error submitting payload '" + pid + "' to VITAL. ";
        message += count + " of " + total + " payloads where successfully";
        message += " sent to VITAL before this error occurred.";
        message += " The VITAL PID is '" + vitalPid + "'.";
        return message;
    }

    /**
     * Stream the data out of storage to our temp directory.
     *
     * @param object : Our digital object.
     * @param pid : The payload ID to retrieve.
     * @return File : The file creating in the temp directory
     * @throws Exception on any errors
     */
    private File getTempFile(DigitalObject object, String pid)
            throws Exception {
        // Create file in temp space, use OID in path for uniqueness
        File directory = new File(tmpDir, object.getId());
        File target = new File(directory, pid);
        if (!target.exists()) {
            target.getParentFile().mkdirs();
            target.createNewFile();
        }

        // These can happily throw exceptions higher
        Payload payload = object.getPayload(pid);
        InputStream in = payload.open();
        FileOutputStream out = null;

        // But here, the payload must receive
        //  a close before throwing the error
        try {
            out = new FileOutputStream(target);
            IOUtils.copyLarge(in, out);

        } catch (Exception ex) {
            close(out);
            target.delete();
            payload.close();
            throw ex;
        }

        // We close out here, because the catch statement needed to close
        //  before it could delete... so it can't be in 'finally'
        close(out);
        payload.close();

        return target;
    }

    /**
     * Retrieve the payload from storage and return as a byte array.
     *
     * @param object : Our digital object.
     * @param pid : The payload ID to retrieve.
     * @return byte[] : The byte array containing payload data
     * @throws Exception on any errors
     */
    private byte[] getBytes(DigitalObject object, String pid)
            throws Exception {
        // These can happily throw exceptions higher
        Payload payload = object.getPayload(pid);
        InputStream in = payload.open();
        byte[] result = null;

        // But here, the payload must receive
        //  a close before throwing the error
        try {
            result = IOUtils.toByteArray(in);
        } catch (Exception ex) {
            throw ex;
        } finally {
            payload.close();
        }

        return result;
    }

    /**
     * Error handling methods. Will at least log the errors, but also try to
     * send emails if configured to do so, and the data provided indicates it
     * is warranted.
     *
     * If an OID and Title are provided it indicates an Object we are confident
     * should have been sent to VITAL, so emails will be sent out
     * (if configured).
     *
     * @param message : Our own error message
     * @param ex : Any exception that has been thrown (OPTIONAL)
     * @param oid : The OID of our Object (OPTIONAL)
     * @param title : The title of our Object (OPTIONAL)
     */
    private void error(String message) {
        error(message, null, null, null);
    }
    private void error(String message, Exception ex) {
        error(message, ex, null, null);
    }
    private void error(String message, Exception ex, String oid, String title) {
        // We are only sending emails when we are configured to
        if (emailQueue != null) {
            // And when a complete and correct document fails to go to VITAL
            if (oid != null && title != null) {
                JsonSimple messageJson = new JsonSimple();
                JSONArray to = messageJson.writeArray("to");
                for (String email : emailAddresses) {
                    to.add(email);
                }
                JsonObject json = messageJson.getJsonObject();
                json.put("subject", emailSubject);
                // Emails require an Object ID... not sure why
                json.put("oid", oid);

                // Grab the template and replace each placeholder
                String body = emailTemplate.replace("[[OID]]", oid);
                body = body.replace("[[TITLE]]", title);
                body = body.replace("[[MESSAGE]]", message);

                // Did we have a genuine exception?
                if (ex != null) {
                    // Message
                    String exception = ex.getMessage() + "\n";
                    // Stack trace
                    StringWriter sw = new StringWriter();
                    ex.printStackTrace(new PrintWriter(sw));
                    body = body.replace("[[ERROR]]", sw.toString());
                } else {
                    body = body.replace("[[ERROR]]",
                            "{No error stacktrace provide}");
                }
                json.put("body", body);

                // Send the message
                log.debug("Error, sending email:\n{}",
                        messageJson.toString(true));
                messaging.queueMessage(emailQueue, messageJson.toString());
            }
        }

        // Always log errors at least
        if (ex != null) {
            log.error("VITAL Subscriber Error: {}", message, ex);
            log.error("STACK TRACE:\n", ex);
        } else {
            log.error("VITAL Subscriber Error: {}", message);
        }
    }
}
