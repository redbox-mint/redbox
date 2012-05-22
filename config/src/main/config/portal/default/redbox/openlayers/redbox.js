function loadOpenLayers() {
    // Default to show Australia
    var lon = 135;
    var lat = -27;
    var zoom = 3;
    // Map and styling
    var map, styles, ignoredFeatures = {};
    var flashBoundingBox = false;
    // Projections
    var projWgs = new OpenLayers.Projection("EPSG:900913");
    var projSm = new OpenLayers.Projection("EPSG:4326");
    // Layers
    var osmLayer, gLayer, vLayer;
    // To turn on google, you also need to provide your API key and
    // uncomment the javascript call in /redbox/workflows/dataset.vm
    var layers = "osm"; // "osm", "google", "both"
    // Controls
    var grippy, drawPoint, drawPath, drawRect, drawCircle, drawPoly, modify;

    // Formats
    var wktFormat = new OpenLayers.Format.WKT({
        internalProjection: projWgs,
        externalProjection: projSm
    });
    var gmlFormat = new OpenLayers.Format.GML({
        internalProjection: projWgs,
        externalProjection: projSm
    });
    var kmlFormat = new OpenLayers.Format.KML({
        internalProjection: projWgs,
        externalProjection: projSm
    });

    // Very hacky, always test null coming back from this, and don't assume a
    //   selector will work... this pulls apart a feature ID and wkt string to
    //   guestimate the selector required to target an SVG element inside the map.
    // Cases observed and supported thus far:
    // POLYGON:    OpenLayers.Feature.Vector_200 => .olMap path[id='OpenLayers.Geometry.Polygon_199']
    // POINT:      OpenLayers.Feature.Vector_200 => .olMap circle[id='OpenLayers.Geometry.Point_199']
    // LINESTRING: OpenLayers.Feature.Vector_200 => .olMap polyline[id='OpenLayers.Geometry.LineString_199']
    
    // TODO - This won't work in IE as it uses the VML renderer
    // TODO - This won't work after data using DCMI bounding boxes is loaded if
    //        'flashBoundingBox' is set to 'true' because of the short lived
    //        features that increment IDs. Other isues can likely cause this too
    function featureSelector(fId, wkt) {
        // Find the digits at the end
        var matches = fId.match(/(_(\d+))$/);
        if (matches == null || matches.lenth < 3) {
            return null;
        }
        // This line is the fragile part '-1' assumes a sequence that is linear
        var number = matches[2] - 1;
        if (wkt.indexOf("POLYGON") == 0) {
            return ".olMap path[id='OpenLayers.Geometry.Polygon_"+number+"']";
        }
        if (wkt.indexOf("POINT") == 0) {
            return ".olMap circle[id='OpenLayers.Geometry.Point_"+number+"']";
        }
        if (wkt.indexOf("LINESTRING") == 0) {
            return ".olMap polyline[id='OpenLayers.Geometry.LineString_"+number+"']";
        }
        return null;
    }

    // This object acts somewhat like an external API. We are going to send it
    // out to redbox/jaffa to allow for integration with the map.
    var rbMapMethods = {
        panTo: function(lon, lat, newZoom) {
            var point = new OpenLayers.LonLat(lon, lat);
            var osmPoint = point.transform(projSm, projWgs);
            map.panTo(osmPoint);
            if (newZoom != null) {
                // You could do this in one hit with setCenter, but this allows
                //  for the panTo() call to be animated if required.
                map.zoomTo(newZoom);
            }
        },
        mapWktData: function(data, newFormat) {
            var feature;

            if (newFormat == null) {
                return null;
            }
            // Non-supported formats
            if (newFormat == "gpx") {
                alert("The GPS Exchange Format (GPX) is not supported when using the map. Direct input is required if you want to submit GPX data.");
                return null;
            }
            if (newFormat == "iso31661" || newFormat == "iso31662") {
                alert("Country codes and subdivisions are not supported when using the map. Direct input is required if you want to submit ISO31661/ISO31662 data.");
                return null;
            }
            // KML long/lat co-ordinates (optionally derived from GML)
            if (newFormat == "gmlKmlPolyCoords" || newFormat == "kmlPolyCoords") {
                alert("KML subsets are not supported when using the map. You can use 'Keyhole Markup Language' to provided a complete KML entry, or use direct input to provide the others.");
                return null;
            }

            // Free text
            if (newFormat == "text") {
                // No mapping required
                return data;
            }
            // OpenGIS Geography Markup Language
            if (newFormat == "gml") {
                feature = wktFormat.read(data);
                return gmlFormat.write(feature);
            }
            // KML long/lat co-ordinates
            if (newFormat == "kml") {
                feature = wktFormat.read(data);
                return kmlFormat.write(feature);
            }
            // DCMI Box notation (iso19139)
            if (newFormat == "iso19139dcmiBox") {
                if (data.indexOf("POINT") == 0) {
                    alert("For POINT data you should use a DCMI Point, rather then a DCMI Box.");
                    return null;
                }

                // Find the bounding box of this feature
                feature = wktFormat.read(data);
                // Before we transform it, build a geometry we'll use later
                var bounds = feature.geometry.getBounds();
                var geometry = bounds.toGeometry();

                // Now transform wo WGS84 and build a return string
                bounds = bounds.transform(projWgs, projSm);
                var dcmiBoxString = "northlimit=" + bounds.top
                    + "; southlimit=" + bounds.bottom
                    + "; westlimit=" + bounds.left
                    + "; eastLimit=" + bounds.right
                    + "; projection=WGS84";

                // For Internet Explorer, stop here, interacting with
                //  the SVG elements will just fail
                if ($.browser["msie"]) {
                    return dcmiBoxString;
                }

                if (flashBoundingBox === true) {
                    map.zoomToExtent(geometry.getBounds());

                    // Using the geometry we grabbed before transforming to create a feature
                    var boxFeature = new OpenLayers.Feature.Vector(geometry);
                    // Make sure it gets ignored by our handlers
                    ignoredFeatures[boxFeature.id] = true;
                    // Add to the map
                    vLayer.addFeatures([boxFeature]);

                    // Remove from the DOM slowly
                    var selector = featureSelector(boxFeature.id, "POLYGON");
                    if (selector != null) {
                        var boxElement = $(selector);
                        if (boxElement.size() != 0) {
                            //  Highlight
                            boxElement.attr("stroke", "#0000FF");
                            boxElement.attr("fill", "#0000FF");
                            // Callback to remove the feature after it hides
                            function removeTempFeature() {
                                vLayer.removeFeatures([boxElement.data("olFeature")]);
                                delete ignoredFeatures[boxElement.data("olFeatureId")];
                            }
                            // Hide after a delay
                            boxElement.data("olFeature", boxFeature);
                            boxElement.data("olFeatureId", boxFeature.id);
                            boxElement.delay(1000).fadeOut(2000, removeTempFeature);
                        }
                    }
                }

                return dcmiBoxString;
            }
            // DCMI Point notation
            if (newFormat == "dcmiPoint") {
                if (data.indexOf("POINT") != 0) {
                    alert("This is for POINT data only. Perhaps you should try a DCMI Box for shapes.");
                    return null;
                }

                // Find the 'center' of the point. The Geometry API is generic,
                //  but the center of any shape works.
                feature = wktFormat.read(data);
                var point = feature.geometry.getCentroid().transform(projWgs, projSm);

                return "east=" + point.x
                    + "; north=" + point.y
                    + "; projection=WGS84";
            }
            return null;
        },
        loadData: function() {
            loadFeatures();
        }
    };

    function olStyles() {
        styles = new OpenLayers.StyleMap({
            "default": new OpenLayers.Style({
                pointRadius: 5,
                fillColor: "#ffff00",
                fillOpacity: 0.33,
                strokeColor: "#000000",
                strokeWidth: 2,
                strokeOpacity: 0.75,
                graphicZIndex: 1
            }),
            "select": new OpenLayers.Style({
                strokeColor: "#00ccff",
                strokeWidth: 4
            })
        });
    }

    function init(){
        //***************************
        // Map
        map = new OpenLayers.Map('map', {
                projection: projWgs,
                displayProjection: projSm,
                units: "m",
                maxResolution: 156543.0339,
                maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
                                                 20037508.34, 20037508.34)
            });
        olStyles();

        //***************************
        // Map Layers
        if (layers == "osm" || layers == "both") {
            osmLayer = new OpenLayers.Layer.OSM("OpenStreetMap (Mapnik)");
            $("#attribution").html(osmLayer.attribution);
            osmLayer.attribution = "";
        }
        if (layers == "google" || layers == "both") {
            gLayer = new OpenLayers.Layer.Google("Google", {sphericalMercator:true});
        }
        vLayer = new OpenLayers.Layer.Vector("Editable", {
            renderers: OpenLayers.Layer.Vector.prototype.renderers,
            //renderers: [OpenLayers.Renderer.SVG], // Firefox + Chrome
            //renderers: [OpenLayers.Renderer.VML], // IE8
            projection: projSm,
            styleMap: styles
        });

        // Add map basics
        if (layers == "osm") {
            map.addLayers([osmLayer, vLayer]);
        }
        if (layers == "google") {
            map.addLayers([gLayer, vLayer]);
        }
        if (layers == "both") {
            map.addLayers([osmLayer, gLayer, vLayer]);
            map.addControl(new OpenLayers.Control.LayerSwitcher());
        }
        map.addControl(new OpenLayers.Control.MousePosition());

        //***************************
        // Edit controls
        var container = document.getElementById("panel");
        var panel = new OpenLayers.Control.Panel(
            {
                div: container
            });
        grippy = new OpenLayers.Control.Navigation(
            {
                title: "Navigate"
            });
        drawPoint = new OpenLayers.Control.DrawFeature(
            vLayer,
            OpenLayers.Handler.Point,
            {
                displayClass: "olControlDrawFeaturePoint",
                title: "Draw Point"
            });
        drawPath = new OpenLayers.Control.DrawFeature(
            vLayer,
            OpenLayers.Handler.Path,
            {
                displayClass: "olControlDrawFeaturePath",
                title: "Draw Path"
            });
        drawRect = new OpenLayers.Control.DrawFeature(
            vLayer,
            OpenLayers.Handler.RegularPolygon,
            {
                displayClass: "olControlDrawFeatureBox",
                title: "Draw Box",
                handlerOptions: {
                    sides: 4,
                    irregular: true
                }
            });
        drawCircle = new OpenLayers.Control.DrawFeature(
            vLayer,
            OpenLayers.Handler.RegularPolygon,
            {
                displayClass: "olControlDrawFeatureCircle",
                title: "Draw Circle",
                handlerOptions: {
                    sides: 20
                }
            });
        var polygonHelpOn = function(event) {
            $("#polygonHelp").show();
        };
        var polygonHelpOff = function(event) {
            $("#polygonHelp").hide();
        };
        drawPoly = new OpenLayers.Control.DrawFeature(
            vLayer,
            OpenLayers.Handler.Polygon, {
                displayClass: "olControlDrawFeaturePolygon",
                title: "Draw Polygon",
                eventListeners: {
                    "activate": polygonHelpOn,
                    "deactivate": polygonHelpOff
                }
            });
        modify = new OpenLayers.Control.ModifyFeature(
            vLayer,
            {
                displayClass: "olControlModifyFeature",
                title: "Modify Features",
                mode: OpenLayers.Control.ModifyFeature.RESHAPE | OpenLayers.Control.ModifyFeature.DRAG
            });
        panel.addControls([grippy, drawPoint, drawPath, drawRect, drawCircle, drawPoly, modify]);
        map.addControl(panel);
        grippy.activate();

        // Feature info extraction
        vLayer.events.register("featureadded", null, featureUpdate);
        vLayer.events.register("featuremodified", null, featureUpdate);

        // Set the starting point. The public panTo() won't work straight away
        map.setCenter(new OpenLayers.LonLat(lon, lat).transform(projSm, projWgs), zoom);
    }

    //***************************
    // Event handling for feature edits
    var featureTable = $(".redboxGeoData");
    var closeIcon = "<span class=\"ui-button-icon-primary ui-icon ui-icon-closethick\"></span>";
    var selectIcon = "<span class=\"ui-button-icon-primary ui-icon ui-icon-arrow-4\"></span>";
    var deleteButton = "<button class=\"deleteFeature ui-button ui-widget ui-state-default ui-corner-all\">"+closeIcon+"</span></button>";
    var selectButton = "<button class=\"selectFeature ui-button ui-widget ui-state-default ui-corner-all\">"+selectIcon+"</span></button>";
    function featureUpdate(event) {
        var element, rowElement, fIdElement;
        var fId = event.feature.id;
        var found = false;

        // Some temporary features should be ignored
        if (fId in ignoredFeatures) {
            return;
        }

        // Is this an existing feature?
        featureTable.find(".redboxGeoDataFid").each(function(i, elem) {
            element = $(elem);
            // Find the row we want
            if (fId == element.val()) {
                fIdElement = element;
                rowElement = element.parents(".redboxGeoDataRow");
                found = true;
            }
        });
        // Or a new feature?
        if (!found) {
            $(".redboxGeoData .add-another-item").click();
            rowElement = featureTable.find(".redboxGeoDataRow:last");
            fIdElement = rowElement.find(".redboxGeoDataFid");
            var outElement = rowElement.find(".redboxGeoDataOutput");
            outElement.attr("readonly", "readonly");
        }

        // Get the formatted String for this feature
        var value = wktFormat.write(event.feature);

        // Load our data into the form
        fIdElement.val(fId);
        rowElement.find(".redboxGeoDataWkt").val(value);

        // Is there a type already?
        var typeElement = rowElement.find(".locationType");
        var type = typeElement.val();
        if (type != null && type != "") {
            // TODO: Go straight to a crosswalk
            var mappedValue = rbMapMethods.mapWktData(value, type);
            if (mappedValue == null) {
                alert("Error mapping data to type '"+type+"'.");
            } else {
                rowElement.find(".redboxGeoDataOutput").val(mappedValue);
            }
        } else {
            // Text only
            rowElement.find(".locationType").val("text");
            rowElement.find(".redboxGeoDataOutput").val(value);
        }

        // Add/update buttons for select/delete
        var toolCell = rowElement.find(".delete-item");
        rowElement.find(".delete-item a").hide();
        // Kind of odd here, but we want to prevent Jaffa events on
        //   $(".delete-item").click() from firing except from our script, so we
        //   will fill the table cell with a div and trap the click events to
        //   prevent them bubbling, then insert OpenLayers tools into this div.
        // This way after our delete function fires it can trigger the delete
        //   in Jaffa directly, but the user can't accidently click on it, which
        //   would result in a disconnect between Jaffa and OpenLayers.
        // Requires some specific styles in our CSS too relating to height.
        // TODO: Still has issues in IE.
        var trapClick = function() {
            // Stop bubbling
            //alert("trapClick()");
            return false;
        };
        var trapDiv = toolCell.find(".trapClickDiv");
        if (trapDiv.size() == 0) {
            trapDiv = $("<div class=\"trapClickDiv\"></div>");
            toolCell.append(trapDiv);
            trapDiv.click(trapClick);

            // Click to select
            var selectLink = $(selectButton);
            trapDiv.append(selectLink);
            selectLink.click(clickFeature);
            // Delete links
            var deleteLink = $(deleteButton);
            trapDiv.append(deleteLink);
            deleteLink.click(deleteFeature);
        }
    }
    function loadFeatures() {
        var element, feature, fIdElement, fString, outElement, rowElement;
        var featureCount = 0;
        featureTable.find(".redboxGeoDataWkt").each(function(i, elem) {
            // Get Jaffa DOM elements
            element = $(elem);
            rowElement = element.parents(".redboxGeoDataRow");
            fIdElement = rowElement.find(".redboxGeoDataFid");
            outElement = rowElement.find(".redboxGeoDataOutput");
            fString = element.val();

            // Test ignores the .0. row used as a template
            if (fString != null && fString != "") {
                featureCount++;
                // Parse into a feature
                feature = wktFormat.read(fString);
                // Add to Jaffa - MUST come before OpenLayers as the
                //  callback on modify will be looking here
                fIdElement.val(feature.id);
                // Add to OpenLayers
                vLayer.addFeatures([feature]);
                // Ensure the user doesn't mistakenly edit formatted outputs
                outElement.attr("readonly", "readonly");
            }
        });
        if (featureCount > 0) {
            vLayer.map.zoomToExtent(vLayer.getDataExtent());
        }
    }
    function clickFeature() {
        // Get Jaffa DOM Elements
        var rowElement = $(this).parents(".redboxGeoDataRow");
        var fIdElement = rowElement.find(".redboxGeoDataFid");
        var fElement = rowElement.find(".redboxGeoDataWkt");
        var fId = fIdElement.val();
        var fString = fElement.val();

        // Update toolbar
        grippy.deactivate();
        drawPoint.deactivate();
        drawPath.deactivate();
        drawRect.deactivate();
        drawCircle.deactivate();
        drawPoly.deactivate();
        modify.activate();

        // TODO - graphical style does not update - needs to go blue as selected.
        //        Points in particular MUST have this to be distinguishable from
        //        other points on the layer.
        // Select and display in OpenLayers
        var feature = vLayer.getFeatureById(fId);
        modify.selectFeature(feature);
        map.zoomToExtent(feature.geometry.getBounds());

        // For POINTs we can get pretty whacky zoom, so zoom back out to default
        if (fString.indexOf("POINT") == 0) {
            map.zoomTo(zoom);
        }

        // Alter styling to emphasize the selected unit
        //  * Zoom first or a redraw will kill our style
        var selector = featureSelector(fId, fString);
        if (selector != null) {
            var svgElement = $(selector);
            if (svgElement.size() != 0) {
                // Reset any styles we drew that are hanging around
                vLayer.redraw();
                // Highlight the edges of this shape
                svgElement.attr("stroke", "#00CCFF");
            }
        }

        // Stop bubbling
        return false;
    }
    function deleteFeature() {
        // Works around a graphical glitch on
        //  selected objects that get deleted.
        drawPoint.deactivate();
        drawPath.deactivate();
        drawRect.deactivate();
        drawCircle.deactivate();
        drawPoly.deactivate();
        modify.deactivate();
        grippy.activate();

        // Get Jaffa DOM elements
        var rowElement = $(this).parents(".redboxGeoDataRow");
        var fIdElement = rowElement.find(".redboxGeoDataFid");
        var fId = fIdElement.val();

        // Remove from OpenLayers
        var feature = vLayer.getFeatureById(fId);
        vLayer.removeFeatures([feature]);

        // Remove from Jaffa
        rowElement.find(".delete-item").click();
        // Stop bubbling
        return false;
    }

    if ((layers == "google" || layers == "both") && $("#google-api-key").size() != 1) {
        alert("You need to provide a Google API key and connect to Google before the map will work.");
    } else {
        init();
    }
    return rbMapMethods;
}
