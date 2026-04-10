from facenet_pytorch import MTCNN
from PIL import Image
from torchvision import transforms
import torch
import io
import os
import tempfile
import base64

# device
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Face detector
# keep_all=False ensures we only keep a single face crop per image.
mtcnn = MTCNN(
    image_size=224,
    margin=20,
    keep_all=False,
    device=device,
    post_process=True,
)

# Inference transform must match the new vision model input format:
# RGB 224x224 -> ToTensor -> ImageNet normalization.
inference_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


def _load_image(image_input):
    """Load supported image input types into an RGB PIL image."""
    if isinstance(image_input, bytes):
        return Image.open(io.BytesIO(image_input)).convert("RGB")
    if isinstance(image_input, (str, os.PathLike)):
        return Image.open(image_input).convert("RGB")
    if isinstance(image_input, Image.Image):
        return image_input.convert("RGB")
    raise ValueError(f"Unsupported image input type: {type(image_input)}")


def _extract_face_pil(image_input):
    """Detect one face and return a stable 224x224 RGB crop from original pixels."""
    img = _load_image(image_input)

    boxes, probs = mtcnn.detect(img)
    if boxes is None or len(boxes) == 0:
        raise ValueError("No face detected.")

    # Pick the highest-confidence face, then crop from the original image.
    best_idx = int(probs.argmax()) if probs is not None else 0
    x1, y1, x2, y2 = boxes[best_idx]

    # Add a small context margin around detected face for robustness.
    w = x2 - x1
    h = y2 - y1
    margin = 0.10
    x1 -= w * margin
    y1 -= h * margin
    x2 += w * margin
    y2 += h * margin

    # Clamp to image bounds.
    img_w, img_h = img.size
    x1 = max(0, int(round(x1)))
    y1 = max(0, int(round(y1)))
    x2 = min(img_w, int(round(x2)))
    y2 = min(img_h, int(round(y2)))

    if x2 <= x1 or y2 <= y1:
        raise ValueError("No face detected.")

    face_img = img.crop((x1, y1, x2, y2)).resize((224, 224), Image.BILINEAR)
    return face_img

def preprocess_image(image_input):
    """
    Preprocess image for emotion detection model.
    Detects face, keeps only face-containing inputs, and outputs normalized tensor.
    
    Args:
        image_input: Can be either:
            - str/path: Path to image file
            - bytes: Raw image bytes
            - PIL Image: PIL Image object
    
    Returns:
        torch.Tensor: Preprocessed face tensor of shape (1, 3, 224, 224)
    """
    face_pil = _extract_face_pil(image_input)

    # Apply model inference transform (RGB + normalization)
    face_tensor = inference_transform(face_pil)
    
    # Add batch dimension
    face_tensor = face_tensor.unsqueeze(0)

    return face_tensor.to(device)


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
    # Save a natural-looking face crop for external APIs/UI.
    face_img = _extract_face_pil(image_input)
    
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
    # Return natural face crop for preview/API while preserving face-only filtering.
    face_img = _extract_face_pil(image_input)
    
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