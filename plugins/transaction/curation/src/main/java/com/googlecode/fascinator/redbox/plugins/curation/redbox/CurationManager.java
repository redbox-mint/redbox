/* 
 * The Fascinator - ReDBox Curation Transaction Manager
 * Copyright (C) 2011-2012 Queensland Cyber Infrastructure Foundation (http://www.qcif.edu.au/)
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
package com.googlecode.fascinator.redbox.plugins.curation.redbox;

import com.googlecode.fascinator.api.PluginException;
import com.googlecode.fascinator.api.PluginManager;
import com.googlecode.fascinator.api.indexer.Indexer;
import com.googlecode.fascinator.api.indexer.SearchRequest;
import com.googlecode.fascinator.api.storage.DigitalObject;
import com.googlecode.fascinator.api.storage.Payload;
import com.googlecode.fascinator.api.storage.Storage;
import com.googlecode.fascinator.api.storage.StorageException;
import com.googlecode.fascinator.api.transaction.TransactionException;
import com.googlecode.fascinator.common.JsonObject;
import com.googlecode.fascinator.common.JsonSimple;
import com.googlecode.fascinator.common.JsonSimpleConfig;
import com.googlecode.fascinator.common.solr.SolrDoc;
import com.googlecode.fascinator.common.solr.SolrResult;
import com.googlecode.fascinator.common.transaction.GenericTransactionManager;
import com.googlecode.fascinator.messaging.EmailNotificationConsumer;
import com.googlecode.fascinator.messaging.TransactionManagerQueueConsumer;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.json.simple.JSONArray;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Implements curation boundary logic for ReDBox. This class is also a
 * replacement for the standard tool chain.
 * 
 * @author Greg Pendlebury
 */
public class CurationManager extends GenericTransactionManager {

	/** Data payload */
	private static String DATA_PAYLOAD_SUFFIX = ".tfpackage";

	/** Workflow payload */
	private static String WORKFLOW_PAYLOAD = "workflow.metadata";

	/** Property to set flag for ready to publish */
	private static String READY_PROPERTY = "ready_to_publish";

	/** Property to set flag for publication allowed */
	private static String PUBLISH_PROPERTY = "published";

	/** Logging **/
	private static Logger log = LoggerFactory.getLogger(CurationManager.class);

	/** System configuration */
	private JsonSimpleConfig systemConfig;

	/** Storage */
	private Storage storage;

	/** Solr Index */
	private Indexer indexer;

	/** External URL base */
	private String urlBase;

	/** Curation staff email address */
	private String emailAddress;

	/** Property to store PIDs */
	private String pidProperty;

	/** Send emails or just curate? */
	private boolean manualConfirmation;

	/** URL for our AMQ broker */
	private String brokerUrl;

	/** URL for Mint's AMQ broker */
	private String mintBroker;

	/** Relationship maps */
	private Map<String, JsonSimple> relationFields;

	/**
	 * Base constructor
	 * 
	 */
	public CurationManager() {
		super("curation-redbox", "ReDBox Curation Transaction Manager");
	}

	/**
	 * Initialise method
	 * 
	 * @throws TransactionException
	 *             if there was an error during initialisation
	 */
	@Override
	public void init() throws TransactionException {
		systemConfig = getJsonConfig();

		// Load the storage plugin
		String storageId = systemConfig.getString("file-system", "storage",
				"type");
		if (storageId == null) {
			throw new TransactionException("No Storage ID provided");
		}
		storage = PluginManager.getStorage(storageId);
		if (storage == null) {
			throw new TransactionException("Unable to load Storage '"
					+ storageId + "'");
		}
		try {
			storage.init(systemConfig.toString());
		} catch (PluginException ex) {
			log.error("Unable to initialise storage layer!", ex);
			throw new TransactionException(ex);
		}

		// Load the indexer plugin
		String indexerId = systemConfig.getString("solr", "indexer", "type");
		if (indexerId == null) {
			throw new TransactionException("No Indexer ID provided");
		}
		indexer = PluginManager.getIndexer(indexerId);
		if (indexer == null) {
			throw new TransactionException("Unable to load Indexer '"
					+ indexerId + "'");
		}
		try {
			indexer.init(systemConfig.toString());
		} catch (PluginException ex) {
			log.error("Unable to initialise indexer!", ex);
			throw new TransactionException(ex);
		}

		// External facing URL
		urlBase = systemConfig.getString(null, "urlBase");
		if (urlBase == null) {
			throw new TransactionException("URL Base in config cannot be null");
		}

		// Where should emails be sent?
		emailAddress = systemConfig.getString(null, "curation",
				"curationEmailAddress");
		if (emailAddress == null) {
			throw new TransactionException("An admin email is required!");
		}

		// Where are PIDs stored?
		pidProperty = systemConfig.getString(null, "curation", "pidProperty");
		if (pidProperty == null) {
			throw new TransactionException("An admin email is required!");
		}

		// Do admin staff want to confirm each curation?
		manualConfirmation = systemConfig.getBoolean(false, "curation",
				"curationRequiresConfirmation");

		// Find the address of our broker
		brokerUrl = systemConfig.getString(null, "messaging", "url");
		if (brokerUrl == null) {
			throw new TransactionException("Cannot find the message broker.");
		}

		// We also need Mint's AMQ url
		mintBroker = systemConfig.getString(null, "curation", "mintBroker");
		if (mintBroker == null) {
			throw new TransactionException("Cannot find Mint's message broker.");
		}

		/** Relationship mapping */
		relationFields = systemConfig.getJsonSimpleMap("curation", "relations");
		if (relationFields == null) {
			log.warn("Curation configuration has no relationships");
			relationFields = new HashMap<String, JsonSimple>();
		}
	}

	/**
	 * Shutdown method
	 * 
	 * @throws PluginException
	 *             if any errors occur
	 */
	@Override
	public void shutdown() throws PluginException {
		if (storage != null) {
			try {
				storage.shutdown();
			} catch (PluginException pe) {
				log.error("Failed to shutdown storage: {}", pe.getMessage());
				throw pe;
			}
		}
		if (indexer != null) {
			try {
				indexer.shutdown();
			} catch (PluginException pe) {
				log.error("Failed to shutdown indexer: {}", pe.getMessage());
				throw pe;
			}
		}
	}

	/**
	 * Assess a workflow event to see how it effects curation
	 * 
	 * @param response
	 *            The response object
	 * @param message
	 *            The incoming message
	 */
	private void workflowCuration(JsonSimple response, JsonSimple message) {
		String oid = message.getString(null, "oid");
		if (!workflowCompleted(oid)) {
			return;
		}

		// Resolve relationships before we continue
		try {
			JSONArray relations = mapRelations(oid);
			// Unless there was an error, we should be good to go
			if (relations != null) {
				JsonObject request = createTask(response, oid,
						"curation-request");
				if (!relations.isEmpty()) {
					request.put("relationships", relations);
				}
			}
		} catch (Exception ex) {
			log.error("Error processing relations: ", ex);
			return;
		}

	}

