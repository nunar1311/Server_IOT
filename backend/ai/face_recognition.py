# ============================================================
# AI-Guardian - Face Recognition Module
# Nhan dien khuon mat (placeholder cho integration)
# ============================================================

from typing import Dict, Any, List, Optional
import base64
import numpy as np

class FaceRecognizer:
    """
    Nhan dien khuon mat tu hinh anh ESP32-CAM.
    Placeholder - can tich hop MTCNN/FaceNet/OpenCV DNN.
    """

    def __init__(self):
        self._known_faces: List[Dict] = []
        self._recognition_enabled = False

    def enable_recognition(self, known_faces: List[Dict] = None):
        """
        Kich hoat nhan dien voi danh sach khuon mat da biet.
        Format: [{"name": str, "embedding": np.array}]
        """
        if known_faces:
            self._known_faces = known_faces
        self._recognition_enabled = True

    def disable_recognition(self):
        self._recognition_enabled = False

    def process_frame(self, frame_data: bytes) -> Dict[str, Any]:
        """
        Xu ly mot frame tu camera.
        Tra ve ket qua nhan dien.
        """
        if not self._recognition_enabled:
            return {"recognized": False, "faces": [], "count": 0}

        # =========================================================
        # PLACEHOLDER: Replace with actual face detection model.
        # Integration options:
        #   1. MTCNN + FaceNet embeddings (most accurate)
        #   2. OpenCV DNN face detection + embedding
        #   3. face_recognition library (dlib-based)
        #   4. ONNX model (best performance)
        #
        # Example with face_recognition:
        #   image = face_recognition.load_image_file(frame_data)
        #   face_locations = face_recognition.face_locations(image)
        #   face_encodings = face_recognition.face_encodings(image, face_locations)
        #   for encoding in face_encodings:
        #       matches = face_recognition.compare_faces(
        #           [f["embedding"] for f in self._known_faces], encoding)
        # =========================================================

        return {
            "recognized": False,
            "faces": [],
            "count": 0,
            "note": "Placeholder - integrate MTCNN/FaceNet/OpenCV DNN for production"
        }

    def add_known_face(self, name: str, embedding: np.ndarray, metadata: Dict = None):
        """Add a known face to the database."""
        self._known_faces.append({
            "name": name,
            "embedding": embedding,
            "metadata": metadata or {},
            "added_at": "now"
        })

    def recognize(self, frame_data: bytes) -> Optional[str]:
        """Recognize a face from frame data. Returns name or None."""
        result = self.process_frame(frame_data)
        if result["faces"]:
            return result["faces"][0].get("name")
        return None


_recognizer: Optional[FaceRecognizer] = None


def get_face_recognizer() -> FaceRecognizer:
    global _recognizer
    if _recognizer is None:
        _recognizer = FaceRecognizer()
    return _recognizer
