## test frontend model

with 9.pt


### Query commands

```sh
egrep 'learning_rate|iph' _logs/exp_v{14..25}.log
```

### polyphone test

`321/321 [01:03<00:00,  5.08it/s]`

Accuracy: 0.9714257717132568

### prosody test

`[00:03<00:00,  8.87it/s]`

pw f1_score 0.9416129032258065 pph f1_score 0.8078595587051055 iph f1_score 0.8355376653248994


## Docker image

* gl8_tts:devel

## Caveats

* install dependencies

    ```
    transformers==4.22.2
    onnxruntime>=1.12.1
    scikit-learn  # sklearn
    WeTextProcessing==0.0.6
    ```

