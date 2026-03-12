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
## For Text to Emotion    

 A Hugging Face pre built model(roberta) used.
 ```bash
 https://huggingface.co/SamLowe/roberta-base-go_emotions
 ```

## For Image preprocessing

**MTCNN** (Multi-task Cascaded Convolutional Network) is used to detect and extract faces from uploaded images.  
The cropped face is resized and fed into the ResNet50-based emotion recognition model.
used throug library(from facenet_pytorch import MTCNN)

## For Image to Emotion
above trained model (accurracy : 67%) on Resnet50 deplyed on huggingface.
```bash
Model 
https://huggingface.co/IIITH-25-27/resnet50_image_to_emotion_acc_67

Deployed URL 
https://huggingface.co/spaces/IIITH-25-27/LyricMind_Models
```

