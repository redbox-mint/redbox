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

import com.googlecode.fascinator.common.JsonSimple;
import java.io.InputStream;
import org.junit.Assert;
import org.junit.Test;

/**
 * Trivial unit test to ensure parser can read expected files and return
 * sensible values
 *
 * @author Greg Pendlebury
 */
public class FormDataParserTest {
    @Test
    public void parseTest() throws Exception {
        InputStream in = getClass().getResourceAsStream("/test.tfpackage");
        JsonSimple formData = FormDataParser.parse(in);

        // Basics
        Assert.assertEquals("Complete dataset example",
                formData.getString(null, "title"));
        Assert.assertEquals("This is the description of a complete dataset",
                formData.getString(null, "description"));
        Assert.assertEquals("2011-10-04",
                formData.getString(null, "dc:created"));
        Assert.assertEquals("",
                formData.getString(null, "dc:Policy"));

        // Nested Objects
        Assert.assertEquals("dataset",
                formData.getString(null,
                    "dc:type", "rdf:PlainLiteral"));
        Assert.assertEquals("2011-10-04",
                formData.getString(null,
                    "dc:coverage", "vivo:DateTimeInterval", "vivo:start"));
        Assert.assertEquals("redbox-mint.googlecode.com/parties/people/1242",
                formData.getString(null,
                    "locrel:prc", "foaf:Person", "dc:identifier"));
        Assert.assertEquals("Access Rights",
                formData.getString(null,
                    "dc:accessRights", "rdf:PlainLiteral"));

        // Arrays
        Assert.assertEquals("",
                formData.getString(null,
                    "dc:coverage", "vivo:GeographicLocation", 0, "dc:type"));
        Assert.assertEquals("Related Publication",
                formData.getString(null,
                    "dc:relation", "swrc:Publication", 0, "dc:title"));
        Assert.assertEquals("redbox-mint.googlecode.com/parties/people/1237",
                formData.getString(null,
                    "dc:creator", "foaf:Person", 1, "dc:identifier"));
        Assert.assertEquals("redbox-mint.googlecode.com/parties/people/1241",
                formData.getString(null,
                    "dc:creator", "foaf:Person", 2, "dc:identifier"));
    }
}