	private boolean workflowCompleted(String oid) {
		JsonSimple workflow = getWorkflowData(oid);
		if (workflow == null) {
			log.error("Error accessing workflow data '{}'", oid);
			return false;
		}

		String step = workflow.getString(null, "step");
		if (step == null || !step.equals("live")) {
			log.debug("Workflow step '{}', ignoring.", step);
			return false;
		}

		return true;
	}

	/**
	 * Map all the relationships buried in this record's data
	 * 
	 * @param oid
	 *            The object ID being curated
	 * @returns True is ready to proceed, otherwise False
	 */
	private JSONArray mapRelations(String oid) {
		// We want our parsed data for reading
		JsonSimple formData = parsedFormData(oid);
		if (formData == null) {
			log.error("Error parsing form data");
			return null;
		}

		// And raw data to see existing relations and write new ones
		JsonSimple rawData = getDataFromStorage(oid);
		if (rawData == null) {
			log.error("Error reading data from storage");
			return null;
		}
		// Existing relationship data
		JSONArray relations = rawData.writeArray("relationships");
		boolean changed = false;

		// For all configured relationships
		for (String baseField : relationFields.keySet()) {
			JsonSimple relationConfig = relationFields.get(baseField);

			// Find the path we need to look under for our related object
			List<String> basePath = relationConfig.getStringList("path");
			if (basePath == null || basePath.isEmpty()) {
				log.error("Ignoring invalid relationship '{}'. No 'path'"
						+ " provided in configuration", baseField);
				continue;
			}

			// Get our base object
			Object object = formData.getPath(basePath.toArray());
			if (object instanceof JsonObject) {
				// And process it
				JsonObject newRelation = lookForRelation(oid, baseField,
						relationConfig, new JsonSimple((JsonObject) object));
				if (newRelation != null
						&& !isKnownRelation(relations, newRelation)) {
					log.info("Adding relation: '{}' => '{}'", baseField,
							newRelation.get("identifier"));
					relations.add(newRelation);
					changed = true;
				}
			}
			// If base path points at an array
			if (object instanceof JSONArray) {
				// Try every entry
				for (Object loopObject : (JSONArray) object) {
					if (loopObject instanceof JsonObject) {
						JsonObject newRelation = lookForRelation(oid,
								baseField, relationConfig, new JsonSimple(
										(JsonObject) loopObject));
						if (newRelation != null
								&& !isKnownRelation(relations, newRelation)) {
							log.info("Adding relation: '{}' => '{}'",
									baseField, newRelation.get("identifier"));
							relations.add(newRelation);
							changed = true;
						}
					}
				}
			}
		}

		// Do we need to store our object again?
		if (changed) {
			try {
				saveObjectData(rawData, oid);
			} catch (TransactionException ex) {
				log.error("Error updating object '{}' in storage: ", oid, ex);
				return null;
			}
		}

		return relations;
	}

	/**
	 * Look through part of the form data for a relationship.
	 * 
	 * @param oid
	 *            The object ID of the current object
	 * @param field
	 *            The full field String to store for comparisons
	 * @param config
	 *            The config relating to the relationship we are looking for
	 * @param baseNode
	 *            The JSON node the relationship should be under
	 * @return JsonObject A relationship in JSON, or null if not found
	 */
	private JsonObject lookForRelation(String oid, String field,
			JsonSimple config, JsonSimple baseNode) {
		JsonObject newRelation = new JsonObject();
		newRelation.put("field", field);
		newRelation.put("authority", true);

		// ** -1- ** EXCLUSIONS
		List<String> exPath = config.getStringList("excludeCondition", "path");
		String exValue = config.getString(null, "excludeCondition", "value");
		if (exPath != null && !exPath.isEmpty() && exValue != null) {
			String value = baseNode.getString(null, exPath.toArray());
			if (value != null && value.equals(exValue)) {
				log.info("Excluding relationship '{}' based on config", field);
				return null;
			}
		}
		String exStartsWith = config.getString(null, "excludeCondition",
				"startsWith");
		if (exPath != null && !exPath.isEmpty() && exStartsWith != null) {
			String value = baseNode.getString(null, exPath.toArray());
			if (value != null && value.startsWith(exStartsWith)) {
				log.info("Excluding relationship '{}' based on config", field);
				return null;
			}
		}

		// ** -2- ** IDENTIFIER
		// Inside that object where can we find the identifier
		List<String> idPath = config.getStringList("identifier");
		if (idPath == null || idPath.isEmpty()) {
			log.error("Ignoring invalid relationship '{}'. No 'identifier'"
					+ " provided in configuration", field);
			return null;
		}
		String id = baseNode.getString(null, idPath.toArray());
		if (id != null && !id.equals("")) {
			newRelation.put("identifier", id.trim());
		} else {
			log.info("Relationship '{}' has no identifier, ignoring!", field);
			return null;
		}

		// ** -3- ** RELATIONSHIP TYPE
		// Relationship type, it may be static and provided for us...
		String staticRelation = config.getString(null, "relationship");
		List<String> relPath = null;
		if (staticRelation == null) {
			// ... or it could be found in the form data
			relPath = config.getStringList("relationship");
		}
		// But we have to have one.
		if (staticRelation == null && (relPath == null || relPath.isEmpty())) {
			log.error("Ignoring invalid relationship '{}'. No relationship"
					+ " String of path in configuration", field);
			return null;
		}
		String relString = null;
		if (staticRelation != null) {
			relString = staticRelation;
		} else {
			relString = baseNode.getString("hasAssociationWith",
					relPath.toArray());
		}
		if (relString == null || relString.equals("")) {
			log.info("Relationship '{}' has no type, ignoring!", field);
			return null;
		}
		newRelation.put("relationship", relString);

		// ** -4- ** REVERSE RELATIONS
		String revRelation = systemConfig.getString("hasAssociationWith",
				"curation", "reverseMappings", relString);
		newRelation.put("reverseRelationship", revRelation);

		// ** -5- ** DESCRIPTION
		String description = config.getString(null, "description");
		if (description != null) {
			newRelation.put("description", description);
		}

		// ** -6- ** SYSTEM / BROKER
		String system = config.getString("mint", "system");
		if (system != null && system.equals("mint")) {
			newRelation.put("broker", mintBroker);
		} else {
			newRelation.put("broker", brokerUrl);
			// ReDBox record's should also be told that the ID is an OID
			// JCU: causes an exception in CurationManager.
			// checkChildren() will convert the identifier to an oid when a
			// 'curation-confirm' is processed
			// newRelation.put("oid", id);
		}

		// ** -7- ** OPTIONAL
		boolean optional = config.getBoolean(false, "optional");
		if (optional) {
			newRelation.put("optional", optional);
		}

		return newRelation;
	}

