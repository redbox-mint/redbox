/*
 * Copyright (C) 2018 Queensland Cyber Infrastructure Foundation (http://www.qcif.edu.au/)
 *
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License along
 *   with this program; if not, write to the Free Software Foundation, Inc.,
 *   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
 */

package au.com.redboxresearchdata.rifcs.transformer

import com.googlecode.fascinator.common.storage.impl.GenericDigitalObject
import groovy.util.logging.Slf4j
import org.ands.rifcs.base.Constants
import org.ands.rifcs.base.RIFCS
import org.ands.rifcs.base.RIFCSException
import org.ands.rifcs.base.RIFCSWrapper
import org.ands.rifcs.base.RegistryObject
import org.joda.time.DateTimeZone
import org.w3c.dom.DOMConfiguration
import org.w3c.dom.DOMImplementation
import org.w3c.dom.Document
import org.w3c.dom.Element
import org.w3c.dom.ls.DOMImplementationLS
import org.w3c.dom.ls.LSOutput
import org.w3c.dom.ls.LSSerializer
import spock.lang.Shared
import spock.lang.Specification
import spock.lang.Unroll

import javax.xml.XMLConstants
import javax.xml.parsers.DocumentBuilder
import javax.xml.parsers.DocumentBuilderFactory
import javax.xml.parsers.ParserConfigurationException
import javax.xml.transform.dom.DOMSource
import javax.xml.validation.Schema
import javax.xml.validation.SchemaFactory
import javax.xml.validation.Validator

/**
 * @author <a href="matt@redboxresearchdata.com.au">Matt Mulholland</a>
 * created on 11/05/16.
 */
@Slf4j
class RifcsScriptTest extends Specification {
    @Shared
            loader = new GroovyClassLoader(getClass().getClassLoader())
    @Shared
            scriptLocation = loader.getResource("home/scripts/tfpackageToRifcs.groovy").text
    @Shared
            scriptClass = new GroovyShell().parse(scriptLocation).class


    def "Basic RIFCSWrapper generates registryObjects NS, but without leading '?xml' declaration"() {
        def tfpackage = tfpackageToRifcs()
        tfpackage.overrideRIFCSWrapper()
        RIFCSWrapper wrapper = new RIFCSWrapper();
        def result = tfpackage.prettyPrint(wrapper)
        log.info(result)

        expect:
        result == stubEmptyXmlRegistryObjectsDoc()

    }

    def "Rifcs transform"() {
        DateTimeZone.setDefault(DateTimeZone.forID("Australia/Brisbane"))
        def currentZone = DateTimeZone.getDefault()
        log.info("current zone is: " + currentZone)
        def rifcs = tfpackageToRifcs().transform()
        expect:
        rifcs == stubRifcsOutput()
    }

    def "Rifcs transform invalid"() {
        DateTimeZone.setDefault(DateTimeZone.forID("Australia/Brisbane"))
        def currentZone = DateTimeZone.getDefault()
        log.info("current zone is: " + currentZone)
        def rifcs = tfpackageToInvalidRifcs().transform()
        expect:
        rifcs == stubRifcsOutputThatHasInvalidXml()
    }

    @Unroll
    def "Date string from date texts"() {
        given:
        DateTimeZone.setDefault(DateTimeZone.forID("Australia/Brisbane"))
        def currentZone = DateTimeZone.getDefault()
        log.info("current zone is: " + currentZone)
        when:
        def result = tfpackageToRifcs().getISO8601DateString(dateText)
        then:
        assert expected == result
        noExceptionThrown()
        where:
        dateText                    | expected
        "2004"                      | "2004-01-01T00:00:00.000+10:00"
        "20040102"                  | "20040102-01-01T00:00:00.000+10:00"
        "2004-01-02"                | "2004-01-02T00:00:00.000+10:00"
        "2004-04-02T18:06"          | "2004-04-02T18:06:00.000+10:00"
        "2004-04-02T18:06:02"       | "2004-04-02T18:06:02.000+10:00"
        "2004-04-02T18:06:02.012"   | "2004-04-02T18:06:02.012+10:00"
        "2004-04-02T18:06:02.01234" | "2004-04-02T18:06:02.012+10:00"
        "2004-04-02T18:06:02z"      | "2004-04-03T04:06:02.000+10:00"
        "2004-04-02T18:06:02.000Z"  | "2004-04-03T04:06:02.000+10:00"
        "2004-04-02T18:06:02+10:00" | "2004-04-02T18:06:02.000+10:00"
    }

    @Unroll
    def "Date string from blank"() {
        when:
        def result = tfpackageToRifcs().getISO8601DateString(dateText)
        then:
        result == expected
        noExceptionThrown()
        where:
        dateText | expected
        null     | null
        ""       | null
        "  "     | null
    }

    @Unroll
    def "Date from text returns exceptions"() {
        when:
        def result = tfpackageToRifcs().getISO8601DateString(dateText)
        then:
        Exception e = thrown()
        e.getClass() == expected
        where:
        dateText | expected
        "test"   | IllegalArgumentException
    }

