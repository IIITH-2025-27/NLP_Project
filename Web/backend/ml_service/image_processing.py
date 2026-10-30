"""
Face extraction for image emotion detection.

MTCNN face detection runs on the ML Utils Space (Web/ml_space) so the API server
doesn't need torch. Output is unchanged: the highest-confidence face with a 10%
margin, resized to a 224x224 RGB PNG.
"""
import base64
import os
import tempfile

from gradio_client import handle_file

from constants import GRADIO_FACE_API_NAME
from .ml_utils_client import get_ml_utils_client


def _extract_face_file(image_input):
    """Send the image to the Space and return the local path of the face crop PNG."""
    tmp_path = None
    if isinstance(image_input, bytes):
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.img')
        tmp_file.write(image_input)
        tmp_file.close()
        tmp_path = image_input = tmp_file.name
    elif not isinstance(image_input, (str, os.PathLike)):
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    try:
        return get_ml_utils_client().predict(
            handle_file(str(image_input)),
            api_name=GRADIO_FACE_API_NAME,
        )
    except Exception as e:
        if "No face detected" in str(e):
            raise ValueError("No face detected.") from e
        raise
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def preprocess_and_get_base64(image_input):
    """
    Extract the face crop and return it as a file (for the emotion API) and base64 (for UI).

    Args:
        image_input: Raw image bytes or a path to an image file

    Returns:
        tuple: (preprocessed_image_path, base64_data_url)

    Raises:
        ValueError: "No face detected." if the Space finds no face
    """
    face_path = _extract_face_file(image_input)

    with open(face_path, 'rb') as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    return face_path, f"data:image/png;base64,{img_base64}"