	/**
	 * Test whether the field provided is already a known relationship
	 * 
	 * @param relations
	 *            The list of current relationships
	 * @param field
	 *            The cleaned field to provide some context
	 * @param id
	 *            The ID of the related object
	 * @returns True is it is a known relationship
	 */
	private boolean isKnownRelation(JSONArray relations, JsonObject newRelation) {
		// Does it have an OID? Highest priority. Avoids infinite loops
		// between ReDBox collections pointing at each other, so strict
		if (newRelation.containsKey("oid")) {
			for (Object relation : relations) {
				JsonObject json = (JsonObject) relation;
				String knownOid = (String) json.get("oid");
				String newOid = (String) newRelation.get("oid");
				// Do they match?
				if (knownOid.equals(newOid)) {
					log.debug("Known ReDBox linkage '{}'", knownOid);
					return true;
				}
			}
			return false;
		}

		// Mint records we are less strict about and happy
		// to allow multiple links in differing fields.
		for (Object relation : relations) {
			JsonObject json = (JsonObject) relation;

			if (json.containsKey("identifier")) {
				String knownId = (String) json.get("identifier");
				String knownField = (String) json.get("field");
				String newId = (String) newRelation.get("identifier");
				String newField = (String) newRelation.get("field");
				// And does the ID match?
				if (knownId.equals(newId) && knownField.equals(newField)) {
					return true;
				}
			}
		}
		// No match found
		return false;
	}

	/**
	 * This method encapsulates the logic for curation in ReDBox
	 * 
	 * @param oid
	 *            The object ID being curated
	 * @returns JsonSimple The response object to send back to the queue
	 *          consumer
	 */
	private JsonSimple curation(JsonSimple message, String task, String oid) {
		JsonSimple response = new JsonSimple();

		// *******************
		// Collect object data

		// Transformer config
		JsonSimple itemConfig = getConfigFromStorage(oid);
		if (itemConfig == null) {
			log.error("Error accessing item configuration!");
			return new JsonSimple();
		}
		// Object properties
		Properties metadata = getObjectMetadata(oid);
		if (metadata == null) {
			log.error("Error accessing item metadata!");
			return new JsonSimple();
		}
		// Object metadata
		JsonSimple data = getDataFromStorage(oid);
		if (data == null) {
			log.error("Error accessing item data!");
			return new JsonSimple();
		}

		// *******************
		// Validate what we can see

		// Check object state
		boolean curated = false;
		boolean alreadyCurated = itemConfig.getBoolean(false, "curation",
				"alreadyCurated");
		boolean errors = false;

		// Can we already see this PID?
		String thisPid = null;
		if (metadata.containsKey(pidProperty)) {
			curated = true;
			thisPid = metadata.getProperty(pidProperty);

			// Or does it claim to have one from pre-ingest curation?
		} else {
			if (alreadyCurated) {
				// Make sure we can actually see an ID
				String id = data.getString(null, "metadata", "dc.identifier");
				if (id == null) {
					log.error("Item claims to be curated, but has no"
							+ " 'dc.identifier': '{}'", oid);
					errors = true;

					// Let's fix this so it doesn't show up again
				} else {
					try {
						log.info("Update object properties with ingested"
								+ " ID: '{}'", oid);
						// Metadata writes can be awkward... thankfully this is
						// code that should only ever execute once per object.
						DigitalObject object = storage.getObject(oid);
						metadata = object.getMetadata();
						metadata.setProperty(pidProperty, id);
						object.close();
						metadata = getObjectMetadata(oid);
						curated = true;
						audit(response, oid, "Persitent ID set in properties");

					} catch (StorageException ex) {
						log.error("Error accessing object '{}' in storage: ",
								oid, ex);
						errors = true;
					}

				}
			}
		}

		// *******************
		// Decision making

		// Errors have occurred, email someone and do nothing
		if (errors) {
			emailObjectLink(
					response,
					oid,
					"An error occurred curating this object, some"
							+ " manual intervention may be required; please see"
							+ " the system logs.");
			audit(response, oid, "Errors during curation; aborted.");
			return response;
		}

		// ***
		// What should happen per task if we have already been curated?
		if (curated) {

			// Happy ending
			if (task.equals("curation-response")) {
				log.info("Confirmation of curated object '{}'.", oid);

				// Send out upstream responses to objects waiting
				JSONArray responses = data.writeArray("responses");
				for (Object thisResponse : responses) {
					JsonSimple json = new JsonSimple((JsonObject) thisResponse);
					String broker = json.getString(brokerUrl, "broker");
					String responseOid = json.getString(null, "oid");
					String responseTask = json.getString(null, "task");
					JsonObject responseObj = createTask(response, broker,
							responseOid, responseTask);
					// Don't forget to tell them where it came from
					responseObj.put("originOid", oid);
					responseObj.put("curatedPid", thisPid);
				}

				// Set a flag to let publish events that may come in later
				// that this is ready to publish (if not already set)
				if (!metadata.containsKey(READY_PROPERTY)) {
					try {
						DigitalObject object = storage.getObject(oid);
						metadata = object.getMetadata();
						metadata.setProperty(READY_PROPERTY, "ready");
						object.close();
						metadata = getObjectMetadata(oid);
						audit(response, oid,
								"This object is ready for publication");

					} catch (StorageException ex) {
						log.error("Error accessing object '{}' in storage: ",
								oid, ex);
						emailObjectLink(
								response,
								oid,
								"This object is ready for publication, but an"
										+ " error occured writing to storage. Please"
										+ " see the system log");
					}

					// Since the flag hasn't been set we also know this is the
					// first time through, so generate some notifications
					emailObjectLink(response, oid,
							"This email is confirming that the object linked"
									+ " below has completed curation.");
					audit(response, oid, "Curation completed.");

					// Schedule a followup to re-index and transform
					createTask(response, oid, "reharvest");
					createTask(response, oid, "publish");

					// This object was asked to curate again, so there may be
					// new 'children' who do need to publish, and external
					// updates required (like VITAL)
				} else {
					createTask(response, oid, "publish");
				}
				return response;
			}

			// A response has come back from downstream
			if (task.equals("curation-pending")) {
				String childOid = message.getString(null, "originOid");
				String childId = message.getString(null, "originId");
				String curatedPid = message.getString(null, "curatedPid");

				boolean isReady = false;
				try {
					// False here will make sure we aren't sending out a bunch
					// of requests again.
					isReady = checkChildren(response, data, oid, thisPid,
							false, childOid, childId, curatedPid);
				} catch (TransactionException ex) {
					log.error("Error updating related objects '{}': ", oid, ex);
					emailObjectLink(
							response,
							oid,
							"An error occurred curating this object, some"
									+ " manual intervention may be required; please see"
									+ " the system logs.");
					audit(response, oid, "Errors curating relations; aborted.");
					return response;
				}

				// If it is ready
				if (isReady) {
					createTask(response, oid, "curation-response");
				}
				return response;
			}

			// The object has finished, work on downstream 'children'
			if (task.equals("curation-confirm")) {
				boolean isReady = false;
				try {
					isReady = checkChildren(response, data, oid, thisPid, true);
				} catch (TransactionException ex) {
					log.error("Error processing related objects '{}': ", oid,
							ex);
					emailObjectLink(
							response,
							oid,
							"An error occurred curating this object, some"
									+ " manual intervention may be required; please see"
									+ " the system logs.");
					audit(response, oid, "Errors curating relations; aborted.");
					return response;
				}

				// If it is ready ont he first pass...
				if (isReady) {
					createTask(response, oid, "curation-response");
				} else {
					// Otherwise we are going to have to wait for children
					audit(response, oid, "Curation complete, but still waiting"
							+ " on relations.");
				}

				return response;
			}

			// Since it is already curated, we are just storing any new
			// relationships / responses and passing things along
			if (task.equals("curation-request")
					|| task.equals("curation-query")) {
				try {
					storeRequestData(message, oid);
				} catch (TransactionException ex) {
					log.error("Error storing request data '{}': ", oid, ex);
					emailObjectLink(
							response,
							oid,
							"An error occurred curating this object, some"
									+ " manual intervention may be required; please see"
									+ " the system logs.");
					audit(response, oid, "Errors during curation; aborted.");
					return response;
				}
				// Requests
				if (task.equals("curation-request")) {
					JsonObject taskObj = createTask(response, oid, "curation");
					taskObj.put("alreadyCurated", true);
					// Queries
				} else {
					// Rather then push to 'curation-response' we are just
					// sending a single response to the querying object
					JsonSimple respond = new JsonSimple(
							message.getObject("respond"));
					String broker = respond.getString(brokerUrl, "broker");
					String responseOid = respond.getString(null, "oid");
					String responseTask = respond.getString(null, "task");
					JsonObject responseObj = createTask(response, broker,
							responseOid, responseTask);
					// Don't forget to tell them where it came from
					responseObj.put("originOid", oid);
					responseObj.put("curatedPid", thisPid);
				}
				return response;
			}

			// Same as above, but this is a second stage request, let's be a
			// little sterner in case log filtering is occurring
			if (task.equals("curation")) {
				log.info("Request to curate ignored. This object '{}' has"
						+ " already been curated.", oid);
				JsonObject taskObj = createTask(response, oid,
						"curation-confirm");
				taskObj.put("alreadyCurated", true);
				return response;
			}

			// ***
			// What should happen per task if we have *NOT* already been
			// curated?
		} else {
			// Whoops! We shouldn't be confirming or responding to a non-curated
			// item!!!
			if (task.equals("curation-confirm")
					|| task.equals("curation-pending")) {
				emailObjectLink(
						response,
						oid,
						"NOTICE: The system has received a '"
								+ task
								+ "'"
								+ " event, but the record does not appear to be"
								+ " curated. If your system is configured for VITAL"
								+ " integration this should clear by itself soon.");
				return response;
			}

			// Standard stuff - a request to curate non-curated data
			if (task.equals("curation-request")) {
				try {
					storeRequestData(message, oid);
				} catch (TransactionException ex) {
					log.error("Error storing request data '{}': ", oid, ex);
					emailObjectLink(
							response,
							oid,
							"An error occurred curating this object, some"
									+ " manual intervention may be required; please see"
									+ " the system logs.");
					audit(response, oid, "Errors during curation; aborted.");
					return response;
				}

				// ReDBox will only curate if the workflow is finished
				if (!workflowCompleted(oid)) {
					log.warn("Curation request recieved, but object has"
							+ " not finished workflow.");
					return response;
				}

				if (manualConfirmation) {
					emailObjectLink(
							response,
							oid,
							"A curation request has been recieved for this"
									+ " object. You can find a link below to approve"
									+ " the request.");
					audit(response, oid, "Curation request received. Pending");
				} else {
					createTask(response, oid, "curation");
				}
				return response;
			}

			// We can't do much here, just store the response address
			if (task.equals("curation-query")) {
				try {
					storeRequestData(message, oid);
				} catch (TransactionException ex) {
					log.error("Error storing request data '{}': ", oid, ex);
					emailObjectLink(
							response,
							oid,
							"An error occurred curating this object, some"
									+ " manual intervention may be required; please see"
									+ " the system logs.");
					audit(response, oid, "Errors during curation; aborted.");
					return response;
				}
				return response;
			}

			// The actual curation event
			if (task.equals("curation")) {
				audit(response, oid, "Object curation requested.");
				List<String> list = itemConfig.getStringList("transformer",
						"curation");

				// Pass through whichever curation transformer are configured
				if (list != null && !list.isEmpty()) {
					for (String id : list) {
						JsonObject order = newTransform(response, id, oid);
						JsonObject config = (JsonObject) order.get("config");
						JsonObject overrides = itemConfig.getObject(
								"transformerOverrides", id);
						if (overrides != null) {
							config.putAll(overrides);
						}
					}

				} else {
					log.warn("This object has no configured transformers!");
				}

				// Force an index update after the ID has been created,
				// but before "curation-confirm"
				JsonObject order = newIndex(response, oid);
				order.put("forceCommit", true);

				// Don't forget to come back
				createTask(response, oid, "curation-confirm");
				return response;
			}
		}

		log.error("Invalid message received. Unknown task:\n{}",
				message.toString(true));
		emailObjectLink(response, oid,
				"The curation manager has received an invalid curation message"
						+ " for this object. Please see the system logs.");
		return response;
	}

