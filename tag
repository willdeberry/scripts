#!/bin/bash

SOURCE=/home/$USER/aokp
REVISION=Build-3

for file in `find . | grep .git/config`; do cat $file  | grep projectname | tr -d ' ' | cut -f2 -d = | grep AOKP; done > .repo_list

cat .repo_list | cut -f2 -d '/' | sed 's/android_//g' | sed 's/_/\//g' | sed 's/external\/wpa\/supplicant\/8/external\/wpa_supplicant_8/g' | sed 's/platform\/manifest/platform_manifest/g' | sed 's/platform\/dalvik/dalvik/g' | sed 's/platform\/development/development/g' | sed 's/input\/LatinIME/inputmethods\/LatinIME/g' | sed 's/SwagPapers\/v2/SwagPapers/g' | sed 's/pseudo\/buildbot/vendor\/aokp\/bot/g' | sed 's/themes-platform-vendor-tmobile-apps-ThemeChooser/vendor\/tmobile\/apps\/ThemeChooser/g' > .dir_list

exec 11<.dir_list
exec 12<.repo_list

find $SOURCE -name .git -execdir git tag -a $REVISION -m "$REVISION" \;

while read -u 11 DIR && read -u 12 REPO_DIR ;do
    cd $SOURCE/$DIR
    git push gerrit:/$REPO_DIR $REVISION
done

exec 11<&- 12<&-
rm $SOURCE/.dir_list $SOURCE/.repo_list
