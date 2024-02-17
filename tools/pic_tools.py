import base64

import cv2


def cv2_to_base64(image) -> str:
    base64_str = cv2.imencode('.jpg', image)[1].tostring()
    base64_str = str(base64.b64encode(base64_str))[2: -1]
    return base64_str
