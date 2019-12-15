### Some Reminder if you would like to run the agent

The current stable tensorflow version (2.0 now) has a severe memory leak issue on Model.predict() function. The nightly build has fixed this issue and I recommend to install the nightly version to run the model.

#### install tensorflow

```bash
conda activate [your-envcironement]
pip install tf-nightly
```

or if you prefer to use your gpu

```
pip install tf-nightly-gpu
```

There is no obvious performance difference between the cpu and gpu version.

#### run the program

File **SHTrain.py** is for the training process. In every training episode it will save current model and its weights in **model-saved** directory.

File **SHExecute.py** is for presenting a trained model. It will load a saved model from **model-saved** directory and run.  To change the loaded model , change the line in file:

```
line 50 agent_net = models.load_model("./model-saved/0.h5")
```