	/**
	 * Look through all known related objects and assess their readiness. Can
	 * optionally send downstream curation requests if required, and update a
	 * relationship based on responses.
	 * 
	 * @param response
	 *            The response currently being built
	 * @param data
	 *            The object's data
	 * @param oid
	 *            The object's ID
	 * @param sendRequests
	 *            True if curation requests should be sent out
	 * @returns boolean True if all 'children' have been curated.
	 * @throws TransactionException
	 *             If an error occurs
	 */
	private boolean checkChildren(JsonSimple response, JsonSimple data,
			String thisOid, String thisPid, boolean sendRequests)
			throws TransactionException {
		return checkChildren(response, data, thisOid, thisPid, sendRequests,
				null, null, null);
	}

	/**
	 * Look through all known related objects and assess their readiness. Can
	 * optionally send downstream curation requests if required, and update a
	 * relationship based on responses.
	 * 
	 * @param response
	 *            The response currently being built
	 * @param data
	 *            The object's data
	 * @param oid
	 *            The object's ID
	 * @param sendRequests
	 *            True if curation requests should be sent out
	 * @param childOid
	 * @returns boolean True if all 'children' have been curated.
	 * @throws TransactionException
	 *             If an error occurs
	 */
	private boolean checkChildren(JsonSimple response, JsonSimple data,
			String thisOid, String thisPid, boolean sendRequests,
			String childOid, String childId, String curatedPid)
			throws TransactionException {

		boolean isReady = true;
		boolean saveData = false;
		log.debug("Checking Children of '{}'", thisOid);

		JSONArray relations = data.writeArray("relationships");
		for (Object relation : relations) {
			JsonSimple json = new JsonSimple((JsonObject) relation);
			String broker = json.getString(brokerUrl, "broker");
			boolean localRecord = broker.equals(brokerUrl);
			String relatedId = json.getString(null, "identifier");

			// We need to find OIDs to match IDs (only for local records)
			String relatedOid = json.getString(null, "oid");
			if (relatedOid == null && localRecord) {
				String identifier = json.getString(null, "identifier");
				if (identifier == null) {
					throw new TransactionException("NULL identifer provided!");
				}
				relatedOid = idToOid(identifier);
				if (relatedOid == null) {
					throw new TransactionException("Cannot resolve identifer: "
							+ identifier);
				}
				((JsonObject) relation).put("oid", relatedOid);
				saveData = true;
			}

			// Are we updating a relationship... and is it this one?
			boolean updatingById = (childId != null && childId
					.equals(relatedId));
			boolean updatingByOid = (childOid != null && childOid
					.equals(relatedOid));
			if (curatedPid != null && (updatingById || updatingByOid)) {
				log.debug("Updating...");
				((JsonObject) relation).put("isCurated", true);
				((JsonObject) relation).put("curatedPid", curatedPid);
				saveData = true;
			}

			// Is this relationship using a curated ID?
			boolean isCurated = json.getBoolean(false, "isCurated");
			if (!isCurated) {
				log.debug(" * Needs curation '{}'", relatedId);
				boolean optional = json.getBoolean(false, "optional");
				if (!optional) {
					isReady = false;
				}
				// Only send out curation requests if asked to
				if (sendRequests) {
					JsonObject task;
					// It is a local object
					if (localRecord) {
						task = createTask(response, relatedOid,
								"curation-query");
						// Or remote
					} else {
						task = createTask(response, broker, relatedOid,
								"curation-query");
						// We won't know OIDs for remote systems
						task.remove("oid");
						task.put("identifier", relatedId);
					}

					// If this record is the authority on the relationship
					// make sure we tell the other object what its relationship
					// back to us should be.
					boolean authority = json.getBoolean(false, "authority");
					if (authority) {
						// Send a full request rather then a query, we need it
						// to propogate through children
						task.put("task", "curation-request");

						// Let the other object know its reverse relationship
						// with us and that we've already been curated.
						String reverseRelationship = json.getString(
								"hasAssociationWith", "reverseRelationship");
						JsonObject relObject = new JsonObject();
						relObject.put("identifier", thisPid);
						relObject.put("curatedPid", thisPid);
						relObject.put("broker", brokerUrl);
						relObject.put("isCurated", true);
						relObject.put("relationship", reverseRelationship);
						// Make sure we send OID to local records
						if (localRecord) {
							relObject.put("oid", thisOid);
						}
						JSONArray newRelations = new JSONArray();
						newRelations.add(relObject);
						task.put("relationships", newRelations);
					}

					// And make sure it knows how to send us curated PIDs
					JsonObject msgResponse = new JsonObject();
					msgResponse.put("broker", brokerUrl);
					msgResponse.put("oid", thisOid);
					msgResponse.put("task", "curation-pending");
					task.put("respond", msgResponse);
				}
			} else {
				log.debug(" * Already curated '{}'", relatedId);
			}
		}

		// Save our data if we changed it
		if (saveData) {
			saveObjectData(data, thisOid);
		}

		return isReady;
	}

