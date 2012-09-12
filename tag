#!/bin/bash

SOURCE=/home/$USER/aokp/
REVISION=Build-2

for file in `find . | grep .git/config`; do cat $file  | grep projectname | tr -d ' ' | cut -f2 -d = | grep AOKP; done > .repo_list

cat .repo_list | cut -f2 -d '/' | sed 's/android_//g' | sed 's/_/\//g' | sed 's/external\/wpa\/supplicant\/8/external\/wpa_supplicant_8/g' | sed 's/platform\/manifest/platform_manifest/g' > .dir_list

exec 11<.dir_list
exec 12<.repo_list

find $SOURCE -name .git -execdir git tag -a $REVISION -m "$REVISION" \;

while read -u 11 DIR && read -u 12 REPO_DIR ;do
    cd $SOURCE/$DIR
    pwd
    echo "git push --tags gerrit:/$REPO_DIR"
done

exec 11<&- 12<&-
rm $SOURCE/.dir_list $SOURCE/.repo_list
