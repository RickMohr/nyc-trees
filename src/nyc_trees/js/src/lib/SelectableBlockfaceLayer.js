"use strict";

var $ = require('jquery'),
    L = require('leaflet'),
    BlockfaceLayer = require('./BlockfaceLayer'),
    mapUtil = require('./mapUtil'),
    zoom = require('./mapUtil').ZOOM,

    // If you change this color, also change src/nyc_trees/sass/partials/_legend.scss
    color = '#FFEB3B';

/* Adds a geojson layer to the given map.
 *
 * Geojson fatures are added to the map when their corresponding
 * features are clicked in the UtfGrid, and they are removed when the geojson
 * feature is clicked.
 *
 * Depends on a UtfGrid with an "id" property. A GeoJSON represention of the
 * selected blockface is fetched via AJAX, using the ID to construct the
 * fetch URL.
 *
 * Accepts two callbacks: onAdd and onRemove, which are called prior to adding
 * or removing geojson features.
 *
 * If the callbacks do not return a truthy value, the feature will not be
 * added/removed.
 *
 */
module.exports = BlockfaceLayer.extend({
    options: {
        onAdd: $.noop,
        onRemove: $.noop,
        onAdded: $.noop,
        color: color
    },

    clicksEnabled: true,

    initialize: function(map, grid, options) {
        BlockfaceLayer.prototype.initialize.call(this, map, options);

        var self = this;

        this.options.onEachFeature = function(feature, layer) {
            self.options.onAdded(feature, layer);
            layer.on('click', function() {
                if (self.clicksEnabled && self.options.onRemove(feature)) {
                    self.removeLayer(layer);
                }
            });
        };

        grid.on('click', function(e) {
            if (self.clicksEnabled) {
                self.addBlockface(e.data, e.latlng);
            }
        });
    },

    addBlockface: function(data, latlng) {
        var self = this;
        if (!data || !data.id) {
            return;
        }
        if (self.options.onAdd(data, latlng)) {
            mapUtil.fetchBlockface(data.id).then(function(blockfaceData) {
                if (blockfaceData && blockfaceData.geojson) {
                    var geom = mapUtil.parseGeoJSON(blockfaceData.geojson);
                    self.addData({
                        "type": "Feature",
                        "geometry": geom,
                        "properties": data
                    });
                }
            });
        }
    }
});