	private String idToOid(String identifier) {
		// Build a query
		String query = "known_ids:\"" + identifier + "\"";
		SearchRequest request = new SearchRequest(query);
		ByteArrayOutputStream out = new ByteArrayOutputStream();

		// Now search and parse response
		SolrResult result = null;
		try {
			indexer.search(request, out);
			InputStream in = new ByteArrayInputStream(out.toByteArray());
			result = new SolrResult(in);
		} catch (Exception ex) {
			log.error("Error searching Solr: ", ex);
			return null;
		}

		// Verify our results
		if (result.getNumFound() == 0) {
			log.error("Cannot resolve ID '{}'", identifier);
			return null;
		}
		if (result.getNumFound() > 1) {
			log.error("Found multiple OIDs for ID '{}'", identifier);
			return null;
		}

		// Return our result
		SolrDoc doc = result.getResults().get(0);
		return doc.getFirst("storage_id");
	}

	/**
	 * Store the important parts of the request data for later use.
	 * 
	 * @param message
	 *            The JsonSimple message to store
	 * @param oid
	 *            The Object to store the message in
	 * @throws TransactionException
	 *             If an error occurred
	 */
	private void storeRequestData(JsonSimple message, String oid)
			throws TransactionException {

		// Get our incoming data to look at
		JsonObject toRespond = message.getObject("respond");
		JSONArray newRelations = message.getArray("relationships");
		if (toRespond == null && newRelations == null) {
			log.warn("This request requires no responses and specifies"
					+ " no relationships.");
			return;
		}

		// Get from storage
		DigitalObject object = null;
		Payload payload = null;
		InputStream inStream = null;
		try {
			object = storage.getObject(oid);
			payload = getDataPayload(object);
			inStream = payload.open();
		} catch (StorageException ex) {
			log.error("Error accessing object '{}' in storage: ", oid, ex);
			throw new TransactionException(ex);
		}

		// Parse existing data
		JsonSimple metadata = null;
		try {
			metadata = new JsonSimple(inStream);
			inStream.close();
		} catch (IOException ex) {
			log.error("Error parsing/reading JSON '{}'", oid, ex);
			throw new TransactionException(ex);
		}

		// Store our new response
		if (toRespond != null) {
			JSONArray responses = metadata.writeArray("responses");
			boolean duplicate = false;
			String newOid = (String) toRespond.get("oid");
			for (Object response : responses) {
				String oldOid = (String) ((JsonObject) response).get("oid");
				if (newOid.equals(oldOid)) {
					log.debug("Ignoring duplicate response request by '{}'"
							+ " on object '{}'", newOid, oid);
					duplicate = true;
				}
			}
			if (!duplicate) {
				log.debug("New response requested by '{}' on object '{}'",
						newOid, oid);
				responses.add(toRespond);
			}
		}

		// Store relationship(s), with some basic de-duping
		if (newRelations != null) {
			JSONArray relations = metadata.writeArray("relationships");
			for (JsonSimple newRelation : JsonSimple.toJavaList(newRelations)) {
				boolean duplicate = false;
				String identifier = newRelation.getString(null, "identifier");
				// Compare to each existing relationship
				for (JsonSimple relation : JsonSimple.toJavaList(relations)) {
					String storedId = relation.getString(null, "identifier");
					if (identifier.equals(storedId)) {
						log.debug("Ignoring duplicate relationship '{}'",
								identifier);
						duplicate = true;
					}
				}

				// Store new entries
				if (!duplicate) {
					log.debug("New relationship added to '{}'", oid);
					relations.add(newRelation.getJsonObject());
				}
			}
		}

		// Store modifications
		if (toRespond != null || newRelations != null) {
			log.info("Updating object in storage '{}'", oid);
			String jsonString = metadata.toString(true);
			try {
				updateDataPayload(object, jsonString);
			} catch (Exception ex) {
				log.error("Unable to store data '{}': ", oid, ex);
				throw new TransactionException(ex);
			}
		}
	}

