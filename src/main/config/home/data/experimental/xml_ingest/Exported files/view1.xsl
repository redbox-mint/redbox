<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:my="http://schemas.microsoft.com/office/infopath/2003/myXSD/2011-09-26T07:17:47" xmlns:xd="http://schemas.microsoft.com/office/infopath/2003" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:msxsl="urn:schemas-microsoft-com:xslt" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns:xdExtension="http://schemas.microsoft.com/office/infopath/2003/xslt/extension" xmlns:xdXDocument="http://schemas.microsoft.com/office/infopath/2003/xslt/xDocument" xmlns:xdSolution="http://schemas.microsoft.com/office/infopath/2003/xslt/solution" xmlns:xdFormatting="http://schemas.microsoft.com/office/infopath/2003/xslt/formatting" xmlns:xdImage="http://schemas.microsoft.com/office/infopath/2003/xslt/xImage" xmlns:xdUtil="http://schemas.microsoft.com/office/infopath/2003/xslt/Util" xmlns:xdMath="http://schemas.microsoft.com/office/infopath/2003/xslt/Math" xmlns:xdDate="http://schemas.microsoft.com/office/infopath/2003/xslt/Date" xmlns:sig="http://www.w3.org/2000/09/xmldsig#" xmlns:xdSignatureProperties="http://schemas.microsoft.com/office/infopath/2003/SignatureProperties" xmlns:ipApp="http://schemas.microsoft.com/office/infopath/2006/XPathExtension/ipApp" xmlns:xdEnvironment="http://schemas.microsoft.com/office/infopath/2006/xslt/environment" xmlns:xdUser="http://schemas.microsoft.com/office/infopath/2006/xslt/User" xmlns:xdServerInfo="http://schemas.microsoft.com/office/infopath/2009/xslt/ServerInfo">
	<xsl:output method="html" indent="no"/>
	<xsl:template match="my:RedboxCollection">
		<html>
			<head>
				<meta content="text/html" http-equiv="Content-Type"></meta>
				<style controlStyle="controlStyle">@media screen 			{ 			BODY{margin-left:21px;background-position:21px 0px;} 			} 		BODY{color:windowtext;background-color:window;layout-grid:none;} 		.xdListItem {display:inline-block;width:100%;vertical-align:text-top;} 		.xdListBox,.xdComboBox{margin:1px;} 		.xdInlinePicture{margin:1px; BEHAVIOR: url(#default#urn::xdPicture) } 		.xdLinkedPicture{margin:1px; BEHAVIOR: url(#default#urn::xdPicture) url(#default#urn::controls/Binder) } 		.xdHyperlinkBox{word-wrap:break-word; text-overflow:ellipsis;overflow-x:hidden; OVERFLOW-Y: hidden; WHITE-SPACE:nowrap; display:inline-block;margin:1px;padding:5px;border: 1pt solid #dcdcdc;color:windowtext;BEHAVIOR: url(#default#urn::controls/Binder) url(#default#DataBindingUI)} 		.xdSection{border:1pt solid transparent ;margin:0px 0px 0px 0px;padding:0px 0px 0px 0px;} 		.xdRepeatingSection{border:1pt solid transparent;margin:0px 0px 0px 0px;padding:0px 0px 0px 0px;} 		.xdMultiSelectList{margin:1px;display:inline-block; border:1pt solid #dcdcdc; padding:1px 1px 1px 5px; text-indent:0; color:windowtext; background-color:window; overflow:auto; behavior: url(#default#DataBindingUI) url(#default#urn::controls/Binder) url(#default#MultiSelectHelper) url(#default#ScrollableRegion);} 		.xdMultiSelectListItem{display:block;white-space:nowrap}		.xdMultiSelectFillIn{display:inline-block;white-space:nowrap;text-overflow:ellipsis;;padding:1px;margin:1px;border: 1pt solid #dcdcdc;overflow:hidden;text-align:left;}		.xdBehavior_Formatting {BEHAVIOR: url(#default#urn::controls/Binder) url(#default#Formatting);} 	 .xdBehavior_FormattingNoBUI{BEHAVIOR: url(#default#CalPopup) url(#default#urn::controls/Binder) url(#default#Formatting);} 	.xdExpressionBox{margin: 1px;padding:1px;word-wrap: break-word;text-overflow: ellipsis;overflow-x:hidden;}.xdBehavior_GhostedText,.xdBehavior_GhostedTextNoBUI{BEHAVIOR: url(#default#urn::controls/Binder) url(#default#TextField) url(#default#GhostedText);}	.xdBehavior_GTFormatting{BEHAVIOR: url(#default#urn::controls/Binder) url(#default#Formatting) url(#default#GhostedText);}	.xdBehavior_GTFormattingNoBUI{BEHAVIOR: url(#default#CalPopup) url(#default#urn::controls/Binder) url(#default#Formatting) url(#default#GhostedText);}	.xdBehavior_Boolean{BEHAVIOR: url(#default#urn::controls/Binder) url(#default#BooleanHelper);}	.xdBehavior_Select{BEHAVIOR: url(#default#urn::controls/Binder) url(#default#SelectHelper);}	.xdBehavior_ComboBox{BEHAVIOR: url(#default#ComboBox)} 	.xdBehavior_ComboBoxTextField{BEHAVIOR: url(#default#ComboBoxTextField);} 	.xdRepeatingTable{BORDER-TOP-STYLE: none; BORDER-RIGHT-STYLE: none; BORDER-LEFT-STYLE: none; BORDER-BOTTOM-STYLE: none; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word;}.xdScrollableRegion{BEHAVIOR: url(#default#ScrollableRegion);} 		.xdLayoutRegion{display:inline-block;} 		.xdMaster{BEHAVIOR: url(#default#MasterHelper);} 		.xdActiveX{margin:1px; BEHAVIOR: url(#default#ActiveX);} 		.xdFileAttachment{display:inline-block;margin:1px;BEHAVIOR:url(#default#urn::xdFileAttachment);} 		.xdSharePointFileAttachment{display:inline-block;margin:2px;BEHAVIOR:url(#default#xdSharePointFileAttachment);} 		.xdAttachItem{display:inline-block;width:100%%;height:25px;margin:1px;BEHAVIOR:url(#default#xdSharePointFileAttachItem);} 		.xdSignatureLine{display:inline-block;margin:1px;background-color:transparent;border:1pt solid transparent;BEHAVIOR:url(#default#SignatureLine);} 		.xdHyperlinkBoxClickable{behavior: url(#default#HyperlinkBox)} 		.xdHyperlinkBoxButtonClickable{border-width:1px;border-style:outset;behavior: url(#default#HyperlinkBoxButton)} 		.xdPictureButton{background-color: transparent; padding: 0px; behavior: url(#default#PictureButton);} 		.xdPageBreak{display: none;}BODY{margin-right:21px;} 		.xdTextBoxRTL{display:inline-block;white-space:nowrap;text-overflow:ellipsis;;padding:1px;margin:1px;border: 1pt solid #dcdcdc;color:windowtext;background-color:window;overflow:hidden;text-align:right;word-wrap:normal;} 		.xdRichTextBoxRTL{display:inline-block;;padding:1px;margin:1px;border: 1pt solid #dcdcdc;color:windowtext;background-color:window;overflow-x:hidden;word-wrap:break-word;text-overflow:ellipsis;text-align:right;font-weight:normal;font-style:normal;text-decoration:none;vertical-align:baseline;} 		.xdDTTextRTL{height:100%;width:100%;margin-left:22px;overflow:hidden;padding:0px;white-space:nowrap;} 		.xdDTButtonRTL{margin-right:-21px;height:17px;width:20px;behavior: url(#default#DTPicker);} 		.xdMultiSelectFillinRTL{display:inline-block;white-space:nowrap;text-overflow:ellipsis;;padding:1px;margin:1px;border: 1pt solid #dcdcdc;overflow:hidden;text-align:right;}.xdTextBox{display:inline-block;white-space:nowrap;text-overflow:ellipsis;;padding:1px;margin:1px;border: 1pt solid #dcdcdc;color:windowtext;background-color:window;overflow:hidden;text-align:left;word-wrap:normal;} 		.xdRichTextBox{display:inline-block;;padding:1px;margin:1px;border: 1pt solid #dcdcdc;color:windowtext;background-color:window;overflow-x:hidden;word-wrap:break-word;text-overflow:ellipsis;text-align:left;font-weight:normal;font-style:normal;text-decoration:none;vertical-align:baseline;} 		.xdDTPicker{;display:inline;margin:1px;margin-bottom: 2px;border: 1pt solid #dcdcdc;color:windowtext;background-color:window;overflow:hidden;text-indent:0; layout-grid: none} 		.xdDTText{height:100%;width:100%;margin-right:22px;overflow:hidden;padding:0px;white-space:nowrap;} 		.xdDTButton{margin-left:-21px;height:17px;width:20px;behavior: url(#default#DTPicker);} 		.xdRepeatingTable TD {VERTICAL-ALIGN: top;}</style>
				<style tableEditor="TableStyleRulesID">TABLE.xdLayout TD {
	BORDER-BOTTOM: medium none; BORDER-LEFT: medium none; BORDER-TOP: medium none; BORDER-RIGHT: medium none
}
TABLE.msoUcTable TD {
	BORDER-BOTTOM: 1pt solid; BORDER-LEFT: 1pt solid; BORDER-TOP: 1pt solid; BORDER-RIGHT: 1pt solid
}
TABLE {
	BEHAVIOR: url (#default#urn::tables/NDTable)
}
</style>
				<style languageStyle="languageStyle">BODY {
	FONT-FAMILY: Calibri; FONT-SIZE: 10pt
}
SELECT {
	FONT-FAMILY: Calibri; FONT-SIZE: 10pt
}
TABLE {
	TEXT-TRANSFORM: none; FONT-STYLE: normal; FONT-FAMILY: Calibri; COLOR: black; FONT-SIZE: 10pt; FONT-WEIGHT: normal
}
.optionalPlaceholder {
	FONT-STYLE: normal; PADDING-LEFT: 20px; FONT-FAMILY: Calibri; COLOR: #333333; FONT-SIZE: 9pt; FONT-WEIGHT: normal; TEXT-DECORATION: none; BEHAVIOR: url(#default#xOptional)
}
.langFont {
	WIDTH: 150px; FONT-FAMILY: Calibri; FONT-SIZE: 10pt
}
.defaultInDocUI {
	FONT-FAMILY: Calibri; FONT-SIZE: 9pt
}
.optionalPlaceholder {
	PADDING-RIGHT: 20px
}
</style>
				<style themeStyle="urn:office.microsoft.com:themeMunicipal">TABLE {
	BORDER-BOTTOM: medium none; BORDER-LEFT: medium none; BORDER-COLLAPSE: collapse; BORDER-TOP: medium none; BORDER-RIGHT: medium none
}
TD {
	BORDER-BOTTOM-COLOR: #d8d8d8; BORDER-TOP-COLOR: #d8d8d8; BORDER-RIGHT-COLOR: #d8d8d8; BORDER-LEFT-COLOR: #d8d8d8
}
TH {
	BORDER-BOTTOM-COLOR: #000000; BACKGROUND-COLOR: #f2f2f2; BORDER-TOP-COLOR: #000000; COLOR: black; BORDER-RIGHT-COLOR: #000000; BORDER-LEFT-COLOR: #000000
}
.xdTableHeader {
	BACKGROUND-COLOR: #f2f2f2; COLOR: black
}
.light1 {
	BACKGROUND-COLOR: #ffffff
}
.dark1 {
	BACKGROUND-COLOR: #000000
}
.light2 {
	BACKGROUND-COLOR: #f0efea
}
.dark2 {
	BACKGROUND-COLOR: #5e5a5a
}
.accent1 {
	BACKGROUND-COLOR: #d34817
}
.accent2 {
	BACKGROUND-COLOR: #9b2d1f
}
.accent3 {
	BACKGROUND-COLOR: #a28e6a
}
.accent4 {
	BACKGROUND-COLOR: #9b694b
}
.accent5 {
	BACKGROUND-COLOR: #918485
}
.accent6 {
	BACKGROUND-COLOR: #855d5d
}
</style>
				<style tableStyle="Playground">TR.xdTitleRow {
	MIN-HEIGHT: 61px
}
TD.xdTitleCell {
	TEXT-ALIGN: right; BORDER-LEFT: #d8d8d8 1.5pt solid; PADDING-BOTTOM: 6px; BACKGROUND-COLOR: #e7dddd; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; BORDER-TOP: #d8d8d8 1.5pt solid; BORDER-RIGHT: #d8d8d8 1.5pt solid; PADDING-TOP: 18px; valign: bottom
}
TR.xdTitleRowWithHeading {
	MIN-HEIGHT: 61px
}
TD.xdTitleCellWithHeading {
	TEXT-ALIGN: right; BORDER-LEFT: #d8d8d8 1.5pt solid; PADDING-BOTTOM: 2px; BACKGROUND-COLOR: #e7dddd; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; BORDER-TOP: #d8d8d8 1.5pt solid; BORDER-RIGHT: #d8d8d8 1.5pt solid; PADDING-TOP: 22px; valign: bottom
}
TR.xdTitleRowWithSubHeading {
	MIN-HEIGHT: 61px
}
TD.xdTitleCellWithSubHeading {
	TEXT-ALIGN: right; BORDER-LEFT: #d8d8d8 1.5pt solid; PADDING-BOTTOM: 6px; BACKGROUND-COLOR: #e7dddd; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; BORDER-TOP: #d8d8d8 1.5pt solid; BORDER-RIGHT: #d8d8d8 1.5pt solid; PADDING-TOP: 22px; valign: bottom
}
TR.xdTitleRowWithOffsetBody {
	MIN-HEIGHT: 61px
}
TD.xdTitleCellWithOffsetBody {
	TEXT-ALIGN: left; BORDER-LEFT: #d8d8d8 1.5pt solid; PADDING-BOTTOM: 6px; BACKGROUND-COLOR: #e7dddd; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; BORDER-TOP: #d8d8d8 1.5pt solid; BORDER-RIGHT: #d8d8d8 1.5pt solid; PADDING-TOP: 18px; valign: bottom
}
TR.xdTitleHeadingRow {
	MIN-HEIGHT: 45px
}
TD.xdTitleHeadingCell {
	TEXT-ALIGN: right; BORDER-LEFT: #d8d8d8 1.5pt solid; PADDING-BOTTOM: 18px; BACKGROUND-COLOR: #e7dddd; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; BORDER-RIGHT: #d8d8d8 1.5pt solid; PADDING-TOP: 0px; valign: top
}
TR.xdTitleSubheadingRow {
	MIN-HEIGHT: 76px
}
TD.xdTitleSubheadingCell {
	BORDER-LEFT: #d8d8d8 1.5pt solid; PADDING-BOTTOM: 14px; BACKGROUND-COLOR: #e7dddd; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; BORDER-RIGHT: #d8d8d8 1.5pt solid; PADDING-TOP: 6px; valign: top
}
TD.xdVerticalFill {
	BORDER-BOTTOM: #d8d8d8 1.5pt solid; BORDER-LEFT: #d8d8d8 1.5pt solid; BACKGROUND-COLOR: #d34817; BORDER-TOP: #d8d8d8 1.5pt solid; BORDER-RIGHT: #3f3f3f 1.5pt solid
}
TD.xdTableContentCellWithVerticalOffset {
	BORDER-BOTTOM: #d8d8d8 1.5pt solid; TEXT-ALIGN: left; BORDER-LEFT: #d8d8d8 1.5pt solid; PADDING-BOTTOM: 6px; BACKGROUND-COLOR: #e7dddd; PADDING-LEFT: 95px; PADDING-RIGHT: 0px; BORDER-RIGHT: #d8d8d8 1.5pt solid; PADDING-TOP: 18px; valign: bottom
}
TR.xdTableContentRow {
	MIN-HEIGHT: 140px
}
TD.xdTableContentCell {
	BORDER-BOTTOM: #d8d8d8 1.5pt solid; BORDER-LEFT: #d8d8d8 1.5pt solid; PADDING-BOTTOM: 0px; BACKGROUND-COLOR: #e7dddd; PADDING-LEFT: 0px; PADDING-RIGHT: 0px; BORDER-RIGHT: #d8d8d8 1.5pt solid; PADDING-TOP: 0px; valign: top
}
TD.xdTableContentCellWithVerticalFill {
	BORDER-BOTTOM: #d8d8d8 1.5pt solid; PADDING-BOTTOM: 0px; BACKGROUND-COLOR: #e7dddd; PADDING-LEFT: 1px; PADDING-RIGHT: 1px; BORDER-RIGHT: #d8d8d8 1.5pt solid; PADDING-TOP: 0px; valign: top
}
TD.xdTableStyleOneCol {
	PADDING-BOTTOM: 4px; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; PADDING-TOP: 4px
}
TR.xdContentRowOneCol {
	MIN-HEIGHT: 45px; valign: center
}
TR.xdHeadingRow {
	MIN-HEIGHT: 37px
}
TD.xdHeadingCell {
	BORDER-BOTTOM: #d34817 1pt solid; PADDING-BOTTOM: 4px; BACKGROUND-COLOR: #ffffff; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; BORDER-TOP: #9e3611 1.5pt dashed; PADDING-TOP: 12px; valign: bottom
}
TR.xdSubheadingRow {
	MIN-HEIGHT: 29px
}
TD.xdSubheadingCell {
	BORDER-BOTTOM: #ee8c69 2.25pt solid; PADDING-BOTTOM: 4px; BACKGROUND-COLOR: #d34817; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; PADDING-TOP: 4px; valign: bottom
}
TR.xdHeadingRowEmphasis {
	MIN-HEIGHT: 37px
}
TD.xdHeadingCellEmphasis {
	BORDER-BOTTOM: #d34817 1pt solid; PADDING-BOTTOM: 4px; BACKGROUND-COLOR: #ffffff; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; BORDER-TOP: #9e3611 1.5pt dashed; PADDING-TOP: 12px; valign: bottom
}
TR.xdSubheadingRowEmphasis {
	MIN-HEIGHT: 29px
}
TD.xdSubheadingCellEmphasis {
	BORDER-BOTTOM: #ee8c69 2.25pt solid; PADDING-BOTTOM: 4px; BACKGROUND-COLOR: #d34817; PADDING-LEFT: 22px; PADDING-RIGHT: 22px; PADDING-TOP: 4px; valign: bottom
}
TR.xdTableLabelControlStackedRow {
	MIN-HEIGHT: 45px
}
TD.xdTableLabelControlStackedCellLabel {
	PADDING-BOTTOM: 4px; PADDING-LEFT: 22px; PADDING-RIGHT: 5px; PADDING-TOP: 4px
}
TD.xdTableLabelControlStackedCellComponent {
	PADDING-BOTTOM: 4px; PADDING-LEFT: 5px; PADDING-RIGHT: 22px; PADDING-TOP: 4px
}
TR.xdTableRow {
	MIN-HEIGHT: 30px
}
TD.xdTableCellLabel {
	PADDING-BOTTOM: 4px; PADDING-LEFT: 22px; PADDING-RIGHT: 5px; PADDING-TOP: 4px
}
TD.xdTableCellComponent {
	PADDING-BOTTOM: 4px; PADDING-LEFT: 5px; PADDING-RIGHT: 22px; PADDING-TOP: 4px
}
TD.xdTableMiddleCell {
	PADDING-BOTTOM: 4px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; PADDING-TOP: 4px
}
TR.xdTableEmphasisRow {
	MIN-HEIGHT: 30px
}
TD.xdTableEmphasisCellLabel {
	BORDER-BOTTOM: #ffffff 1pt solid; PADDING-BOTTOM: 4px; BACKGROUND-COLOR: #b89a9a; PADDING-LEFT: 22px; PADDING-RIGHT: 5px; BORDER-TOP: #ffffff 1pt solid; PADDING-TOP: 4px
}
TD.xdTableEmphasisCellComponent {
	BORDER-BOTTOM: #ffffff 1pt solid; PADDING-BOTTOM: 4px; BACKGROUND-COLOR: #b89a9a; PADDING-LEFT: 5px; PADDING-RIGHT: 22px; BORDER-TOP: #ffffff 1pt solid; PADDING-TOP: 4px
}
TD.xdTableMiddleCellEmphasis {
	BORDER-BOTTOM: #ffffff 1pt solid; PADDING-BOTTOM: 4px; BACKGROUND-COLOR: #b89a9a; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-TOP: #ffffff 1pt solid; PADDING-TOP: 4px
}
TR.xdTableOffsetRow {
	MIN-HEIGHT: 30px
}
TD.xdTableOffsetCellLabel {
	BORDER-BOTTOM: #ffffff 1pt solid; PADDING-BOTTOM: 4px; BACKGROUND-COLOR: #b89a9a; PADDING-LEFT: 22px; PADDING-RIGHT: 5px; BORDER-TOP: #ffffff 1pt solid; PADDING-TOP: 4px
}
TD.xdTableOffsetCellComponent {
	BORDER-BOTTOM: #ffffff 1pt solid; PADDING-BOTTOM: 4px; BACKGROUND-COLOR: #b89a9a; PADDING-LEFT: 5px; PADDING-RIGHT: 22px; BORDER-TOP: #ffffff 1pt solid; PADDING-TOP: 4px
}
P {
	MARGIN-TOP: 0px; COLOR: #3f3f3f; FONT-SIZE: 11pt
}
H1 {
	MARGIN-TOP: 0px; MARGIN-BOTTOM: 0px; COLOR: #3f3f3f; FONT-SIZE: 22pt; FONT-WEIGHT: bold
}
H2 {
	MARGIN-TOP: 0px; MARGIN-BOTTOM: 0px; COLOR: #262626; FONT-SIZE: 16pt; FONT-WEIGHT: normal
}
H3 {
	TEXT-TRANSFORM: uppercase; MARGIN-TOP: 0px; MARGIN-BOTTOM: 0px; COLOR: #ffffff; FONT-SIZE: 12pt; FONT-WEIGHT: bold
}
H4 {
	MARGIN-TOP: 0px; MARGIN-BOTTOM: 0px; COLOR: #3f3f3f; FONT-SIZE: 11pt; FONT-WEIGHT: bold
}
H5 {
	MARGIN-TOP: 0px; MARGIN-BOTTOM: 0px; COLOR: #3f3f3f; FONT-SIZE: 11pt; FONT-WEIGHT: normal
}
H6 {
	MARGIN-TOP: 0px; MARGIN-BOTTOM: 0px; COLOR: #3f3f3f; FONT-SIZE: 11pt; FONT-WEIGHT: normal
}
BODY {
	COLOR: black
}
</style>
			</head>
			<body>
				<div align="center">
					<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 629px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout">
						<colgroup>
							<col style="WIDTH: 629px"></col>
						</colgroup>
						<tbody>
							<tr class="xdTitleRow">
								<td vAlign="bottom" class="xdTitleCell">
									<h1>ReDBox Collection Description</h1>
								</td>
							</tr>
							<tr class="xdTableContentRow">
								<td vAlign="top" class="xdTableContentCell">
									<div>
										<div>
											<div> </div>
										</div>
										<div>
											<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 624px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol">
												<colgroup>
													<col style="WIDTH: 192px"></col>
													<col style="WIDTH: 432px"></col>
												</colgroup>
												<tbody vAlign="top">
													<tr class="xdHeadingRow">
														<td colSpan="2" class="xdHeadingCell">
															<h2>Submission details</h2>
														</td>
													</tr>
													<tr class="xdTableRow">
														<td vAlign="top" class="xdTableCellLabel">
															<h4>Data Source</h4>
														</td>
														<td vAlign="top" class="xdTableCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:SubmissionDetails/my:WorkflowSource" xd:CtrlId="CTRL120" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:SubmissionDetails/my:WorkflowSource"/>
															</span>
														</td>
													</tr>
													<tr class="xdTableRow">
														<td vAlign="top" class="xdTableCellLabel">
															<h4>Contact person</h4>
														</td>
														<td vAlign="top" class="xdTableCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:SubmissionDetails/my:ContactPersonName" xd:CtrlId="CTRL121" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:SubmissionDetails/my:ContactPersonName"/>
															</span>
														</td>
													</tr>
													<tr class="xdTableRow">
														<td vAlign="top" class="xdTableCellLabel">
															<h4>Contact person - email</h4>
														</td>
														<td vAlign="top" class="xdTableCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:SubmissionDetails/my:ContactPersonEmail" xd:CtrlId="CTRL122" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:SubmissionDetails/my:ContactPersonEmail"/>
															</span>
														</td>
													</tr>
													<tr class="xdTableRow">
														<td vAlign="top" class="xdTableCellLabel">
															<h4>Contact person - phone</h4>
														</td>
														<td vAlign="top" class="xdTableCellComponent">
															<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:SubmissionDetails/my:ContactPersonPhone" xd:CtrlId="CTRL123" xd:xctname="PlainText" style="WIDTH: 100%">
																	<xsl:value-of select="my:SubmissionDetails/my:ContactPersonPhone"/>
																</span>
															</div>
														</td>
													</tr>
												</tbody>
											</table>
										</div>
										<div> </div>
										<div>
											<hr/>
										</div>
										<div> </div>
									</div>
									<div>
										<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 625px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol">
											<colgroup>
												<col style="WIDTH: 125px"></col>
												<col style="WIDTH: 500px"></col>
											</colgroup>
											<tbody vAlign="top">
												<tr class="xdHeadingRowEmphasis">
													<td colSpan="2" class="xdHeadingCellEmphasis">
														<h2>General</h2>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Title (*)</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<span class="xdlabel"></span>
														<font style="BACKGROUND-COLOR: #ffffff"></font><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Title" xd:CtrlId="CTRL2" xd:xctname="PlainText" style="WIDTH: 100%">
															<xsl:value-of select="my:Title"/>
														</span>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Type (*)</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent"><select class="xdComboBox xdBehavior_Select" title="" size="1" tabIndex="0" xd:binding="my:Type" xd:CtrlId="CTRL4" xd:xctname="dropdown" xd:boundProp="value" style="WIDTH: 100%">
															<xsl:attribute name="value">
																<xsl:value-of select="my:Type"/>
															</xsl:attribute>
															<option>
																<xsl:if test="my:Type=&quot;&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Select...</option>
															<option value="catalogueOrIndex">
																<xsl:if test="my:Type=&quot;catalogueOrIndex&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Catalogue or Index</option>
															<option value="collection">
																<xsl:if test="my:Type=&quot;collection&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Collection</option>
															<option value="registry">
																<xsl:if test="my:Type=&quot;registry&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Registry</option>
															<option value="repository">
																<xsl:if test="my:Type=&quot;repository&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Repository</option>
															<option value="dataset">
																<xsl:if test="my:Type=&quot;dataset&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Dataset</option>
														</select>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Date record created (*)</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div style="WIDTH: 100%" class="xdDTPicker" title="" noWrap="1" xd:CtrlId="CTRL5" xd:xctname="DTPicker"><span hideFocus="1" class="xdDTText xdBehavior_FormattingNoBUI" contentEditable="true" tabIndex="0" xd:binding="my:DateCreated" xd:xctname="DTPicker_DTText" xd:boundProp="xd:num" xd:innerCtrl="_DTText" xd:datafmt="&quot;date&quot;,&quot;dateFormat:Short Date;&quot;">
																<xsl:attribute name="xd:num">
																	<xsl:value-of select="my:DateCreated"/>
																</xsl:attribute>
																<xsl:choose>
																	<xsl:when test="function-available('xdFormatting:formatString')">
																		<xsl:value-of select="xdFormatting:formatString(my:DateCreated,&quot;date&quot;,&quot;dateFormat:Short Date;&quot;)"/>
																	</xsl:when>
																	<xsl:otherwise>
																		<xsl:value-of select="my:DateCreated"/>
																	</xsl:otherwise>
																</xsl:choose>
															</span>
															<button class="xdDTButton" xd:xctname="DTPicker_DTButton" xd:innerCtrl="_DTButton" tabIndex="0">
																<img src="res://infopath.exe/calendar.gif"/>
															</button>
														</div>
													</td>
												</tr>
												<tr style="MIN-HEIGHT: 30px" class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Date record modified</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div>
															<div style="WIDTH: 100%" class="xdDTPicker" title="" noWrap="1" xd:CtrlId="CTRL6" xd:xctname="DTPicker"><span hideFocus="1" class="xdDTText xdBehavior_FormattingNoBUI" contentEditable="true" tabIndex="0" xd:binding="my:DateModified" xd:xctname="DTPicker_DTText" xd:boundProp="xd:num" xd:innerCtrl="_DTText" xd:datafmt="&quot;date&quot;,&quot;dateFormat:Short Date;&quot;">
																	<xsl:attribute name="xd:num">
																		<xsl:value-of select="my:DateModified"/>
																	</xsl:attribute>
																	<xsl:choose>
																		<xsl:when test="function-available('xdFormatting:formatString')">
																			<xsl:value-of select="xdFormatting:formatString(my:DateModified,&quot;date&quot;,&quot;dateFormat:Short Date;&quot;)"/>
																		</xsl:when>
																		<xsl:otherwise>
																			<xsl:value-of select="my:DateModified"/>
																		</xsl:otherwise>
																	</xsl:choose>
																</span>
																<button class="xdDTButton" xd:xctname="DTPicker_DTButton" xd:innerCtrl="_DTButton" tabIndex="0">
																	<img src="res://infopath.exe/calendar.gif"/>
																</button>
															</div>
														</div>
													</td>
												</tr>
												<tr style="MIN-HEIGHT: 30px" class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Language</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div>
															<select style="WIDTH: 100%" class="xdComboBox xdBehavior_Select" title="" size="1" xd:binding="my:Language" xd:CtrlId="CTRL124" xd:xctname="dropdown" value="" xd:boundProp="value" tabIndex="0">
																<xsl:attribute name="value">
																	<xsl:value-of select="my:Language"/>
																</xsl:attribute>
																<xsl:choose>
																	<xsl:when test="function-available('xdXDocument:GetDOM')">
																		<option/>
																		<xsl:variable name="val" select="my:Language"/>
																		<xsl:if test="not(xdXDocument:GetDOM(&quot;Languages&quot;)/languages/language[key=$val] or $val='')">
																			<option selected="selected">
																				<xsl:attribute name="value">
																					<xsl:value-of select="$val"/>
																				</xsl:attribute>
																				<xsl:value-of select="$val"/>
																			</option>
																		</xsl:if>
																		<xsl:for-each select="xdXDocument:GetDOM(&quot;Languages&quot;)/languages/language">
																			<option>
																				<xsl:attribute name="value">
																					<xsl:value-of select="key"/>
																				</xsl:attribute>
																				<xsl:if test="$val=key">
																					<xsl:attribute name="selected">selected</xsl:attribute>
																				</xsl:if>
																				<xsl:value-of select="value"/>
																			</option>
																		</xsl:for-each>
																	</xsl:when>
																	<xsl:otherwise>
																		<option>
																			<xsl:value-of select="my:Language"/>
																		</option>
																	</xsl:otherwise>
																</xsl:choose>
															</select>
														</div>
													</td>
												</tr>
												<tr style="MIN-HEIGHT: 30px" class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Description (*)</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Description" xd:CtrlId="CTRL14" xd:xctname="PlainText" xd:datafmt="&quot;string&quot;,&quot;plainMultiline&quot;" style="OVERFLOW-X: auto; OVERFLOW-Y: auto; WIDTH: 100%; WORD-WRAP: break-word; WHITE-SPACE: normal; HEIGHT: 208px">
																<xsl:choose>
																	<xsl:when test="function-available('xdFormatting:formatString')">
																		<xsl:value-of select="xdFormatting:formatString(my:Description,&quot;string&quot;,&quot;plainMultiline&quot;)" disable-output-escaping="yes"/>
																	</xsl:when>
																	<xsl:otherwise>
																		<xsl:value-of select="my:Description" disable-output-escaping="yes"/>
																	</xsl:otherwise>
																</xsl:choose>
															</span>
														</div>
													</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div>
										<font size="2"></font> </div>
									<div>
										<hr/>
									</div>
									<div>
										<div>
											<div> </div>
										</div>
										<div>
											<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 625px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout">
												<colgroup>
													<col style="WIDTH: 625px"></col>
												</colgroup>
												<tbody vAlign="top">
													<tr class="xdHeadingRow">
														<td class="xdHeadingCell">
															<h2>People</h2>
														</td>
													</tr>
													<tr class="xdSubheadingRow">
														<td class="xdSubheadingCell">
															<h3>Creators</h3>
														</td>
													</tr>
													<tr class="xdContentRowOneCol">
														<td class="xdTableStyleOneCol">
															<div>
																<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 579px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdRepeatingTable msoUcTable" title="" border="1" xd:CtrlId="CTRL7" xd:widgetIndex="0">
																	<colgroup>
																		<col style="WIDTH: 34px"></col>
																		<col style="WIDTH: 40px"></col>
																		<col style="WIDTH: 51px"></col>
																		<col style="WIDTH: 132px"></col>
																		<col style="WIDTH: 114px"></col>
																		<col style="WIDTH: 76px"></col>
																		<col style="WIDTH: 76px"></col>
																		<col style="WIDTH: 56px"></col>
																	</colgroup>
																	<tbody class="xdTableHeader">
																		<tr style="MIN-HEIGHT: 40px">
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>CI</strong>
																					</h5>
																				</div>
																			</td>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>PI</strong>
																					</h5>
																				</div>
																			</td>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>Title</strong>
																					</h5>
																				</div>
																			</td>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>Given Name</strong>
																					</h5>
																				</div>
																			</td>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>Family Name</strong>
																					</h5>
																				</div>
																			</td>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>Identifier</strong>
																					</h5>
																				</div>
																			</td>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>Affiliation</strong>
																					</h5>
																				</div>
																			</td>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>Affiliation ID</strong>
																					</h5>
																				</div>
																			</td>
																		</tr>
																	</tbody><tbody xd:xctname="RepeatingTable">
																		<xsl:for-each select="my:Creators/my:Creator">
																			<tr style="MIN-HEIGHT: 25px">
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																					<div align="center"><input class="xdBehavior_Boolean" title="" type="checkbox" tabIndex="0" xd:binding="my:CreatorCI" xd:CtrlId="CTRL52" xd:xctname="CheckBox" xd:boundProp="xd:value" xd:offValue="false" xd:onValue="true">
																							<xsl:attribute name="xd:value">
																								<xsl:value-of select="my:CreatorCI"/>
																							</xsl:attribute>
																							<xsl:if test="my:CreatorCI=&quot;true&quot;">
																								<xsl:attribute name="CHECKED">CHECKED</xsl:attribute>
																							</xsl:if>
																						</input>
																					</div>
																				</td>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																					<div align="center"><input class="xdBehavior_Boolean" title="" type="checkbox" tabIndex="0" xd:binding="my:CreatorPI" xd:CtrlId="CTRL51" xd:xctname="CheckBox" xd:boundProp="xd:value" xd:offValue="false" xd:onValue="true">
																							<xsl:attribute name="xd:value">
																								<xsl:value-of select="my:CreatorPI"/>
																							</xsl:attribute>
																							<xsl:if test="my:CreatorPI=&quot;true&quot;">
																								<xsl:attribute name="CHECKED">CHECKED</xsl:attribute>
																							</xsl:if>
																						</input>
																					</div>
																				</td>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:CreatorTitle" xd:CtrlId="CTRL8" xd:xctname="PlainText" style="WIDTH: 100%">
																						<xsl:value-of select="my:CreatorTitle"/>
																					</span>
																				</td>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:CreatorGiven" xd:CtrlId="CTRL9" xd:xctname="PlainText" style="WIDTH: 100%">
																						<xsl:value-of select="my:CreatorGiven"/>
																					</span>
																				</td>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:CreatorFamily" xd:CtrlId="CTRL10" xd:xctname="PlainText" style="WIDTH: 100%">
																						<xsl:value-of select="my:CreatorFamily"/>
																					</span>
																				</td>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:CreatorID" xd:CtrlId="CTRL11" xd:xctname="PlainText" style="WIDTH: 100%">
																						<xsl:value-of select="my:CreatorID"/>
																					</span>
																				</td>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:CreatorAffiliation" xd:CtrlId="CTRL12" xd:xctname="PlainText" style="WIDTH: 100%">
																						<xsl:value-of select="my:CreatorAffiliation"/>
																					</span>
																				</td>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																					<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:CreatorAffiliationID" xd:CtrlId="CTRL13" xd:xctname="PlainText" style="WIDTH: 100%">
																							<xsl:value-of select="my:CreatorAffiliationID"/>
																						</span>
																					</div>
																				</td>
																			</tr>
																		</xsl:for-each>
																	</tbody>
																</table>
																<div class="optionalPlaceholder" xd:xmlToEdit="Creator_8" tabIndex="0" xd:action="xCollection::insert" style="WIDTH: 579px">Insert item</div>
															</div>
														</td>
													</tr>
													<tr class="xdSubheadingRow">
														<td class="xdSubheadingCell">
															<h3>PRIMARY CONTACT</h3>
														</td>
													</tr>
													<tr class="xdContentRowOneCol">
														<td class="xdTableStyleOneCol">
															<div><xsl:apply-templates select="my:PrimaryContact" mode="_1"/>
															</div>
														</td>
													</tr>
													<tr class="xdSubheadingRow">
														<td class="xdSubheadingCell">
															<h3>Supervisors</h3>
														</td>
													</tr>
													<tr class="xdContentRowOneCol">
														<td class="xdTableStyleOneCol">
															<div>
																<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 580px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdRepeatingTable msoUcTable" title="" border="1" xd:CtrlId="CTRL63" xd:widgetIndex="0">
																	<colgroup>
																		<col style="WIDTH: 145px"></col>
																		<col style="WIDTH: 145px"></col>
																		<col style="WIDTH: 145px"></col>
																		<col style="WIDTH: 145px"></col>
																	</colgroup>
																	<tbody class="xdTableHeader">
																		<tr>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>Title</strong>
																					</h5>
																				</div>
																			</td>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>First name</strong>
																					</h5>
																				</div>
																			</td>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>Family name</strong>
																					</h5>
																				</div>
																			</td>
																			<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																				<div>
																					<h5 style="FONT-WEIGHT: normal">
																						<strong>ID</strong>
																					</h5>
																				</div>
																			</td>
																		</tr>
																	</tbody><tbody xd:xctname="RepeatingTable">
																		<xsl:for-each select="my:Supervisors/my:Supervisor">
																			<tr>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:SupervisorTitle" xd:CtrlId="CTRL64" xd:xctname="PlainText" style="WIDTH: 100%">
																						<xsl:value-of select="my:SupervisorTitle"/>
																					</span>
																				</td>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:SupervisorFirstName" xd:CtrlId="CTRL65" xd:xctname="PlainText" style="WIDTH: 100%">
																						<xsl:value-of select="my:SupervisorFirstName"/>
																					</span>
																				</td>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:SupervisorFamilyName" xd:CtrlId="CTRL66" xd:xctname="PlainText" style="WIDTH: 100%">
																						<xsl:value-of select="my:SupervisorFamilyName"/>
																					</span>
																				</td>
																				<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:SupervisorID" xd:CtrlId="CTRL67" xd:xctname="PlainText" style="WIDTH: 100%">
																						<xsl:value-of select="my:SupervisorID"/>
																					</span>
																				</td>
																			</tr>
																		</xsl:for-each>
																	</tbody>
																</table>
																<div class="optionalPlaceholder" xd:xmlToEdit="group23_73" tabIndex="0" xd:action="xCollection::insert" style="WIDTH: 580px">Insert item</div>
															</div>
														</td>
													</tr>
													<tr class="xdSubheadingRow">
														<td class="xdSubheadingCell">
															<h3>collaborators</h3>
														</td>
													</tr>
													<tr class="xdContentRowOneCol">
														<td class="xdTableStyleOneCol">
															<div><xsl:apply-templates select="my:Collaborators/my:Collaborator" mode="_2"/>
																<div class="optionalPlaceholder" xd:xmlToEdit="group21_71" tabIndex="0" xd:action="xCollection::insert" align="left" style="WIDTH: 100%">Insert item</div>
															</div>
														</td>
													</tr>
												</tbody>
											</table>
										</div>
										<div> </div>
									</div>
									<div>
										<div>
											<hr/>
										</div>
										<div> </div>
									</div>
									<div>
										<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 625px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout">
											<colgroup>
												<col style="WIDTH: 625px"></col>
											</colgroup>
											<tbody vAlign="top">
												<tr class="xdHeadingRow">
													<td class="xdHeadingCell">
														<h2>Related Items</h2>
													</td>
												</tr>
												<tr class="xdContentRowOneCol">
													<td class="xdTableStyleOneCol">
														<div>Related Publications</div>
														<div>
															<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 582px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdRepeatingTable msoUcTable" title="" border="1" xd:CtrlId="CTRL15" xd:widgetIndex="0">
																<colgroup>
																	<col style="WIDTH: 194px"></col>
																	<col style="WIDTH: 194px"></col>
																	<col style="WIDTH: 194px"></col>
																</colgroup>
																<tbody class="xdTableHeader">
																	<tr>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>URL</strong>
																				</h5>
																			</div>
																		</td>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Title</strong>
																				</h5>
																			</div>
																		</td>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Notes</strong>
																				</h5>
																			</div>
																		</td>
																	</tr>
																</tbody><tbody xd:xctname="RepeatingTable">
																	<xsl:for-each select="my:RelatedPublications/my:relatedPublication">
																		<tr>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:RelatedPublicationURL" xd:CtrlId="CTRL16" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:RelatedPublicationURL"/>
																				</span>
																			</td>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:RelatedPublicationTitle" xd:CtrlId="CTRL17" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:RelatedPublicationTitle"/>
																				</span>
																			</td>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:RelatedPublicationNotes" xd:CtrlId="CTRL18" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:RelatedPublicationNotes"/>
																				</span>
																			</td>
																		</tr>
																	</xsl:for-each>
																</tbody>
															</table>
															<div class="optionalPlaceholder" xd:xmlToEdit="relatedPublication_16" tabIndex="0" xd:action="xCollection::insert" style="WIDTH: 582px">Insert item</div>
														</div>
													</td>
												</tr>
												<tr class="xdContentRowOneCol">
													<td class="xdTableStyleOneCol">
														<div>Related Websites</div>
														<div>
															<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 582px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdRepeatingTable msoUcTable" title="" border="1" xd:CtrlId="CTRL27" xd:widgetIndex="0">
																<colgroup>
																	<col style="WIDTH: 194px"></col>
																	<col style="WIDTH: 194px"></col>
																	<col style="WIDTH: 194px"></col>
																</colgroup>
																<tbody class="xdTableHeader">
																	<tr>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>URL</strong>
																				</h5>
																			</div>
																		</td>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Title</strong>
																				</h5>
																			</div>
																		</td>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Notes</strong>
																				</h5>
																			</div>
																		</td>
																	</tr>
																</tbody><tbody xd:xctname="RepeatingTable">
																	<xsl:for-each select="my:RelatedWebsites/my:RelatedWebsite">
																		<tr>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:RelatedWebsiteURL" xd:CtrlId="CTRL28" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:RelatedWebsiteURL"/>
																				</span>
																			</td>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:RelatedWebsiteTitle" xd:CtrlId="CTRL29" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:RelatedWebsiteTitle"/>
																				</span>
																			</td>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:RelatedWebsiteNotes" xd:CtrlId="CTRL30" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:RelatedWebsiteNotes"/>
																				</span>
																			</td>
																		</tr>
																	</xsl:for-each>
																</tbody>
															</table>
															<div class="optionalPlaceholder" xd:xmlToEdit="group6_22" tabIndex="0" xd:action="xCollection::insert" style="WIDTH: 582px">Insert item</div>
														</div>
														<div> </div>
													</td>
												</tr>
												<tr class="xdContentRowOneCol">
													<td class="xdTableStyleOneCol">
														<div>Related Data</div>
														<div>
															<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 580px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdRepeatingTable msoUcTable" title="" border="1" xd:CtrlId="CTRL31" xd:widgetIndex="0">
																<colgroup>
																	<col style="WIDTH: 145px"></col>
																	<col style="WIDTH: 145px"></col>
																	<col style="WIDTH: 145px"></col>
																	<col style="WIDTH: 145px"></col>
																</colgroup>
																<tbody class="xdTableHeader">
																	<tr>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Relationship</strong>
																				</h5>
																			</div>
																		</td>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Key/URL</strong>
																				</h5>
																			</div>
																		</td>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Title</strong>
																				</h5>
																			</div>
																		</td>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Notes</strong>
																				</h5>
																			</div>
																		</td>
																	</tr>
																</tbody><tbody xd:xctname="RepeatingTable">
																	<xsl:for-each select="my:RelatedData/my:RelatedDataItem">
																		<tr>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><select class="xdComboBox xdBehavior_Select" title="" size="1" tabIndex="0" xd:binding="my:RelatedDataItemRelationship" xd:CtrlId="CTRL119" xd:xctname="dropdown" xd:boundProp="value" style="WIDTH: 100%">
																					<xsl:attribute name="value">
																						<xsl:value-of select="my:RelatedDataItemRelationship"/>
																					</xsl:attribute>
																					<option>
																						<xsl:if test="my:RelatedDataItemRelationship=&quot;&quot;">
																							<xsl:attribute name="selected">selected</xsl:attribute>
																						</xsl:if>Select...</option>
																					<option value="isDerivedFrom">
																						<xsl:if test="my:RelatedDataItemRelationship=&quot;isDerivedFrom&quot;">
																							<xsl:attribute name="selected">selected</xsl:attribute>
																						</xsl:if>Derived from:</option>
																					<option value="isDescribedBy">
																						<xsl:if test="my:RelatedDataItemRelationship=&quot;isDescribedBy&quot;">
																							<xsl:attribute name="selected">selected</xsl:attribute>
																						</xsl:if>Described by:</option>
																					<option value="describes">
																						<xsl:if test="my:RelatedDataItemRelationship=&quot;describes&quot;">
																							<xsl:attribute name="selected">selected</xsl:attribute>
																						</xsl:if>Describes:</option>
																					<option value="hasAssociationWith">
																						<xsl:if test="my:RelatedDataItemRelationship=&quot;hasAssociationWith&quot;">
																							<xsl:attribute name="selected">selected</xsl:attribute>
																						</xsl:if>Has association with:</option>
																					<option value="hasDerivedCollection">
																						<xsl:if test="my:RelatedDataItemRelationship=&quot;hasDerivedCollection&quot;">
																							<xsl:attribute name="selected">selected</xsl:attribute>
																						</xsl:if>Has derivation:</option>
																					<option value="hasPart">
																						<xsl:if test="my:RelatedDataItemRelationship=&quot;hasPart&quot;">
																							<xsl:attribute name="selected">selected</xsl:attribute>
																						</xsl:if>Has part:</option>
																					<option value="isPartOf">
																						<xsl:if test="my:RelatedDataItemRelationship=&quot;isPartOf&quot;">
																							<xsl:attribute name="selected">selected</xsl:attribute>
																						</xsl:if>Part of:</option>
																				</select>
																			</td>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:RelatedDataItemURL" xd:CtrlId="CTRL33" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:RelatedDataItemURL"/>
																				</span>
																			</td>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:RelatedDataItemTitle" xd:CtrlId="CTRL34" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:RelatedDataItemTitle"/>
																				</span>
																			</td>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:RelatedDataItemNotes" xd:CtrlId="CTRL35" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:RelatedDataItemNotes"/>
																				</span>
																			</td>
																		</tr>
																	</xsl:for-each>
																</tbody>
															</table>
															<div class="optionalPlaceholder" xd:xmlToEdit="group8_26" tabIndex="0" xd:action="xCollection::insert" style="WIDTH: 580px">Insert item</div>
														</div>
													</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div> </div>
									<div>
										<hr/>
									</div>
									<div>
										<div> </div>
									</div>
									<div>
										<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 625px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol">
											<colgroup>
												<col style="WIDTH: 625px"></col>
											</colgroup>
											<tbody vAlign="top">
												<tr class="xdHeadingRowEmphasis">
													<td class="xdHeadingCellEmphasis">
														<h2>Coverage</h2>
													</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div><xsl:apply-templates select="my:Coverage" mode="_6"/>
									</div>
									<div>
										<hr/>
									</div>
									<div>
										<div> </div>
									</div>
									<div>
										<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 625px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol">
											<colgroup>
												<col style="WIDTH: 143px"></col>
												<col style="WIDTH: 482px"></col>
											</colgroup>
											<tbody vAlign="top">
												<tr class="xdHeadingRowEmphasis">
													<td colSpan="2" class="xdHeadingCellEmphasis">
														<h2>Subject</h2>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Field of research</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div>
															<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 475px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdRepeatingTable msoUcTable" title="" border="1" xd:CtrlId="CTRL42" xd:widgetIndex="0">
																<colgroup>
																	<col style="WIDTH: 475px"></col>
																</colgroup>
																<tbody class="xdTableHeader">
																	<tr>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Use 2, 4 or 6 - digit code only</strong>
																				</h5>
																			</div>
																		</td>
																	</tr>
																</tbody><tbody xd:xctname="RepeatingTable">
																	<xsl:for-each select="my:FORCodes/my:FORCode">
																		<tr>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" contentEditable="true" tabIndex="0" xd:binding="my:FORCodeValue" xd:CtrlId="CTRL43" xd:xctname="PlainText" style="WIDTH: 100%; WHITE-SPACE: nowrap">
																					<xsl:value-of select="my:FORCodeValue"/>
																				</span>
																			</td>
																		</tr>
																	</xsl:for-each>
																</tbody>
															</table>
															<div class="optionalPlaceholder" xd:xmlToEdit="group12_38" tabIndex="0" xd:action="xCollection::insert" style="WIDTH: 475px">Insert item</div>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Socio-economic Objective</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div>
															<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 475px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdRepeatingTable msoUcTable" title="" border="1" xd:CtrlId="CTRL44" xd:widgetIndex="0">
																<colgroup>
																	<col style="WIDTH: 475px"></col>
																</colgroup>
																<tbody class="xdTableHeader">
																	<tr style="MIN-HEIGHT: 19px">
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<h5 style="FONT-WEIGHT: normal">
																				<strong>Use 2, 4 or 6 - digit code only</strong>
																			</h5>
																		</td>
																	</tr>
																</tbody><tbody xd:xctname="RepeatingTable">
																	<xsl:for-each select="my:SEOCodes/my:SEOCode">
																		<tr style="MIN-HEIGHT: 25px">
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" contentEditable="true" tabIndex="0" xd:binding="my:SEOCodeValue" xd:CtrlId="CTRL45" xd:xctname="PlainText" style="WIDTH: 100%; WHITE-SPACE: nowrap">
																					<xsl:value-of select="my:SEOCodeValue"/>
																				</span>
																			</td>
																		</tr>
																	</xsl:for-each>
																</tbody>
															</table>
															<div class="optionalPlaceholder" xd:xmlToEdit="group14_40" tabIndex="0" xd:action="xCollection::insert" style="WIDTH: 475px">Insert item</div>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Keywords</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div>
															<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 475px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdRepeatingTable msoUcTable" title="" border="1" xd:CtrlId="CTRL46" xd:widgetIndex="0">
																<colgroup>
																	<col style="WIDTH: 475px"></col>
																</colgroup><tbody xd:xctname="RepeatingTable">
																	<xsl:for-each select="my:Keywords/my:Keyword">
																		<tr>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:KeywordValue" xd:CtrlId="CTRL47" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:KeywordValue"/>
																				</span>
																			</td>
																		</tr>
																	</xsl:for-each>
																</tbody>
															</table>
															<div class="optionalPlaceholder" xd:xmlToEdit="group16_37" tabIndex="0" xd:action="xCollection::insert" style="WIDTH: 475px">Insert item</div>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Type of research activity</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div><select class="xdComboBox xdBehavior_Select" title="" size="1" tabIndex="0" xd:binding="my:TypeOfActivity" xd:CtrlId="CTRL68" xd:xctname="dropdown" xd:boundProp="value" style="WIDTH: 100%">
																<xsl:attribute name="value">
																	<xsl:value-of select="my:TypeOfActivity"/>
																</xsl:attribute>
																<option>
																	<xsl:if test="my:TypeOfActivity=&quot;&quot;">
																		<xsl:attribute name="selected">selected</xsl:attribute>
																	</xsl:if>Select...</option>
																<option value="applied">
																	<xsl:if test="my:TypeOfActivity=&quot;applied&quot;">
																		<xsl:attribute name="selected">selected</xsl:attribute>
																	</xsl:if>Applied research</option>
																<option value="experimental">
																	<xsl:if test="my:TypeOfActivity=&quot;experimental&quot;">
																		<xsl:attribute name="selected">selected</xsl:attribute>
																	</xsl:if>Experimental development</option>
																<option value="pure">
																	<xsl:if test="my:TypeOfActivity=&quot;pure&quot;">
																		<xsl:attribute name="selected">selected</xsl:attribute>
																	</xsl:if>Pure basic research</option>
																<option value="strategic">
																	<xsl:if test="my:TypeOfActivity=&quot;strategic&quot;">
																		<xsl:attribute name="selected">selected</xsl:attribute>
																	</xsl:if>Strategic basic research</option>
															</select>
														</div>
													</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div> </div>
									<div>
										<hr/>
									</div>
									<div>
										<div> </div>
									</div>
									<div>
										<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 624px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol">
											<colgroup>
												<col style="WIDTH: 197px"></col>
												<col style="WIDTH: 427px"></col>
											</colgroup>
											<tbody vAlign="top">
												<tr class="xdHeadingRowEmphasis">
													<td colSpan="2" class="xdHeadingCellEmphasis">
														<h2>Rights</h2>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Access rights/conditions</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Rights/my:RightsAccess" xd:CtrlId="CTRL69" xd:xctname="PlainText" style="WIDTH: 100%">
															<xsl:value-of select="my:Rights/my:RightsAccess"/>
														</span>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Rights</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Rights/my:RightsStatement" xd:CtrlId="CTRL70" xd:xctname="PlainText" style="WIDTH: 100%">
															<xsl:value-of select="my:Rights/my:RightsStatement"/>
														</span>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>CC Licence</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent"><select class="xdComboBox xdBehavior_Select" title="" size="1" tabIndex="0" xd:binding="my:Rights/my:RightsCCLicence" xd:CtrlId="CTRL71" xd:xctname="dropdown" xd:boundProp="value" style="WIDTH: 100%">
															<xsl:attribute name="value">
																<xsl:value-of select="my:Rights/my:RightsCCLicence"/>
															</xsl:attribute>
															<option>
																<xsl:if test="my:Rights/my:RightsCCLicence=&quot;&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Select...</option>
															<option value="http://creativecommons.org/licenses/by-nc-nd/3.0/au">
																<xsl:if test="my:Rights/my:RightsCCLicence=&quot;http://creativecommons.org/licenses/by-nc-nd/3.0/au&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>CC BY-NC-ND: Attribution-Noncommercial-No Derivatives</option>
															<option value="http://creativecommons.org/licenses/by-nc-sa/3.0/au">
																<xsl:if test="my:Rights/my:RightsCCLicence=&quot;http://creativecommons.org/licenses/by-nc-sa/3.0/au&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>CC BY-NC-SA: Attribution-Noncommercial-Share Alike</option>
															<option value="http://creativecommons.org/licenses/by-nc/3.0/au">
																<xsl:if test="my:Rights/my:RightsCCLicence=&quot;http://creativecommons.org/licenses/by-nc/3.0/au&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>CC BY-NC: Attribution-Noncommercial</option>
															<option value="http://creativecommons.org/licenses/by-nd/3.0/au">
																<xsl:if test="my:Rights/my:RightsCCLicence=&quot;http://creativecommons.org/licenses/by-nd/3.0/au&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>CC BY-ND: Attribution-No Derivative Works</option>
															<option value="http://creativecommons.org/licenses/by-sa/3.0/au">
																<xsl:if test="my:Rights/my:RightsCCLicence=&quot;http://creativecommons.org/licenses/by-sa/3.0/au&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>CC BY-SA: Attribution-Share Alike</option>
															<option value="http://creativecommons.org/licenses/by/3.0/au">
																<xsl:if test="my:Rights/my:RightsCCLicence=&quot;http://creativecommons.org/licenses/by/3.0/au&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>CC BY: Attribution</option>
														</select>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Other licence</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div>
															<div> </div>
														</div>
														<div>
															<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 398px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol">
																<colgroup>
																	<col style="WIDTH: 199px"></col>
																	<col style="WIDTH: 199px"></col>
																</colgroup>
																<tbody vAlign="top">
																	<tr class="xdTableRow">
																		<td vAlign="top" class="xdTableCellLabel">
																			<h4>Name</h4>
																		</td>
																		<td vAlign="top" class="xdTableCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Rights/my:RightsOtherName" xd:CtrlId="CTRL72" xd:xctname="PlainText" style="WIDTH: 100%">
																				<xsl:value-of select="my:Rights/my:RightsOtherName"/>
																			</span>
																		</td>
																	</tr>
																	<tr class="xdTableRow">
																		<td vAlign="top" class="xdTableCellLabel">
																			<h4>URL</h4>
																		</td>
																		<td vAlign="top" class="xdTableCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Rights/my:RightsOtherURL" xd:CtrlId="CTRL74" xd:xctname="PlainText" style="WIDTH: 100%">
																				<xsl:value-of select="my:Rights/my:RightsOtherURL"/>
																			</span>
																		</td>
																	</tr>
																</tbody>
															</table>
														</div>
														<div> </div>
													</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div> </div>
									<div>
										<hr/>
									</div>
									<div>
										<div> </div>
									</div>
									<div>
										<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 624px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol">
											<colgroup>
												<col style="WIDTH: 312px"></col>
												<col style="WIDTH: 312px"></col>
											</colgroup>
											<tbody vAlign="top">
												<tr class="xdHeadingRowEmphasis">
													<td colSpan="2" class="xdHeadingCellEmphasis">
														<h2>Identifier and location</h2>
													</td>
												</tr>
												<tr class="xdSubheadingRowEmphasis">
													<td colSpan="2" class="xdSubheadingCellEmphasis">
														<h3>Identifier</h3>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Type of identifier</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent"><select class="xdComboBox xdBehavior_Select" title="" size="1" tabIndex="0" xd:binding="my:Identifier/my:IdentifierType" xd:CtrlId="CTRL96" xd:xctname="dropdown" xd:boundProp="value" style="WIDTH: 100%">
															<xsl:attribute name="value">
																<xsl:value-of select="my:Identifier/my:IdentifierType"/>
															</xsl:attribute>
															<option>
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Select...</option>
															<option value="infouri">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;infouri&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>'info' URI scheme</option>
															<option value="ark">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;ark&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>ARK Persistent Identifier Scheme</option>
															<option value="abn">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;abn&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Australian Business Number</option>
															<option value="arc">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;arc&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Australian Research Council identifier</option>
															<option value="doi">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;doi&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Digital Object Identifier</option>
															<option value="handle">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;handle&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>HANDLE System Identifier</option>
															<option value="isil">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;isil&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>International Standard Identifier for Libraries</option>
															<option value="local">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;local&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Local Identifier</option>
															<option value="nla">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;nla&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>National Library of Australia identifier</option>
															<option value="purl">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;purl&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Persistent Uniform Resource Locator</option>
															<option value="uri">
																<xsl:if test="my:Identifier/my:IdentifierType=&quot;uri&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Uniform Resource Identifier</option>
														</select>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Identifier</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Identifier/my:IdentifierValue" xd:CtrlId="CTRL97" xd:xctname="PlainText" style="WIDTH: 100%">
															<xsl:value-of select="my:Identifier/my:IdentifierValue"/>
														</span>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Use this record's ID</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent"><input class="xdBehavior_Boolean" title="" type="checkbox" tabIndex="0" xd:binding="my:Identifier/my:IdentifierUseMetadataID" xd:CtrlId="CTRL98" xd:xctname="CheckBox" xd:boundProp="xd:value" xd:offValue="false" xd:onValue="true">
															<xsl:attribute name="xd:value">
																<xsl:value-of select="my:Identifier/my:IdentifierUseMetadataID"/>
															</xsl:attribute>
															<xsl:if test="my:Identifier/my:IdentifierUseMetadataID=&quot;true&quot;">
																<xsl:attribute name="CHECKED">CHECKED</xsl:attribute>
															</xsl:if>
														</input>
													</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div>
										<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 624px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol" width="undefined">
											<colgroup>
												<col style="WIDTH: 624px"></col>
											</colgroup>
											<tbody vAlign="top">
												<tr class="xdSubheadingRowEmphasis">
													<td class="xdSubheadingCellEmphasis">
														<h3>location</h3>
													</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div>
										<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 624px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol" width="undefined">
											<colgroup>
												<col style="WIDTH: 149px"></col>
												<col style="WIDTH: 475px"></col>
											</colgroup>
											<tbody vAlign="top">
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>URL(s)</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div><xsl:apply-templates select="my:Location/my:LocationURLs/my:LocationURL" mode="_5"/>
															<div class="optionalPlaceholder" xd:xmlToEdit="group31_104" tabIndex="0" xd:action="xCollection::insert" align="left" style="WIDTH: 100%">Insert item</div>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Stored at</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Location/my:LocationStoredAt" xd:CtrlId="CTRL102" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:Location/my:LocationStoredAt"/>
															</span>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Notes</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Location/my:LocationNotes" xd:CtrlId="CTRL101" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:Location/my:LocationNotes"/>
															</span>
														</div>
													</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div> </div>
									<div>
										<hr/>
									</div>
									<div>
										<div> </div>
									</div>
									<div>
										<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 624px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol">
											<colgroup>
												<col style="WIDTH: 194px"></col>
												<col style="WIDTH: 87px"></col>
												<col style="WIDTH: 343px"></col>
											</colgroup>
											<tbody vAlign="top">
												<tr class="xdHeadingRowEmphasis">
													<td colSpan="3" class="xdHeadingCellEmphasis">
														<h2>Management</h2>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Retention period</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:RetentionPeriod" xd:CtrlId="CTRL75" xd:xctname="PlainText" style="WIDTH: 100%">
															<xsl:value-of select="my:RetentionPeriod"/>
														</span>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Extent or quantity</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Extent" xd:CtrlId="CTRL76" xd:xctname="PlainText" style="WIDTH: 100%">
															<xsl:value-of select="my:Extent"/>
														</span>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Disposal date</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent">
														<div style="WIDTH: 100%" class="xdDTPicker" title="" noWrap="1" xd:CtrlId="CTRL77" xd:xctname="DTPicker"><span hideFocus="1" class="xdDTText xdBehavior_FormattingNoBUI" contentEditable="true" tabIndex="0" xd:binding="my:DisposalDate" xd:xctname="DTPicker_DTText" xd:boundProp="xd:num" xd:innerCtrl="_DTText" xd:datafmt="&quot;date&quot;,&quot;dateFormat:Short Date;&quot;">
																<xsl:attribute name="xd:num">
																	<xsl:value-of select="my:DisposalDate"/>
																</xsl:attribute>
																<xsl:choose>
																	<xsl:when test="function-available('xdFormatting:formatString')">
																		<xsl:value-of select="xdFormatting:formatString(my:DisposalDate,&quot;date&quot;,&quot;dateFormat:Short Date;&quot;)"/>
																	</xsl:when>
																	<xsl:otherwise>
																		<xsl:value-of select="my:DisposalDate"/>
																	</xsl:otherwise>
																</xsl:choose>
															</span>
															<button class="xdDTButton" xd:xctname="DTPicker_DTButton" xd:innerCtrl="_DTButton" tabIndex="0">
																<img src="res://infopath.exe/calendar.gif"/>
															</button>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Data owner</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent">
														<div><xsl:apply-templates select="my:DataOwners/my:DataOwner" mode="_3"/>
															<div class="optionalPlaceholder" xd:xmlToEdit="group25_84" tabIndex="0" xd:action="xCollection::insert" align="left" style="WIDTH: 100%">Insert item</div>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Data custodian</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent">
														<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:DataCustodian" xd:CtrlId="CTRL80" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:DataCustodian"/>
															</span>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Data affiliation</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent">
														<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:DataAffiliation" xd:CtrlId="CTRL81" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:DataAffiliation"/>
															</span>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Funding bodies</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent">
														<div><xsl:apply-templates select="my:FundingBodies/my:FundingBody" mode="_4"/>
															<div class="optionalPlaceholder" xd:xmlToEdit="group27_85" tabIndex="0" xd:action="xCollection::insert" align="left" style="WIDTH: 100%">Insert item</div>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Grant numbers</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent">
														<div>
															<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 285px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdRepeatingTable msoUcTable" title="" border="1" xd:CtrlId="CTRL84" xd:widgetIndex="0">
																<colgroup>
																	<col style="WIDTH: 64px"></col>
																	<col style="WIDTH: 84px"></col>
																	<col style="WIDTH: 137px"></col>
																</colgroup>
																<tbody class="xdTableHeader">
																	<tr>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Internal</strong>
																				</h5>
																			</div>
																		</td>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Grant #</strong>
																				</h5>
																			</div>
																		</td>
																		<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
																			<div>
																				<h5 style="FONT-WEIGHT: normal">
																					<strong>Description</strong>
																				</h5>
																			</div>
																		</td>
																	</tr>
																</tbody><tbody xd:xctname="RepeatingTable">
																	<xsl:for-each select="my:GrantNumbers/my:GrantNumber">
																		<tr>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><input class="xdBehavior_Boolean" title="" type="checkbox" tabIndex="0" xd:binding="my:GrantNumberInternal" xd:CtrlId="CTRL88" xd:xctname="CheckBox" xd:boundProp="xd:value" xd:offValue="false" xd:onValue="true">
																					<xsl:attribute name="xd:value">
																						<xsl:value-of select="my:GrantNumberInternal"/>
																					</xsl:attribute>
																					<xsl:if test="my:GrantNumberInternal=&quot;true&quot;">
																						<xsl:attribute name="CHECKED">CHECKED</xsl:attribute>
																					</xsl:if>
																				</input>
																			</td>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:GrantNumberID" xd:CtrlId="CTRL86" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:GrantNumberID"/>
																				</span>
																			</td>
																			<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:GrantNumberDescription" xd:CtrlId="CTRL87" xd:xctname="PlainText" style="WIDTH: 100%">
																					<xsl:value-of select="my:GrantNumberDescription"/>
																				</span>
																			</td>
																		</tr>
																	</xsl:for-each>
																</tbody>
															</table>
															<div class="optionalPlaceholder" xd:xmlToEdit="group29_91" tabIndex="0" xd:action="xCollection::insert" style="WIDTH: 285px">Insert item</div>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Project title</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent">
														<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:ProjectTitle" xd:CtrlId="CTRL89" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:ProjectTitle"/>
															</span>
														</div>
													</td>
												</tr>
												<tr style="MIN-HEIGHT: 30px" class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Depositor</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent">
														<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:Depositor" xd:CtrlId="CTRL90" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:Depositor"/>
															</span>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Data size</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent">
														<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:DataSize" xd:CtrlId="CTRL91" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:DataSize"/>
															</span>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Institutional data management policy</h4>
													</td>
													<td colSpan="2" vAlign="top" class="xdTableEmphasisCellComponent">
														<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:DataManagementPolicy" xd:CtrlId="CTRL92" xd:xctname="PlainText" xd:datafmt="&quot;string&quot;,&quot;plainMultiline&quot;" style="OVERFLOW-X: auto; OVERFLOW-Y: auto; WIDTH: 400px; WORD-WRAP: break-word; WHITE-SPACE: normal; HEIGHT: 73px">
																<xsl:choose>
																	<xsl:when test="function-available('xdFormatting:formatString')">
																		<xsl:value-of select="xdFormatting:formatString(my:DataManagementPolicy,&quot;string&quot;,&quot;plainMultiline&quot;)" disable-output-escaping="yes"/>
																	</xsl:when>
																	<xsl:otherwise>
																		<xsl:value-of select="my:DataManagementPolicy" disable-output-escaping="yes"/>
																	</xsl:otherwise>
																</xsl:choose>
															</span>
														</div>
													</td>
												</tr>
												<tr class="xdTableEmphasisRow">
													<td vAlign="top" class="xdTableEmphasisCellLabel">
														<h4>Data management plan</h4>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div>
															<div><input class="xdBehavior_Boolean" title="" type="checkbox" tabIndex="0" xd:binding="my:DataManagementPlan/my:DataManagementPlanExists" xd:CtrlId="CTRL117" xd:xctname="CheckBox" xd:boundProp="xd:value" xd:offValue="false" xd:onValue="true">
																	<xsl:attribute name="xd:value">
																		<xsl:value-of select="my:DataManagementPlan/my:DataManagementPlanExists"/>
																	</xsl:attribute>
																	<xsl:if test="my:DataManagementPlan/my:DataManagementPlanExists=&quot;true&quot;">
																		<xsl:attribute name="CHECKED">CHECKED</xsl:attribute>
																	</xsl:if>
																</input>Yes</div>
														</div>
													</td>
													<td vAlign="top" class="xdTableEmphasisCellComponent">
														<div>
															<font style="FONT-SIZE: 11pt">
																<strong>Notes</strong>
															</font>
														</div>
														<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:DataManagementPlan/my:DataManagementPlanNotes" xd:CtrlId="CTRL95" xd:xctname="PlainText" style="WIDTH: 100%">
																<xsl:value-of select="my:DataManagementPlan/my:DataManagementPlanNotes"/>
															</span>
														</div>
													</td>
												</tr>
											</tbody>
										</table>
									</div>
									<div> </div>
								</td>
							</tr>
						</tbody>
					</table>
				</div>
				<div align="center"> </div>
			</body>
		</html>
	</xsl:template>
	<xsl:template match="my:PrimaryContact" mode="_1">
		<div style="BORDER-BOTTOM: 0pt; BORDER-LEFT: 0pt; WIDTH: 577px; MARGIN-BOTTOM: 0px; BORDER-TOP: 0pt; BORDER-RIGHT: 0pt" class="xdSection xdRepeating" title="" align="left" xd:CtrlId="CTRL59" xd:xctname="Section" tabIndex="-1" xd:widgetIndex="0">
			<div>
				<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 576px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleFourCol">
					<colgroup>
						<col style="WIDTH: 76px"></col>
						<col style="WIDTH: 253px"></col>
						<col style="WIDTH: 97px"></col>
						<col style="WIDTH: 150px"></col>
					</colgroup>
					<tbody vAlign="top">
						<tr style="MIN-HEIGHT: 54px" class="xdTableRow">
							<td class="xdTableCellLabel" style="PADDING-RIGHT: 5px">
								<div>
									<strong>Title</strong>
								</div>
								<div align="left"><span hideFocus="1" class="xdTextBox" title="" contentEditable="true" tabIndex="0" xd:binding="my:PrimaryContactTitle" xd:CtrlId="CTRL108" xd:xctname="PlainText" style="WIDTH: 100%; WHITE-SPACE: nowrap">
										<xsl:value-of select="my:PrimaryContactTitle"/>
									</span>
								</div>
							</td>
							<td class="xdTableMiddleCell" style="PADDING-RIGHT: 5px">
								<h4>First name</h4>
								<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:PrimaryContactFirstName" xd:CtrlId="CTRL105" xd:xctname="PlainText" style="WIDTH: 100%">
										<xsl:value-of select="my:PrimaryContactFirstName"/>
									</span>
								</div>
							</td>
							<td colSpan="2" class="xdTableMiddleCell" style="PADDING-RIGHT: 22px">
								<h4>Family name</h4><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:PrimaryContactFamilyName" xd:CtrlId="CTRL106" xd:xctname="PlainText" style="WIDTH: 100%">
									<xsl:value-of select="my:PrimaryContactFamilyName"/>
								</span>
							</td>
						</tr>
						<tr class="xdTableRow">
							<td class="xdTableCellLabel">
								<h4>email</h4>
							</td>
							<td class="xdTableMiddleCell"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:PrimaryContactEmail" xd:CtrlId="CTRL107" xd:xctname="PlainText" style="WIDTH: 100%">
									<xsl:value-of select="my:PrimaryContactEmail"/>
								</span>
							</td>
							<td class="xdTableMiddleCell">
								<h4>ID</h4>
							</td>
							<td class="xdTableCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:PrimaryContactID" xd:CtrlId="CTRL109" xd:xctname="PlainText" style="WIDTH: 100%">
									<xsl:value-of select="my:PrimaryContactID"/>
								</span>
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</xsl:template>
	<xsl:template match="my:Collaborator" mode="_2">
		<div style="WIDTH: 100%; MARGIN-BOTTOM: 0px" class="xdRepeatingSection xdRepeating" title="" align="left" xd:CtrlId="CTRL60" xd:xctname="RepeatingSection" tabIndex="-1" xd:widgetIndex="0">
			<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:CollaboratorName" xd:CtrlId="CTRL62" xd:xctname="PlainText" style="WIDTH: 100%">
					<xsl:value-of select="my:CollaboratorName"/>
				</span>
			</div>
		</div>
	</xsl:template>
	<xsl:template match="my:Coverage" mode="_6">
		<div style="BORDER-BOTTOM: 0pt; BORDER-LEFT: 0pt; WIDTH: 100%; MARGIN-BOTTOM: 0px; HEIGHT: 127px; BORDER-TOP: 0pt; BORDER-RIGHT: 0pt" class="xdSection xdRepeating" title="" align="left" xd:CtrlId="CTRL110" xd:xctname="Section" tabIndex="-1" xd:widgetIndex="0">
			<div>
				<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 624px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdFormLayout xdTableStyleTwoCol" width="undefined">
					<colgroup>
						<col style="WIDTH: 163px"></col>
						<col style="WIDTH: 461px"></col>
					</colgroup>
					<tbody vAlign="top">
						<tr class="xdTableEmphasisRow">
							<td vAlign="top" class="xdTableEmphasisCellLabel">
								<h4>Date Coverage</h4>
							</td>
							<td vAlign="top" class="xdTableEmphasisCellComponent">
								<div style="WIDTH: 167px" class="xdDTPicker" title="" noWrap="1" xd:CtrlId="CTRL111" xd:xctname="DTPicker"><span hideFocus="1" class="xdDTText xdBehavior_FormattingNoBUI" contentEditable="true" tabIndex="0" xd:binding="my:DateFrom" xd:xctname="DTPicker_DTText" xd:boundProp="xd:num" xd:innerCtrl="_DTText" xd:datafmt="&quot;date&quot;,&quot;dateFormat:Short Date;&quot;">
										<xsl:attribute name="xd:num">
											<xsl:value-of select="my:DateFrom"/>
										</xsl:attribute>
										<xsl:choose>
											<xsl:when test="function-available('xdFormatting:formatString')">
												<xsl:value-of select="xdFormatting:formatString(my:DateFrom,&quot;date&quot;,&quot;dateFormat:Short Date;&quot;)"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="my:DateFrom"/>
											</xsl:otherwise>
										</xsl:choose>
									</span>
									<button class="xdDTButton" xd:xctname="DTPicker_DTButton" xd:innerCtrl="_DTButton" tabIndex="0">
										<img src="res://infopath.exe/calendar.gif"/>
									</button>
								</div>to 
<div style="WIDTH: 152px" class="xdDTPicker" title="" noWrap="1" xd:CtrlId="CTRL112" xd:xctname="DTPicker"><span hideFocus="1" class="xdDTText xdBehavior_FormattingNoBUI" contentEditable="true" tabIndex="0" xd:binding="my:DateTo" xd:xctname="DTPicker_DTText" xd:boundProp="xd:num" xd:innerCtrl="_DTText" xd:datafmt="&quot;date&quot;,&quot;dateFormat:Short Date;&quot;">
										<xsl:attribute name="xd:num">
											<xsl:value-of select="my:DateTo"/>
										</xsl:attribute>
										<xsl:choose>
											<xsl:when test="function-available('xdFormatting:formatString')">
												<xsl:value-of select="xdFormatting:formatString(my:DateTo,&quot;date&quot;,&quot;dateFormat:Short Date;&quot;)"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="my:DateTo"/>
											</xsl:otherwise>
										</xsl:choose>
									</span>
									<button class="xdDTButton" xd:xctname="DTPicker_DTButton" xd:innerCtrl="_DTButton" tabIndex="0">
										<img src="res://infopath.exe/calendar.gif"/>
									</button>
								</div>
							</td>
						</tr>
						<tr class="xdTableEmphasisRow">
							<td vAlign="top" class="xdTableEmphasisCellLabel">
								<h4>Time Period</h4>
							</td>
							<td vAlign="top" class="xdTableEmphasisCellComponent"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:TimePeriod" xd:CtrlId="CTRL113" xd:xctname="PlainText" style="WIDTH: 100%">
									<xsl:value-of select="my:TimePeriod"/>
								</span>
							</td>
						</tr>
						<tr class="xdTableEmphasisRow">
							<td vAlign="top" class="xdTableEmphasisCellLabel">
								<h4>Geospatial Location</h4>
							</td>
							<td vAlign="top" class="xdTableEmphasisCellComponent">
								<div>
									<table style="BORDER-BOTTOM-STYLE: none; BORDER-RIGHT-STYLE: none; WIDTH: 434px; BORDER-COLLAPSE: collapse; WORD-WRAP: break-word; BORDER-TOP-STYLE: none; TABLE-LAYOUT: fixed; BORDER-LEFT-STYLE: none" class="xdRepeatingTable msoUcTable" title="" border="1" xd:CtrlId="CTRL114" xd:widgetIndex="0">
										<colgroup>
											<col style="WIDTH: 217px"></col>
											<col style="WIDTH: 217px"></col>
										</colgroup>
										<tbody class="xdTableHeader">
											<tr>
												<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
													<div>
														<h5 style="FONT-WEIGHT: normal">
															<strong>Type</strong>
														</h5>
													</div>
												</td>
												<td style="TEXT-ALIGN: center; BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px">
													<div>
														<h5 style="FONT-WEIGHT: normal">
															<strong>Value</strong>
														</h5>
													</div>
												</td>
											</tr>
										</tbody><tbody xd:xctname="RepeatingTable">
											<xsl:for-each select="my:GeospatialLocations/my:GeospatialLocation">
												<tr>
													<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><select class="xdComboBox xdBehavior_Select" title="" size="1" tabIndex="0" xd:binding="my:GeospatialLocationType" xd:CtrlId="CTRL118" xd:xctname="dropdown" xd:boundProp="value" style="WIDTH: 100%">
															<xsl:attribute name="value">
																<xsl:value-of select="my:GeospatialLocationType"/>
															</xsl:attribute>
															<option>
																<xsl:if test="my:GeospatialLocationType=&quot;&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Select...</option>
															<option value="gml">
																<xsl:if test="my:GeospatialLocationType=&quot;gml&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>OpenGIS Geography Markup Language</option>
															<option value="gmlKmlPolyCoords">
																<xsl:if test="my:GeospatialLocationType=&quot;gmlKmlPolyCoords&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>KML long/lat co-ordinates derived from GML</option>
															<option value="gpx">
																<xsl:if test="my:GeospatialLocationType=&quot;gpx&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>GPS Exchange Format</option>
															<option value="iso31661">
																<xsl:if test="my:GeospatialLocationType=&quot;iso31661&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Country code (iso31661)</option>
															<option value="iso31662">
																<xsl:if test="my:GeospatialLocationType=&quot;iso31662&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Country subdivision code (iso31662)</option>
															<option value="iso19139dcmiBox">
																<xsl:if test="my:GeospatialLocationType=&quot;iso19139dcmiBox&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>DCMI Box notation (iso19139)</option>
															<option value="kml">
																<xsl:if test="my:GeospatialLocationType=&quot;kml&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Keyhole Markup Language</option>
															<option value="kmlPolyCoords">
																<xsl:if test="my:GeospatialLocationType=&quot;kmlPolyCoords&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>KML long/lat co-ordinates</option>
															<option value="dcmiPoint">
																<xsl:if test="my:GeospatialLocationType=&quot;dcmiPoint&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>DCMI Point notation</option>
															<option value="text">
																<xsl:if test="my:GeospatialLocationType=&quot;text&quot;">
																	<xsl:attribute name="selected">selected</xsl:attribute>
																</xsl:if>Free text</option>
														</select>
													</td>
													<td style="BORDER-LEFT: medium none; PADDING-BOTTOM: 1px; PADDING-LEFT: 5px; PADDING-RIGHT: 5px; BORDER-RIGHT: medium none; PADDING-TOP: 1px"><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:GeospatialLocationValue" xd:CtrlId="CTRL116" xd:xctname="PlainText" style="WIDTH: 100%">
															<xsl:value-of select="my:GeospatialLocationValue"/>
														</span>
													</td>
												</tr>
											</xsl:for-each>
										</tbody>
									</table>
									<div class="optionalPlaceholder" xd:xmlToEdit="GeospatialLocation_188" tabIndex="0" xd:action="xCollection::insert" style="WIDTH: 434px">Insert item</div>
								</div>
							</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>
	</xsl:template>
	<xsl:template match="my:LocationURL" mode="_5">
		<div style="WIDTH: 100%; MARGIN-BOTTOM: 0px" class="xdRepeatingSection xdRepeating" title="" align="left" xd:CtrlId="CTRL99" xd:xctname="RepeatingSection" tabIndex="-1" xd:widgetIndex="0">
			<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:LocationURLValue" xd:CtrlId="CTRL100" xd:xctname="PlainText" style="WIDTH: 100%">
					<xsl:value-of select="my:LocationURLValue"/>
				</span>
			</div>
		</div>
	</xsl:template>
	<xsl:template match="my:DataOwner" mode="_3">
		<div style="WIDTH: 100%; MARGIN-BOTTOM: 0px" class="xdRepeatingSection xdRepeating" title="" align="left" xd:CtrlId="CTRL78" xd:xctname="RepeatingSection" tabIndex="-1" xd:widgetIndex="0">
			<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:DataOwnerName" xd:CtrlId="CTRL79" xd:xctname="PlainText" style="WIDTH: 100%">
					<xsl:value-of select="my:DataOwnerName"/>
				</span>
			</div>
		</div>
	</xsl:template>
	<xsl:template match="my:FundingBody" mode="_4">
		<div style="WIDTH: 100%; MARGIN-BOTTOM: 0px" class="xdRepeatingSection xdRepeating" title="" align="left" xd:CtrlId="CTRL82" xd:xctname="RepeatingSection" tabIndex="-1" xd:widgetIndex="0">
			<div><span hideFocus="1" class="xdTextBox" title="" tabIndex="0" xd:binding="my:FundingBodyName" xd:CtrlId="CTRL83" xd:xctname="PlainText" style="WIDTH: 100%">
					<xsl:value-of select="my:FundingBodyName"/>
				</span>
			</div>
			<div> </div>
		</div>
	</xsl:template>
</xsl:stylesheet>
