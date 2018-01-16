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

package au.com.redboxresearchdata.rifcs

import com.googlecode.fascinator.common.JsonSimple
import com.googlecode.fascinator.common.JsonSimpleConfig
import com.googlecode.fascinator.common.StorageDataUtil
import com.googlecode.fascinator.common.storage.impl.GenericDigitalObject
import groovy.util.logging.Slf4j
import groovy.xml.XmlUtil
import org.joda.time.DateTimeZone
import spock.lang.Shared

/**
 * @author <a href="matt@redboxresearchdata.com.au">Matt Mulholland</a>
 * Created on 21/10/2016.
 */
@Slf4j
class RifVelocityTest extends GenericVelocitySpecification {
    @Shared loader = new GroovyClassLoader(getClass().getClassLoader())
    @Shared scriptLocation = loader.getResource("home/scripts/tfpackageToRifcs.groovy").text
    @Shared scriptClass = new GroovyShell().parse(scriptLocation).class

    private def rifTemplateName = "rif.vm"

    def setup() {
        initTemplate(rifTemplateName)
    }

    def "main rifcs velocity test"() {
        given:
        loadTfPackage()
        when:
        def result = getRifcsVelocityOutputForAEST()
        def expected = new XmlSlurper().parseText(stubRifcsOutput()).declareNamespace("rif":"http://ands.org.au/standards/rif-cs/registryObjects")
        then:
        log.debug("result is " + result)
        assert result == XmlUtil.serialize(expected)
    }

    def "test invalid group and invalid id"() {
        given:
        loadTfPackageThatProducesInvalidXml()
        when:
        def result = getRifcsVelocityOutputForAEST()
        def preSanitised = preXmlHandle(stubRifcsOutputThatHasInvalidXml())
        def expected = new XmlSlurper().parseText(preSanitised).declareNamespace("rif":"http://ands.org.au/standards/rif-cs/registryObjects")
        then:
        log.debug("result is " + result)
        assert result == postXmlHandle(XmlUtil.serialize(expected))
    }

    def prettyprintXml(def xml) {
        def stringWriter = new StringWriter()
        new XmlNodePrinter(new PrintWriter(stringWriter)).print(xml)
        return stringWriter.toString()
    }

    def getRifcsVelocityOutputForAEST() {
        DateTimeZone.setDefault(DateTimeZone.forID("Australia/Brisbane"))
        def currentZone = DateTimeZone.getDefault()
        log.info("current zone is: " + currentZone)
        StringWriter writer = new StringWriter()
        velocityTemplate.merge(velocityContext, writer)
        String xml = writer.toString()
        return handleXml(xml)
    }

    def handleXml(xml) {
        //bypass test serialisation of invalid '&' markers we want to keep in order to fail rda ingest
        def preSanitised = preXmlHandle(xml)
        def result = new XmlSlurper().parseText(preSanitised)
        def serialised = XmlUtil.serialize(result)
        //add back '&' markers removed earlier
        def postSanitised = postXmlHandle(serialised)
        // any other legitimate '&' need to be escaped back after serialiser's work so reflects what actually happens in redbox
        def unescaped = postSanitised.replaceAll("&amp;", "&")
        return unescaped
    }

    
    def preXmlHandle(xml) {
        def pass1 =  xml.replaceAll("&Invalid XML placeholder... prevents ANDS Harvesting records in error&", "dummyinvalidxmlmarker1")
        def pass2 = pass1.replaceAll("&Invalid ID: Not curated yet&", "dummyinvalidxmlmarker2")
        return pass2
    }

    def postXmlHandle(xml) {
        def pass1 = xml.replaceAll("dummyinvalidxmlmarker1", "&Invalid XML placeholder... prevents ANDS Harvesting records in error&")
        def pass2 = pass1.replaceAll("dummyinvalidxmlmarker2", "&Invalid ID: Not curated yet&")
        return pass2
    }

