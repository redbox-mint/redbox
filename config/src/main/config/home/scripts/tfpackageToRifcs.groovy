/*
 *
 *  Copyright (C) 2016 Queensland Cyber Infrastructure Foundation (http://www.qcif.edu.au/)
 *
 *    This program is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation; either version 2 of the License, or
 *    (at your option) any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License along
 *    with this program; if not, write to the Free Software Foundation, Inc.,
 *    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 * /
 */
package au.com.redboxresearchdata.rifcs.transformer

import au.com.redboxresearchdata.rifcs.ands.builder.impl.RifcsCollectionBuilder
import au.com.redboxresearchdata.rifcs.ands.builder.impl.RifcsCoreBuilder
import au.com.redboxresearchdata.rifcs.ands.builder.sub.impl.RifcsLocationBuilder
import au.com.redboxresearchdata.rifcs.ands.builder.sub.impl.RifcsRightsBuilder
import au.com.redboxresearchdata.rifcs.ands.builder.sub.impl.RifcsSpatialCoverageBuilder
import au.com.redboxresearchdata.rifcs.ands.builder.sub.impl.RifcsTemporalCoverageBuilder
import com.googlecode.fascinator.api.storage.DigitalObject
import com.googlecode.fascinator.api.storage.StorageException
import com.googlecode.fascinator.api.transformer.TransformerException
import com.googlecode.fascinator.common.JsonSimpleConfig
import com.googlecode.fascinator.common.StorageDataUtil
import com.googlecode.fascinator.transformer.ScriptingTransformer
import groovy.json.JsonSlurper
import groovy.util.logging.Slf4j
import org.ands.rifcs.base.RIFCSWrapper
import org.apache.commons.lang3.StringUtils
import org.slf4j.LoggerFactory
import org.w3c.dom.DOMConfiguration
import org.w3c.dom.DOMImplementation
import org.w3c.dom.ls.DOMImplementationLS
import org.w3c.dom.ls.LSOutput
import org.w3c.dom.ls.LSSerializer

import javax.xml.XMLConstants
import javax.xml.transform.dom.DOMSource
import javax.xml.validation.Schema
import javax.xml.validation.SchemaFactory
import javax.xml.validation.Validator

/**
 * Builder to wrap <a href="https://github.com/au-research/ANDS-RIFCS-API.git">ANDS-RIFCS-API</a>
 * @version
 * @author <a href="matt@redboxresearchdata.com.au">Matt Mulholland</a>
 */

def log = LoggerFactory.getLogger(ScriptingTransformer.class)
log.info("TfpackageToRifcs script starting...")

String data = null
try {
    data = new TfpackageToRifcs(digitalObject).transformAndStore()
} catch (Exception e) {
    throw new TransformerException("Could not create rifcs from script.", e)
}

return digitalObject

// convenience method
static def createInstance(digitalObject, config) {
    return new TfpackageToRifcs(digitalObject, config)
}

@Slf4j
class TfpackageToRifcs {
    final DigitalObject digitalObject
    // using methods from JsonSimple ensures system properties are injected
    final JsonSimpleConfig config
    final def metadata
    final def tfpackage
    final def urlBase

    TfpackageToRifcs(final DigitalObject digitalObject) {
        this.digitalObject = digitalObject
        this.config = new JsonSimpleConfig()
        this.urlBase = this.config.getString(null, "urlBase")
        this.metadata = digitalObject.getMetadata()
        this.tfpackage = parseJson(getTfpackage(digitalObject))
    }

    TfpackageToRifcs(final DigitalObject digitalObject, final String config) {
        this.digitalObject = digitalObject
        this.config = new JsonSimpleConfig(config)
        this.urlBase = this.config.getString(null, "urlBase")
        this.metadata = digitalObject.getMetadata()
        this.tfpackage = parseJson(getTfpackage(digitalObject))
    }

    def parseJson(text) {
        JsonSlurper slurper = new JsonSlurper()
        log.info 'slurping text...'
        def json = slurper.parseText(text)
        log.debug("Printing json text as groovy json...")
        log.trace(json.toString())
        return json
    }

