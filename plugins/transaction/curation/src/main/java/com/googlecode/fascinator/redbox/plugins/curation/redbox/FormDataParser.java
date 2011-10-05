/*
 * The Fascinator - Form Data Parser
 * Copyright (C) 2011 Queensland Cyber Infrastructure Foundation (http://www.qcif.edu.au/)
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

import com.googlecode.fascinator.common.JsonObject;
import com.googlecode.fascinator.common.JsonSimple;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.List;

import org.json.simple.JSONArray;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The purpose of this class is to parse ReDBox form data packages and break the
 * the complicated String field names into meaningful JSON data structures that
 * are easier to traverse and interrogate.
 *
 * @author Greg Pendlebury
 */
public class FormDataParser {
    /** Logging **/
    private static Logger log = LoggerFactory.getLogger(FormDataParser.class);

    /** Excluded top level nodes from parse */
    private static final List<String> EXCLUDED_FIELDS =
            Arrays.asList("metaList", "relationships", "responses");

    /**
     * A wrapper for Stream based parsing. This method accepts a String and
     * will internally create a Stream for it.
     *
     * @param input The form data to parse from a String
     * @return JsonSimple The parsed form data in JSON
     * @throws IOException if there are errors reading/parsing the form data
     */
    public static JsonSimple parse(String input) throws IOException {
        ByteArrayInputStream bytes = new ByteArrayInputStream(
                input.getBytes("UTF-8"));
        return parse(bytes);
    }

    /**
     * Accept and parse raw JSON data from an InputStream. Field name String
     * literals will be broken down into meaningful JSON data structures.
     *
     * @param input The form data to parse from an InputStream
     * @return JsonSimple The parsed form data in JSON
     * @throws IOException if there are errors reading/parsing the form data
     */
    public static JsonSimple parse(InputStream input) throws IOException {
        JsonSimple inputData = new JsonSimple(input);
        JsonSimple responseData = new JsonSimple();

        // Go through every top level node
        JsonObject object = inputData.getJsonObject();
        for (Object key : object.keySet()) {
            // Ignoring some non-form related nodes
            String strKey = validString(key);
            if (!EXCLUDED_FIELDS.contains(strKey)) {
                // And parse them into the repsonse
                String data = validString(object.get(key));
                parseField(responseData, strKey, data);
            }
        }
        return responseData;
    }

    /**
     * Ensures one of the generic objects coming from the JSON library
     * is in fact a String.
     *
     * @param data The generic object
     * @return String The String instance of the object
     * @throws IOException if the object is not a String
     */
    private static String validString(Object data) throws IOException {
        // Null is ok
        if (data == null) {
            return "";
        }
        if (!(data instanceof String)) {
            throw new IOException("Invalid non-String value found!");
        }
        return (String) data;
    }

    /**
     * Parse an individual field into the response object.
     *
     * @param response The response JSON data structure being built.
     * @param field The current field name to parse
     * @param data The data contained in this current field
     * @throws IOException if errors occur during the parse
     */
    private static void parseField(JsonSimple response, String field,
            String data) throws IOException {
        // Break it into pieces
        String [] fieldParts = field.split("\\.");
        // These are used as replacable pointers
        //  to the last object used on the path
        JsonObject lastObject = null;
        JSONArray lastArray = null;

        for (int i = 0; i < fieldParts.length; i++) {
            // What is this segment?
            String segment = fieldParts[i];
            int number = parseInt(segment);

            //**************************
            // 1 (of 3) The first segment adds our
            //    new empty object to the repsonse
            if (i == 0) {
                JsonObject topObject = response.getJsonObject();
                // Numbers aren't allowed here
                if (number != -1) {
                    throw new IOException("Field '" + field + "' starts with"
                            + " an array... this is illegal form data!");
                }

                // Really simple fields... just one segment
                if (i + 1 == fieldParts.length) {
                    topObject.put(segment, data);


                // Longer field, but what to add?
                } else {
                    String nextSegment = fieldParts[i + 1];
                    int nextNumber = parseInt(nextSegment);

                    // Objects... nextSegment is a String key
                    if (nextNumber == -1) {
                        lastObject = getObject(topObject, segment);
                        lastArray = null;

                    // Arrays... nextSegment is an integer index 
                    } else {
                        lastObject = null;
                        lastArray = getArray(topObject, segment);
                    }
                }

            } else {
                //**************************
                // 2 (of 3) The last segment is pretty simple
                if (i == (fieldParts.length - 1)) {
                    lastObject.put(segment, data);

                //**************************
                // 3 (of 3) Anything in between
                } else {
                    // Check what comes next
                    String nextSegment = fieldParts[i + 1];
                    int nextNumber = parseInt(nextSegment);

                    // We are populating an object
                    if (lastArray == null) {
                        // So we shouldn't be looking at a number
                        if (number != -1) {
                            // In theory you'd need a logic bug to reach here;
                            // illegal syntax should have been caught already.
                            throw new IOException("Field '" + field + "' has an"
                                    + " illegal syntax!");
                        }

                        // Objects... nextSegment is a String key
                        if (nextNumber == -1) {
                            lastObject = getObject(lastObject, segment);
                            lastArray = null;

                        // Arrays... nextSegment is an integer index 
                        } else {
                            lastArray = getArray(lastObject, segment);
                            lastObject = null;
                        }

                    // Populating an array
                    } else {
                        // We should be looking at number
                        if (number == -1) {
                            // In theory you'd need a logic bug to reach here;
                            // illegal syntax should have been caught already.
                            throw new IOException("Field '" + field + "' has an"
                                    + " illegal syntax!");
                        }

                        // This is actually quite simple, because we can only
                        //  store objects. 
                        lastObject = getObject(lastArray, number);
                        lastArray = null;
                    }
                }
            }
        }
    }

