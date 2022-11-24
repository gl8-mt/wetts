#!/bin/bash

set -e

# path/to/txt/files
sdir=${1-_output/eval_domain_inv}

# [0] text => prosody text
for x in ${sdir}/raw/eval_domain_*.txt; do
	ddir=${sdir}/prosody
	mkdir -p ${ddir}
	echo $x; python ./frontend_cli.py $x --with_id True > ${ddir}/$(basename $x .txt).txt;
done

# [1] prosody text => prosody tuned text
for x in ${sdir}/prosody/*.txt; do
	ddir=${sdir}/prosody_tuned
	mkdir -p ${ddir}
	echo === $x ===;  python3 _my/rhy_postprocess.py --sep ' ' $x >  ${ddir}/$(basename $x);
done