    @Unroll
    def "Relations returns collection for all valid relationships"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackageStub)).getAllRelations()
        then:
        result.size() == size
        def actualTypes = result.collect { k, v ->
            v.collect {
                it.type
            }
        }.flatten()
        actualTypes == type
        def actualDescription = result.collect { k, v ->
            v.collect {
                it.description
            }
        }.flatten()
        actualDescription == description
        where:
        size << [5, 1, 2]
        key << [["http://demo.redboxresearchdata.com.au/mint/published/detail/84176738cc5e80306afc7adb163a4bab", "http://nla.gov.au/nla.party-965000"], ["foo"], ["foo"]]
        type << [["hasCollector", "hasAssociationWith", "hasCollector", "hasCollector", "hasCollector"], ["hasFooBar"], ["hasFooBar", "hasFooBar2"]]
        description << [[null, null, null, null, null], ["bar"], ["bar", "bar2"]]
        tfpackageStub << [
                stubTfpackage(),
                "{\n" +
                        "  \"relationships\": [\n" +
                        "    {\n" +
                        "      \"relationship\": \"hasFooBar\"," +
                        "      \"description\": \"bar\"," +
                        "      \"isCurated\": true," +
                        "      \"curatedPid\": \"foo\"" +
                        "    }\n" +
                        "  ]\n" +
                        "}",
                "{\n" +
                        "  \"relationships\": [\n" +
                        "    {\n" +
                        "      \"relationship\": \"hasFooBar\"," +
                        "      \"description\": \"bar\"," +
                        "      \"isCurated\": true," +
                        "      \"curatedPid\": \"foo\"" +
                        "    }\n" +
                        "," +
                        "    {\n" +
                        "      \"relationship\": \"hasFooBar2\"," +
                        "      \"description\": \"bar2\"," +
                        "      \"isCurated\": true," +
                        "      \"curatedPid\": \"foo2\"" +
                        "    }\n" +
                        "  ]\n" +
                        "}"
        ]
    }

    @Unroll
    def "Relations returns single collection for all valid relationships with identical key"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackageStub)).getAllRelations()
        def firstResult = result["foo"][0]
        def secondResult = result["foo"][1]
        then:
        result.size() == 1
        result.containsKey("foo")
        firstResult.type == "hasFooBar"
        firstResult.description == "bar"
        secondResult.type == "hasFooBar2"
        secondResult.description == "bar2"
        where:
        tfpackageStub << [
                "{\n" +
                        "  \"relationships\": [\n" +
                        "    {\n" +
                        "      \"relationship\": \"hasFooBar\"," +
                        "      \"description\": \"bar\"," +
                        "      \"isCurated\": true," +
                        "      \"curatedPid\": \"foo\"" +
                        "    }\n" +
                        "," +
                        "    {\n" +
                        "      \"relationship\": \"hasFooBar2\"," +
                        "      \"description\": \"bar2\"," +
                        "      \"isCurated\": true," +
                        "      \"curatedPid\": \"foo\"" +
                        "    }\n" +
                        "  ]\n" +
                        "}"
        ]
    }

    @Unroll
    def "Relations returns empty if not curated or no curated pid"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackageStub)).getAllRelations()
        then:
        result.size() == 0
        where:
        tfpackageStub << [
                "{\n" +
                        "  \"relationships\": [\n" +
                        "    {\n" +
                        "      \"relationship\": \"hasFooBar\"," +
                        "      \"description\": \"bar\"," +
                        "      \"curatedPid\": \"foo\"" +
                        "    }\n" +
                        "  ]\n" +
                        "}"
                ,
                "{\n" +
                        "  \"relationships\": [\n" +
                        "    {\n" +
                        "      \"relationship\": \"hasFooBar\"," +
                        "      \"description\": \"bar\"," +
                        "      \"isCurated\": true,\n" +
                        "    }\n" +
                        "  ]\n" +
                        "}"
                ,
                "{\n" +
                        "  \"relationships\": [\n" +
                        "    {\n" +
                        "      \"relationship\": \"hasFooBar\"," +
                        "      \"description\": \"bar\"," +
                        "      \"isCurated\": false,\n" +
                        "      \"curatedPid\": \"foo\"" +
                        "    }\n" +
                        "  ]\n" +
                        "}"
                ,
                "{\n" +
                        "  \"relationships\": [\n" +
                        "    {\n" +
                        "      \"relationship\": \"hasFooBar\"," +
                        "      \"description\": \"bar\"," +
                        "      \"isCurated\": true,\n" +
                        "    }\n" +
                        "," +
                        "    {\n" +
                        "      \"relationship\": \"hasFooBar\"," +
                        "      \"description\": \"bar\"," +
                        "      \"isCurated\": false,\n" +
                        "      \"curatedPid\": \"foo\"" +
                        "    }\n" +
                        "  ]\n" +
                        "}"
        ]
    }

    @Unroll
    def "collection name exists in valid RIF-CS xml where dc:title exists in tfpackage"() {
        when:
        def rifcs = tfpackageToRifcs(stubDigitalObject(tfpackage)).transform()
        def sanitised = preXmlHandle(rifcs)
        // the sanitising result doesn't matter - we just don't want invalid xml from another entity we don't care about for this test
        def registryObjects = new XmlSlurper().parseText(sanitised);
        then:
        registryObjects.registryObject.collection.name.namePart == "Research Data Collection"
        registryObjects.registryObject.collection.name.@type == "primary"
        where:
        tfpackage << ["{\n" +
                              "  \"dc:type.rdf:PlainLiteral\": \"collection\",\n" +
                              "  \"dc:title\": \"Research Data Collection\",\n" +
                              "}"]
    }

    @Unroll
    def "collection name does NOT exist in valid RIF-CS xml where NO dc:title exists in tfpackage"() {
        when:
        def rifcs = tfpackageToRifcs(stubDigitalObject(tfpackage)).transform()
        def sanitised = preXmlHandle(rifcs)
        // the sanitising result doesn't matter - we just don't want invalid xml from another entity we don't care about for this test
        def registryObjects = new XmlSlurper().parseText(sanitised);
        then:
        registryObjects.registryObject.collection.name.size() == 0
        where:
        tfpackage << ["{\n" +
                              "  \"dc:type.rdf:PlainLiteral\": \"collection\",\n" +
                              "}"]
    }

    def preXmlHandle(xml) {
        def pass1 = xml.replaceAll("&Invalid XML placeholder... prevents ANDS Harvesting records in error&", "dummyinvalidxmlmarker1")
        def pass2 = pass1.replaceAll("&Invalid ID: Not curated yet&", "dummyinvalidxmlmarker2")
        return pass2
    }

    def postXmlHandle(xml) {
        def pass1 = xml.replaceAll("dummyinvalidxmlmarker1", "&Invalid XML placeholder... prevents ANDS Harvesting records in error&")
        def pass2 = pass1.replaceAll("dummyinvalidxmlmarker2", "&Invalid ID: Not curated yet&")
        return pass2
    }

    def "identifier and identifier type"() {
        when:

        def identiferData = tfpackageToRifcs(stubDigitalObject(tfpackage, metadata), config).createIdentifierData();
        then:
        identiferData.identifier == identifier
        identiferData.identifierType == identifierType
        where:
        tfpackage =
                '''{
                          "dc:type.rdf:PlainLiteral": "collection",
                          "dc:identifier.redbox:origin": "internal"
                         }'''

        metadata = '''objectId=df96891d804da76bf2f30fb253d4aebb
                   localPid=http\\://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb'''
        config =
                '''{
            "curation": {
                "pidType": "local",
                "pidProperty": "localPid"
                },
            "identity": {
                "RIF_CSGroup": "The University of Examples, Australia",
                },
            "urlBase": "http://demo.redboxresearchdata.com.au/redbox/default"
        }'''

        identifier = "http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb"
        identifierType = "local"

    }

    def "identifier and identifier type where config has NO curation attributes"() {
        when:

        def identiferData = tfpackageToRifcs(stubDigitalObject(tfpackage, metadata), config).createIdentifierData();
        then:
        identiferData.identifier == identifier
        identiferData.identifierType == identifierType
        where:
        tfpackage =
                '''{
                          "dc:type.rdf:PlainLiteral": "collection",
                          "dc:identifier.redbox:origin": "internal",
                           "metadata": {
                            "rdf:resource" : "metadatardfresource"
                          }
                         }'''
        metadata = '''objectId=df96891d804da76bf2f30fb253d4aebb
                   localPid=http\\://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb'''
        config =
                '''{
            "identity": {
                "RIF_CSGroup": "The University of Examples, Australia",
                },
            "urlBase": "http://demo.redboxresearchdata.com.au/redbox/foobar"
        }'''
        identifier = "metadatardfresource"
        identifierType = "&Invalid XML placeholder... prevents ANDS Harvesting records in error&"

    }

    @Unroll
    def "identifier and identifier type where redbox origin is NOT internal"() {
        when:
        def identiferData = tfpackageToRifcs(stubDigitalObject(tfpackage, metadata), config).createIdentifierData();
        then:
        identiferData.identifier == identifier
        identiferData.identifierType == identifierType
        where:
        tfpackage << [
                '''{
                          "dc:type.rdf:PlainLiteral": "collection",
                          "dc:identifier.redbox:origin": "foo",
                          "dc:identifier.rdf:PlainLiteral": "bar",
                          "dc:identifier.dc:type.rdf:PlainLiteral": "handle"
                         }''',
                '''{
                          "dc:type.rdf:PlainLiteral": "collection",
                          "dc:identifier.redbox:origin": "foo",
                          }''',
                '''{
                          "dc:type.rdf:PlainLiteral": "collection",
                          "dc:identifier.redbox:origin": "foo",
                          "dc:identifier.rdf:PlainLiteral": "bar",
                         }'''
        ]
        metadata = '''objectId=df96891d804da76bf2f30fb253d4aebb
                   localPid=http\\://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb'''
        config << ['''{
            "curation": {
                "pidType": "local",
                "pidProperty": "localPid"
                },
            "identity": {
                "RIF_CSGroup": "The University of Examples, Australia",
                },
            "urlBase": "http://demo.redboxresearchdata.com.au/redbox/default"
        }'''].multiply(3).flatten()

        identifier << ["bar", "&Invalid ID: Not curated yet&", "bar"]
        identifierType << ["handle", "invalid", null]

    }

    @Unroll
    def "identifier and identifier type where config has no pidProperty"() {
        when:

        def identiferData = tfpackageToRifcs(stubDigitalObject(tfpackage, metadata), config).createIdentifierData();
        then:
        identiferData.identifier == identifier
        identiferData.identifierType == identifierType
        where:
        tfpackage << [
                '''{
                          "dc:type.rdf:PlainLiteral": "collection",
                          "dc:identifier.redbox:origin": "internal",
                          "metadata": {
                            "rdf:resource" : "metadatardfresource"
                          }
                         }''',
                '''{
                          "dc:type.rdf:PlainLiteral": "collection",
                          "dc:identifier.redbox:origin": "internal",
                          "metadata": {
                            "dc.identifier" : "metadatadcidentifier"
                          }
                         }''',
                '''{
                          "dc:type.rdf:PlainLiteral": "collection",
                          "dc:identifier.redbox:origin": "internal",
                         }'''
        ]
        metadata = '''objectId=df96891d804da76bf2f30fb253d4aebb
                   localPid=http\\://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb'''
        config << [['''{
            "curation": {
                "pidType": "local"
                },
            "identity": {
                "RIF_CSGroup": "The University of Examples, Australia",
                },
            "urlBase": "http://demo.redboxresearchdata.com.au/redbox/foobar"
        }'''].multiply(3),
        ].flatten()

        identifier << ["metadatardfresource", "metadatadcidentifier", "http://demo.redboxresearchdata.com.au/redbox/foobar/detail/df96891d804da76bf2f30fb253d4aebb"]
        identifierType << ["local", "local", "uri"]

    }

    def "json"() {
        when:
        def result = tfpackageToRifcs().parseJson(stubTfpackage())
        then:
        result in Map
    }

    def "electronicAddress"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackage)).getAllElectronicAddress()
        then:
        result << [["http://www.google.com", "http://www.foo.bar", null],
                   ["http://www.google.com", "http://www.foo.bar", "http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb"]
        ]
        where:
        tfpackage << ['''{
                        "dc:type.rdf:PlainLiteral": "collection",
                        "bibo:Website.1.dc:identifier": "http://www.google.com",
                        "bibo:Website.2.dc:identifier": "http://www.foo.bar",
                        "recordAsLocationDefault": "http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb"
        }''',
                      '''{
                        "dc:type.rdf:PlainLiteral": "collection",
                        "bibo:Website.1.dc:identifier": "http://www.google.com",
                        "bibo:Website.2.dc:identifier": "http://www.foo.bar",
                        "recordAsLocationDefault": "http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb"
        }''']
    }

    def "subject"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackage)).getAllSubjects()
        then:
        result == [[value: "keywords", type: "local"], [value: "0402", type: "anzsrc-for"], [value: "820102", type: "anzsrc-seo"]]
        where:
        tfpackage = '''{
                        "dc:subject.vivo:keyword.1.rdf:PlainLiteral": "keywords",
                        "dc:subject.anzsrc:for.1.skos:prefLabel": "0402 - Geochemistry",
                        "dc:subject.anzsrc:for.1.rdf:resource": "http://purl.org/asc/1297.0/2008/for/0402",
                        "dc:subject.anzsrc:seo.1.skos:prefLabel": "820102 - Harvesting and Transport of Forest Products",
                        "dc:subject.anzsrc:seo.1.rdf:resource": "http://purl.org/asc/1297.0/2008/seo/820102"
        }'''
    }

    def "description"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackage)).getAllDescriptions()
        then:
        result == expectedResult
        where:
        tfpackage << ['''{
                        "dc:description.1.text": "The description",
                        "dc:description.1.type": "full",
                        }''',
                      '''{
                        "dc:description.1.text": "descriptiona",
                        "dc:description.1.type": "full",
                        "dc:description.2.text": "descriptionb",
                        "dc:description.2.type": "brief",
                        }''',
                      '''{
                        "dc:description.1.text": "",
                        "dc:description.1.type": "",
        }''']
        expectedResult << [[[value: "The description", type: "full"]],
                           [[value: "descriptiona", type: "full"], [value: "descriptionb", type: "brief"]],
                           []
        ]
    }

    def "geoSpatialCoverage"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackage)).getAllGeoSpatialCoverage()
        then:
        result == expectedResult
        where:
        tfpackage << ['''{
                      "dc:coverage.vivo:GeographicLocation.1.dc:type": "text",
                      "dc:coverage.vivo:GeographicLocation.1.redbox:wktRaw": "POLYGON((142.78350830078 -45.766200546705,132.78350830078 -16.452951287538,152.62725830079 -36.452951287538,152.62725830079 -45.766200546705,142.78350830078 -45.766200546705))",
                      "dc:coverage.vivo:GeographicLocation.1.rdf:PlainLiteral": "POLYGON((142.78350830078 -45.766200546705,132.78350830078 -16.452951287538,152.62725830079 -36.452951287538,152.62725830079 -45.766200546705,142.78350830078 -45.766200546705))",
                      "dc:coverage.vivo:GeographicLocation.1.geo:long": "180",
                      "dc:coverage.vivo:GeographicLocation.1.geo:lat": "170",
                      "dc:coverage.vivo:GeographicLocation.1.dc:identifier": ""
        }''', '''{
                      "dc:coverage.vivo:GeographicLocation.1.dc:type": "text",
                      "dc:coverage.vivo:GeographicLocation.1.redbox:wktRaw": "Brisbane",
                      "dc:coverage.vivo:GeographicLocation.1.rdf:PlainLiteral": "Brisbane",
                      "dc:coverage.vivo:GeographicLocation.1.geo:long": "180",
                      "dc:coverage.vivo:GeographicLocation.1.geo:lat": "170",
                      "dc:coverage.vivo:GeographicLocation.1.dc:identifier": ""
        }''', '''{
                      "dc:coverage.vivo:GeographicLocation.1.dc:type": "text",
                      "dc:coverage.vivo:GeographicLocation.1.redbox:wktRaw": "",
                      "dc:coverage.vivo:GeographicLocation.1.rdf:PlainLiteral": "Brisbane",
                      "dc:coverage.vivo:GeographicLocation.1.geo:long": "180",
                      "dc:coverage.vivo:GeographicLocation.1.geo:lat": "170",
                      "dc:coverage.vivo:GeographicLocation.1.dc:identifier": ""
        }''',
                      '''{
                      "dc:coverage.vivo:GeographicLocation.1.dc:type": "text",
                      "dc:coverage.vivo:GeographicLocation.1.redbox:wktRaw": "",
                      "dc:coverage.vivo:GeographicLocation.1.rdf:PlainLiteral": "Brisbane",
                      "dc:coverage.vivo:GeographicLocation.1.geo:long": "180",
                      "dc:coverage.vivo:GeographicLocation.1.geo:lat": "170",
                      "dc:coverage.vivo:GeographicLocation.1.dc:identifier": "",
                       "dc:coverage.vivo:GeographicLocation.2.dc:type": "text",
                      "dc:coverage.vivo:GeographicLocation.2.redbox:wktRaw": "POLYGON((142.78350830078 -45.766200546705,132.78350830078 -16.452951287538,152.62725830079 -36.452951287538,152.62725830079 -45.766200546705,142.78350830078 -45.766200546705))",
                      "dc:coverage.vivo:GeographicLocation.2.rdf:PlainLiteral": "POLYGON((142.78350830078 -45.766200546705,132.78350830078 -16.452951287538,152.62725830079 -36.452951287538,152.62725830079 -45.766200546705,142.78350830078 -45.766200546705))",
                      "dc:coverage.vivo:GeographicLocation.2.geo:long": "180",
                      "dc:coverage.vivo:GeographicLocation.2.geo:lat": "170",
                      "dc:coverage.vivo:GeographicLocation.2.dc:identifier": ""
        }''']
        expectedResult << [[[value: "142.78350830078,-45.766200546705 132.78350830078,-16.452951287538 152.62725830079,-36.452951287538 152.62725830079,-45.766200546705 142.78350830078,-45.766200546705", type: "kmlPolyCoords"]],
                           [[value: "Brisbane", type: "text"]],
                           [[type: "text", value: "Brisbane"], [type: "dcmiPoint", value: "name=Brisbane; east=180; north=170; projection=WGS84"]],
                           [[type: "text", value: "Brisbane"], [type: "dcmiPoint", value: "name=Brisbane; east=180; north=170; projection=WGS84"],
                            [value: "142.78350830078,-45.766200546705 132.78350830078,-16.452951287538 152.62725830079,-36.452951287538 152.62725830079,-45.766200546705 142.78350830078,-45.766200546705", type: "kmlPolyCoords"]]
        ]
    }

    @Unroll
    def "accessRights"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackage)).getAccessRights()
        then:
        result == expectedResult
        where:
        tfpackage << ['''{
                        "dc:accessRights.skos:prefLabel": "Access rights",
                        "dc:accessRights.dc:identifier": "",
        }''', '''{
                        "dc:accessRights.skos:prefLabel": "Access rights",
                        "dc:accessRights.dc:identifier": "",
                        "dc:accessRightsType": "Open"
        }''', '''{
                        "dc:accessRights.skos:prefLabel": "",
                        "dc:accessRights.dc:identifier": "foo",
        }''', '''{
                        "dc:accessRights.dc:identifier": "foo",
        }''', '''{
                        "dc:accessRights.skos:prefLabel": "Access rights",
                        "dc:accessRights.dc:identifier": "foo",
                        "dc:accessRights.dc:RightsStatement.skos:prefLabel": "",
                        "dc:accessRights.dc:RightsStatement.dc:identifier": "",
                        "dc:accessRightsType": "Closed",
                        "dc:license.skos:prefLabel": "",
                        "dc:license.dc:identifier": "",
                        "dc:license.rdf:Alt.skos:prefLabel": "",
                        "dc:license.rdf:Alt.dc:identifier": "",
        }''']
        expectedResult << [[value: "Access rights"], [value: "Access rights", type: "Open"], null, null, [value: "Access rights", uri: "foo", type: "Closed"]]
    }

    @Unroll
    def "rightsStatement"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackage)).getRightsStatement()
        then:
        result == expectedResult
        where:
        tfpackage << ['''{
                        "dc:accessRights.dc:RightsStatement.skos:prefLabel": "rights statement",
                        "dc:accessRights.dc:RightsStatement.dc:identifier": "foo",
        }''', '''{
                        "dc:accessRights.dc:RightsStatement.skos:prefLabel": "rights statement",
                        "dc:accessRights.dc:RightsStatement.dc:identifier": "",
        }''', '''{
                        "dc:accessRights.dc:RightsStatement.skos:prefLabel": "",
                        "dc:accessRights.dc:RightsStatement.dc:identifier": "foo",
        }''', '''{
                        "dc:accessRights.skos:prefLabel": "Access rights",
                        "dc:accessRights.dc:identifier": "foo",
                        "dc:accessRights.dc:RightsStatement.skos:prefLabel": "",
                        "dc:accessRights.dc:RightsStatement.dc:identifier": "",
                        "dc:license.skos:prefLabel": "",
                        "dc:license.dc:identifier": "",
                        "dc:license.rdf:Alt.skos:prefLabel": "",
                        "dc:license.rdf:Alt.dc:identifier": "",
        }''']
        expectedResult << [[value: "rights statement", uri: "foo"], [value: "rights statement"], null, null]
    }

    @Unroll
    def "licence"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackage)).getLicence()
        then:
        result == expectedResult
        where:
        tfpackage << ['''{
                         "dc:license.skos:prefLabel": "licence",
                        "dc:license.dc:identifier": "foo",
                        "dc:license.rdf:Alt.skos:prefLabel": "licence2",
                        "dc:license.rdf:Alt.dc:identifier": "bar"
        }''',
                      '''{
                         "dc:license.skos:prefLabel": "CC BY-ND: Attribution-No Derivative Works 3.0 AU",
                        "dc:license.dc:identifier": "foo",
                        "dc:license.rdf:Alt.skos:prefLabel": "licence2",
                        "dc:license.rdf:Alt.dc:identifier": "bar"
        }''',
                      '''{
                         "dc:license.skos:prefLabel": "CC BY-ND 4.0: Attribution-No Derivative Works 4.0 International",
                        "dc:license.dc:identifier": "foo",
                        "dc:license.rdf:Alt.skos:prefLabel": "licence2",
                        "dc:license.rdf:Alt.dc:identifier": "bar"
        }''',
                      '''{
                         "dc:license.skos:prefLabel": "ODC-By - Attribution License 1.0",
                        "dc:license.dc:identifier": "foo",
                        "dc:license.rdf:Alt.skos:prefLabel": "licence2",
                        "dc:license.rdf:Alt.dc:identifier": "bar"
        }''',
                      '''{
                          "dc:license.skos:prefLabel": "licence",
                        "dc:license.dc:identifier": "",
                        "dc:license.rdf:Alt.skos:prefLabel": "licence2",
                        "dc:license.rdf:Alt.dc:identifier": "bar"

        }''', '''{
                          "dc:license.skos:prefLabel": "",
                        "dc:license.dc:identifier": "foo",
                        "dc:license.rdf:Alt.skos:prefLabel": "licence2",
                        "dc:license.rdf:Alt.dc:identifier": "bar"
        }''', '''{
                          "dc:license.skos:prefLabel": "",
                        "dc:license.dc:identifier": "foo",
                        "dc:license.rdf:Alt.skos:prefLabel": "licence2",
                        "dc:license.rdf:Alt.dc:identifier": ""
        }''', '''{
                        "dc:accessRights.skos:prefLabel": "Access rights",
                        "dc:accessRights.dc:identifier": "foo",
                        "dc:accessRights.dc:RightsStatement.skos:prefLabel": "",
                        "dc:accessRights.dc:RightsStatement.dc:identifier": "",
                        "dc:license.skos:prefLabel": "",
                        "dc:license.dc:identifier": "foo",
                        "dc:license.rdf:Alt.skos:prefLabel": "",
                        "dc:license.rdf:Alt.dc:identifier": "bar",
        }''']
        expectedResult << [[value: "licence", uri: "foo", type: "Unknown/Other"], [value: "CC BY-ND: Attribution-No Derivative Works 3.0 AU", uri: "foo", type: "CC-BY-ND"], [value: "CC BY-ND 4.0: Attribution-No Derivative Works 4.0 International", uri: "foo", type: "CC-BY-ND"], [value: "ODC-By - Attribution License 1.0", uri: "foo", type: "Unknown/Other"], [value: "licence2", uri: "bar", type: "Unknown/Other"], [value: "licence2", uri: "bar", type: "Unknown/Other"], [value: "licence2", type: "Unknown/Other"], null]
    }

    def "relatedObject"() {
        when:
        def result = tfpackageToRifcs(stubDigitalObject(tfpackage)).getRelatedObject("dc:relation.vivo:Service")
        then:
        result == expectedResult
        where:
        tfpackage << ['''{
                         "dc:relation.vivo:Service.1.dc:identifier": "avivodcidentifier",
                "dc:relation.vivo:Service.1.vivo:Relationship.rdf:PlainLiteral": "hasAssociationWith",
                "dc:relation.vivo:Service.1.vivo:Relationship.skos:prefLabel": "Has association with:",
                "dc:relation.vivo:Service.1.dc:title": "avivodctitle",
                "dc:relation.vivo:Service.1.skos:note": "avivoskosnote"
        }''']
        expectedResult << [[[key: "avivodcidentifier", type: "hasAssociationWith"]]]
    }


    def tfpackageToRifcs() {
        def tfPackageToRifcsInstance = scriptClass.createInstance(stubDigitalObject(), stubConfig())
        return tfPackageToRifcsInstance
    }

    def tfpackageToInvalidRifcs() {
        def tfPackageToRifcsInstance = scriptClass.createInstance(stubInvalidDigitalObject(), stubInvalidConfig())
        return tfPackageToRifcsInstance
    }

    def tfpackageToRifcs(def digitalObjectStub) {
        def tfPackageToRifcsInstance = scriptClass.createInstance(digitalObjectStub, stubConfig())
        return tfPackageToRifcsInstance
    }

    def tfpackageToRifcs(def digitalObjectStub, def configStub) {
        def tfPackageToRifcsInstance = scriptClass.createInstance(digitalObjectStub, configStub)
        return tfPackageToRifcsInstance
    }

    def getStandardBinding() {
        Binding binding = new Binding()
        binding.setVariable("digitalObject", stubDigitalObject())
//        binding.setVariable("config", stubConfig())
        return binding
    }

    def stubConfig() {
        return '''{
            "curation": {
                "pidType": "local",
                "pidProperty": "localPid"
                },
            "identity": {
                "RIF_CSGroup": "The University of Examples, Australia",
                },
            "urlBase": "http://demo.redboxresearchdata.com.au/redbox/default"
        }'''
    }

    def stubInvalidConfig() {
        return '''{
            "curation": {
                "pidType": "local",
                "pidProperty": "localPid"
                },
            "identity": {
                "dummy": "The University of Examples, Australia",
                },
            "urlBase": "http://demo.redboxresearchdata.com.au/redbox/default"
        }'''
    }

    def stubDigitalObject() {
        def digitalObject = new GenericDigitalObject('1234')
        InputStream metadataStream = new ByteArrayInputStream(stubMetadata().bytes)
        InputStream dataStream = new ByteArrayInputStream(stubTfpackage().bytes)
        digitalObject.createStoredPayload('TF-OBJ-META', metadataStream)
        metadataStream.close()
        digitalObject.createStoredPayload('test.tfpackage', dataStream)
        dataStream.close()
        return digitalObject
    }

    def stubInvalidDigitalObject() {
        def digitalObject = new GenericDigitalObject('1234')
        InputStream metadataStream = new ByteArrayInputStream(stubMetadata().bytes)
        InputStream dataStream = new ByteArrayInputStream(stubTfpackageNoFormOrigin().bytes)
        digitalObject.createStoredPayload('TF-OBJ-META', metadataStream)
        metadataStream.close()
        digitalObject.createStoredPayload('test.tfpackage', dataStream)
        dataStream.close()
        return digitalObject
    }

    def stubDigitalObject(def tfPackageStub) {
        def digitalObject = new GenericDigitalObject('1234')
        InputStream metadataStream = new ByteArrayInputStream(stubMetadata().bytes)
        InputStream dataStream = new ByteArrayInputStream(tfPackageStub.bytes)
        digitalObject.createStoredPayload('TF-OBJ-META', metadataStream)
        metadataStream.close()
        digitalObject.createStoredPayload('test.tfpackage', dataStream)
        dataStream.close()
        return digitalObject
    }

    def stubDigitalObject(def tfPackageStub, def metdataStub) {
        def digitalObject = new GenericDigitalObject('1234')
        InputStream metadataStream = new ByteArrayInputStream(metdataStub.bytes)
        InputStream dataStream = new ByteArrayInputStream(tfPackageStub.bytes)
        digitalObject.createStoredPayload('TF-OBJ-META', metadataStream)
        metadataStream.close()
        digitalObject.createStoredPayload('test.tfpackage', dataStream)
        dataStream.close()
        return digitalObject
    }

    def stubEmptyXmlRegistryObjectsDoc() {
        return '''<registryObjects
    xmlns="http://ands.org.au/standards/rif-cs/registryObjects"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://ands.org.au/standards/rif-cs/registryObjects http://services.ands.org.au/documentation/rifcs/1.6/schema/registryObjects.xsd"/>
'''
    }

    def stubMetadata() {
        return "objectId=df96891d804da76bf2f30fb253d4aebb\n" +
                "owner=admin\n" +
                "scriptType=python\n" +
                "render-pending=false\n" +
                "localPid=http\\://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb\n" +
                "jsonConfigPid=dataset.json\n" +
                "file.path=/opt/redbox/home/packages/f6f70b21-a9a2-474a-8d5c-db67f0d4d92c.tfpackage\n" +
                "repository.name=ReDBox\n" +
                "rulesPid=dataset-rules.py\n" +
                "date_object_modified=2016-03-09T00\\:22\\:56Z\n" +
                "repository.type=Metadata Registry\n" +
                "date_object_created=2016-03-08T04\\:21\\:55Z\n" +
                "metaPid=TF-OBJ-META\n" +
                "jsonConfigOid=2b7bc449532696b3b2fc53d8cd141a69\n" +
                "ready_to_publish=ready\n" +
                "rulesOid=7fde9d0fd2106a4175bfda7d60bbcd6c\n" +
                "last_modified=20160309002256\n" +
                "published=true"
    }

    def stubTfpackage() {
        return "{\n" +
                "  \"title\": \"Research Data Collection\",\n" +
                "  \"viewId\": \"default\",\n" +
                "  \"packageType\": \"dataset\",\n" +
                "  \"description\": \"The description\",\n" +
                "  \"redbox:newForm\": \"false\",\n" +
                "  \"redbox:formVersion\": \"1.9-SNAPSHOT\",\n" +
                "  \"dc:title\": \"Research Data Collection\",\n" +
                "  \"dc:type.rdf:PlainLiteral\": \"collection\",\n" +
                "  \"dc:type.skos:prefLabel\": \"Collection\",\n" +
                "  \"dc:modified\": \"\",\n" +
                "  \"dc:created\": \"2016-10-18\",\n" +
                "  \"dc:language.dc:identifier\": \"http://id.loc.gov/vocabulary/iso639-2/eng\",\n" +
                "  \"dc:language.skos:prefLabel\": \"English\",\n" +
                "  \"dc:coverage.vivo:DateTimeInterval.vivo:start\": \"2004-04-02T18:06:02\",\n" +
                "  \"dc:coverage.vivo:DateTimeInterval.vivo:end\": \"2004-04-30T18:06:02\",\n" +
                "  \"dc:coverage.redbox:timePeriod\": \"21st Century\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.dc:type\": \"text\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.redbox:wktRaw\": \"\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.rdf:PlainLiteral\": \"Brisbane\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.geo:long\": \"180\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.geo:lat\": \"170\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.dc:identifier\": \"\",\n" +
                "  \"dc:description.1.text\": \"<p>The description</p>\",\n" +
                "  \"dc:description.1.shadow\": \"&lt;p&gt;The description&lt;p&gt;\",\n" +
                "  \"dc:description.1.type\": \"full\",\n" +
                "  \"dc:description.2.text\": \"<p>The Brief description</p>\",\n" +
                "  \"dc:description.2.shadow\": \"&lt;p&gt;The Brief description&lt;p&gt;\",\n" +
                "  \"dc:description.2.type\": \"brief\",\n" +
                "  \"dc:relation.swrc:Publication.1.dc:identifier\": \"answrcidentifier\",\n" +
                "  \"dc:relation.swrc:Publication.1.dc:title\": \"answrcdctitle\",\n" +
                "  \"dc:relation.swrc:Publication.1.skos:note\": \"answrcskosnote\",\n" +
                "  \"dc:relation.bibo:Website.1.dc:identifier\": \"abiboidentifier\",\n" +
                "  \"dc:relation.bibo:Website.1.dc:title\": \"abibodctitle\",\n" +
                "  \"dc:relation.bibo:Website.1.skos:note\": \"abiboskosnote\",\n" +
                "  \"dc:relation.vivo:Dataset.1.dc:identifier\": \"\",\n" +
                "  \"dc:relation.vivo:Dataset.1.vivo:Relationship.rdf:PlainLiteral\": \"hasAssociationWith\",\n" +
                "  \"dc:relation.vivo:Dataset.1.vivo:Relationship.skos:prefLabel\": \"Has association with:\",\n" +
                "  \"dc:relation.vivo:Dataset.1.dc:title\": \"\",\n" +
                "  \"dc:relation.vivo:Dataset.1.skos:note\": \"\",\n" +
                "  \"dc:relation.vivo:Dataset.1.redbox:origin\": \"on\",\n" +
                "  \"dc:relation.vivo:Dataset.1.redbox:publish\": \"\",\n" +
                "  \"dc:relation.vivo:Service.1.dc:identifier\": \"avivodcidentifier\",\n" +
                "  \"dc:relation.vivo:Service.1.vivo:Relationship.rdf:PlainLiteral\": \"hasAssociationWith\",\n" +
                "  \"dc:relation.vivo:Service.1.vivo:Relationship.skos:prefLabel\": \"Has association with:\",\n" +
                "  \"dc:relation.vivo:Service.1.dc:title\": \"avivodctitle\",\n" +
                "  \"dc:relation.vivo:Service.1.skos:note\": \"avivoskosnote\",\n" +
                "  \"dc:relation.vivo:Service.2.dc:identifier\": \"redbox-mint.googlecode.com/services/4\",\n" +
                "  \"dc:relation.vivo:Service.2.vivo:Relationship.rdf:PlainLiteral\": \"hasAssociationWith\",\n" +
                "  \"dc:relation.vivo:Service.2.vivo:Relationship.skos:prefLabel\": \"Has association with:\",\n" +
                "  \"dc:relation.vivo:Service.2.dc:title\": \"Service test\",\n" +
                "  \"dc:relation.vivo:Service.2.skos:note\": \"service note\",\n" +
                "  \"identifierText.1.creatorName.input\": \"\",\n" +
                "  \"dc:creator.foaf:Person.1.dc:identifier\": \"redbox-mint.googlecode.com/parties_people/1241\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:name\": \"James, Paul\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:title\": \"Dr\",\n" +
                "  \"dc:creator.foaf:Person.1.redbox:isCoPrimaryInvestigator\": \"\",\n" +
                "  \"dc:creator.foaf:Person.1.redbox:isPrimaryInvestigator\": \"\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:givenName\": \"Paul\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:familyName\": \"James\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:Organization.dc:identifier\": \"\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:Organization.skos:prefLabel\": \"\",\n" +
                "  \"identifierText.3.creatorName.input\": \"\",\n" +
                "  \"dc:creator.foaf:Person.3.dc:identifier\": \"http://orcid.org/0000-0001-6810-1260\",\n" +
                "  \"dc:creator.foaf:Person.3.foaf:name\": \"Chambers, John\",\n" +
                "   \"dc:creator.foaf:Person.3.foaf:title\": \"Prof\",\n" +
                "   \"dc:creator.foaf:Person.3.redbox:isCoPrimaryInvestigator\": \"\",\n" +
                "   \"dc:creator.foaf:Person.3.redbox:isPrimaryInvestigator\": \"\",\n" +
                "   \"dc:creator.foaf:Person.3.foaf:givenName\": \"John\",\n" +
                "   \"dc:creator.foaf:Person.3.foaf:familyName\": \"Chambers\",\n" +
                "   \"dc:creator.foaf:Person.3.foaf:Organization.dc:identifier\": \"redbox-mint.googlecode.com/parties/group/2\",\n" +
                "   \"dc:creator.foaf:Person.3.foaf:Organization.skos:prefLabel\": \"Faculty of Technology\",\n" +
                "  \"dc:creator.foaf:Person.4.dc:identifier\": \"https://www.scopus.com/authid/detail.uri?authorId=000111\",\n" +
                "  \"identifierText.4.creatorName.input\": \"https://www.scopus.com/authid/detail.uri?authorId=000111\",\n" +
                "  \"dc:creator.foaf:Person.4.foaf:name\": \"Smith, John\",\n" +
                "   \"dc:creator.foaf:Person.4.foaf:title\": \"Prof\",\n" +
                "   \"dc:creator.foaf:Person.4.redbox:isCoPrimaryInvestigator\": \"\",\n" +
                "   \"dc:creator.foaf:Person.4.redbox:isPrimaryInvestigator\": \"\",\n" +
                "   \"dc:creator.foaf:Person.4.foaf:givenName\": \"John\",\n" +
                "   \"dc:creator.foaf:Person.4.foaf:familyName\": \"Smith\",\n" +
                "   \"dc:creator.foaf:Person.4.foaf:Organization.dc:identifier\": \"redbox-mint.googlecode.com/parties/group/2\",\n" +
                "   \"dc:creator.foaf:Person.4.foaf:Organization.skos:prefLabel\": \"Faculty of Technology\",\n" +
                "  \"locrel:prc.foaf:Person.dc:identifier\": \"\",\n" +
                "  \"locrel:prc.foaf:Person.foaf:name\": \"\",\n" +
                "  \"locrel:prc.foaf:Person.foaf:title\": \"\",\n" +
                "  \"locrel:prc.foaf:Person.foaf:givenName\": \"\",\n" +
                "  \"locrel:prc.foaf:Person.foaf:familyName\": \"\",\n" +
                "  \"locrel:prc.foaf:Person.foaf:email\": \"anemail.com.au\",\n" +
                "  \"swrc:supervisor.foaf:Person.1.dc:identifier\": \"\",\n" +
                "  \"swrc:supervisor.foaf:Person.1.foaf:name\": \"\",\n" +
                "  \"swrc:supervisor.foaf:Person.1.foaf:title\": \"\",\n" +
                "  \"swrc:supervisor.foaf:Person.1.foaf:givenName\": \"\",\n" +
                "  \"swrc:supervisor.foaf:Person.1.foaf:familyName\": \"\",\n" +
                "  \"dc:contributor.locrel:clb.1.foaf:Agent\": \"\",\n" +
                "  \"dc:subject.vivo:keyword.1.rdf:PlainLiteral\": \"keywords\",\n" +
                "  \"dc:subject.anzsrc:toa.rdf:resource\": \"\",\n" +
                "  \"dc:subject.anzsrc:toa.skos:prefLabel\": \"\",\n" +
                "  \"dc:accessRights.skos:prefLabel\": \"Access rights\",\n" +
                "  \"dc:accessRights.dc:identifier\": \"\",\n" +
                "  \"dc:accessRights.dc:RightsStatement.skos:prefLabel\": \"\",\n" +
                "  \"dc:accessRights.dc:RightsStatement.dc:identifier\": \"\",\n" +
                "  \"dc:license.skos:prefLabel\": \"\",\n" +
                "  \"dc:license.dc:identifier\": \"\",\n" +
                "  \"dc:license.rdf:Alt.skos:prefLabel\": \"\",\n" +
                "  \"dc:license.rdf:Alt.dc:identifier\": \"\",\n" +
                "  \"dc:identifier.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:identifier.dc:type.rdf:PlainLiteral\": \"handle\",\n" +
                "  \"dc:identifier.dc:type.skos:prefLabel\": \"HANDLE System Identifier\",\n" +
                "  \"dc:identifier.redbox:origin\": \"internal\",\n" +
                "  \"dc:additionalidentifier.1.rdf:PlainLiteral\": \"Local identifier\",\n" +
                "  \"dc:additionalidentifier.1.type.rdf:PlainLiteral\": \"local\",\n" +
                "  \"dc:additionalidentifier.1.type.skos:prefLabel\": \"local Identifier\",\n" +
                "  \"dc:additionalidentifier.3.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:additionalidentifier.3.type.rdf:PlainLiteral\": \"handle\",\n" +
                "  \"dc:additionalidentifier.3.type.skos:prefLabel\": \"HANDLE System Identifier\",\n" +
                "  \"dc:additionalidentifier.2.rdf:PlainLiteral\": \"abn stuff\",\n" +
                "  \"dc:additionalidentifier.2.type.rdf:PlainLiteral\": \"abn\",\n" +
                "  \"dc:additionalidentifier.2.type.skos:prefLabel\": \"Australian Business Number\",\n" +
                "  \"bibo:Website.1.dc:identifier\": \"http://www.google.com\",\n" +
                "  \"vivo:Location.vivo:GeographicLocation.gn:name\": \"Brisbane\",\n" +
                "  \"vivo:Location.vivo:GeographicLocation.skos:note\": \"\",\n" +
                "  \"redbox:retentionPeriod\": \"12\",\n" +
                "  \"dc:extent\": \"1\",\n" +
                "  \"redbox:disposalDate\": \"\",\n" +
                "  \"locrel:own.foaf:Agent.1.foaf:name\": \"\",\n" +
                "  \"locrel:dtm.foaf:Agent.foaf:name\": \"\",\n" +
                "  \"foaf:Organization.dc:identifier\": \"\",\n" +
                "  \"foaf:Organization.skos:prefLabel\": \"\",\n" +
                "  \"foaf:fundedBy.foaf:Agent.1.skos:prefLabel\": \"\",\n" +
                "  \"foaf:fundedBy.foaf:Agent.1.dc:identifier\": \"\",\n" +
                "  \"foaf:fundedBy.vivo:Grant.1.redbox:internalGrant\": \"\",\n" +
                "  \"foaf:fundedBy.vivo:Grant.1.redbox:grantNumber\": \"\",\n" +
                "  \"foaf:fundedBy.vivo:Grant.1.dc:identifier\": \"\",\n" +
                "  \"foaf:fundedBy.vivo:Grant.1.skos:prefLabel\": \"\",\n" +
                "  \"swrc:ResearchProject.dc:title\": \"\",\n" +
                "  \"locrel:dpt.foaf:Person.foaf:name\": \"\",\n" +
                "  \"dc:SizeOrDuration\": \"\",\n" +
                "  \"dc:Policy\": \"\",\n" +
                "  \"redbox:ManagementPlan.redbox:hasPlan\": null,\n" +
                "  \"redbox:ManagementPlan.skos:note\": \"\",\n" +
                "  \"skos:note.1.dc:created\": \"\",\n" +
                "  \"skos:note.1.foaf:name\": \"\",\n" +
                "  \"skos:note.1.dc:description\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.skos:prefLabel\": \"citation data id: {ID_WILL_BE_HERE}\",\n" +
                "  \"dc:biblioGraphicCitation.redbox:sendCitation\": \"on\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:identifier.skos:note\": \"useCuration\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:title\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:givenName\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:familyName\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:title\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:hasVersion.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:publisher.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.vivo:Publisher.vivo:Location\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.dc:type.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.dc:type.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.dc:type.skos:prefLabel\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.dc:type.skos:prefLabel\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.skos:scopeNote\": \"\",\n" +
                "  \"redbox:submissionProcess.redbox:submitted\": \"null\",\n" +
                "  \"redbox:submissionProcess.dc:date\": \"\",\n" +
                "  \"foo:bar\" : {\n" +
                "      \"foo\":\"tested\"\n" +
                "  },\n" +
                "  \"redbox:submissionProcess.dc:description\": \"\",\n" +
                "  \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name\": \"\",\n" +
                "  \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone\": \"\",\n" +
                "  \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox\": \"\",\n" +
                "  \"redbox:submissionProcess.dc:title\": \"\",\n" +
                "  \"redbox:submissionProcess.skos:note\": \"\",\n" +
                "  \"redbox:embargo.redbox:isEmbargoed\": \"\",\n" +
                "  \"redbox:embargo.dc:date\": \"2016-03-17\",\n" +
                "  \"redbox:embargo.skos:note\": \"\",\n" +
                "  \"dc:relation.redbox:TechnicalMetadata.1.dc:identifier\": \"\",\n" +
                "  \"dc:relation.redbox:TechnicalMetadata.1.dc:title\": \"\",\n" +
                "  \"dc:relation.redbox:TechnicalMetadata.1.dc:type\": \"\",\n" +
                "  \"dc:relation.redbox:TechnicalMetadata.1.dc:conformsTo\": \"\",\n" +
                "  \"xmlns:dc\": \"http://dublincore.org/documents/2008/01/14/dcmi-terms/\",\n" +
                "  \"xmlns:foaf\": \"http://xmlns.com/foaf/spec/\",\n" +
                "  \"xmlns:anzsrc\": \"http://purl.org/anzsrc/\",\n" +
                "  \"metaList\": [\n" +
                "    \"dc:title\",\n" +
                "    \"dc:type.rdf:PlainLiteral\",\n" +
                "    \"dc:type.skos:prefLabel\",\n" +
                "    \"dc:created\",\n" +
                "    \"dc:modified\",\n" +
                "    \"dc:language.dc:identifier\",\n" +
                "    \"dc:language.skos:prefLabel\",\n" +
                "    \"redbox:formVersion\",\n" +
                "    \"redbox:newForm\",\n" +
                "    \"dc:coverage.vivo:DateTimeInterval.vivo:start\",\n" +
                "    \"dc:coverage.vivo:DateTimeInterval.vivo:end\",\n" +
                "    \"dc:coverage.redbox:timePeriod\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.dc:type\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.dc:type\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.redbox:wktRaw\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.redbox:wktRaw\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.rdf:PlainLiteral\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.rdf:PlainLiteral\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.geo:long\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.geo:long\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.geo:lat\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.geo:lat\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.dc:identifier\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.dc:identifier\",\n" +
                "    \"dc:description.1.text\",\n" +
                "    \"dc:description.1.type\",\n" +
                "    \"dc:relation.swrc:Publication.1.dc:identifier\",\n" +
                "    \"dc:relation.swrc:Publication.1.dc:title\",\n" +
                "    \"dc:relation.swrc:Publication.1.skos:note\",\n" +
                "    \"dc:relation.bibo:Website.1.dc:identifier\",\n" +
                "    \"dc:relation.bibo:Website.1.dc:title\",\n" +
                "    \"dc:relation.bibo:Website.1.skos:note\",\n" +
                "    \"dc:relation.vivo:Dataset.1.dc:identifier\",\n" +
                "    \"dc:relation.vivo:Dataset.1.vivo:Relationship.rdf:PlainLiteral\",\n" +
                "    \"dc:relation.vivo:Dataset.1.vivo:Relationship.skos:prefLabel\",\n" +
                "    \"dc:relation.vivo:Dataset.1.dc:title\",\n" +
                "    \"dc:relation.vivo:Dataset.1.skos:note\",\n" +
                "    \"dc:relation.vivo:Dataset.1.redbox:origin\",\n" +
                "    \"dc:relation.vivo:Dataset.1.redbox:publish\",\n" +
                "    \"dc:relation.vivo:Service.1.dc:identifier\",\n" +
                "    \"dc:relation.vivo:Service.1.vivo:Relationship.rdf:PlainLiteral\",\n" +
                "    \"dc:relation.vivo:Service.1.vivo:Relationship.skos:prefLabel\",\n" +
                "    \"dc:relation.vivo:Service.1.dc:title\",\n" +
                "    \"dc:relation.vivo:Service.1.skos:note\",\n" +
                "    \"dc:creator.foaf:Person.1.dc:identifier\",\n" +
                "    \"dc:creator.foaf:Person.2.dc:identifier\",\n" +
                "    \"identifierText.2.creatorName.input\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:name\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:name\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:title\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:title\",\n" +
                "    \"dc:creator.foaf:Person.1.redbox:isCoPrimaryInvestigator\",\n" +
                "    \"dc:creator.foaf:Person.2.redbox:isCoPrimaryInvestigator\",\n" +
                "    \"dc:creator.foaf:Person.1.redbox:isPrimaryInvestigator\",\n" +
                "    \"dc:creator.foaf:Person.2.redbox:isPrimaryInvestigator\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:givenName\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:givenName\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:familyName\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:familyName\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:Organization.dc:identifier\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:Organization.dc:identifier\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:Organization.skos:prefLabel\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:Organization.skos:prefLabel\",\n" +
                "    \"identifierText.1.creatorName.input\",\n" +
                "    \"identifierText.2.creatorName.input\",\n" +
                "    \"locrel:prc.foaf:Person.dc:identifier\",\n" +
                "    \"locrel:prc.foaf:Person.foaf:name\",\n" +
                "    \"locrel:prc.foaf:Person.foaf:title\",\n" +
                "    \"locrel:prc.foaf:Person.foaf:givenName\",\n" +
                "    \"locrel:prc.foaf:Person.foaf:familyName\",\n" +
                "    \"locrel:prc.foaf:Person.foaf:email\",\n" +
                "    \"swrc:supervisor.foaf:Person.1.dc:identifier\",\n" +
                "    \"swrc:supervisor.foaf:Person.1.foaf:name\",\n" +
                "    \"swrc:supervisor.foaf:Person.1.foaf:title\",\n" +
                "    \"swrc:supervisor.foaf:Person.1.foaf:givenName\",\n" +
                "    \"swrc:supervisor.foaf:Person.1.foaf:familyName\",\n" +
                "    \"dc:contributor.locrel:clb.1.foaf:Agent\",\n" +
                "    \"dc:subject.anzsrc:for.1.skos:prefLabel\",\n" +
                "    \"dc:subject.anzsrc:for.1.rdf:resource\",\n" +
                "    \"dc:subject.vivo:keyword.1.rdf:PlainLiteral\",\n" +
                "    \"dc:subject.anzsrc:toa.rdf:resource\",\n" +
                "    \"dc:subject.anzsrc:toa.skos:prefLabel\",\n" +
                "    \"dc:accessRights.skos:prefLabel\",\n" +
                "    \"dc:accessRights.dc:identifier\",\n" +
                "    \"dc:accessRights.dc:RightsStatement.skos:prefLabel\",\n" +
                "    \"dc:accessRights.dc:RightsStatement.dc:identifier\",\n" +
                "    \"dc:license.skos:prefLabel\",\n" +
                "    \"dc:license.dc:identifier\",\n" +
                "    \"dc:license.rdf:Alt.skos:prefLabel\",\n" +
                "    \"dc:license.rdf:Alt.dc:identifier\",\n" +
                "    \"dc:identifier.rdf:PlainLiteral\",\n" +
                "    \"dc:identifier.dc:type.rdf:PlainLiteral\",\n" +
                "    \"dc:identifier.dc:type.skos:prefLabel\",\n" +
                "    \"dc:identifier.redbox:origin\",\n" +
                "    \"bibo:Website.1.dc:identifier\",\n" +
                "    \"vivo:Location.vivo:GeographicLocation.gn:name\",\n" +
                "    \"vivo:Location.vivo:GeographicLocation.skos:note\",\n" +
                "    \"redbox:retentionPeriod\",\n" +
                "    \"dc:extent\",\n" +
                "    \"redbox:disposalDate\",\n" +
                "    \"locrel:own.foaf:Agent.1.foaf:name\",\n" +
                "    \"locrel:dtm.foaf:Agent.foaf:name\",\n" +
                "    \"foaf:Organization.dc:identifier\",\n" +
                "    \"foaf:Organization.skos:prefLabel\",\n" +
                "    \"foaf:fundedBy.foaf:Agent.1.skos:prefLabel\",\n" +
                "    \"foaf:fundedBy.foaf:Agent.1.dc:identifier\",\n" +
                "    \"foaf:fundedBy.vivo:Grant.1.redbox:internalGrant\",\n" +
                "    \"foaf:fundedBy.vivo:Grant.1.redbox:grantNumber\",\n" +
                "    \"foaf:fundedBy.vivo:Grant.1.dc:identifier\",\n" +
                "    \"foaf:fundedBy.vivo:Grant.1.skos:prefLabel\",\n" +
                "    \"swrc:ResearchProject.dc:title\",\n" +
                "    \"locrel:dpt.foaf:Person.foaf:name\",\n" +
                "    \"dc:SizeOrDuration\",\n" +
                "    \"dc:Policy\",\n" +
                "    \"redbox:ManagementPlan.redbox:hasPlan\",\n" +
                "    \"redbox:ManagementPlan.skos:note\",\n" +
                "    \"skos:note.1.dc:created\",\n" +
                "    \"skos:note.1.foaf:name\",\n" +
                "    \"skos:note.1.dc:description\",\n" +
                "    \"dc:biblioGraphicCitation.skos:prefLabel\",\n" +
                "    \"dc:biblioGraphicCitation.redbox:sendCitation\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:identifier.skos:note\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:title\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:givenName\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:familyName\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:title\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:hasVersion.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:publisher.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.vivo:Publisher.vivo:Location\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.dc:type.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.dc:type.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.dc:type.skos:prefLabel\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.dc:type.skos:prefLabel\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.skos:scopeNote\",\n" +
                "    \"redbox:submissionProcess.redbox:submitted\",\n" +
                "    \"redbox:submissionProcess.dc:date\",\n" +
                "    \"redbox:submissionProcess.dc:description\",\n" +
                "    \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name\",\n" +
                "    \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone\",\n" +
                "    \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox\",\n" +
                "    \"redbox:submissionProcess.dc:title\",\n" +
                "    \"redbox:submissionProcess.skos:note\",\n" +
                "    \"redbox:embargo.redbox:isEmbargoed\",\n" +
                "    \"redbox:embargo.dc:date\",\n" +
                "    \"redbox:embargo.skos:note\",\n" +
                "    \"dc:relation.redbox:TechnicalMetadata.1.dc:identifier\",\n" +
                "    \"dc:relation.redbox:TechnicalMetadata.1.dc:title\",\n" +
                "    \"dc:relation.redbox:TechnicalMetadata.1.dc:type\",\n" +
                "    \"dc:relation.redbox:TechnicalMetadata.1.dc:conformsTo\",\n" +
                "    \"xmlns:dc\",\n" +
                "    \"xmlns:foaf\",\n" +
                "    \"xmlns:anzsrc\"\n" +
                "  ],\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.dc:type\": \"text\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.redbox:wktRaw\": \"POLYGON((132.78350830078 -35.766200546705,132.78350830078 -26.452951287538,142.62725830079 -26.452951287538,142.62725830079 -35.766200546705,132.78350830078 -35.766200546705))\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.rdf:PlainLiteral\": \"POLYGON((132.78350830078 -35.766200546705,132.78350830078 -26.452951287538,142.62725830079 -26.452951287538,142.62725830079 -35.766200546705,132.78350830078 -35.766200546705))\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.geo:long\": \"180\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.geo:lat\": \"170\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.dc:identifier\": \"\",\n" +
                "  \"dc:creator.foaf:Person.2.dc:identifier\": \"http://nla.gov.au/nla.party-965000\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:name\": \"Jensen, Liz\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:title\": \"\",\n" +
                "  \"dc:creator.foaf:Person.2.redbox:isCoPrimaryInvestigator\": \"\",\n" +
                "  \"dc:creator.foaf:Person.2.redbox:isPrimaryInvestigator\": \"\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:givenName\": \"Liz\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:familyName\": \"Jensen\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:Organization.dc:identifier\": \"\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:Organization.skos:prefLabel\": \"\",\n" +
                "  \"dc:subject.anzsrc:for.1.skos:prefLabel\": \"0402 - Geochemistry\",\n" +
                "  \"dc:subject.anzsrc:for.1.rdf:resource\": \"http://purl.org/asc/1297.0/2008/for/0402\",\n" +
                "  \"recordAsLocationDefault\": \"http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb\",\n" +
                "  \"relationships\": [\n" +
                "    {\n" +
                "      \"field\": \"dc:creator.foaf:Person.0.dc:identifier\",\n" +
                "      \"authority\": true,\n" +
                "      \"identifier\": \"redbox-mint.googlecode.com/parties_people/1241\",\n" +
                "      \"relationship\": \"hasCollector\",\n" +
                "      \"reverseRelationship\": \"isCollectorOf\",\n" +
                "      \"broker\": \"tcp://localhost:9201\",\n" +
                "      \"isCurated\": true,\n" +
                "      \"curatedPid\": \"http://demo.redboxresearchdata.com.au/mint/published/detail/84176738cc5e80306afc7adb163a4bab\"\n" +
                "    },\n" +
                " {\n" +
                "            \"field\": \"dc:relation.vivo:Service.1.dc:identifier\",\n" +
                "            \"authority\": true,\n" +
                "            \"identifier\": \"redbox-mint.googlecode.com/services/4\",\n" +
                "            \"relationship\": \"hasAssociationWith\",\n" +
                "            \"reverseRelationship\": \"hasAssociationWith\",\n" +
                "            \"broker\": \"tcp://localhost:9201\",\n" +
                "            \"isCurated\": true,\n" +
                "            \"curatedPid\": \"http://127.0.0.1:9001/mint/published/detail/6f4c827aabf664dbefec80e243adf891\"\n" +
                "        }\n" +
                "  ]\n" +
                "}"
    }

    def stubTfpackageNoFormOrigin() {
        return "{\n" +
                "  \"title\": \"Research Data Collection\",\n" +
                "  \"viewId\": \"default\",\n" +
                "  \"packageType\": \"dataset\",\n" +
                "  \"description\": \"The description\",\n" +
                "  \"redbox:newForm\": \"false\",\n" +
                "  \"redbox:formVersion\": \"1.9-SNAPSHOT\",\n" +
                "  \"dc:title\": \"Research Data Collection\",\n" +
                "  \"dc:type.rdf:PlainLiteral\": \"collection\",\n" +
                "  \"dc:type.skos:prefLabel\": \"Collection\",\n" +
                "  \"dc:modified\": \"\",\n" +
                "  \"dc:created\": \"2016-10-18\",\n" +
                "  \"dc:language.dc:identifier\": \"http://id.loc.gov/vocabulary/iso639-2/eng\",\n" +
                "  \"dc:language.skos:prefLabel\": \"English\",\n" +
                "  \"dc:coverage.vivo:DateTimeInterval.vivo:start\": \"2004-04-02T18:06:02\",\n" +
                "  \"dc:coverage.vivo:DateTimeInterval.vivo:end\": \"2004-04-30T18:06:02\",\n" +
                "  \"dc:coverage.redbox:timePeriod\": \"21st Century\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.dc:type\": \"text\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.redbox:wktRaw\": \"\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.rdf:PlainLiteral\": \"Brisbane\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.geo:long\": \"180\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.geo:lat\": \"170\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.dc:identifier\": \"\",\n" +
                "  \"dc:description.1.text\": \"<p>The description</p>\",\n" +
                "  \"dc:description.1.shadow\": \"&lt;p&gt;The description&lt;p&gt;\",\n" +
                "  \"dc:description.1.type\": \"full\",\n" +
                "  \"dc:description.2.text\": \"<p>The Brief description</p>\",\n" +
                "  \"dc:description.2.shadow\": \"&lt;p&gt;The Brief description&lt;p&gt;\",\n" +
                "  \"dc:description.2.type\": \"brief\",\n" +
                "  \"dc:relation.swrc:Publication.1.dc:identifier\": \"answrcidentifier\",\n" +
                "  \"dc:relation.swrc:Publication.1.dc:title\": \"answrcdctitle\",\n" +
                "  \"dc:relation.swrc:Publication.1.skos:note\": \"answrcskosnote\",\n" +
                "  \"dc:relation.bibo:Website.1.dc:identifier\": \"abiboidentifier\",\n" +
                "  \"dc:relation.bibo:Website.1.dc:title\": \"abibodctitle\",\n" +
                "  \"dc:relation.bibo:Website.1.skos:note\": \"abiboskosnote\",\n" +
                "  \"dc:relation.vivo:Dataset.1.dc:identifier\": \"\",\n" +
                "  \"dc:relation.vivo:Dataset.1.vivo:Relationship.rdf:PlainLiteral\": \"hasAssociationWith\",\n" +
                "  \"dc:relation.vivo:Dataset.1.vivo:Relationship.skos:prefLabel\": \"Has association with:\",\n" +
                "  \"dc:relation.vivo:Dataset.1.dc:title\": \"\",\n" +
                "  \"dc:relation.vivo:Dataset.1.skos:note\": \"\",\n" +
                "  \"dc:relation.vivo:Dataset.1.redbox:origin\": \"on\",\n" +
                "  \"dc:relation.vivo:Dataset.1.redbox:publish\": \"\",\n" +
                "  \"dc:relation.vivo:Service.1.dc:identifier\": \"avivodcidentifier\",\n" +
                "  \"dc:relation.vivo:Service.1.vivo:Relationship.rdf:PlainLiteral\": \"hasAssociationWith\",\n" +
                "  \"dc:relation.vivo:Service.1.vivo:Relationship.skos:prefLabel\": \"Has association with:\",\n" +
                "  \"dc:relation.vivo:Service.1.dc:title\": \"avivodctitle\",\n" +
                "  \"dc:relation.vivo:Service.1.skos:note\": \"avivoskosnote\",\n" +
                "  \"dc:relation.vivo:Service.2.dc:identifier\": \"redbox-mint.googlecode.com/services/4\",\n" +
                "  \"dc:relation.vivo:Service.2.vivo:Relationship.rdf:PlainLiteral\": \"hasAssociationWith\",\n" +
                "  \"dc:relation.vivo:Service.2.vivo:Relationship.skos:prefLabel\": \"Has association with:\",\n" +
                "  \"dc:relation.vivo:Service.2.dc:title\": \"Service test\",\n" +
                "  \"dc:relation.vivo:Service.2.skos:note\": \"service note\",\n" +
                "  \"dc:creator.foaf:Person.1.dc:identifier\": \"redbox-mint.googlecode.com/parties_people/1241\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:name\": \"James, Paul\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:title\": \"Dr\",\n" +
                "  \"dc:creator.foaf:Person.1.redbox:isCoPrimaryInvestigator\": \"\",\n" +
                "  \"dc:creator.foaf:Person.1.redbox:isPrimaryInvestigator\": \"\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:givenName\": \"Paul\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:familyName\": \"James\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:Organization.dc:identifier\": \"\",\n" +
                "  \"dc:creator.foaf:Person.1.foaf:Organization.skos:prefLabel\": \"\",\n" +
                "  \"dc:creator.foaf:Person.3.dc:identifier\": \"http://orcid.org/0000-0001-6810-1260\",\n" +
                "  \"dc:creator.foaf:Person.3.foaf:name\": \"Chambers, John\",\n" +
                "   \"dc:creator.foaf:Person.3.foaf:title\": \"Prof\",\n" +
                "   \"dc:creator.foaf:Person.3.redbox:isCoPrimaryInvestigator\": \"\",\n" +
                "   \"dc:creator.foaf:Person.3.redbox:isPrimaryInvestigator\": \"\",\n" +
                "   \"dc:creator.foaf:Person.3.foaf:givenName\": \"John\",\n" +
                "   \"dc:creator.foaf:Person.3.foaf:familyName\": \"Chambers\",\n" +
                "   \"dc:creator.foaf:Person.3.foaf:Organization.dc:identifier\": \"redbox-mint.googlecode.com/parties/group/2\",\n" +
                "   \"dc:creator.foaf:Person.3.foaf:Organization.skos:prefLabel\": \"Faculty of Technology\",\n" +
                "  \"locrel:prc.foaf:Person.dc:identifier\": \"\",\n" +
                "  \"locrel:prc.foaf:Person.foaf:name\": \"\",\n" +
                "  \"locrel:prc.foaf:Person.foaf:title\": \"\",\n" +
                "  \"locrel:prc.foaf:Person.foaf:givenName\": \"\",\n" +
                "  \"locrel:prc.foaf:Person.foaf:familyName\": \"\",\n" +
                "  \"locrel:prc.foaf:Person.foaf:email\": \"anemail.com.au\",\n" +
                "  \"swrc:supervisor.foaf:Person.1.dc:identifier\": \"\",\n" +
                "  \"swrc:supervisor.foaf:Person.1.foaf:name\": \"\",\n" +
                "  \"swrc:supervisor.foaf:Person.1.foaf:title\": \"\",\n" +
                "  \"swrc:supervisor.foaf:Person.1.foaf:givenName\": \"\",\n" +
                "  \"swrc:supervisor.foaf:Person.1.foaf:familyName\": \"\",\n" +
                "  \"dc:contributor.locrel:clb.1.foaf:Agent\": \"\",\n" +
                "  \"dc:subject.vivo:keyword.1.rdf:PlainLiteral\": \"keywords\",\n" +
                "  \"dc:subject.anzsrc:toa.rdf:resource\": \"\",\n" +
                "  \"dc:subject.anzsrc:toa.skos:prefLabel\": \"\",\n" +
                "  \"dc:accessRights.skos:prefLabel\": \"Access rights\",\n" +
                "  \"dc:accessRights.dc:identifier\": \"\",\n" +
                "  \"dc:accessRights.dc:RightsStatement.skos:prefLabel\": \"\",\n" +
                "  \"dc:accessRights.dc:RightsStatement.dc:identifier\": \"\",\n" +
                "  \"dc:license.skos:prefLabel\": \"\",\n" +
                "  \"dc:license.dc:identifier\": \"\",\n" +
                "  \"dc:license.rdf:Alt.skos:prefLabel\": \"\",\n" +
                "  \"dc:license.rdf:Alt.dc:identifier\": \"\",\n" +
                "  \"dc:identifier.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:identifier.dc:type.rdf:PlainLiteral\": \"handle\",\n" +
                "  \"dc:identifier.dc:type.skos:prefLabel\": \"HANDLE System Identifier\",\n" +
                "  \"dc:identifier.redbox:origin\": \"\",\n" +
                "  \"dc:additionalidentifier.1.rdf:PlainLiteral\": \"Local identifier\",\n" +
                "  \"dc:additionalidentifier.1.type.rdf:PlainLiteral\": \"local\",\n" +
                "  \"dc:additionalidentifier.1.type.skos:prefLabel\": \"local Identifier\",\n" +
                "  \"dc:additionalidentifier.3.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:additionalidentifier.3.type.rdf:PlainLiteral\": \"handle\",\n" +
                "  \"dc:additionalidentifier.3.type.skos:prefLabel\": \"HANDLE System Identifier\",\n" +
                "  \"dc:additionalidentifier.2.rdf:PlainLiteral\": \"abn stuff\",\n" +
                "  \"dc:additionalidentifier.2.type.rdf:PlainLiteral\": \"abn\",\n" +
                "  \"dc:additionalidentifier.2.type.skos:prefLabel\": \"Australian Business Number\",\n" +
                "  \"bibo:Website.1.dc:identifier\": \"http://www.google.com\",\n" +
                "  \"vivo:Location.vivo:GeographicLocation.gn:name\": \"Brisbane\",\n" +
                "  \"vivo:Location.vivo:GeographicLocation.skos:note\": \"\",\n" +
                "  \"redbox:retentionPeriod\": \"12\",\n" +
                "  \"dc:extent\": \"1\",\n" +
                "  \"redbox:disposalDate\": \"\",\n" +
                "  \"locrel:own.foaf:Agent.1.foaf:name\": \"\",\n" +
                "  \"locrel:dtm.foaf:Agent.foaf:name\": \"\",\n" +
                "  \"foaf:Organization.dc:identifier\": \"\",\n" +
                "  \"foaf:Organization.skos:prefLabel\": \"\",\n" +
                "  \"foaf:fundedBy.foaf:Agent.1.skos:prefLabel\": \"\",\n" +
                "  \"foaf:fundedBy.foaf:Agent.1.dc:identifier\": \"\",\n" +
                "  \"foaf:fundedBy.vivo:Grant.1.redbox:internalGrant\": \"\",\n" +
                "  \"foaf:fundedBy.vivo:Grant.1.redbox:grantNumber\": \"\",\n" +
                "  \"foaf:fundedBy.vivo:Grant.1.dc:identifier\": \"\",\n" +
                "  \"foaf:fundedBy.vivo:Grant.1.skos:prefLabel\": \"\",\n" +
                "  \"swrc:ResearchProject.dc:title\": \"\",\n" +
                "  \"locrel:dpt.foaf:Person.foaf:name\": \"\",\n" +
                "  \"dc:SizeOrDuration\": \"\",\n" +
                "  \"dc:Policy\": \"\",\n" +
                "  \"redbox:ManagementPlan.redbox:hasPlan\": null,\n" +
                "  \"redbox:ManagementPlan.skos:note\": \"\",\n" +
                "  \"skos:note.1.dc:created\": \"\",\n" +
                "  \"skos:note.1.foaf:name\": \"\",\n" +
                "  \"skos:note.1.dc:description\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.skos:prefLabel\": \"citation data id: {ID_WILL_BE_HERE}\",\n" +
                "  \"dc:biblioGraphicCitation.redbox:sendCitation\": \"on\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:identifier.skos:note\": \"useCuration\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:title\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:givenName\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:familyName\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:title\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:hasVersion.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:publisher.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.vivo:Publisher.vivo:Location\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.dc:type.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.dc:type.rdf:PlainLiteral\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.dc:type.skos:prefLabel\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.dc:type.skos:prefLabel\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier\": \"\",\n" +
                "  \"dc:biblioGraphicCitation.dc:hasPart.skos:scopeNote\": \"\",\n" +
                "  \"redbox:submissionProcess.redbox:submitted\": \"null\",\n" +
                "  \"redbox:submissionProcess.dc:date\": \"\",\n" +
                "  \"foo:bar\" : {\n" +
                "      \"foo\":\"tested\"\n" +
                "  },\n" +
                "  \"redbox:submissionProcess.dc:description\": \"\",\n" +
                "  \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name\": \"\",\n" +
                "  \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone\": \"\",\n" +
                "  \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox\": \"\",\n" +
                "  \"redbox:submissionProcess.dc:title\": \"\",\n" +
                "  \"redbox:submissionProcess.skos:note\": \"\",\n" +
                "  \"redbox:embargo.redbox:isEmbargoed\": \"\",\n" +
                "  \"redbox:embargo.dc:date\": \"2016-03-17\",\n" +
                "  \"redbox:embargo.skos:note\": \"\",\n" +
                "  \"dc:relation.redbox:TechnicalMetadata.1.dc:identifier\": \"\",\n" +
                "  \"dc:relation.redbox:TechnicalMetadata.1.dc:title\": \"\",\n" +
                "  \"dc:relation.redbox:TechnicalMetadata.1.dc:type\": \"\",\n" +
                "  \"dc:relation.redbox:TechnicalMetadata.1.dc:conformsTo\": \"\",\n" +
                "  \"xmlns:dc\": \"http://dublincore.org/documents/2008/01/14/dcmi-terms/\",\n" +
                "  \"xmlns:foaf\": \"http://xmlns.com/foaf/spec/\",\n" +
                "  \"xmlns:anzsrc\": \"http://purl.org/anzsrc/\",\n" +
                "  \"metaList\": [\n" +
                "    \"dc:title\",\n" +
                "    \"dc:type.rdf:PlainLiteral\",\n" +
                "    \"dc:type.skos:prefLabel\",\n" +
                "    \"dc:created\",\n" +
                "    \"dc:modified\",\n" +
                "    \"dc:language.dc:identifier\",\n" +
                "    \"dc:language.skos:prefLabel\",\n" +
                "    \"redbox:formVersion\",\n" +
                "    \"redbox:newForm\",\n" +
                "    \"dc:coverage.vivo:DateTimeInterval.vivo:start\",\n" +
                "    \"dc:coverage.vivo:DateTimeInterval.vivo:end\",\n" +
                "    \"dc:coverage.redbox:timePeriod\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.dc:type\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.dc:type\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.redbox:wktRaw\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.redbox:wktRaw\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.rdf:PlainLiteral\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.rdf:PlainLiteral\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.geo:long\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.geo:long\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.geo:lat\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.geo:lat\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.1.dc:identifier\",\n" +
                "    \"dc:coverage.vivo:GeographicLocation.2.dc:identifier\",\n" +
                "    \"dc:description.1.text\",\n" +
                "    \"dc:description.1.type\",\n" +
                "    \"dc:relation.swrc:Publication.1.dc:identifier\",\n" +
                "    \"dc:relation.swrc:Publication.1.dc:title\",\n" +
                "    \"dc:relation.swrc:Publication.1.skos:note\",\n" +
                "    \"dc:relation.bibo:Website.1.dc:identifier\",\n" +
                "    \"dc:relation.bibo:Website.1.dc:title\",\n" +
                "    \"dc:relation.bibo:Website.1.skos:note\",\n" +
                "    \"dc:relation.vivo:Dataset.1.dc:identifier\",\n" +
                "    \"dc:relation.vivo:Dataset.1.vivo:Relationship.rdf:PlainLiteral\",\n" +
                "    \"dc:relation.vivo:Dataset.1.vivo:Relationship.skos:prefLabel\",\n" +
                "    \"dc:relation.vivo:Dataset.1.dc:title\",\n" +
                "    \"dc:relation.vivo:Dataset.1.skos:note\",\n" +
                "    \"dc:relation.vivo:Dataset.1.redbox:origin\",\n" +
                "    \"dc:relation.vivo:Dataset.1.redbox:publish\",\n" +
                "    \"dc:relation.vivo:Service.1.dc:identifier\",\n" +
                "    \"dc:relation.vivo:Service.1.vivo:Relationship.rdf:PlainLiteral\",\n" +
                "    \"dc:relation.vivo:Service.1.vivo:Relationship.skos:prefLabel\",\n" +
                "    \"dc:relation.vivo:Service.1.dc:title\",\n" +
                "    \"dc:relation.vivo:Service.1.skos:note\",\n" +
                "    \"dc:creator.foaf:Person.1.dc:identifier\",\n" +
                "    \"dc:creator.foaf:Person.2.dc:identifier\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:name\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:name\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:title\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:title\",\n" +
                "    \"dc:creator.foaf:Person.1.redbox:isCoPrimaryInvestigator\",\n" +
                "    \"dc:creator.foaf:Person.2.redbox:isCoPrimaryInvestigator\",\n" +
                "    \"dc:creator.foaf:Person.1.redbox:isPrimaryInvestigator\",\n" +
                "    \"dc:creator.foaf:Person.2.redbox:isPrimaryInvestigator\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:givenName\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:givenName\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:familyName\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:familyName\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:Organization.dc:identifier\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:Organization.dc:identifier\",\n" +
                "    \"dc:creator.foaf:Person.1.foaf:Organization.skos:prefLabel\",\n" +
                "    \"dc:creator.foaf:Person.2.foaf:Organization.skos:prefLabel\",\n" +
                "    \"locrel:prc.foaf:Person.dc:identifier\",\n" +
                "    \"locrel:prc.foaf:Person.foaf:name\",\n" +
                "    \"locrel:prc.foaf:Person.foaf:title\",\n" +
                "    \"locrel:prc.foaf:Person.foaf:givenName\",\n" +
                "    \"locrel:prc.foaf:Person.foaf:familyName\",\n" +
                "    \"locrel:prc.foaf:Person.foaf:email\",\n" +
                "    \"swrc:supervisor.foaf:Person.1.dc:identifier\",\n" +
                "    \"swrc:supervisor.foaf:Person.1.foaf:name\",\n" +
                "    \"swrc:supervisor.foaf:Person.1.foaf:title\",\n" +
                "    \"swrc:supervisor.foaf:Person.1.foaf:givenName\",\n" +
                "    \"swrc:supervisor.foaf:Person.1.foaf:familyName\",\n" +
                "    \"dc:contributor.locrel:clb.1.foaf:Agent\",\n" +
                "    \"dc:subject.anzsrc:for.1.skos:prefLabel\",\n" +
                "    \"dc:subject.anzsrc:for.1.rdf:resource\",\n" +
                "    \"dc:subject.vivo:keyword.1.rdf:PlainLiteral\",\n" +
                "    \"dc:subject.anzsrc:toa.rdf:resource\",\n" +
                "    \"dc:subject.anzsrc:toa.skos:prefLabel\",\n" +
                "    \"dc:accessRights.skos:prefLabel\",\n" +
                "    \"dc:accessRights.dc:identifier\",\n" +
                "    \"dc:accessRights.dc:RightsStatement.skos:prefLabel\",\n" +
                "    \"dc:accessRights.dc:RightsStatement.dc:identifier\",\n" +
                "    \"dc:license.skos:prefLabel\",\n" +
                "    \"dc:license.dc:identifier\",\n" +
                "    \"dc:license.rdf:Alt.skos:prefLabel\",\n" +
                "    \"dc:license.rdf:Alt.dc:identifier\",\n" +
                "    \"dc:identifier.rdf:PlainLiteral\",\n" +
                "    \"dc:identifier.dc:type.rdf:PlainLiteral\",\n" +
                "    \"dc:identifier.dc:type.skos:prefLabel\",\n" +
                "    \"dc:identifier.redbox:origin\",\n" +
                "    \"bibo:Website.1.dc:identifier\",\n" +
                "    \"vivo:Location.vivo:GeographicLocation.gn:name\",\n" +
                "    \"vivo:Location.vivo:GeographicLocation.skos:note\",\n" +
                "    \"redbox:retentionPeriod\",\n" +
                "    \"dc:extent\",\n" +
                "    \"redbox:disposalDate\",\n" +
                "    \"locrel:own.foaf:Agent.1.foaf:name\",\n" +
                "    \"locrel:dtm.foaf:Agent.foaf:name\",\n" +
                "    \"foaf:Organization.dc:identifier\",\n" +
                "    \"foaf:Organization.skos:prefLabel\",\n" +
                "    \"foaf:fundedBy.foaf:Agent.1.skos:prefLabel\",\n" +
                "    \"foaf:fundedBy.foaf:Agent.1.dc:identifier\",\n" +
                "    \"foaf:fundedBy.vivo:Grant.1.redbox:internalGrant\",\n" +
                "    \"foaf:fundedBy.vivo:Grant.1.redbox:grantNumber\",\n" +
                "    \"foaf:fundedBy.vivo:Grant.1.dc:identifier\",\n" +
                "    \"foaf:fundedBy.vivo:Grant.1.skos:prefLabel\",\n" +
                "    \"swrc:ResearchProject.dc:title\",\n" +
                "    \"locrel:dpt.foaf:Person.foaf:name\",\n" +
                "    \"dc:SizeOrDuration\",\n" +
                "    \"dc:Policy\",\n" +
                "    \"redbox:ManagementPlan.redbox:hasPlan\",\n" +
                "    \"redbox:ManagementPlan.skos:note\",\n" +
                "    \"skos:note.1.dc:created\",\n" +
                "    \"skos:note.1.foaf:name\",\n" +
                "    \"skos:note.1.dc:description\",\n" +
                "    \"dc:biblioGraphicCitation.skos:prefLabel\",\n" +
                "    \"dc:biblioGraphicCitation.redbox:sendCitation\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:identifier.skos:note\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:title\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:givenName\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.locrel:ctb.1.foaf:familyName\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:title\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:hasVersion.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:publisher.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.vivo:Publisher.vivo:Location\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.dc:type.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.dc:type.rdf:PlainLiteral\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.1.dc:type.skos:prefLabel\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.dc:date.2.dc:type.skos:prefLabel\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.bibo:Website.dc:identifier\",\n" +
                "    \"dc:biblioGraphicCitation.dc:hasPart.skos:scopeNote\",\n" +
                "    \"redbox:submissionProcess.redbox:submitted\",\n" +
                "    \"redbox:submissionProcess.dc:date\",\n" +
                "    \"redbox:submissionProcess.dc:description\",\n" +
                "    \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:name\",\n" +
                "    \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:phone\",\n" +
                "    \"redbox:submissionProcess.locrel:prc.foaf:Person.foaf:mbox\",\n" +
                "    \"redbox:submissionProcess.dc:title\",\n" +
                "    \"redbox:submissionProcess.skos:note\",\n" +
                "    \"redbox:embargo.redbox:isEmbargoed\",\n" +
                "    \"redbox:embargo.dc:date\",\n" +
                "    \"redbox:embargo.skos:note\",\n" +
                "    \"dc:relation.redbox:TechnicalMetadata.1.dc:identifier\",\n" +
                "    \"dc:relation.redbox:TechnicalMetadata.1.dc:title\",\n" +
                "    \"dc:relation.redbox:TechnicalMetadata.1.dc:type\",\n" +
                "    \"dc:relation.redbox:TechnicalMetadata.1.dc:conformsTo\",\n" +
                "    \"xmlns:dc\",\n" +
                "    \"xmlns:foaf\",\n" +
                "    \"xmlns:anzsrc\"\n" +
                "  ],\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.dc:type\": \"text\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.redbox:wktRaw\": \"POLYGON((132.78350830078 -35.766200546705,132.78350830078 -26.452951287538,142.62725830079 -26.452951287538,142.62725830079 -35.766200546705,132.78350830078 -35.766200546705))\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.rdf:PlainLiteral\": \"POLYGON((132.78350830078 -35.766200546705,132.78350830078 -26.452951287538,142.62725830079 -26.452951287538,142.62725830079 -35.766200546705,132.78350830078 -35.766200546705))\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.geo:long\": \"180\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.geo:lat\": \"170\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.2.dc:identifier\": \"\",\n" +
                "  \"dc:creator.foaf:Person.2.dc:identifier\": \"http://nla.gov.au/nla.party-965000\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:name\": \"Jensen, Liz\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:title\": \"\",\n" +
                "  \"dc:creator.foaf:Person.2.redbox:isCoPrimaryInvestigator\": \"\",\n" +
                "  \"dc:creator.foaf:Person.2.redbox:isPrimaryInvestigator\": \"\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:givenName\": \"Liz\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:familyName\": \"Jensen\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:Organization.dc:identifier\": \"\",\n" +
                "  \"dc:creator.foaf:Person.2.foaf:Organization.skos:prefLabel\": \"\",\n" +
                "  \"dc:subject.anzsrc:for.1.skos:prefLabel\": \"0402 - Geochemistry\",\n" +
                "  \"dc:subject.anzsrc:for.1.rdf:resource\": \"http://purl.org/asc/1297.0/2008/for/0402\",\n" +
                "  \"recordAsLocationDefault\": \"http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb\",\n" +
                "  \"relationships\": [\n" +
                "    {\n" +
                "      \"field\": \"dc:creator.foaf:Person.0.dc:identifier\",\n" +
                "      \"authority\": true,\n" +
                "      \"identifier\": \"redbox-mint.googlecode.com/parties_people/1241\",\n" +
                "      \"relationship\": \"hasCollector\",\n" +
                "      \"reverseRelationship\": \"isCollectorOf\",\n" +
                "      \"broker\": \"tcp://localhost:9201\",\n" +
                "      \"isCurated\": true,\n" +
                "      \"curatedPid\": \"http://demo.redboxresearchdata.com.au/mint/published/detail/84176738cc5e80306afc7adb163a4bab\"\n" +
                "    },\n" +
                " {\n" +
                "            \"field\": \"dc:relation.vivo:Service.1.dc:identifier\",\n" +
                "            \"authority\": true,\n" +
                "            \"identifier\": \"redbox-mint.googlecode.com/services/4\",\n" +
                "            \"relationship\": \"hasAssociationWith\",\n" +
                "            \"reverseRelationship\": \"hasAssociationWith\",\n" +
                "            \"broker\": \"tcp://localhost:9201\",\n" +
                "            \"isCurated\": true,\n" +
                "            \"curatedPid\": \"http://127.0.0.1:9001/mint/published/detail/6f4c827aabf664dbefec80e243adf891\"\n" +
                "        }\n" +
                "  ]\n" +
                "}"
    }

    def stubRifcsOutput() {
        return "<registryObjects\n" +
                "    xmlns=\"http://ands.org.au/standards/rif-cs/registryObjects\"\n" +
                "    xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://ands.org.au/standards/rif-cs/registryObjects http://services.ands.org.au/documentation/rifcs/1.6/schema/registryObjects.xsd\">\n" +
                "    <registryObject group=\"The University of Examples, Australia\">\n" +
                "        <key>http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb</key>\n" +
                "        <originatingSource>http://demo.redboxresearchdata.com.au/redbox/default</originatingSource>\n" +
                "        <collection dateAccessioned=\"2016-10-18T00:00:00.000+10:00\" type=\"collection\">\n" +
                "            <identifier type=\"local\">http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb</identifier>\n" +
                "            <identifier type=\"local\">Local identifier</identifier>\n" +
                "            <identifier type=\"abn\">abn stuff</identifier>\n" +
                "            <dates type=\"dc.created\">\n" +
                "                <date dateFormat=\"W3CDTF\" type=\"dateFrom\">2016-10-18T00:00:00.000+10:00</date>\n" +
                "            </dates>\n" +
                "            <relatedObject>\n" +
                "                <key>http://demo.redboxresearchdata.com.au/mint/published/detail/84176738cc5e80306afc7adb163a4bab</key>\n" +
                "                <relation type=\"hasCollector\"/>\n" +
                "            </relatedObject>\n" +
                "            <relatedObject>\n" +
                "                <key>http://127.0.0.1:9001/mint/published/detail/6f4c827aabf664dbefec80e243adf891</key>\n" +
                "                <relation type=\"hasAssociationWith\"/>\n" +
                "            </relatedObject>\n" +
                "            <relatedObject>\n" +
                "                <key>http://nla.gov.au/nla.party-965000</key>\n" +
                "                <relation type=\"hasCollector\"/>\n" +
                "            </relatedObject>\n" +
                "            <relatedObject>\n" +
                "                <key>http://orcid.org/0000-0001-6810-1260</key>\n" +
                "                <relation type=\"hasCollector\"/>\n" +
                "            </relatedObject>\n" +
                "            <relatedObject>\n" +
                "                <key>https://www.scopus.com/authid/detail.uri?authorId=000111</key>\n" +
                "                <relation type=\"hasCollector\"/>\n" +
                "            </relatedObject>\n" +
                "            <name type=\"primary\" xml:lang=\"en\">\n" +
                "                <namePart>Research Data Collection</namePart>\n" +
                "            </name>\n" +
                "            <location>\n" +
                "                <address>\n" +
                "                    <physical>\n" +
                "                        <addressPart type=\"text\">Brisbane</addressPart>\n" +
                "                    </physical>\n" +
                "                </address>\n" +
                "                <address>\n" +
                "                    <electronic type=\"url\">\n" +
                "                        <value>http://www.google.com</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "                <address>\n" +
                "                    <electronic type=\"url\">\n" +
                "                        <value>http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "                <address>\n" +
                "                    <electronic type=\"email\">\n" +
                "                        <value>anemail.com.au</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "            </location>\n" +
                "            <coverage>\n" +
                "                <temporal>\n" +
                "                    <date dateFormat=\"W3CDTF\" type=\"dateFrom\">2004-04-02T18:06:02.000+10:00</date>\n" +
                "                </temporal>\n" +
                "                <temporal>\n" +
                "                    <date dateFormat=\"W3CDTF\" type=\"dateTo\">2004-04-30T18:06:02.000+10:00</date>\n" +
                "                </temporal>\n" +
                "                <temporal>\n" +
                "                    <text>21st Century</text>\n" +
                "                </temporal>\n" +
                "            </coverage>\n" +
                "            <coverage>\n" +
                "                <spatial type=\"text\" xml:lang=\"en\">Brisbane</spatial>\n" +
                "                <spatial type=\"dcmiPoint\" xml:lang=\"en\">name=Brisbane; east=180; north=170; projection=WGS84</spatial>\n" +
                "                <spatial type=\"kmlPolyCoords\" xml:lang=\"en\">132.78350830078,-35.766200546705 132.78350830078,-26.452951287538 142.62725830079,-26.452951287538 142.62725830079,-35.766200546705 132.78350830078,-35.766200546705</spatial>\n" +
                "            </coverage>\n" +
                "            <subject type=\"local\" xml:lang=\"en\">keywords</subject>\n" +
                "            <subject type=\"anzsrc-for\" xml:lang=\"en\">0402</subject>\n" +
                "            <description type=\"full\" xml:lang=\"en\">&lt;p&gt;The description&lt;/p&gt;</description>\n" +
                "            <description type=\"brief\" xml:lang=\"en\">&lt;p&gt;The Brief description&lt;/p&gt;</description>\n" +
                "            <rights>\n" +
                "                <accessRights>Access rights</accessRights>\n" +
                "            </rights>\n" +
                "            <relatedInfo type=\"publication\">\n" +
                "                <title>answrcdctitle</title>\n" +
                "                <identifier type=\"uri\">answrcidentifier</identifier>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"website\">\n" +
                "                <title>abibodctitle</title>\n" +
                "                <identifier type=\"uri\">abiboidentifier</identifier>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"service\">\n" +
                "                <title>avivodctitle</title>\n" +
                "                <identifier type=\"uri\">avivodcidentifier</identifier>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"service\">\n" +
                "                <title>Service test</title>\n" +
                "                <identifier type=\"uri\">redbox-mint.googlecode.com/services/4</identifier>\n" +
                "            </relatedInfo>\n" +
                "            <relatedObject>\n" +
                "                <key>avivodcidentifier</key>\n" +
                "                <relation type=\"hasAssociationWith\"/>\n" +
                "            </relatedObject>\n" +
                "            <relatedObject>\n" +
                "                <key>redbox-mint.googlecode.com/services/4</key>\n" +
                "                <relation type=\"hasAssociationWith\"/>\n" +
                "            </relatedObject>\n" +
                "            <citationInfo>\n" +
                "                <fullCitation style=\"Datacite\">citation data id: http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb</fullCitation>\n" +
                "            </citationInfo>\n" +
                "        </collection>\n" +
                "    </registryObject>\n" +
                "</registryObjects>\n"
    }

    def stubRifcsOutputThatHasInvalidXml() {
        return "<registryObjects\n" +
                "    xmlns=\"http://ands.org.au/standards/rif-cs/registryObjects\"\n" +
                "    xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://ands.org.au/standards/rif-cs/registryObjects http://services.ands.org.au/documentation/rifcs/1.6/schema/registryObjects.xsd\">\n" +
                "    <registryObject group=\"\">\n" +
                "        <key>&Invalid ID: Not curated yet&</key>\n" +
                "        <originatingSource>http://demo.redboxresearchdata.com.au/redbox/default</originatingSource>\n" +
                "        <collection dateAccessioned=\"2016-10-18T00:00:00.000+10:00\" type=\"collection\">\n" +
                "            <identifier type=\"invalid\">&Invalid ID: Not curated yet&</identifier>\n" +
                "            <identifier type=\"local\">Local identifier</identifier>\n" +
                "            <identifier type=\"abn\">abn stuff</identifier>\n" +
                "            <dates type=\"dc.created\">\n" +
                "                <date dateFormat=\"W3CDTF\" type=\"dateFrom\">2016-10-18T00:00:00.000+10:00</date>\n" +
                "            </dates>\n" +
                "            <relatedObject>\n" +
                "                <key>http://demo.redboxresearchdata.com.au/mint/published/detail/84176738cc5e80306afc7adb163a4bab</key>\n" +
                "                <relation type=\"hasCollector\"/>\n" +
                "            </relatedObject>\n" +
                "            <relatedObject>\n" +
                "                <key>http://127.0.0.1:9001/mint/published/detail/6f4c827aabf664dbefec80e243adf891</key>\n" +
                "                <relation type=\"hasAssociationWith\"/>\n" +
                "            </relatedObject>\n" +
                "            <relatedObject>\n" +
                "                <key>http://nla.gov.au/nla.party-965000</key>\n" +
                "                <relation type=\"hasCollector\"/>\n" +
                "            </relatedObject>\n" +
                "            <relatedObject>\n" +
                "                <key>http://orcid.org/0000-0001-6810-1260</key>\n" +
                "                <relation type=\"hasCollector\"/>\n" +
                "            </relatedObject>\n" +
                "            <name type=\"primary\" xml:lang=\"en\">\n" +
                "                <namePart>Research Data Collection</namePart>\n" +
                "            </name>\n" +
                "            <location>\n" +
                "                <address>\n" +
                "                    <physical>\n" +
                "                        <addressPart type=\"text\">Brisbane</addressPart>\n" +
                "                    </physical>\n" +
                "                </address>\n" +
                "                <address>\n" +
                "                    <electronic type=\"url\">\n" +
                "                        <value>http://www.google.com</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "                <address>\n" +
                "                    <electronic type=\"url\">\n" +
                "                        <value>http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "                <address>\n" +
                "                    <electronic type=\"email\">\n" +
                "                        <value>anemail.com.au</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "            </location>\n" +
                "            <coverage>\n" +
                "                <temporal>\n" +
                "                    <date dateFormat=\"W3CDTF\" type=\"dateFrom\">2004-04-02T18:06:02.000+10:00</date>\n" +
                "                </temporal>\n" +
                "                <temporal>\n" +
                "                    <date dateFormat=\"W3CDTF\" type=\"dateTo\">2004-04-30T18:06:02.000+10:00</date>\n" +
                "                </temporal>\n" +
                "                <temporal>\n" +
                "                    <text>21st Century</text>\n" +
                "                </temporal>\n" +
                "            </coverage>\n" +
                "            <coverage>\n" +
                "                <spatial type=\"text\" xml:lang=\"en\">Brisbane</spatial>\n" +
                "                <spatial type=\"dcmiPoint\" xml:lang=\"en\">name=Brisbane; east=180; north=170; projection=WGS84</spatial>\n" +
                "                <spatial type=\"kmlPolyCoords\" xml:lang=\"en\">132.78350830078,-35.766200546705 132.78350830078,-26.452951287538 142.62725830079,-26.452951287538 142.62725830079,-35.766200546705 132.78350830078,-35.766200546705</spatial>\n" +
                "            </coverage>\n" +
                "            <subject type=\"local\" xml:lang=\"en\">keywords</subject>\n" +
                "            <subject type=\"anzsrc-for\" xml:lang=\"en\">0402</subject>\n" +
                "            <description type=\"full\" xml:lang=\"en\">&lt;p&gt;The description&lt;/p&gt;</description>\n" +
                "            <description type=\"brief\" xml:lang=\"en\">&lt;p&gt;The Brief description&lt;/p&gt;</description>\n" +
                "            <rights>\n" +
                "                <accessRights>Access rights</accessRights>\n" +
                "            </rights>\n" +
                "            <relatedInfo type=\"publication\">\n" +
                "                <title>answrcdctitle</title>\n" +
                "                <identifier type=\"uri\">answrcidentifier</identifier>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"website\">\n" +
                "                <title>abibodctitle</title>\n" +
                "                <identifier type=\"uri\">abiboidentifier</identifier>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"service\">\n" +
                "                <title>avivodctitle</title>\n" +
                "                <identifier type=\"uri\">avivodcidentifier</identifier>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"service\">\n" +
                "                <title>Service test</title>\n" +
                "                <identifier type=\"uri\">redbox-mint.googlecode.com/services/4</identifier>\n" +
                "            </relatedInfo>\n" +
                "            <relatedObject>\n" +
                "                <key>avivodcidentifier</key>\n" +
                "                <relation type=\"hasAssociationWith\"/>\n" +
                "            </relatedObject>\n" +
                "            <relatedObject>\n" +
                "                <key>redbox-mint.googlecode.com/services/4</key>\n" +
                "                <relation type=\"hasAssociationWith\"/>\n" +
                "            </relatedObject>\n" +
                "            <citationInfo>\n" +
                "                <fullCitation style=\"Datacite\">citation data id: &Invalid ID: Not curated yet&</fullCitation>\n" +
                "            </citationInfo>\n" +
                "        </collection>\n" +
                "    </registryObject>\n" +
                "</registryObjects>\n"
    }

}
