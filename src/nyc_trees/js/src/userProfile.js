"use strict";

var $ = require('jquery'),
    privacySettings = require('./privacySettings.js'),

    dom = {
        privacyForm: '#privacy-form',
        saveButton: '.js-save',
        cancelButton: '.js-cancel'
    };

$(dom.saveButton).on('click', function (e) {
    privacySettings.prepareForSave();

    var url = $(e.target).data('url'),
        data = $(dom.privacyForm).serialize();
    $.post(url, data);
});

$(dom.cancelButton).on('click', function () {
    privacySettings.revert();
});
