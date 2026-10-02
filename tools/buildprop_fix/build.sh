#!/bin/sh
# Construit les zips TWRP : ujc201_buildprop_fix.zip et ujc201_buildprop_restore.zip (dans out/)
set -e
cd "$(dirname "$0")"
mkdir -p out
for d in patch restore; do
	n=ujc201_buildprop_fix; [ $d = restore ] && n=ujc201_buildprop_restore
	rm -f out/$n.zip
	(cd $d && zip -q -X -r ../out/$n.zip META-INF)
	echo "out/$n.zip"
done
