/*
 * The Fascinator - ReDBox - Index Queue Consumer
 * Copyright (C) 2009-2011 University of Southern Queensland
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

import au.edu.usq.fascinator.api.PluginException;
import au.edu.usq.fascinator.api.PluginManager;
import au.edu.usq.fascinator.api.indexer.Indexer;
import au.edu.usq.fascinator.api.indexer.IndexerException;
import au.edu.usq.fascinator.api.storage.DigitalObject;
import au.edu.usq.fascinator.api.storage.Storage;
import au.edu.usq.fascinator.api.transformer.Transformer;
import au.edu.usq.fascinator.api.transformer.TransformerException;
import au.edu.usq.fascinator.common.GenericListener;
import au.edu.usq.fascinator.common.JsonSimple;
import au.edu.usq.fascinator.common.JsonSimpleConfig;
import au.edu.usq.fascinator.common.storage.StorageUtils;

import java.io.IOException;
import javax.jms.Connection;
import javax.jms.JMSException;
import javax.jms.Message;
import javax.jms.MessageConsumer;
import javax.jms.Session;
import javax.jms.TextMessage;

import org.apache.activemq.ActiveMQConnectionFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * A trivial queue consumer to request index events via AMQ.
 *
 * @author Greg Pendlebury
 */
public class IndexQueueConsumer implements GenericListener {

    /** Service Loader will look for this */
    public static final String LISTENER_ID = "indexer";

    /** Render queue string */
    private String QUEUE_ID;

    /** Logging */
    private Logger log = LoggerFactory.getLogger(IndexQueueConsumer.class);

    /** JSON configuration */
    private JsonSimpleConfig globalConfig;

    /** JMS connection */
    private Connection connection;

    /** JMS Session */
    private Session session;

    /** JMS Topic */
    // private Topic broadcast;

    /** Indexer object */
    private Indexer indexer;

    /** Storage object */
    private Storage storage;

    /** Message Consumer instance */
    private MessageConsumer consumer;

    /** Name identifier to be put in the queue */
    private String name;

    /** Thread reference */
    private Thread thread;

    /**
     * Constructor required by ServiceLoader. Be sure to use init()
     *
     */
    public IndexQueueConsumer() {
        thread = new Thread(this, LISTENER_ID);
    }

    /**
     * Start thread running
     *
     */
    @Override
    public void run() {
        try {
            log.info("Starting {}...", name);

            // Get a connection to the broker
            String brokerUrl = globalConfig.getString(
                    ActiveMQConnectionFactory.DEFAULT_BROKER_BIND_URL,
                    "messaging", "url");
            ActiveMQConnectionFactory connectionFactory =
                    new ActiveMQConnectionFactory(brokerUrl);
            connection = connectionFactory.createConnection();
            // Set ourselves up as a listener
            session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);
            consumer = session.createConsumer(session.createQueue(QUEUE_ID));
            consumer.setMessageListener(this);
            connection.start();
        } catch (JMSException ex) {
            log.error("Error starting message thread!", ex);
        }
    }

    /**
     * Initialization method
     *
     * @param config Configuration to use
     * @throws IOException if the configuration file not found
     */
    @Override
    public void init(JsonSimpleConfig config) throws Exception {
        name = config.getString(null, "config", "name");
        QUEUE_ID = name;
        thread.setName(name);

        try {
            globalConfig = new JsonSimpleConfig();
            indexer = PluginManager.getIndexer(
                    globalConfig.getString("solr", "indexer", "type"));
            indexer.init(JsonSimpleConfig.getSystemFile());
            storage = PluginManager.getStorage(
                    globalConfig.getString("file-system", "storage", "type"));
            storage.init(JsonSimpleConfig.getSystemFile());
        } catch (IOException ioe) {
            log.error("Failed to read configuration: {}", ioe.getMessage());
            throw ioe;
        } catch (PluginException pe) {
            log.error("Failed to initialise plugin: {}", pe.getMessage());
            throw pe;
        }
    }

    /**
     * Return the ID string for this listener
     *
     */
    @Override
    public String getId() {
        return LISTENER_ID;
    }

    /**
     * Start the queue based on the name identifier
     *
     * @throws JMSException if an error occurred starting the JMS connections
     */
    @Override
    public void start() throws Exception {
        thread.start();
    }

    /**
     * Stop the Queue Consumer. Including all instantiated plugins
     */
    @Override
    public void stop() throws Exception {
        log.info("Stopping {}...", name);
        if (indexer != null) {
            try {
                indexer.shutdown();
            } catch (PluginException pe) {
                log.error("Failed to shutdown indexer: {}", pe.getMessage());
                throw pe;
            }
        }
        if (storage != null) {
            try {
                storage.shutdown();
            } catch (PluginException pe) {
                log.error("Failed to shutdown storage: {}", pe.getMessage());
                throw pe;
            }
        }
        if (consumer != null) {
            try {
                consumer.close();
            } catch (JMSException jmse) {
                log.warn("Failed to close consumer: {}", jmse.getMessage());
                throw jmse;
            }
        }
        if (session != null) {
            try {
                session.close();
            } catch (JMSException jmse) {
                log.warn("Failed to close consumer session: {}", jmse);
            }
        }
        if (connection != null) {
            try {
                connection.close();
            } catch (JMSException jmse) {
                log.warn("Failed to close connection: {}", jmse);
            }
        }
    }

    /**
     * Callback function for incoming messages.
     *
     * @param message The incoming message
     */
    @Override
    public void onMessage(Message message) {
        MDC.put("name", name);
        try {
            // Make sure thread priority is correct
            if (!Thread.currentThread().getName().equals(thread.getName())) {
                Thread.currentThread().setName(thread.getName());
                Thread.currentThread().setPriority(thread.getPriority());
            }

            // Get the message deatils
            String text = ((TextMessage) message).getText();
            JsonSimple config = new JsonSimple(text);
            String oid = config.getString(null, "oid");
            log.info("Received job, object id={}", oid);

            // Transform the object, to update our payloads
            log.info("Transforming object '{}'...", oid);
            DigitalObject object = StorageUtils.getDigitalObject(storage, oid);
            Transformer transformer = PluginManager.getTransformer("jsonVelocity");
            transformer.init(JsonSimpleConfig.getSystemFile());
            transformer.transform(object, "{}");

            // Index the object
            log.info("Indexing object '{}'...", oid);
            indexer.index(oid);
            if (config.getBoolean(true, "commit")) {
                indexer.commit();
            }
    } catch (JMSException jmse) {
            log.error("Failed to send/receive message: {}", jmse.getMessage());
        } catch (IOException ioe) {
            log.error("Failed to parse message: {}", ioe.getMessage());
        } catch (TransformerException te) {
            log.error("Failed to transform object: {}", te.getMessage());
        } catch (IndexerException ie) {
            log.error("Failed to index object: {}", ie.getMessage());
        } catch (Exception e) {
            log.error("Unknown error: {}", e.getMessage());
        }
    }

    /**
     * Sets the priority level for the thread. Used by the OS.
     *
     * @param newPriority The priority level to set the thread at
     */
    @Override
    public void setPriority(int newPriority) {
        if (newPriority >= Thread.MIN_PRIORITY
                && newPriority <= Thread.MAX_PRIORITY) {
            thread.setPriority(newPriority);
        }
    }
}
