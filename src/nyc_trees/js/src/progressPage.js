"use strict";

var $ = require('jquery'),
    zoom = require('./lib/mapUtil').ZOOM,
    L = require('leaflet'),
    mapModule = require('./map'),
    SelectableBlockfaceLayer = require('./lib/SelectableBlockfaceLayer');

require('./lib/mapHelp');

var progressMap = mapModule.create({
        geolocation: true,
        legend: true,
        search: true
    }),
    tileLayer = null,
    selectedLayer = null,
    geojsonLayer = null,

    dom = {
        modeDropdown: '.dropdown',
        modeButton: '.btn',
        modeChoice: '.dropdown li a',
        legendEntries: '[data-mode]',
        actionBar: '#action-bar'
    },
    $actionBar = $(dom.actionBar),
    $mode = null;

$(dom.modeChoice).click(onModeChanged);

// The progress page does not have a grid, so we set a pointer
// cursor to indicate that a click/tap will do something no
// matter where you click/tap.
$('.leaflet-container').css('cursor', 'pointer');

loadLayers($(dom.modeChoice).first());

function onModeChanged(e) {
    e.preventDefault();
    if ($mode !== null && $mode[0] === e.currentTarget) {
        return;
    }
    $mode = $(e.currentTarget);

    // Shown chosen mode on dropdown button
    $mode.parents(dom.modeDropdown).find(dom.modeButton).text($mode.text());

    // Show appropriate legend entries
    var mode = $mode.attr('href').slice(1);  // strip leading #
    $(dom.legendEntries).addClass('hidden');
    $('[data-mode=' + mode + ']').removeClass('hidden');

    loadLayers($mode);
}

function loadLayers($mode) {
    var tileUrl = $mode.data('tile-url'),
        geojsonUrl = $mode.data('geojson-url'),
        bounds = $mode.data('bounds');

    // Clear action bar
    $actionBar.empty();
    $('body').removeClass('actionbar-triggered');

    // Replace layers
    if (tileLayer) {
        progressMap.removeLayer(tileLayer);
    }
    if (selectedLayer) {
        progressMap.removeLayer(selectedLayer);
    }
    if (geojsonLayer) {
        progressMap.removeLayer(geojsonLayer);
    }
    if (tileUrl) {
        tileLayer = mapModule.addTileLayer(progressMap, tileUrl);

        createSelectableLayer();

        if (bounds) {
            mapModule.fitBounds(progressMap, bounds);
        }
    }
    if (geojsonUrl) {
        $.getJSON(geojsonUrl, function(geojson) {
            geojsonLayer = L.geoJson(geojson, {
                style: function() {
                    return {
                        color: '#36b5db',
                        weight: 3,
                    };
                },
                onEachFeature: function(feature, layer) {
                    layer.on('click', function showGroupBlockfaces() {
                        progressMap.removeLayer(tileLayer);

                        tileLayer = mapModule.addTileLayer(progressMap, feature.properties.tileUrl);

                        createSelectableLayer();

                        mapModule.fitBounds(progressMap, feature.properties.bounds);
                        $actionBar.load(feature.properties.popupUrl);
                        $('body').addClass('actionbar-triggered');
                    });
                }
            });
            geojsonLayer.addTo(progressMap);
        });
    }
}

function createSelectableLayer() {
    selectedLayer = new SelectableBlockfaceLayer(progressMap, null, {
        onAdd: function() { return true; }, // Always try and fetch the feature
        onAdded: function(feature, layer) {
            selectedLayer.clearLayers();

            // Note: this must be kept in sync with
            // src/nyc_trees/apps/survey/urls/blockface.py
            var url = '/blockedge/' + feature.properties.id + '/progress-page-blockedge-popup/';

            $actionBar.load(url);
            $('body').addClass('actionbar-triggered');
            return true;
        }
    });
    progressMap.addLayer(selectedLayer);
}
