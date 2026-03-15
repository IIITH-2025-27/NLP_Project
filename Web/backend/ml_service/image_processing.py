from facenet_pytorch import MTCNN
from PIL import Image
from torchvision import transforms
import torch
import io
import os
import tempfile
import numpy as np
import base64

# device
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Face detector
mtcnn = MTCNN(keep_all=False, device=device)

# Transform for ResNet
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

def preprocess_image(image_input):
    """
    Preprocess image for emotion detection model.
    Detects face, crops, and resizes to 224x224.
    
    Args:
        image_input: Can be either:
            - str/path: Path to image file
            - bytes: Raw image bytes
            - PIL Image: PIL Image object
    
    Returns:
        torch.Tensor: Preprocessed face tensor of shape (1, 3, 224, 224)
    """
    # Handle different input types
    if isinstance(image_input, bytes):
        img = Image.open(io.BytesIO(image_input)).convert("RGB")
    elif isinstance(image_input, (str, os.PathLike)):
        img = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    # Detect and crop face
    face = mtcnn(img)

    if face is None:
        # Raise error if no face detected
        raise ValueError("No face detected in the image. Please provide an image with a clear, visible face.")
    
    # face is already a tensor from MTCNN, just need to ensure it's in right format
    # Ensure batch dimension
    if face.dim() == 3:
        face = face.unsqueeze(0)

    return face


def preprocess_and_save_image(image_input, output_path=None):
    """
    Preprocess image and save it to disk for use with external APIs.
    Returns path to the saved preprocessed image.
    
    Args:
        image_input: Can be bytes, path, or PIL Image
        output_path: Optional path to save the preprocessed image.
                    If None, creates a temporary file.
    
    Returns:
        str: Path to the saved preprocessed image
    """
    # Get preprocessed face tensor
    face_tensor = preprocess_image(image_input)
    
    # Convert tensor back to PIL Image (denormalize and convert to uint8)
    # face_tensor shape: (1, 3, 224, 224)
    face_np = face_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
    
    # Denormalize if needed (scale back to 0-255)
    if face_np.max() <= 1.0:
        face_np = (face_np * 255).astype(np.uint8)
    else:
        face_np = face_np.astype(np.uint8)
    
    # Convert to PIL Image
    face_img = Image.fromarray(face_np)
    
    # Save to output path or temp file
    if output_path is None:
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        output_path = tmp_file.name
        tmp_file.close()
    
    face_img.save(output_path, format='PNG')
    
    return output_path


def preprocess_and_get_base64(image_input):
    """
    Preprocess image and return it as base64 string for displaying in UI.
    
    Args:
        image_input: Can be bytes, path, or PIL Image
    
    Returns:
        tuple: (preprocessed_image_path, base64_string)
    """
    # Get preprocessed face tensor
    face_tensor = preprocess_image(image_input)
    
    # Convert tensor back to PIL Image (denormalize and convert to uint8)
    # face_tensor shape: (1, 3, 224, 224)
    face_np = face_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
    
    # Denormalize if needed (scale back to 0-255)
    if face_np.max() <= 1.0:
        face_np = (face_np * 255).astype(np.uint8)
    else:
        face_np = face_np.astype(np.uint8)
    
    # Convert to PIL Image
    face_img = Image.fromarray(face_np)
    
    # Save to temporary file for API
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    tmp_path = tmp_file.name
    tmp_file.close()
    face_img.save(tmp_path, format='PNG')
    
    # Convert to base64 for UI display
    buffer = io.BytesIO()
    face_img.save(buffer, format='PNG')
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')
    
    return tmp_path, f"data:image/png;base64,{img_base64}"