    /**
     * Get a child JSON Object from an incoming JSON array. If the child does
     * not exist it will be created, along with any smaller index values. The
     * index is expected to be 1 based (like form data).
     * 
     * It is only valid for form arrays to hold JSON Objects.
     * 
     * @param array The incoming array we are to look inside
     * @param index The child index we are looking for (1 based)
     * @return JsonObject The child we found or created
     * @throws IOException if anything other than an object is found, or an
     * invalid index is provided
     */
    private static JsonObject getObject(JSONArray array, int index)
            throws IOException {
        // We can't just jam an entry into the array without
        //  checking that earlier indexes exist. Also we need
        //  to account for 0 versus 1 based indexing.

        // Index changed to 0 based
        if (index < 1) {
            throw new IOException("Invalid index value provided in form data.");
        }
        index -= 1;

        // Nice and easy, it already exists
        if (array.size() > index) {
            Object object = array.get(index);
            if (object instanceof JsonObject) {
                return (JsonObject) object;
            }
            throw new IOException("Non-Object found in array!");

        // Slightly more annoying, we need to fill in
        //  all the indices up to this point
        } else {
            for (int i = array.size(); i <= index; i++) {
                JsonObject object = new JsonObject();
                array.add(object);
            }
            return (JsonObject) array.get(index);
        }
    }

    /**
     * Get a child JSON Array from an incoming JSON object. If the child does
     * not exist it will be created.
     *
     * @param object The incoming object we are to look inside
     * @param key The child node we are looking for
     * @return JSONArray The child we found or created
     * @throws IOException if there is a type mismatch on existing data
     */
    private static JSONArray getArray(JsonObject object, String key)
            throws IOException {
        // Get the existing one
        if (object.containsKey(key)) {
            Object existing = object.get(key);
            if (!(existing instanceof JSONArray)) {
                throw new IOException("Invalid field structure, '" + key +
                        "' expected to be an array, but incompatible "
                        + "data type already present.");
            }
            return (JSONArray) existing;

        // Or add a new one
        } else {
            JSONArray newObject = new JSONArray();
            object.put(key, newObject);
            return newObject;
        }
    }

    /**
     * Get a child JSON Object from an incoming JSON object. If the child does
     * not exist it will be created.
     *
     * @param object The incoming object we are to look inside
     * @param key The child node we are looking for
     * @return JsonObject The child we found or created
     * @throws IOException if there is a type mismatch on existing data
     */
    private static JsonObject getObject(JsonObject object, String key)
            throws IOException {
        // Get the existing one
        if (object.containsKey(key)) {
            Object existing = object.get(key);
            if (!(existing instanceof JsonObject)) {
                throw new IOException("Invalid field structure, '" + key +
                        "' expected to be an object, but incompatible "
                        + "data type already present.");
            }
            return (JsonObject) existing;

        // Or add a new one
        } else {
            JsonObject newObject = new JsonObject();
            object.put(key, newObject);
            return newObject;
        }
    }

    /**
     * Parse a String to an integer. This wrapper is simply to avoid the try
     * catch statement repeatedly. Tests for -1 are sufficient, since it is
     * illegal in form data. Valid integers below 1 throw exceptions because
     * of this illegality.
     *
     * @param integer The incoming integer to parse
     * @return int The parsed integer, or -1 if it is not an integer
     * @throws IOException if errors occur during the parse
     */
    private static int parseInt(String integer) throws IOException {
        try {
            int value = Integer.parseInt(integer);
            if (value < 0) {
                throw new IOException("Invalid number in field name: '"
                        + integer + "'");
            }
            return value;
        } catch (NumberFormatException ex) {
            // It's not an integer
            return -1;
        }
    }
}
