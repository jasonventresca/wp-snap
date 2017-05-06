#! /bin/bash
set -eu

# TODO - To run this under cron, first replace all executables with absolute paths (e.g. tar -> /usr/bin/tar)

MYSQL_CREDS='-u root --password=YOUR_PASSWORD'
WP_DBS_DUMP_FILE="$HOME/sql_dump.sql"

echo "Dumping MySQL databases..."
mysqldump --all-databases $MYSQL_CREDS >$WP_DBS_DUMP_FILE

echo "Archiving public_html directory..."
rm -f public_html.tar.gz
tar cf public_html{.tar,}
gzip -f public_html.tar

echo "Please copy the backup files to Google Drive or somewhere safe:"
for bak_file in public_html.tar.gz $WP_DBS_DUMP_FILE ; do
    echo "    $(ls -lh $bak_file)"
done

echo
echo "Thanks, bye :)"