    def prettyPrint(RIFCSWrapper data) {
        ByteArrayOutputStream baos = new ByteArrayOutputStream()
        // turn off the <?xml.../> declaration at start: this will interfere in generating xml list of records later (ie: xml can only appear ONCE in xml doc)
        def parameters = ["xml-declaration": false]
        data.write(baos, parameters)
        log.debug("returning pretty print format for ${data.class} ...")
        return baos.toString()
    }

    def getTfpackage(DigitalObject digitalObject) {
        def tfpackageKey = digitalObject.getPayloadIdList().find { it =~ /.*\.tfpackage/ }
        log.debug("tf package key is " + tfpackageKey)
        def tfpackage = digitalObject.getPayload(tfpackageKey).open().text
        log.trace("tfpackage text is: " + tfpackage)
        return tfpackage
    }

    def getISO8601DateString(String date) {
        if (StringUtils.isNotBlank(date)) {
            return new StorageDataUtil().getW3CDateTime(date)
        }
    }

    Expando createIdentifierData() {
        def pidProperty = config.getString(null, "curation", "pidProperty")
        def metadataPid = pidProperty ? digitalObject?.getMetadata().get(pidProperty) : null
        String pid = metadataPid ?: tfpackage.metadata?.'rdf:resource' ?: tfpackage.metadata?.'dc.identifier'
        log.debug("pid is: " + pid)

        def expando = new Expando()
        if (tfpackage.'dc:identifier.redbox:origin' == 'internal') {
            expando.identifier = pid ?: urlBase + "/detail/" + metadata.get("objectId")
            expando.identifierType = pid ? StringUtils.defaultIfBlank(config.getString(null, "curation", "pidType"), "&Invalid XML placeholder... prevents ANDS Harvesting records in error&") : "uri"
        } else {
            expando.identifier = tfpackage.'dc:identifier.rdf:PlainLiteral' ?: "&Invalid ID: Not curated yet&"
            expando.identifierType = tfpackage.'dc:identifier.rdf:PlainLiteral' ? tfpackage.'dc:identifier.dc:type.rdf:PlainLiteral' : "invalid"
        }
        if (!expando.identifierType) {
            log.warn("No identifier type set for identifier: " + expando.identifier)
        }
        log.debug("identifier is: " + expando.identifier)
        log.debug("identifier type is: " + expando.identifierType)
        return expando
    }

    def getAllRelations() {
        def relations = tfpackage.relationships
        log.trace("relations are: " + relations)
        def collected = relations.findAll {
            log.debug("next relation: " + it)
            it.isCurated && it.curatedPid?.trim()
        }.collect {
            [key: it.curatedPid, type: it.relationship ?: "hasAssociationWith", description: it.description]
        }
        log.debug("relations collected: " + collected)
        def grouped = collected.plus(getAllNlaRelations()).plus(getAllOrcidRelations()).plus(getAllFreeTextRelations()).groupBy {
            it.key
        }
        log.debug("grouped: " + grouped)
        return grouped
    }

    def getAllElectronicAddress() {
        return findAndCollect(getTfpackageNumberedCollection("bibo:Website"), 'dc:identifier') << tfpackage.'recordAsLocationDefault'
    }

    def getAllNlaRelations() {
        return findAndCollect(getTfpackageNumberedCollection("dc:creator.foaf:Person"),
                { k, v -> v.'dc:identifier'?.trim() && v.'dc:identifier' =~ /http:\/\/nla.gov.au\/nla.party-/ },
                { k, v -> [key: v.'dc:identifier', type: "hasCollector"] }
        )
    }

