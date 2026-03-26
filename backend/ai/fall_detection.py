# ============================================================
# AI-Guardian - Fall Detection Module
# Phat hien nguoi bi nga tu hinh anh camera
# ============================================================

from typing import Dict, Any, Optional, List
import numpy as np

class FallDetector:
    """
    Phat hien nguoi bi nga bang cach phan tich tu the (pose estimation).
    Placeholder - can tich hop PoseNet/MoveNet/Mediapipe.
    """

    def __init__(self):
        self._history: List[Dict] = []
        self._max_history = 30

    def analyze_pose(self, keypoints: Dict[str, tuple]) -> Dict[str, Any]:
        """
        Phan tich tu the nguoi tu keypoints.
        keypoints: dict of {name: (x, y, confidence)}

        Returns fall detection result.
        """
        # =========================================================
        # PLACEHOLDER: Replace with actual pose estimation.
        # Integration options:
        #   1. MediaPipe Pose (Google) - fast, accurate
        #   2. MoveNet (TF Lite) - lightweight
        #   3. PoseNet (TensorFlow.js) - browser-based
        #   4. OpenPose (CMU) - most accurate but heavy
        #
        # Key fall indicators:
        #   - Head position drops rapidly
        #   - Body angle exceeds 60 degrees from vertical
        #   - Person motionless on ground for >threshold seconds
        # =========================================================

        self._history.append(keypoints)
        if len(self._history) > self._max_history:
            self._history.pop(0)

        if len(self._history) < 5:
            return {"detected": False, "confidence": 0, "type": None}

        # Simple heuristic: check head height relative to body
        # In production, use proper pose estimation output
        head_y = keypoints.get("nose", (0, 0, 0))[1]
        shoulder_y = keypoints.get("left_shoulder", (0, 0, 0))[1]

        if head_y == 0 or shoulder_y == 0:
            return {"detected": False, "confidence": 0, "type": None}

        body_length = abs(
            keypoints.get("left_shoulder", (0, 0, 0))[1] -
            keypoints.get("left_hip", (0, 0, 0))[1]
        )

        if body_length < 10:
            return {"detected": True, "confidence": 0.85, "type": "person_on_ground"}

        return {"detected": False, "confidence": 0, "type": None}

    def evaluate_frame(self, frame_data: bytes) -> Dict[str, Any]:
        """
        Evaluate a camera frame for fall detection.
        Returns detection result.
        """
        # =========================================================
        # In production, run pose estimation on the frame:
        #
        # with MediaPipe:
        #   with mp_pose.Pose(static_image_mode=False) as pose:
        #       results = pose.process(frame_data)
        #       keypoints = extract_keypoints(results)
        #       return self.analyze_pose(keypoints)
        # =========================================================

        return {
            "detected": False,
            "confidence": 0.0,
            "type": None,
            "note": "Integrate MediaPipe/MoveNet for production use"
        }

    def get_fall_trajectory(self) -> Optional[Dict]:
        """Analyze the trajectory of a detected fall."""
        if len(self._history) < 10:
            return None

        head_positions = []
        for h in self._history[-10:]:
            nose = h.get("nose", (0, 0))
            head_positions.append((nose[0], nose[1]))

        if all(p[0] == 0 for p in head_positions):
            return None

        return {
            "start_position": head_positions[0],
            "end_position": head_positions[-1],
            "duration_frames": len(head_positions),
            "dropped": head_positions[-1][1] > head_positions[0][1] + 50
        }


_detector: Optional[FallDetector] = None


def get_fall_detector() -> FallDetector:
    global _detector
    if _detector is None:
        _detector = FallDetector()
    return _detector
