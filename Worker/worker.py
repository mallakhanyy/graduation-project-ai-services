"""
Background worker for processing vision predictions asynchronously.
"""

import json
import logging
import time
import os
import uuid          # ✅ أضفت السطر ده
import requests      # ✅ أضفت السطر ده
from datetime import datetime

from Infrastructure.queue_broker import RabbitMQBroker
from Infrastructure.logger import setup_logger
from Core.model import predict_image
from Infrastructure.utils import enhance_image, check_image_quality
from Infrastructure.config import get_settings
from Core.binary_model import is_irrigation_problem  # ✅ أضف السطر ده

# Setup logger
logger = setup_logger("VisionService.Worker")
settings = get_settings()


# ============================================
# ✅ NEW: دالة تحميل الصورة من URL
# ============================================
def download_image(image_url: str, extension: str = "jpg") -> str:
    """
    Download an image from a URL and save it temporarily.

    Args:
        image_url: URL of the image
        extension: File extension (default: jpg)

    Returns:
        Path to the downloaded image
    """
    try:
        logger.info(f"⬇️ Downloading image from: {image_url}")

        response = requests.get(
            image_url,
            timeout=settings.IMAGE_DOWNLOAD_TIMEOUT,
            stream=True
        )
        response.raise_for_status()

        # Ensure extension starts with a dot
        if not extension.startswith("."):
            extension = "." + extension

        temp_path = f"temp_{uuid.uuid4().hex[:8]}{extension}"

        with open(temp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"✅ Image downloaded: {temp_path}")
        return temp_path

    except Exception as e:
        logger.error(f"❌ Failed to download image: {e}")
        raise


def process_prediction(ch, method, properties, body):
    """
    Process a prediction request from the queue.
    
    Args:
        ch: Channel
        method: Method frame
        properties: Properties
        body: Message body
    """
    broker = None
    start_time = time.time()
    request_id = "unknown"       # ✅ أضفت السطر ده
    image_path = None            # ✅ أضفت السطر ده
    
    try:
        # Parse message
        message = json.loads(body)
        request_id = message['request_id']
        image_url = message['image_url']              # ✅ عدلت: بدل image_path
        extension = message.get('extension', 'jpg')   # ✅ أضفت السطر ده
        
        logger.info(f"[{request_id}] Processing started")
        logger.info(f"[{request_id}] Image URL: {image_url}")   # ✅ أضفت السطر ده
        
        # ✅ عدلت: بدل ما يتحقق إن الملف موجود، بيحمله من الـ URL
        image_path = download_image(image_url, extension)
        
        # Optional: Quality check
        if settings.QUALITY_CHECK_ENABLED:
            is_good, quality_msg = check_image_quality(image_path)
            if not is_good:
                logger.warning(f"[{request_id}] Poor quality: {quality_msg}")
        
        # Optional: Enhance image
        image_to_predict = image_path
        if settings.ENHANCE_IMAGE_ENABLED:
            enhanced_path = enhance_image(image_path)
            if enhanced_path != image_path:
                image_to_predict = enhanced_path
                logger.info(f"[{request_id}] Image enhanced")
        
        # ============================================
        # ✅ BINARY CLASSIFIER CHECK (مثل الـ Sync)
        # ============================================
        
        # Check if image is actually an irrigation problem
        is_problem, binary_confidence = is_irrigation_problem(
            image_to_predict, 
            threshold=settings.BINARY_THRESHOLD
        )
        
        logger.info(f"[{request_id}] Binary check: is_problem={is_problem}, confidence={binary_confidence:.2f}")
        
        # If NOT a problem → refuse
        if not is_problem:
            result = {
                "problem_code": "Unknown",
                "problem_arabic": "لا توجد مشكلة",
                "confidence": binary_confidence * 100,
                "severity": "غير معروفة",
                "recommendation": "الصورة لا تظهر مشكلة ري واضحة.",
                "explanation": "لم يتم الكشف عن مشكلة في الري.",
                "repair_steps": []
            }
            prediction_time = time.time() - start_time     # ✅ أضفت السطر ده
            logger.info(f"[{request_id}] Refused: Not an irrigation problem")
        else:
            # Run prediction
            prediction_start = time.time()
            result = predict_image(image_to_predict)
            prediction_time = time.time() - prediction_start
            
            logger.info(f"[{request_id}] Prediction: {result['problem_code']} ({result['confidence']:.2f}%) in {prediction_time:.2f}s")
        
        # Publish result
        broker = RabbitMQBroker()
        broker.publish_result(request_id, result, prediction_time if 'prediction_time' in locals() else 0.5)
        
        # Clean up enhanced image (if created)
        if image_to_predict != image_path and os.path.exists(image_to_predict):
            os.remove(image_to_predict)
            logger.info(f"[{request_id}] Cleaned up enhanced image")
        
        # Acknowledge message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
        total_time = time.time() - start_time
        logger.info(f"[{request_id}] Completed successfully (total: {total_time:.2f}s)")
        
    except Exception as e:
        logger.error(f"[{request_id}] Failed: {e}")
        
        # Publish error result
        try:
            broker = RabbitMQBroker()
            broker.publish_error(request_id, str(e), time.time() - start_time)
        except Exception as pub_error:
            logger.error(f"[{request_id}] Failed to publish error: {pub_error}")
        
        # Reject and requeue for retry
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    finally:
        # ✅ أضفت: تنظيف الصورة المحملة
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                logger.info(f"[{request_id}] Cleaned up downloaded image")
            except Exception as cleanup_error:
                logger.warning(f"[{request_id}] Cleanup failed: {cleanup_error}")
        
        if broker:
            broker.close()

def start_worker():
    """Start the worker to process queue messages."""
    logger.info("=" * 60)
    logger.info("Starting Vision Service Worker...")
    logger.info(f"RabbitMQ Host: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
    logger.info("Waiting for messages...")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    broker = None
    try:
        broker = RabbitMQBroker()
        broker.consume_requests(process_prediction)
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker failed: {e}")
    finally:
        if broker:
            broker.close()

if __name__ == "__main__":
    start_worker()