    def getAllOrcidRelations() {
        return findAndCollect(getTfpackageNumberedCollection("dc:creator.foaf:Person"),
                { k, v -> v.'dc:identifier'?.trim() && v.'dc:identifier' =~ /http:\/\/orcid.org\// },
                { k, v -> [key: v.'dc:identifier', type: "hasCollector"] }
        )
    }

    def getAllFreeTextRelations() {
        return findAndCollect(getTfpackageNumberedCollection("identifierText"),
                { k, v -> v.'creatorName.input'?.trim()?.length() > 0 },
                { k, v -> [key: v.'creatorName.input', type: "hasCollector"] }
        )
    }

    def getAllGeoSpatialCoverage() {
        return findAndCollect(getTfpackageNumberedCollection("dc:coverage.vivo:GeographicLocation"),
                { k, v ->
                    log.debug("next key: ${k} has value: ${v}")
                    v.'rdf:PlainLiteral'?.trim()
                },
                { k, v ->
                    def first = [[type: v.'dc:type', value: v.'rdf:PlainLiteral']]
                    if (!(v.'redbox:wktRaw'?.trim())) {
                        return v.'dc:type'.trim() == 'text' ? first <<
                                [type: "dcmiPoint", value: "name="
                                        + v.'rdf:PlainLiteral'
                                        + "; east="
                                        + v.'geo:long'
                                        + "; north="
                                        + v.'geo:lat'
                                        + "; projection=WGS84"
                                ]
                                : first
                    } else if (v.'dc:type'?.trim()) {
                        if (v.'rdf:PlainLiteral'?.startsWith("POLYGON")) {
                            //the placement of commas is counter to what's required
                            def kmlResult = v.'rdf:PlainLiteral'.replaceFirst(/POLYGON\(\((.*)\)\)/, "\$1").split(",").collect {
                                it.replace(" ", ",")
                            }.join(" ")
                            return [type: "kmlPolyCoords", value: kmlResult]
                        } else
                            return first
                    } else {
                        log.debug("redbox:wktRaw is not empty, but there is no type present. No geo spatial coverage collected.")
                    }
                }).flatten()
    }

    def getAllSubjects() {
        def subjects = findAndCollect(getTfpackageNumberedCollection("dc:subject.vivo:keyword"), "rdf:PlainLiteral",
                { k, v ->
                    [value: v.'rdf:PlainLiteral', type: "local"]
                })
                .plus(
                findAndCollect(getTfpackageNumberedCollection("dc:subject.anzsrc:for"), "rdf:resource",
                        { k, v ->
                            [value: ("${v.'rdf:resource'}".replaceFirst(~".*[/]", "")), type: "anzsrc-for"]
                        }))
                .plus(
                findAndCollect(getTfpackageNumberedCollection("dc:subject.anzsrc:seo"), "rdf:resource",
                        { k, v ->
                            [value: ("${v.'rdf:resource'}".replaceFirst(~".*[/]", "")), type: "anzsrc-seo"]
                        }))
        return tfpackage.'dc:subject.anzsrc:toa.skos:prefLabel' ? subjects.plus([value: tfpackage.'dc:subject.anzsrc:toa.skos:prefLabel', type: "anzsrc-toa"]) : subjects
    }

    def getAllRelatedInfo() {
        return getRelatedInfo("dc:relation.swrc:Publication", "publication", "uri").
                plus(getRelatedInfo("dc:relation.bibo:Website", "website", "uri")).
                plus(getRelatedInfo("dc:relation.vivo:Service", "service", "uri")).flatten()
    }

    def getRelatedInfo(def field, def type, def identifierType) {
        return findAndCollect(getTfpackageNumberedCollection(field), "dc:identifier",
                { k, v ->
                    if ((v.'dc:identifier')?.trim()) {
                        def returned = [identifier: v.'dc:identifier', type: type, identifierType: identifierType]
                        if ((v.'dc:title')?.trim()) {
                            returned << [title: v.'dc:title']
                        }
                        return returned
                    }
                })
    }

    def getRelatedObject(def field) {
        def relations = tfpackage.relationships
        // check relations for duplicate of relatedObject
        def relationsCollected = relations.findAll {
            log.debug("next checked relation for related object: " + it)
            it.isCurated && it.curatedPid?.trim()
        }.collect {
            it.curatedPid
        }
        log.debug("relation keys to check against object are: " + relationsCollected)
        return findAndCollect(getTfpackageNumberedCollection(field), "dc:identifier",
                { k, v ->
                    if ((v.'dc:identifier')?.trim() && !relationsCollected.contains(v.'dc:identifier')) {
                        def returned = [key: v.'dc:identifier']
                        if ((v.'vivo:Relationship.rdf:PlainLiteral')?.trim()) {
                            returned << [type: v.'vivo:Relationship.rdf:PlainLiteral']
                        }
                        return returned
                    }
                })
    }

    def getCitation(def identifierData) {
//        <citationInfo> element should contain either <fullCitation> or <citationMetadata> (not both)
        def doiProperty = config.getString(null, "andsDoi", "doiProperty")
        if (tfpackage.'dc:biblioGraphicCitation.redbox:sendCitation'?.trim() == "on") {
            String value = tfpackage.'dc:biblioGraphicCitation.skos:prefLabel'
            def doi = doiProperty ? metadata.get(doiProperty) : null
            if (value?.trim()) {
                // send citation info value
                return [style: "Datacite", citation: value.replaceAll(/\{ID_WILL_BE_HERE\}/, doi ? "http://dx.doi.org/" + doi : identifierData.identifier)]
            }
        }
    }


    def getAllDescriptions() {
        return findAndCollect(getTfpackageNumberedCollection("dc:description"),
                { k, v -> v.'text'?.trim() && v.'type'?.trim() },
                { k, v -> [value: v.'text', type: v.'type'] }
        )
    }

    def getAllAdditionalIdentifiers() {
        log.debug("adding additional identifiers");
        return findAndCollect(getTfpackageNumberedCollection("dc:additionalidentifier"),
                { k, v -> v.'rdf:PlainLiteral'?.trim() && v.'type.rdf:PlainLiteral'?.trim() },
                { k, v -> [value: v.'rdf:PlainLiteral', type: v.'type.rdf:PlainLiteral'] }
        )
    }

    def getAccessRights() {
        if (tfpackage.'dc:accessRights.skos:prefLabel'?.trim()) {
            def returned = [value: tfpackage.'dc:accessRights.skos:prefLabel']
            if (tfpackage.'dc:accessRightsType'?.trim()) {
                returned << [type: tfpackage.'dc:accessRightsType']
            }
            if (tfpackage.'dc:accessRights.dc:identifier'?.trim()) {
                returned << [uri: tfpackage.'dc:accessRights.dc:identifier']
            }
            return returned
        }
    }

    def getLicence() {
        def licenceTypes = ["CC BY: Attribution 3.0 AU"                                                  : "CC-BY",
                            "CC BY-SA: Attribution-Share Alike 3.0 AU"                                   : "CC-BY-SA",
                            "CC BY-ND: Attribution-No Derivative Works 3.0 AU"                           : "CC-BY-ND",
                            "CC BY-NC: Attribution-Noncommercial 3.0 AU"                                 : "CC-BY-NC",
                            "CC BY-NC-SA: Attribution-Noncommercial-Share Alike 3.0 AU"                  : "CC-BY-NC-SA",
                            "CC BY-NC-ND: Attribution-Noncommercial-No Derivatives 3.0 AU"               : "CC-BY-NC-ND",
                            "CC BY 4.0: Attribution 4.0 International"                                   : "CC-BY",
                            "CC BY-SA 4.0: Attribution-Share Alike 4.0 International"                    : "CC-BY-SA",
                            "CC BY-ND 4.0: Attribution-No Derivative Works 4.0 International"            : "CC-BY-ND",
                            "CC BY-NC 4.0: Attribution-Noncommercial 4.0 International"                  : "CC-BY-NC",
                            "CC BY-NC-SA 4.0: Attribution-Noncommercial-Share Alike 4.0 International"   : "CC-BY-NC-SA",
                            "CC BY-NC-ND 4.0: Attribution-Noncommercial-No Derivatives 4.0 International": "CC-BY-NC-ND",
                            "PDDL - Public Domain Dedication and License 1.0"                            : "Unknown/Other",
                            "ODC-By - Attribution License 1.0"                                           : "Unknown/Other",
                            "ODC-ODbL - Attribution Share-Alike for data/databases 1.0"                  : "Unknown/Other"
        ]
        def defaultLicenceType = "Unknown/Other"
        if (tfpackage.'dc:license.skos:prefLabel'?.trim() && tfpackage.'dc:license.dc:identifier'?.trim()) {
            def licenceType = licenceTypes[(tfpackage.'dc:license.skos:prefLabel')] ?: defaultLicenceType
            return [value: tfpackage.'dc:license.skos:prefLabel', uri: tfpackage.'dc:license.dc:identifier', type: licenceType]
        } else if (tfpackage.'dc:license.rdf:Alt.skos:prefLabel'?.trim()) {
            def licenceType = licenceTypes[(tfpackage.'dc:license.rdf:Alt.skos:prefLabel')] ?: defaultLicenceType
            return tfpackage.'dc:license.rdf:Alt.dc:identifier' ? [value: tfpackage.'dc:license.rdf:Alt.skos:prefLabel', uri: tfpackage.'dc:license.rdf:Alt.dc:identifier', type: licenceType] :
                    [value: tfpackage.'dc:license.rdf:Alt.skos:prefLabel', type: licenceType]
        } else {
            return null
        }
    }

    def getRightsStatement() {
        if (tfpackage.'dc:accessRights.dc:RightsStatement.skos:prefLabel'?.trim()) {
            return tfpackage.'dc:accessRights.dc:RightsStatement.dc:identifier' ? [value: tfpackage.'dc:accessRights.dc:RightsStatement.skos:prefLabel', uri: tfpackage.'dc:accessRights.dc:RightsStatement.dc:identifier'] :
                    [value: tfpackage.'dc:accessRights.dc:RightsStatement.skos:prefLabel']

        }
    }

    def getTfpackageNumberedCollection(String listCriteria) {
        return new StorageDataUtil().getList(tfpackage, listCriteria)
    }

    def findAndCollect(def data, String findCriteria) {
        findAndCollect(data, findCriteria, findCriteria)
    }


    def findAndCollect(def data, String findCriteria, String collectCriteria) {
        findAndCollect(data,
                { k, v -> v[(findCriteria)]?.trim() },
                { k, v -> v[(collectCriteria)] })
    }

    def findAndCollect(def data, String findCriteria, Closure collectCriteria) {
        findAndCollect(data,
                { k, v -> v[(findCriteria)]?.trim() },
                collectCriteria)
    }

    def findAndCollect(def data, Closure findCriteria, Closure collectCriteria) {
        log.debug("data to search is: " + data)
        def collected = data.findAll(findCriteria).collect(collectCriteria)
        log.debug("collected: " + collected)
        return collected
    }


    def addNonEmpty = { methodName, value ->
        if (value) {
            return delegate."${methodName}"(value)
        }
        return delegate
    }

    def addEveryNonEmpty = { methodName, values ->
        values.each {
            if (it) {
                owner.delegate = owner.delegate."${methodName}"(it)
            }
        }
        return delegate
    }

    def addEveryNonEmptyMap = { methodName, values ->
        values.each { k, v ->
            if (k) {
                owner.delegate = owner.delegate."${methodName}"(k, v)
            }
        }
        return delegate
    }

    /** ensure that any class additions such as ExpandoMetaClass are added to implementations not abstract/parent classes, so that
     * they are reset with each run.
     *
     */
    def resetCollectClosures() {
        RifcsCollectionBuilder.metaClass.addNonEmpty = addNonEmpty
        RifcsCollectionBuilder.metaClass.addEveryNonEmpty = addEveryNonEmpty
        RifcsCollectionBuilder.metaClass.addEveryNonEmptyMap = addEveryNonEmptyMap

        RifcsLocationBuilder.metaClass.addNonEmpty = addNonEmpty
        RifcsLocationBuilder.metaClass.addEveryNonEmpty = addEveryNonEmpty
        RifcsTemporalCoverageBuilder.metaClass.addNonEmpty = addNonEmpty
        RifcsSpatialCoverageBuilder.metaClass.addEveryNonEmpty = addEveryNonEmpty
        RifcsRightsBuilder.metaClass.addNonEmpty = addNonEmpty
    }

    def overrideRIFCSWrapper() {
        RIFCSWrapper.metaClass.validate = {
            // ensures dependencies do not override schema factory library that works with ANDS library
            SchemaFactory factory = SchemaFactory.newInstance(
                    XMLConstants.W3C_XML_SCHEMA_NS_URI, "com.sun.org.apache.xerces.internal.jaxp.validation.XMLSchemaFactory", null)
            Schema schema = factory.newSchema(doXercesWorkaround())

            Validator validator = schema.newValidator()
            validator.validate(new DOMSource(doc))
        }

        // enable setting of parameters
        RIFCSWrapper.metaClass.write << { final OutputStream os, Map<String, Boolean> parameters ->
            DOMImplementation impl = doc.getImplementation();
            DOMImplementationLS implLS =
                    (DOMImplementationLS) impl.getFeature("LS", "3.0");

            LSOutput lso = implLS.createLSOutput()
            lso.setByteStream(os)
            LSSerializer writer = implLS.createLSSerializer()
            DOMConfiguration domConfig = writer.getDomConfig()
            // keep default parameter for pretty print, but allow it also to be overridden
            domConfig.setParameter("format-pretty-print", Boolean.TRUE);
            for (Map.Entry<String, Boolean> entry : parameters.entrySet()) {
                String key = entry.getKey()
                Boolean value = entry.getValue()
                domConfig.setParameter(key, value)
            }
            writer.write(doc, lso);
        }
    }


    def transform() {
        def identifierData = createIdentifierData()

        overrideRIFCSWrapper()

        resetCollectClosures()

        RifcsCoreBuilder.metaClass.dateModified = { String date ->
            proxy.setDateModified(date)
            return delegate
        }

        RifcsCollectionBuilder.metaClass.dateModified = { String date ->
            coreBuilder.dateModified(date);
            return delegate
        }

        def rifcs = new RifcsCollectionBuilder(identifierData.identifier, urlBase, config.getString(null, "identity", "RIF_CSGroup"), tfpackage.'dc:type.rdf:PlainLiteral')
                .identifier(identifierData.identifier, identifierData.identifierType)
                .addEveryNonEmpty('identifier', getAllAdditionalIdentifiers())
                .addNonEmpty('dateModified', getISO8601DateString(tfpackage.'dc:modified'))
                .addNonEmpty('dateAccessioned', getISO8601DateString(tfpackage.'dc:created'))
                .addNonEmpty('dateCreated', getISO8601DateString(tfpackage.'dc:created'))
                .addEveryNonEmptyMap('relatedObjects', getAllRelations())
                .addNonEmpty('primaryName', tfpackage.'dc:title')
                .locationBuilder()
                .addNonEmpty('physicalAddress', tfpackage.'vivo:Location.vivo:GeographicLocation.gn:name')
                .addEveryNonEmpty('urlElectronicAddress', getAllElectronicAddress())
                .addNonEmpty('emailElectronicAddress', tfpackage.'locrel:prc.foaf:Person.foaf:email')
                .build()
                .temporalCoverageBuilder()
                .addNonEmpty('coverageDateFrom', getISO8601DateString(tfpackage.'dc:coverage.vivo:DateTimeInterval.vivo:start'))
                .addNonEmpty('coverageDateTo', getISO8601DateString(tfpackage.'dc:coverage.vivo:DateTimeInterval.vivo:end'))
                .addNonEmpty('coveragePeriod', tfpackage.'dc:coverage.redbox:timePeriod')
                .build()
                .spatialCoverageBuilder()
                .addEveryNonEmpty('spatial', getAllGeoSpatialCoverage())
                .build()
                .addEveryNonEmpty('subject', getAllSubjects())
                .addEveryNonEmpty('description', getAllDescriptions())
                .rightsBuilder()
                .addNonEmpty('accessRights', getAccessRights())
                .addNonEmpty('licence', getLicence())
                .addNonEmpty('rightsStatement', getRightsStatement())
                .build()
                .addEveryNonEmpty('relatedInfo', getAllRelatedInfo())
                .addEveryNonEmpty('relatedObject', getRelatedObject("dc:relation.vivo:Service"))
                .addNonEmpty('fullCitation', getCitation(identifierData))
                .build()

        def prettyPrintedRifcs = fixEscapedInvalidMarkers(prettyPrint(rifcs))
        log.info("pre-validation rifcs transformation: " + prettyPrintedRifcs)
        // validation is slow as fetches schema every time for Document - TODO: fetch and cache
//        rifcs.validate()
        return prettyPrintedRifcs
    }

    def fixEscapedInvalidMarkers(xml) {
        def pass1 = xml.replaceAll("&amp;Invalid ID: Not curated yet&amp;", "&Invalid ID: Not curated yet&")
        def pass2 = pass1.replaceAll("&amp;Invalid XML placeholder... prevents ANDS Harvesting records in error&amp;", "&Invalid XML placeholder... prevents ANDS Harvesting records in error&")
        return pass2
    }


    def transformAndStore() {
        String transformation = this.transform()
        try {
            return digitalObject.createStoredPayload("rif.xml", getInputStream(transformation))
        } catch (StorageException e) {
            log.warn("Assuming digital object already exists. Will try to update it....", e.getCause())
            return digitalObject.updatePayload("rif.xml", getInputStream(transformation))
        }
    }

    def getInputStream(String data) {
        return new ByteArrayInputStream(data.getBytes("UTF8"))
    }
}