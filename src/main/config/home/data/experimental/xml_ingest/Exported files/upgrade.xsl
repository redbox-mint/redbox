<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:my="http://schemas.microsoft.com/office/infopath/2003/myXSD/2011-09-26T07:17:47" xmlns:xd="http://schemas.microsoft.com/office/infopath/2003" version="1.0">
	<xsl:output encoding="UTF-8" method="xml"/>
	<xsl:template match="/">
		<xsl:copy-of select="processing-instruction() | comment()"/>
		<xsl:choose>
			<xsl:when test="my:RedboxCollection">
				<xsl:apply-templates select="my:RedboxCollection" mode="_0"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:variable name="var">
					<xsl:element name="my:RedboxCollection"/>
				</xsl:variable>
				<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_0"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template match="my:Creator" mode="_2">
		<xsl:copy>
			<xsl:element name="my:CreatorTitle">
				<xsl:copy-of select="my:CreatorTitle/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:CreatorGiven">
				<xsl:copy-of select="my:CreatorGiven/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:CreatorFamily">
				<xsl:copy-of select="my:CreatorFamily/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:CreatorID">
				<xsl:copy-of select="my:CreatorID/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:CreatorAffiliation">
				<xsl:copy-of select="my:CreatorAffiliation/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:CreatorAffiliationID">
				<xsl:copy-of select="my:CreatorAffiliationID/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:CreatorPI">
				<xsl:choose>
					<xsl:when test="my:CreatorPI/text()[1]">
						<xsl:copy-of select="my:CreatorPI/text()[1]"/>
					</xsl:when>
					<xsl:otherwise>false</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
			<xsl:element name="my:CreatorCI">
				<xsl:choose>
					<xsl:when test="my:CreatorCI/text()[1]">
						<xsl:copy-of select="my:CreatorCI/text()[1]"/>
					</xsl:when>
					<xsl:otherwise>false</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Creators" mode="_1">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:Creator">
					<xsl:apply-templates select="my:Creator" mode="_2"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Creator"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_2"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:PrimaryContact" mode="_3">
		<xsl:copy>
			<xsl:element name="my:PrimaryContactFirstName">
				<xsl:copy-of select="my:PrimaryContactFirstName/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:PrimaryContactFamilyName">
				<xsl:copy-of select="my:PrimaryContactFamilyName/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:PrimaryContactEmail">
				<xsl:copy-of select="my:PrimaryContactEmail/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:PrimaryContactTitle">
				<xsl:copy-of select="my:PrimaryContactTitle/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:PrimaryContactID">
				<xsl:copy-of select="my:PrimaryContactID/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Supervisor" mode="_5">
		<xsl:copy>
			<xsl:element name="my:SupervisorTitle">
				<xsl:copy-of select="my:SupervisorTitle/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:SupervisorFirstName">
				<xsl:copy-of select="my:SupervisorFirstName/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:SupervisorFamilyName">
				<xsl:copy-of select="my:SupervisorFamilyName/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:SupervisorID">
				<xsl:copy-of select="my:SupervisorID/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Supervisors" mode="_4">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:Supervisor">
					<xsl:apply-templates select="my:Supervisor" mode="_5"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Supervisor"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_5"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Collaborator" mode="_7">
		<xsl:copy>
			<xsl:element name="my:CollaboratorName">
				<xsl:copy-of select="my:CollaboratorName/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Collaborators" mode="_6">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:Collaborator">
					<xsl:apply-templates select="my:Collaborator" mode="_7"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Collaborator"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_7"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:relatedPublication" mode="_9">
		<xsl:copy>
			<xsl:element name="my:RelatedPublicationURL">
				<xsl:copy-of select="my:RelatedPublicationURL/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RelatedPublicationTitle">
				<xsl:copy-of select="my:RelatedPublicationTitle/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RelatedPublicationNotes">
				<xsl:copy-of select="my:RelatedPublicationNotes/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:RelatedPublications" mode="_8">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:relatedPublication">
					<xsl:apply-templates select="my:relatedPublication" mode="_9"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:relatedPublication"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_9"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:RelatedWebsite" mode="_11">
		<xsl:copy>
			<xsl:element name="my:RelatedWebsiteURL">
				<xsl:copy-of select="my:RelatedWebsiteURL/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RelatedWebsiteTitle">
				<xsl:copy-of select="my:RelatedWebsiteTitle/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RelatedWebsiteNotes">
				<xsl:copy-of select="my:RelatedWebsiteNotes/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:RelatedWebsites" mode="_10">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:RelatedWebsite">
					<xsl:apply-templates select="my:RelatedWebsite" mode="_11"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:RelatedWebsite"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_11"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:RelatedDataItem" mode="_13">
		<xsl:copy>
			<xsl:element name="my:RelatedDataItemRelationship">
				<xsl:copy-of select="my:RelatedDataItemRelationship/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RelatedDataItemURL">
				<xsl:copy-of select="my:RelatedDataItemURL/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RelatedDataItemTitle">
				<xsl:copy-of select="my:RelatedDataItemTitle/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RelatedDataItemNotes">
				<xsl:copy-of select="my:RelatedDataItemNotes/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:RelatedData" mode="_12">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:RelatedDataItem">
					<xsl:apply-templates select="my:RelatedDataItem" mode="_13"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:RelatedDataItem"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_13"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:GeospatialLocation" mode="_16">
		<xsl:copy>
			<xsl:element name="my:GeospatialLocationType">
				<xsl:copy-of select="my:GeospatialLocationType/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:GeospatialLocationValue">
				<xsl:copy-of select="my:GeospatialLocationValue/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:GeospatialLocations" mode="_15">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:GeospatialLocation">
					<xsl:apply-templates select="my:GeospatialLocation" mode="_16"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:GeospatialLocation"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_16"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Coverage" mode="_14">
		<xsl:copy>
			<xsl:element name="my:DateFrom">
				<xsl:choose>
					<xsl:when test="my:DateFrom/text()[1]">
						<xsl:copy-of select="my:DateFrom/text()[1]"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:attribute name="xsi:nil">true</xsl:attribute>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
			<xsl:element name="my:DateTo">
				<xsl:choose>
					<xsl:when test="my:DateTo/text()[1]">
						<xsl:copy-of select="my:DateTo/text()[1]"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:attribute name="xsi:nil">true</xsl:attribute>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
			<xsl:element name="my:TimePeriod">
				<xsl:copy-of select="my:TimePeriod/text()[1]"/>
			</xsl:element>
			<xsl:choose>
				<xsl:when test="my:GeospatialLocations">
					<xsl:apply-templates select="my:GeospatialLocations[1]" mode="_15"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:GeospatialLocations"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_15"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:FORCode" mode="_18">
		<xsl:copy>
			<xsl:element name="my:FORCodeValue">
				<xsl:copy-of select="my:FORCodeValue/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:FORCodes" mode="_17">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:FORCode">
					<xsl:apply-templates select="my:FORCode" mode="_18"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:FORCode"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_18"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:SEOCode" mode="_20">
		<xsl:copy>
			<xsl:element name="my:SEOCodeValue">
				<xsl:copy-of select="my:SEOCodeValue/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:SEOCodes" mode="_19">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:SEOCode">
					<xsl:apply-templates select="my:SEOCode" mode="_20"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:SEOCode"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_20"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Keyword" mode="_22">
		<xsl:copy>
			<xsl:element name="my:KeywordValue">
				<xsl:copy-of select="my:KeywordValue/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Keywords" mode="_21">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:Keyword">
					<xsl:apply-templates select="my:Keyword" mode="_22"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Keyword"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_22"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Rights" mode="_23">
		<xsl:copy>
			<xsl:element name="my:RightsAccess">
				<xsl:copy-of select="my:RightsAccess/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RightsStatement">
				<xsl:copy-of select="my:RightsStatement/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RightsCCLicence">
				<xsl:copy-of select="my:RightsCCLicence/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RightsOtherName">
				<xsl:copy-of select="my:RightsOtherName/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:RightsOtherURL">
				<xsl:copy-of select="my:RightsOtherURL/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Identifier" mode="_24">
		<xsl:copy>
			<xsl:element name="my:IdentifierType">
				<xsl:copy-of select="my:IdentifierType/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:IdentifierValue">
				<xsl:copy-of select="my:IdentifierValue/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:IdentifierUseMetadataID">
				<xsl:choose>
					<xsl:when test="my:IdentifierUseMetadataID/text()[1]">
						<xsl:copy-of select="my:IdentifierUseMetadataID/text()[1]"/>
					</xsl:when>
					<xsl:otherwise>false</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:LocationURL" mode="_27">
		<xsl:copy>
			<xsl:element name="my:LocationURLValue">
				<xsl:copy-of select="my:LocationURLValue/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:LocationURLs" mode="_26">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:LocationURL">
					<xsl:apply-templates select="my:LocationURL" mode="_27"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:LocationURL"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_27"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:Location" mode="_25">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:LocationURLs">
					<xsl:apply-templates select="my:LocationURLs[1]" mode="_26"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:LocationURLs"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_26"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:element name="my:LocationStoredAt">
				<xsl:copy-of select="my:LocationStoredAt/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:LocationNotes">
				<xsl:copy-of select="my:LocationNotes/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:DataOwner" mode="_29">
		<xsl:copy>
			<xsl:element name="my:DataOwnerName">
				<xsl:copy-of select="my:DataOwnerName/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:DataOwners" mode="_28">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:DataOwner">
					<xsl:apply-templates select="my:DataOwner" mode="_29"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:DataOwner"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_29"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:FundingBody" mode="_31">
		<xsl:copy>
			<xsl:element name="my:FundingBodyName">
				<xsl:copy-of select="my:FundingBodyName/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:FundingBodies" mode="_30">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:FundingBody">
					<xsl:apply-templates select="my:FundingBody" mode="_31"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:FundingBody"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_31"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:GrantNumber" mode="_33">
		<xsl:copy>
			<xsl:element name="my:GrantNumberInternal">
				<xsl:choose>
					<xsl:when test="my:GrantNumberInternal/text()[1]">
						<xsl:copy-of select="my:GrantNumberInternal/text()[1]"/>
					</xsl:when>
					<xsl:otherwise>false</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
			<xsl:element name="my:GrantNumberID">
				<xsl:copy-of select="my:GrantNumberID/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:GrantNumberDescription">
				<xsl:copy-of select="my:GrantNumberDescription/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:GrantNumbers" mode="_32">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="my:GrantNumber">
					<xsl:apply-templates select="my:GrantNumber" mode="_33"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:GrantNumber"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_33"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:DataManagementPlan" mode="_34">
		<xsl:copy>
			<xsl:element name="my:DataManagementPlanExists">
				<xsl:choose>
					<xsl:when test="my:DataManagementPlanExists/text()[1]">
						<xsl:copy-of select="my:DataManagementPlanExists/text()[1]"/>
					</xsl:when>
					<xsl:otherwise>false</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
			<xsl:element name="my:DataManagementPlanNotes">
				<xsl:copy-of select="my:DataManagementPlanNotes/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:SubmissionDetails" mode="_35">
		<xsl:copy>
			<xsl:element name="my:WorkflowSource">
				<xsl:copy-of select="my:WorkflowSource/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:ContactPersonName">
				<xsl:copy-of select="my:ContactPersonName/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:ContactPersonEmail">
				<xsl:copy-of select="my:ContactPersonEmail/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:ContactPersonPhone">
				<xsl:copy-of select="my:ContactPersonPhone/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
	<xsl:template match="my:RedboxCollection" mode="_0">
		<xsl:copy>
			<xsl:element name="my:Title">
				<xsl:copy-of select="my:Title/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:Type">
				<xsl:copy-of select="my:Type/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:DateCreated">
				<xsl:copy-of select="my:DateCreated/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:DateModified">
				<xsl:choose>
					<xsl:when test="my:DateModified/text()[1]">
						<xsl:copy-of select="my:DateModified/text()[1]"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:attribute name="xsi:nil">true</xsl:attribute>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
			<xsl:element name="my:Description">
				<xsl:copy-of select="my:Description/text()[1]"/>
			</xsl:element>
			<xsl:choose>
				<xsl:when test="my:Creators">
					<xsl:apply-templates select="my:Creators[1]" mode="_1"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Creators"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_1"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:PrimaryContact">
					<xsl:apply-templates select="my:PrimaryContact[1]" mode="_3"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:PrimaryContact"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_3"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:Supervisors">
					<xsl:apply-templates select="my:Supervisors[1]" mode="_4"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Supervisors"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_4"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:Collaborators">
					<xsl:apply-templates select="my:Collaborators[1]" mode="_6"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Collaborators"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_6"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:RelatedPublications">
					<xsl:apply-templates select="my:RelatedPublications[1]" mode="_8"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:RelatedPublications"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_8"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:RelatedWebsites">
					<xsl:apply-templates select="my:RelatedWebsites[1]" mode="_10"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:RelatedWebsites"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_10"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:RelatedData">
					<xsl:apply-templates select="my:RelatedData[1]" mode="_12"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:RelatedData"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_12"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:Coverage">
					<xsl:apply-templates select="my:Coverage[1]" mode="_14"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Coverage"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_14"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:FORCodes">
					<xsl:apply-templates select="my:FORCodes[1]" mode="_17"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:FORCodes"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_17"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:SEOCodes">
					<xsl:apply-templates select="my:SEOCodes[1]" mode="_19"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:SEOCodes"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_19"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:Keywords">
					<xsl:apply-templates select="my:Keywords[1]" mode="_21"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Keywords"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_21"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:element name="my:TypeOfActivity">
				<xsl:copy-of select="my:TypeOfActivity/text()[1]"/>
			</xsl:element>
			<xsl:choose>
				<xsl:when test="my:Rights">
					<xsl:apply-templates select="my:Rights[1]" mode="_23"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Rights"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_23"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:Identifier">
					<xsl:apply-templates select="my:Identifier[1]" mode="_24"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Identifier"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_24"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:Location">
					<xsl:apply-templates select="my:Location[1]" mode="_25"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:Location"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_25"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:element name="my:RetentionPeriod">
				<xsl:copy-of select="my:RetentionPeriod/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:Extent">
				<xsl:copy-of select="my:Extent/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:DisposalDate">
				<xsl:choose>
					<xsl:when test="my:DisposalDate/text()[1]">
						<xsl:copy-of select="my:DisposalDate/text()[1]"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:attribute name="xsi:nil">true</xsl:attribute>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
			<xsl:choose>
				<xsl:when test="my:DataOwners">
					<xsl:apply-templates select="my:DataOwners[1]" mode="_28"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:DataOwners"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_28"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:element name="my:DataCustodian">
				<xsl:copy-of select="my:DataCustodian/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:DataAffiliation">
				<xsl:copy-of select="my:DataAffiliation/text()[1]"/>
			</xsl:element>
			<xsl:choose>
				<xsl:when test="my:FundingBodies">
					<xsl:apply-templates select="my:FundingBodies[1]" mode="_30"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:FundingBodies"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_30"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:GrantNumbers">
					<xsl:apply-templates select="my:GrantNumbers[1]" mode="_32"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:GrantNumbers"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_32"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:element name="my:ProjectTitle">
				<xsl:copy-of select="my:ProjectTitle/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:Depositor">
				<xsl:copy-of select="my:Depositor/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:DataSize">
				<xsl:copy-of select="my:DataSize/text()[1]"/>
			</xsl:element>
			<xsl:element name="my:DataManagementPolicy">
				<xsl:copy-of select="my:DataManagementPolicy/text()[1]"/>
			</xsl:element>
			<xsl:choose>
				<xsl:when test="my:DataManagementPlan">
					<xsl:apply-templates select="my:DataManagementPlan[1]" mode="_34"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:DataManagementPlan"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_34"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:choose>
				<xsl:when test="my:SubmissionDetails">
					<xsl:apply-templates select="my:SubmissionDetails[1]" mode="_35"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:variable name="var">
						<xsl:element name="my:SubmissionDetails"/>
					</xsl:variable>
					<xsl:apply-templates select="msxsl:node-set($var)/*" mode="_35"/>
				</xsl:otherwise>
			</xsl:choose>
			<xsl:element name="my:Language">
				<xsl:copy-of select="my:Language/text()[1]"/>
			</xsl:element>
		</xsl:copy>
	</xsl:template>
</xsl:stylesheet>