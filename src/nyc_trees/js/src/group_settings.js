"use strict";

require('./event_list');

var $ = require('jquery'),
    U = require('./utils');

var dom = {
    copyEventUrl: '.js-copy-event-url'
};

$(dom.copyEventUrl).click(function (e) {
    var eventUrl = $(e.target).data('event-url');
    U.copyToClipboard(eventUrl);
});

