#! /bin/bash
set -eu

# TODO - To run this under cron, first replace all executables with absolute paths (e.g. tar -> /usr/bin/tar)

# TODO - the two variables should be sourced into the environment
MYSQL_USER='YOUR_USERNAME'
MYSQL_PASS='YOUR_PASSWORD'
SQL_DUMP_FILE="$HOME/sql_dump.sql"

MYSQL_CREDS="-u ${MYSQL_USER} --password='${MYSQL_PASS}'"

echo "Dumping MySQL databases..."
mysqldump --all-databases $MYSQL_CREDS >$SQL_DUMP_FILE

echo "Archiving public_html directory..."
rm -f public_html.tar.gz
tar cf public_html{.tar,}
gzip -f public_html.tar

echo "Please copy the backup files to Google Drive or somewhere safe:"
for bak_file in public_html.tar.gz $SQL_DUMP_FILE ; do
    echo "    $(ls -lh $bak_file)"
done

echo
echo "Thanks, bye :)"
