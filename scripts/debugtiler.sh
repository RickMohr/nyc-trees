#!/bin/bash

set -e
set -x

vagrant ssh tiler -c "sudo service nyc-trees-tiler stop || /bin/true"
vagrant ssh tiler -c "cd /opt/tiler/ && npm run watch"
