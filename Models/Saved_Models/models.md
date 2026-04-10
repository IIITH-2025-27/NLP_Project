# Saved Models

## Model : Text to Emotion [Pre-built]

 A Hugging Face pre built model(roberta) used.
 ```bash
 https://huggingface.co/SamLowe/roberta-base-go_emotions
 ```

## For Image preprocessing

Currently used preprocessing: detect the highest-confidence face with MTCNN(Multi-task Cascaded Convolutional Network), crop from original RGB image (with margin), resize to 224x224, normalize using ImageNet mean/std, and reject inputs where no face is detected.

## Model : Image to Emotion
Below trained model (accurracy : 89%) on densenet_121 deplyed on huggingface.
```bash
Model 
https://huggingface.co/IIITH-25-27/Image_to_emotion_model

Deployed URL 
https://huggingface.co/spaces/IIITH-25-27/image_to_emotion
```

## Model : Emotion to Lyrics
Below trained model deplyed on huggingface.
```bash
Model 
https://huggingface.co/IIITH-25-27/Emotion_to_lyrics_model

Deployed URL 
https://huggingface.co/spaces/IIITH-25-27/lyrics_Generator_for_emotion
```