    def loadTfPackage() {
        JsonSimple jsonSimple = new JsonSimple(stubTfpackage())
        JsonSimpleConfig jsonConfig = new JsonSimpleConfig(stubConfig())
        velocityContext.put("item", jsonSimple)
        velocityContext.put("util", new StorageDataUtil())
        velocityContext.put("systemConfig", jsonConfig)
        velocityContext.put("object", stubDigitalObject())
        velocityContext.put("urlBase", jsonConfig.getString(null, "urlBase"))
    }

    def loadTfPackageThatProducesInvalidXml() {
        JsonSimple jsonSimple = new JsonSimple(stubTfpackageNoFormOrigin())
        JsonSimpleConfig jsonConfig = new JsonSimpleConfig(stubConfigInvalidXml())
        velocityContext.put("item", jsonSimple)
        velocityContext.put("util", new StorageDataUtil())
        velocityContext.put("systemConfig", jsonConfig)
        velocityContext.put("object", stubDigitalObject())
        velocityContext.put("urlBase", jsonConfig.getString(null, "urlBase"))
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

    def stubConfigInvalidXml() {
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
                "  \"dc:coverage.redbox:timePeriod\": \"21st century\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.dc:type\": \"text\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.redbox:wktRaw\": \"\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.rdf:PlainLiteral\": \"Brisbane\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.geo:long\": \"180\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.geo:lat\": \"170\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.dc:identifier\": \"\",\n" +
                "  \"dc:description.1.text\": \"<p>The description</p>\",\n" +
                "  \"dc:description.1.shadow\": \"&lt;p&gt;The description&lt;/p&gt;\",\n" +
                "  \"dc:description.1.type\": \"full\",\n" +
                "  \"dc:description.2.text\": \"<p>The Brief description</p>\",\n" +
                "  \"dc:description.2.shadow\": \"&lt;p&gt;The Brief description&lt;/p&gt;\",\n" +
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
                "  \"dc:coverage.redbox:timePeriod\": \"21st century\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.dc:type\": \"text\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.redbox:wktRaw\": \"\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.rdf:PlainLiteral\": \"Brisbane\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.geo:long\": \"180\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.geo:lat\": \"170\",\n" +
                "  \"dc:coverage.vivo:GeographicLocation.1.dc:identifier\": \"\",\n" +
                "  \"dc:description.1.text\": \"<p>The description</p>\",\n" +
                "  \"dc:description.1.shadow\": \"&lt;p&gt;The description&lt;/p&gt;\",\n" +
                "  \"dc:description.1.type\": \"full\",\n" +
                "  \"dc:description.2.text\": \"<p>The Brief description</p>\",\n" +
                "  \"dc:description.2.shadow\": \"&lt;p&gt;The Brief description&lt;/p&gt;\",\n" +
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
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
                "<registryObjects\n" +
                "    xmlns=\"http://ands.org.au/standards/rif-cs/registryObjects\"\n" +
                "    xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://ands.org.au/standards/rif-cs/registryObjects http://services.ands.org.au/documentation/rifcs/1.6/schema/registryObjects.xsd\">\n" +
                "    <registryObject group=\"The University of Examples, Australia\">\n" +
                "        <key>http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb</key>\n" +
                "        <originatingSource>http://demo.redboxresearchdata.com.au/redbox/default</originatingSource>\n" +
                "        <collection dateAccessioned=\"2016-10-18T00:00:00.000+10:00\" type=\"collection\">\n" +
                "            <identifier type=\"local\">http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb</identifier>\n" +
                "            <identifier type=\"local\">Local identifier</identifier>\n" +
                "            <identifier type=\"abn\">abn stuff</identifier>\n" +
                "            <name type=\"primary\" xml:lang=\"en\">\n" +
                "                <namePart>Research Data Collection</namePart>\n" +
                "            </name>\n" +
                "            <dates type=\"dc.created\">\n" +
                "                <date dateFormat=\"W3CDTF\" type=\"dateFrom\">2016-10-18T00:00:00.000+10:00</date>\n" +
                "            </dates>\n" +
                "            <location>\n" +
                "                <address>\n" +
                "                    <electronic type=\"url\">\n" +
                "                        <value>http://www.google.com</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "                <address>\n" +
                "                    <physical>\n" +
                "                        <addressPart type=\"text\">Brisbane</addressPart>\n" +
                "                    </physical>\n" +
                "                </address>\n" +
                "                <address>\n" +
                "                   <electronic type=\"email\">\n" +
                "                        <value>anemail.com.au</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "            </location>\n" +
                "            <location>\n" +
                "                <address>\n" +
                "                    <electronic type=\"url\">\n" +
                "                        <value>http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "            </location>\n" +
                "            <coverage>\n" +
                "                <temporal>\n" +
                "                    <date dateFormat=\"W3CDTF\" type=\"dateFrom\">2004-04-02T18:06:02.000+10:00</date>\n" +
                "                    <date dateFormat=\"W3CDTF\" type=\"dateTo\">2004-04-30T18:06:02.000+10:00</date>\n" +
                "                    <text>21st century</text>\n" +
                "                </temporal>\n" +
                "            </coverage>\n" +
                "            <coverage>\n" +
                "                <spatial type=\"text\" xml:lang=\"en\">Brisbane</spatial>\n" +
                "                <spatial type=\"dcmiPoint\" xml:lang=\"en\">name=Brisbane; east=180; north=170; projection=WGS84</spatial>\n" +
                "            </coverage>\n" +
                "            <coverage>\n" +
                "                <spatial type=\"kmlPolyCoords\" xml:lang=\"en\">132.78350830078,-35.766200546705 132.78350830078,-26.452951287538 142.62725830079,-26.452951287538 142.62725830079,-35.766200546705 132.78350830078,-35.766200546705</spatial>\n" +
                "            </coverage>\n" +
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
                "            <subject type=\"local\" xml:lang=\"en\">keywords</subject>\n" +
                "            <subject type=\"anzsrc-for\" xml:lang=\"en\">0402</subject>\n" +
                "            <description type=\"full\" xml:lang=\"en\">&lt;p&gt;The description&lt;/p&gt;</description>\n" +
                "            <description type=\"brief\" xml:lang=\"en\">&lt;p&gt;The Brief description&lt;/p&gt;</description>\n" +
                "            <rights>\n" +
                "                <accessRights>Access rights</accessRights>\n" +
                "            </rights>\n" +
                "            <relatedInfo type=\"publication\">\n" +
                "                <identifier type=\"uri\">answrcidentifier</identifier>\n" +
                "                <title>answrcdctitle</title>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"website\">\n" +
                "                <identifier type=\"uri\">abiboidentifier</identifier>\n" +
                "                <title>abibodctitle</title>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"service\">\n" +
                "                <identifier type=\"uri\">avivodcidentifier</identifier>\n" +
                "                <title>avivodctitle</title>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"service\">\n" +
                "                <identifier type=\"uri\">redbox-mint.googlecode.com/services/4</identifier>\n" +
                "                <title>Service test</title>\n" +
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
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
                "<registryObjects\n" +
                "    xmlns=\"http://ands.org.au/standards/rif-cs/registryObjects\"\n" +
                "    xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://ands.org.au/standards/rif-cs/registryObjects http://services.ands.org.au/documentation/rifcs/1.6/schema/registryObjects.xsd\">\n" +
                "    <registryObject group=\"&Invalid XML placeholder... prevents ANDS Harvesting records in error&\">\n" +
                "        <key>&Invalid ID: Not curated yet&</key>\n" +
                "        <originatingSource>http://demo.redboxresearchdata.com.au/redbox/default</originatingSource>\n" +
                "        <collection dateAccessioned=\"2016-10-18T00:00:00.000+10:00\" type=\"collection\">\n" +
                "            <identifier type=\"invalid\">&Invalid ID: Not curated yet&</identifier>\n" +
                "            <identifier type=\"local\">Local identifier</identifier>\n" +
                "            <identifier type=\"abn\">abn stuff</identifier>\n" +
                "            <name type=\"primary\" xml:lang=\"en\">\n" +
                "                <namePart>Research Data Collection</namePart>\n" +
                "            </name>\n" +
                "            <dates type=\"dc.created\">\n" +
                "                <date dateFormat=\"W3CDTF\" type=\"dateFrom\">2016-10-18T00:00:00.000+10:00</date>\n" +
                "            </dates>\n" +
                "            <location>\n" +
                "                <address>\n" +
                "                    <electronic type=\"url\">\n" +
                "                        <value>http://www.google.com</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "                <address>\n" +
                "                    <physical>\n" +
                "                        <addressPart type=\"text\">Brisbane</addressPart>\n" +
                "                    </physical>\n" +
                "                </address>\n" +
                "                <address>\n" +
                "                   <electronic type=\"email\">\n" +
                "                        <value>anemail.com.au</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "            </location>\n" +
                "            <location>\n" +
                "                <address>\n" +
                "                    <electronic type=\"url\">\n" +
                "                        <value>http://demo.redboxresearchdata.com.au/redbox/published/detail/df96891d804da76bf2f30fb253d4aebb</value>\n" +
                "                    </electronic>\n" +
                "                </address>\n" +
                "            </location>\n" +
                "            <coverage>\n" +
                "                <temporal>\n" +
                "                    <date dateFormat=\"W3CDTF\" type=\"dateFrom\">2004-04-02T18:06:02.000+10:00</date>\n" +
                "                    <date dateFormat=\"W3CDTF\" type=\"dateTo\">2004-04-30T18:06:02.000+10:00</date>\n" +
                "                    <text>21st century</text>\n" +
                "                </temporal>\n" +
                "            </coverage>\n" +
                "            <coverage>\n" +
                "                <spatial type=\"text\" xml:lang=\"en\">Brisbane</spatial>\n" +
                "                <spatial type=\"dcmiPoint\" xml:lang=\"en\">name=Brisbane; east=180; north=170; projection=WGS84</spatial>\n" +
                "            </coverage>\n" +
                "            <coverage>\n" +
                "                <spatial type=\"kmlPolyCoords\" xml:lang=\"en\">132.78350830078,-35.766200546705 132.78350830078,-26.452951287538 142.62725830079,-26.452951287538 142.62725830079,-35.766200546705 132.78350830078,-35.766200546705</spatial>\n" +
                "            </coverage>\n" +
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
                "            <subject type=\"local\" xml:lang=\"en\">keywords</subject>\n" +
                "            <subject type=\"anzsrc-for\" xml:lang=\"en\">0402</subject>\n" +
                "            <description type=\"full\" xml:lang=\"en\">&lt;p&gt;The description&lt;/p&gt;</description>\n" +
                "            <description type=\"brief\" xml:lang=\"en\">&lt;p&gt;The Brief description&lt;/p&gt;</description>\n" +
                "            <rights>\n" +
                "                <accessRights>Access rights</accessRights>\n" +
                "            </rights>\n" +
                "            <relatedInfo type=\"publication\">\n" +
                "                <identifier type=\"uri\">answrcidentifier</identifier>\n" +
                "                <title>answrcdctitle</title>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"website\">\n" +
                "                <identifier type=\"uri\">abiboidentifier</identifier>\n" +
                "                <title>abibodctitle</title>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"service\">\n" +
                "                <identifier type=\"uri\">avivodcidentifier</identifier>\n" +
                "                <title>avivodctitle</title>\n" +
                "            </relatedInfo>\n" +
                "            <relatedInfo type=\"service\">\n" +
                "                <identifier type=\"uri\">redbox-mint.googlecode.com/services/4</identifier>\n" +
                "                <title>Service test</title>\n" +
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
