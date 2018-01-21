#!/bin/bash
set -eu

# Brief:    If you're getting something like
#               ERROR 1273 (HY000) at line 1996: Unknown collation: 'utf8mb4_unicode_520_ci'
#           this script may help. In my case, it seemed to have been caused by exporting a sql dump
#           from MySQL 5.7 and then importing that dump file into MySQL 5.5.
#           Adapted from https://stackoverflow.com/a/42649372

# Usage:    ./fix_encoding_collation_import_errors.sh db_dump.sql

sed -i.bak \
    -e 's/utf8mb4/utf8/g' \
    -e 's/utf8_unicode_ci/utf8_general_ci/g' \
    -e 's/utf8_unicode_520_ci/utf8_general_ci/g' \
    $@