	/**
	 * Get the requested object ready for publication. This would typically just
	 * involve setting a flag
	 * 
	 * @param message
	 *            The incoming message
	 * @param oid
	 *            The object identifier to publish
	 * @return JsonSimple The response object
	 * @throws TransactionException
	 *             If an error occurred
	 */
	private JsonSimple publish(JsonSimple message, String oid)
			throws TransactionException {
		log.debug("Publishing '{}'", oid);
		JsonSimple response = new JsonSimple();
		try {
			DigitalObject object = storage.getObject(oid);
			Properties metadata = object.getMetadata();
			// Already published?
			if (!metadata.containsKey(PUBLISH_PROPERTY)) {
				metadata.setProperty(PUBLISH_PROPERTY, "true");
				object.close();
				log.info("Publication flag set '{}'", oid);
				audit(response, oid, "Publication flag set");
			} else {
				log.info("Publication flag is already set '{}'", oid);
			}
		} catch (StorageException ex) {
			throw new TransactionException("Error setting publish property: ",
					ex);
		}

		// Make a final pass through the curation tool(s),
		// allows for external publication. eg. VITAL
		JsonSimple itemConfig = getConfigFromStorage(oid);
		if (itemConfig == null) {
			log.error("Error accessing item configuration!");
		} else {
			List<String> list = itemConfig.getStringList("transformer",
					"curation");

			if (list != null && !list.isEmpty()) {
				for (String id : list) {
					JsonObject order = newTransform(response, id, oid);
					JsonObject config = (JsonObject) order.get("config");
					JsonObject overrides = itemConfig.getObject(
							"transformerOverrides", id);
					if (overrides != null) {
						config.putAll(overrides);
					}
				}
			}
		}

		// Don't forget to publish children
		publishRelations(response, oid);
		return response;
	}

	/**
	 * Send out requests to all relations to publish
	 * 
	 * @param oid
	 *            The object identifier to publish
	 */
	private void publishRelations(JsonSimple response, String oid) {
		log.debug("Publishing Children of '{}'", oid);

		JsonSimple data = getDataFromStorage(oid);
		if (data == null) {
			log.error("Error accessing item data! '{}'", oid);
			emailObjectLink(response, oid,
					"An error occured publishing the related objects for this"
							+ " record. Please check the system logs.");
			return;
		}

		JSONArray relations = data.writeArray("relationships");
		for (Object relation : relations) {
			JsonSimple json = new JsonSimple((JsonObject) relation);
			String broker = json.getString(null, "broker");
			boolean localRecord = broker.equals(brokerUrl);
			String relatedId = json.getString(null, "identifier");

			// We need to find OIDs to match IDs (only for local records)
			String relatedOid = json.getString(null, "oid");
			if (relatedOid == null && localRecord) {
				String identifier = json.getString(null, "identifier");
				if (identifier == null) {
					log.error("NULL identifer provided!");
				}
				relatedOid = idToOid(identifier);
				if (relatedOid == null) {
					log.error("Cannot resolve identifer: '{}'", identifier);
				}
			}

			// We only publish downstream relations (ie. we are their authority)
			boolean authority = json.getBoolean(false, "authority");
			if (authority) {
				// Is this relationship using a curated ID?
				boolean isCurated = json.getBoolean(false, "isCurated");
				if (isCurated) {
					log.debug(" * Publishing '{}'", relatedId);
					// It is a local object
					if (localRecord) {
						createTask(response, relatedOid, "publish");

						// Or remote
					} else {
						JsonObject task = createTask(response, broker,
								relatedOid, "publish");
						// We won't know OIDs for remote systems
						task.remove("oid");
						task.put("identifier", relatedId);
					}
				} else {
					log.debug(" * Ignoring non-curated relationship '{}'",
							relatedId);
				}
			}
		}
	}

	/**
	 * Processing method
	 * 
	 * @param message
	 *            The JsonSimple message to process
	 * @return JsonSimple The actions to take in response
	 * @throws TransactionException
	 *             If an error occurred
	 */
	@Override
	public JsonSimple parseMessage(JsonSimple message)
			throws TransactionException {
		log.debug("\n{}", message.toString(true));

		// A standard harvest event
		JsonObject harvester = message.getObject("harvester");
		String repoType= message.getString("", "indexer", "params", "repository.type");
		if (harvester != null && !"Attachment".equalsIgnoreCase(repoType)) {
			try {
				String oid = message.getString(null, "oid");
				JsonSimple response = new JsonSimple();
				audit(response, oid, "Tool Chain");

				// Standard transformers... ie. not related to curation
				scheduleTransformers(message, response);

				// Solr Index
				JsonObject order = newIndex(response, oid);
				order.put("forceCommit", true);

				// Send a message back here
				createTask(response, oid, "clear-render-flag");
				return response;
			} catch (Exception ex) {
				throw new TransactionException(ex);
			}
		} else {
			log.debug("Is type attachment, ignoring...");
		}

		// It's not a harvest, what else could be asked for?
		String task = message.getString(null, "task");
		if (task != null) {
			String oid = message.getString(null, "oid");

			// ######################
			// Workflow related events
			if (task.equals("workflow-curation")) {
				JsonSimple response = new JsonSimple();
				workflowCuration(response, message);
				return response;
			}
			if (task.equals("workflow")) {
				JsonSimple response = new JsonSimple();

				String eventType = message.getString(null, "eventType");
				String newStep = message.getString(null, "newStep");
				// The workflow has altered data, run the tool chain
				if (newStep != null || eventType.equals("ReIndex")) {
					// For housekeeping, we need to alter the
					// Solr index fairly speedily
					boolean quickIndex = message
							.getBoolean(false, "quickIndex");
					if (quickIndex) {
						JsonObject order = newIndex(response, oid);
						order.put("forceCommit", true);
					}

					// send a copy to the audit log
					JsonObject order = newSubscription(response, oid);
					JsonObject audit = (JsonObject) order.get("message");
					audit.putAll(message.getJsonObject());

					// Then business as usual
					reharvest(response, message);

					// Once the dust settles come back here
					createTask(response, oid, "workflow-curation");

					// A traditional Subscriber message for audit logs
				} else {
					JsonObject order = newSubscription(response, oid);
					JsonObject audit = (JsonObject) order.get("message");
					audit.putAll(message.getJsonObject());
				}
				return response;
			}

			// ######################
			// Start a reharvest for this object
			if (task.equals("reharvest")) {
				JsonSimple response = new JsonSimple();
				reharvest(response, message);
				return response;
			}

			// ######################
			// Tool chain, clear render flag
			if (task.equals("clear-render-flag")) {
				if (oid != null) {
					clearRenderFlag(oid);
				} else {
					log.error("Cannot clear render flag without an OID!");
				}
			}

			// ######################
			// Curation
			if (task.startsWith("curation")) {
				try {
					if (oid != null) {
						JsonSimple response = curation(message, task, oid);

						// We should always index afterwards
						JsonObject order = newIndex(response, oid);
						order.put("forceCommit", true);
						return response;

					} else {
						log.error("We need an OID to curate!");
					}
				} catch (Exception ex) {
					JsonSimple response = new JsonSimple();
					log.error("Error during curation: ", ex);
					emailObjectLink(response, oid,
							"An unknown error occurred curating this object. "
									+ "Please check the system logs.");
					return response;
				}
			}

			// ######################
			// Publication
			if (task.startsWith("publish")) {
				try {
					if (oid == null) {
						oid = idToOid(message.getString(null, "identifier"));
						// Update out message so the reharvest function gets OID
						if (oid != null) {
							message.getJsonObject().put("oid", oid);
						}
					}
					if (oid != null) {
						JsonSimple response = publish(message, oid);
						// We should always go through the tool chain afterwards
						reharvest(response, message);
						return response;

					} else {
						log.error("We need an OID to publish!");
					}
				} catch (Exception ex) {
					JsonSimple response = new JsonSimple();
					log.error("Error during publication: ", ex);
					emailObjectLink(response, oid,
							"An unknown error occurred publishing this object."
									+ " Please check the system logs.");
					return response;
				}
			}
		}

		// Do nothing
		return new JsonSimple();
	}

