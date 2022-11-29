    # -e 's: #1 ::g' \
    # -e 's: #2 : #1 :g' \
    # -e 's: #3 : #2 :g' \
sed -E \
    -e 's: #4 *$::' \
    -e 's: #1 ::g' \
    -e 's: #2 : #1 :g' \
    -e 's: #3 : #2 :g' \
    -e 's: #1 :<break time="sp0"></break>:g' \
    -e 's: #2 :<break time="sp1"></break>:g' \
    -e 's: #3 :<break time="sp2"></break>:g' \
    -e 's:^:<speak>:' \
    -e 's:$:</speak>:' \
    $@
