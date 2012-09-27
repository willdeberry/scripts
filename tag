#!/bin/bash

SOURCE=/home/$USER/aokp
REVISION=Build-3

grep AOKP/ .repo/manifest.xml | cut -f4 -d '"' > $SOURCE/.repo_list
grep AOKP/ .repo/manifest.xml | cut -f2 -d '"' > $SOURCE/.dir_list

exec 11<.dir_list
exec 12<.repo_list

find $SOURCE -name .git -execdir git tag -a $REVISION -m "$REVISION" \;

while read -u 11 DIR && read -u 12 REPO_DIR ;do
    cd $SOURCE/$DIR
    git push gerrit:/$REPO_DIR $REVISION
done

exec 11<&- 12<&-
rm $SOURCE/.dir_list $SOURCE/.repo_list