	/**
	 * Generate a fairly common list of orders to transform and index an object.
	 * This mirrors the traditional tool chain.
	 * 
	 * @param message
	 *            The response to modify
	 * @param message
	 *            The message we received
	 */
	private void reharvest(JsonSimple response, JsonSimple message) {
		String oid = message.getString(null, "oid");

		try {
			if (oid != null) {
				setRenderFlag(oid);

				// Transformer config
				JsonSimple itemConfig = getConfigFromStorage(oid);
				if (itemConfig == null) {
					log.error("Error accessing item configuration!");
					return;
				}
				itemConfig.getJsonObject().put("oid", oid);

				// Tool chain
				scheduleTransformers(itemConfig, response);
				JsonObject order = newIndex(response, oid);
				order.put("forceCommit", true);
				createTask(response, oid, "clear-render-flag");
			} else {
				log.error("Cannot reharvest without an OID!");
			}
		} catch (Exception ex) {
			log.error("Error during reharvest setup: ", ex);
		}
	}

	/**
	 * Generate an order to send an email to the intended recipient with a link
	 * to an object
	 * 
	 * @param response
	 *            The response to add an order to
	 * @param message
	 *            The message we want to send
	 */
	private void emailObjectLink(JsonSimple response, String oid, String message) {
		String link = urlBase + "default/detail/" + oid;
		String text = "This is an automated message from the ";
		text += "ReDBox Curation Manager.\n\n" + message;
		text += "\n\nYou can find this object here:\n" + link;
		email(response, oid, text);
	}

	/**
	 * Generate an order to send an email to the intended recipient
	 * 
	 * @param response
	 *            The response to add an order to
	 * @param message
	 *            The message we want to send
	 */
	private void email(JsonSimple response, String oid, String text) {
		JsonObject object = newMessage(response,
				EmailNotificationConsumer.LISTENER_ID);
		JsonObject message = (JsonObject) object.get("message");
		message.put("to", emailAddress);
		message.put("body", text);
		message.put("oid", oid);
	}

	/**
	 * Generate an order to add a message to the System's audit log
	 * 
	 * @param response
	 *            The response to add an order to
	 * @param oid
	 *            The object ID we are logging
	 * @param message
	 *            The message we want to log
	 */
	private void audit(JsonSimple response, String oid, String message) {
		JsonObject order = newSubscription(response, oid);
		JsonObject messageObject = (JsonObject) order.get("message");
		messageObject.put("eventType", message);
	}

	/**
	 * Generate orders for the list of normal transformers scheduled to execute
	 * on the tool chain
	 * 
	 * @param message
	 *            The incoming message, which contains the tool chain config for
	 *            this object
	 * @param response
	 *            The response to edit
	 * @param oid
	 *            The object to schedule for clearing
	 */
	private void scheduleTransformers(JsonSimple message, JsonSimple response) {
		String oid = message.getString(null, "oid");
		List<String> list = message.getStringList("transformer", "metadata");
		if (list != null && !list.isEmpty()) {
			for (String id : list) {
				JsonObject order = newTransform(response, id, oid);
				// Add item config to message... if it exists
				JsonObject itemConfig = message.getObject(
						"transformerOverrides", id);
				if (itemConfig != null) {
					JsonObject config = (JsonObject) order.get("config");
					config.putAll(itemConfig);
				}
			}
		}
	}

	/**
	 * Clear the render flag for objects that have finished in the tool chain
	 * 
	 * @param oid
	 *            The object to clear
	 */
	private void clearRenderFlag(String oid) {
		try {
			DigitalObject object = storage.getObject(oid);
			Properties props = object.getMetadata();
			props.setProperty("render-pending", "false");
			object.close();
		} catch (StorageException ex) {
			log.error("Error accessing storage for '{}'", oid, ex);
		}
	}

	/**
	 * Set the render flag for objects that are starting in the tool chain
	 * 
	 * @param oid
	 *            The object to set
	 */
	private void setRenderFlag(String oid) {
		try {
			DigitalObject object = storage.getObject(oid);
			Properties props = object.getMetadata();
			props.setProperty("render-pending", "true");
			object.close();
		} catch (StorageException ex) {
			log.error("Error accessing storage for '{}'", oid, ex);
		}
	}

	/**
	 * Create a task. Tasks are basically just trivial messages that will come
	 * back to this manager for later action.
	 * 
	 * @param response
	 *            The response to edit
	 * @param oid
	 *            The object to schedule for clearing
	 * @param task
	 *            The task String to use on receipt
	 * @return JsonObject Access to the 'message' node of this task to provide
	 *         further details after creation.
	 */
	private JsonObject createTask(JsonSimple response, String oid, String task) {
		return createTask(response, null, oid, task);
	}

	/**
	 * Create a task. This is a more detailed option allowing for tasks being
	 * sent to remote brokers.
	 * 
	 * @param response
	 *            The response to edit
	 * @param broker
	 *            The broker URL to use
	 * @param oid
	 *            The object to schedule for clearing
	 * @param task
	 *            The task String to use on receipt
	 * @return JsonObject Access to the 'message' node of this task to provide
	 *         further details after creation.
	 */
	private JsonObject createTask(JsonSimple response, String broker,
			String oid, String task) {
		JsonObject object = newMessage(response,
				TransactionManagerQueueConsumer.LISTENER_ID);
		if (broker != null) {
			object.put("broker", broker);
		}
		JsonObject message = (JsonObject) object.get("message");
		message.put("task", task);
		message.put("oid", oid);
		return message;
	}

	/**
	 * Creation of new Orders with appropriate default nodes
	 * 
	 */
	private JsonObject newIndex(JsonSimple response, String oid) {
		JsonObject order = createNewOrder(response,
				TransactionManagerQueueConsumer.OrderType.INDEXER.toString());
		order.put("oid", oid);
		return order;
	}

	private JsonObject newMessage(JsonSimple response, String target) {
		JsonObject order = createNewOrder(response,
				TransactionManagerQueueConsumer.OrderType.MESSAGE.toString());
		order.put("target", target);
		order.put("message", new JsonObject());
		return order;
	}

	private JsonObject newSubscription(JsonSimple response, String oid) {
		JsonObject order = createNewOrder(response,
				TransactionManagerQueueConsumer.OrderType.SUBSCRIBER.toString());
		order.put("oid", oid);
		JsonObject message = new JsonObject();
		message.put("oid", oid);
		message.put("context", "Curation");
		message.put("eventType", "Sending test message");
		message.put("user", "system");
		order.put("message", message);
		return order;
	}

