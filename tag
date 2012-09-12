#!/bin/bash

SOURCE=/home/$USER/aokp/
REVISION=Build-2

for file in `find . | grep .git/config`; do cat $file  | grep projectname | tr -d ' ' | cut -f2 -d = | grep AOKP; done > .tag_list

cat .tag_list | cut -f2 -d '/' | sed 's/android_//g' | sed 's/_/\//g' | sed 's/external\/wpa\/supplicant\/8/external\/wpa_supplicant_8/g' | sed 's/platform\/manifest/platform_manifest/g' > .dir_list

find $SOURCE -name .git -execdir git tag -a $REVISION -m "$REVISION" \;

while read REPO ;do
    cd $SOURCE/$REPO
    pwd
    echo "git push --tags gerrit:/$repo_name" \;
done < .dir_list
rm $SOURCE/.dir_list $SOURCE/.tag_list
