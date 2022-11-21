#!/bin/bash

set -e

# path/to/txt/files
sdir=${1-_output/eval_domain_inv}
root_dir=${2-_dump/audio/eval_domain_inv}

# [0] text => audio
for x in ${sdir}/raw/eval_domain_*.txt; do
	bn=$(basename $x .txt)
	ddir=${root_dir}/${bn}/raw
	mkdir -p ${ddir}

	echo "$x => $ddir";
	# python3 ./_my/run_tts_http.py --has_prosody False $x ${ddir};
done

# [1] prosody text => audio
for x in ${sdir}/prosody_tuned/*.txt; do
	bn=$(basename $x .txt)
	ddir=${root_dir}/${bn}/prosody_tuned
	mkdir -p ${ddir}

	echo "$x => $ddir";
	# python3 ./_my/run_tts_http.py $x ${ddir};
	
	cp "$x" "$ddir/../text.txt"  # copy text
done