	private JsonObject newTransform(JsonSimple response, String target,
			String oid) {
		JsonObject order = createNewOrder(response,
				TransactionManagerQueueConsumer.OrderType.TRANSFORMER
						.toString());
		order.put("target", target);
		order.put("oid", oid);
		JsonObject config = systemConfig.getObject("transformerDefaults",
				target);
		if (config == null) {
			order.put("config", new JsonObject());
		} else {
			order.put("config", config);
		}

		return order;
	}

	private JsonObject createNewOrder(JsonSimple response, String type) {
		JsonObject order = response.writeObject("orders", -1);
		order.put("type", type);
		return order;
	}

	/**
	 * Get the stored harvest configuration from storage for the indicated
	 * object.
	 * 
	 * @param oid
	 *            The object we want config for
	 */
	private JsonSimple getConfigFromStorage(String oid) {
		String configOid = null;
		String configPid = null;

		// Get our object and look for its config info
		try {
			DigitalObject object = storage.getObject(oid);
			Properties metadata = object.getMetadata();
			configOid = metadata.getProperty("jsonConfigOid");
			configPid = metadata.getProperty("jsonConfigPid");
		} catch (StorageException ex) {
			log.error("Error accessing object '{}' in storage: ", oid, ex);
			return null;
		}

		// Validate
		if (configOid == null || configPid == null) {
			log.error("Unable to find configuration for OID '{}'", oid);
			return null;
		}

		// Grab the config from storage
		try {
			DigitalObject object = storage.getObject(configOid);
			Payload payload = object.getPayload(configPid);
			try {
				return new JsonSimple(payload.open());
			} catch (IOException ex) {
				log.error("Error accessing config '{}' in storage: ",
						configOid, ex);
			} finally {
				payload.close();
			}
		} catch (StorageException ex) {
			log.error("Error accessing object in storage: ", ex);
		}

		// Something screwed the pooch
		return null;
	}

	/**
	 * Get the form data from storage for the indicated object and parse it into
	 * a JSON structure.
	 * 
	 * @param oid
	 *            The object we want
	 */
	private JsonSimple parsedFormData(String oid) {
		// Get our data from Storage
		Payload payload = null;
		try {
			DigitalObject object = storage.getObject(oid);
			payload = getDataPayload(object);
		} catch (StorageException ex) {
			log.error("Error accessing object '{}' in storage: ", oid, ex);
			return null;
		}

		// Parse the JSON
		try {
			try {
				return FormDataParser.parse(payload.open());
			} catch (IOException ex) {
				log.error("Error parsing data '{}': ", oid, ex);
				return null;
			} finally {
				payload.close();
			}
		} catch (StorageException ex) {
			log.error("Error accessing data '{}' in storage: ", oid, ex);
			return null;
		}
	}

	/**
	 * Get the stored data from storage for the indicated object.
	 * 
	 * @param oid
	 *            The object we want
	 */
	private JsonSimple getDataFromStorage(String oid) {
		// Get our data from Storage
		Payload payload = null;
		try {
			DigitalObject object = storage.getObject(oid);
			payload = getDataPayload(object);
		} catch (StorageException ex) {
			log.error("Error accessing object '{}' in storage: ", oid, ex);
			return null;
		}

		// Parse the JSON
		try {
			try {
				return new JsonSimple(payload.open());
			} catch (IOException ex) {
				log.error("Error parsing data '{}': ", oid, ex);
				return null;
			} finally {
				payload.close();
			}
		} catch (StorageException ex) {
			log.error("Error accessing data '{}' in storage: ", oid, ex);
			return null;
		}
	}

	/**
	 * Get the metadata properties for the indicated object.
	 * 
	 * @param oid
	 *            The object we want config for
	 */
	private Properties getObjectMetadata(String oid) {
		try {
			DigitalObject object = storage.getObject(oid);
			return object.getMetadata();
		} catch (StorageException ex) {
			log.error("Error accessing object '{}' in storage: ", oid, ex);
			return null;
		}
	}

	/**
	 * Save the provided object data back into storage
	 * 
	 * @param data
	 *            The data to save
	 * @param oid
	 *            The object we want it saved in
	 */
	private void saveObjectData(JsonSimple data, String oid)
			throws TransactionException {
		// Get from storage
		DigitalObject object = null;
		try {
			object = storage.getObject(oid);
			getDataPayload(object);
		} catch (StorageException ex) {
			log.error("Error accessing object '{}' in storage: ", oid, ex);
			throw new TransactionException(ex);
		}

		// Store modifications
		String jsonString = data.toString(true);
		try {
			updateDataPayload(object, jsonString);
		} catch (Exception ex) {
			log.error("Unable to store data '{}': ", oid, ex);
			throw new TransactionException(ex);
		}
	}

	/**
	 * Get the data payload (ending in '.tfpackage') from the provided object.
	 * 
	 * @param object
	 *            The digital object holding our payload
	 * @return Payload The payload requested
	 * @throws StorageException
	 *             if an errors occurs or the payload is not found
	 */
	private JsonSimple getWorkflowData(String oid) {
		// Get our data from Storage
		Payload payload = null;
		try {
			DigitalObject object = storage.getObject(oid);
			payload = object.getPayload(WORKFLOW_PAYLOAD);
		} catch (StorageException ex) {
			log.error("Error accessing object '{}' in storage: ", oid, ex);
			return null;
		}

		// Parse the JSON
		try {
			try {
				return new JsonSimple(payload.open());
			} catch (IOException ex) {
				log.error("Error parsing workflow '{}': ", oid, ex);
				return null;
			} finally {
				payload.close();
			}
		} catch (StorageException ex) {
			log.error("Error accessing workflow '{}' in storage: ", oid, ex);
			return null;
		}
	}

	/**
	 * Get the data payload (ending in '.tfpackage') from the provided object.
	 * 
	 * @param object
	 *            The digital object holding our payload
	 * @return Payload The payload requested
	 * @throws StorageException
	 *             if an errors occurs or the payload is not found
	 */
	private Payload getDataPayload(DigitalObject object)
			throws StorageException {
		for (String pid : object.getPayloadIdList()) {
			if (pid.endsWith(DATA_PAYLOAD_SUFFIX)) {
				return object.getPayload(pid);
			}
		}
		throw new StorageException("Data payload not found on storage!");
	}

	/**
	 * Update the data payload (ending in '.tfpackage') in the provided object.
	 * 
	 * @param object
	 *            The digital object holding our payload
	 * @param input
	 *            The String to store
	 * @throws StorageException
	 *             if an errors occurs or the payload is not found
	 */
	private void updateDataPayload(DigitalObject object, String input)
			throws StorageException {
		try {
			for (String pid : object.getPayloadIdList()) {
				if (pid.endsWith(DATA_PAYLOAD_SUFFIX)) {
					InputStream inStream = new ByteArrayInputStream(
							input.getBytes("UTF-8"));
					object.updatePayload(pid, inStream);
					return;
				}
			}
			throw new StorageException("Data payload not found on storage!");
		} catch (Exception ex) {
			throw new StorageException("Error storing payload data!", ex);
		}
	}
}
