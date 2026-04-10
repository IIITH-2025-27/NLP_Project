# Saved Models


## Vision to Emotion Models

## On Kaggle
```bash
https://www.kaggle.com/datasets/hritik567/fer-hypertuning-checkpoints
```
## On Google Drive
```bash
https://drive.google.com/drive/folders/1amWTLh-jdjT_Hg1m_IgyjQzHdwAadYAf?usp=sharing
```

---
## Model : Text to Emotion [Pre-built]

 A Hugging Face pre built model(roberta) used.
 ```bash
 https://huggingface.co/SamLowe/roberta-base-go_emotions
 ```

## For Image preprocessing

**MTCNN** (Multi-task Cascaded Convolutional Network) is used to detect and extract faces from uploaded images.  
The cropped face is resized and fed into the ResNet50-based emotion recognition model.
used throug library(from facenet_pytorch import MTCNN)

## Model : Image to Emotion
Below trained model (accurracy : 67%) on Resnet50 deplyed on huggingface.
```bash
Model 
https://huggingface.co/IIITH-25-27/resnet50_image_to_emotion_acc_67

Deployed URL 
https://huggingface.co/spaces/IIITH-25-27/image_to_emotion
```

## Model : Emotion to Lyrics
Below trained model deplyed on huggingface.
```bash
Model 
https://huggingface.co/IIITH-25-27/Spotify_gpt2_medium

Deployed URL 
https://huggingface.co/spaces/IIITH-25-27/lyrics_Generator_for_emotion
```

