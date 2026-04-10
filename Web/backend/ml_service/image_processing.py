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
# Keep raw pixel output (no post-process normalization) so downstream
# preprocessing and UI previews use stable, natural-looking intensities.
mtcnn = MTCNN(keep_all=False, device=device, post_process=False)

# Transform for ResNet - MUST match training pipeline exactly
# Training used: Resize -> Grayscale -> ToTensor -> Normalize
inference_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),  # CRITICAL: Convert to 3-channel grayscale like training
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],  # ImageNet normalization
        std=[0.229, 0.224, 0.225]
    )
])

def preprocess_image(image_input):
    """
    Preprocess image for emotion detection model.
    Detects face, crops, and resizes to 224x224.
    CRITICAL: Applies grayscale conversion to match training pipeline.
    
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
    
    # Convert MTCNN tensor output back to PIL Image for proper transforms.
    # Depending on MTCNN settings/version, values can be in [-1, 1], [0, 1], or [0, 255].
    face_np = face.permute(1, 2, 0).cpu().numpy().astype(np.float32)

    min_val = float(face_np.min())
    max_val = float(face_np.max())

    if min_val >= -1.1 and max_val <= 1.1:
        # Likely normalized range [-1, 1] or [0, 1]
        if min_val < 0:
            face_np = (face_np + 1.0) / 2.0
        face_np = np.clip(face_np * 255.0, 0, 255)
    else:
        # Likely raw pixel range [0, 255]
        face_np = np.clip(face_np, 0, 255)

    face_np = face_np.astype(np.uint8)
    face_pil = Image.fromarray(face_np)
    
    # Apply the inference transform (grayscale + normalization to match training)
    face_tensor = inference_transform(face_pil)
    
    # Add batch dimension
    face_tensor = face_tensor.unsqueeze(0)

    return face_tensor


def preprocess_and_save_image(image_input, output_path=None):
    """
    Preprocess image and save it to disk for use with external APIs.
    Returns path to the saved preprocessed image.
    NOTE: Saves the **denormalized** version for API consumption
    
    Args:
        image_input: Can be bytes, path, or PIL Image
        output_path: Optional path to save the preprocessed image.
                    If None, creates a temporary file.
    
    Returns:
        str: Path to the saved preprocessed image
    """
    # Get preprocessed face tensor from inference_transform (already normalized)
    face_tensor = preprocess_image(image_input)
    
    # Denormalize for saving/API (reverse ImageNet normalization)
    # face_tensor shape: (1, 3, 224, 224), already normalized
    face = face_tensor.squeeze(0)  # (3, 224, 224)
    
    # Reverse normalization
    denorm_means = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    denorm_stds = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    face = (face * denorm_stds + denorm_means)
    
    # Convert to numpy and PIL
    face_np = face.permute(1, 2, 0).cpu().numpy()
    
    # Scale to 0-255
    if face_np.max() <= 1.0:
        face_np = (face_np * 255).astype(np.uint8)
    else:
        face_np = np.clip(face_np, 0, 255).astype(np.uint8)
    
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
    NOTE: Returns the **denormalized** version for proper display
    
    Args:
        image_input: Can be bytes, path, or PIL Image
    
    Returns:
        tuple: (preprocessed_image_path, base64_string)
    """
    # Get preprocessed face tensor from inference_transform (already normalized)
    face_tensor = preprocess_image(image_input)
    
    # Denormalize for display/API (reverse ImageNet normalization)
    # face_tensor shape: (1, 3, 224, 224), already normalized
    face = face_tensor.squeeze(0)  # (3, 224, 224)
    
    # Reverse normalization
    denorm_means = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    denorm_stds = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    face = (face * denorm_stds + denorm_means)
    
    # Convert to numpy
    face_np = face.permute(1, 2, 0).cpu().numpy()
    
    # Scale to 0-255
    if face_np.max() <= 1.0:
        face_np = (face_np * 255).astype(np.uint8)
    else:
        face_np = np.clip(face_np, 0, 255).astype(np.uint8)
    
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
