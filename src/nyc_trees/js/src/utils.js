"use strict";

module.exports = {

    copyToClipboard: function (text) {
        var isMac = navigator.platform.toUpperCase().indexOf('MAC') !== -1,
            shortcut = isMac ? 'Cmd+C' : 'Ctrl+C',
            prompt = 'Hit <' + shortcut + '>, <Enter> to copy to clipboard.';
        window.prompt(prompt, text)
    }

}
