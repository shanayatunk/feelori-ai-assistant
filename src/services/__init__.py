# src/services/__init__.py
from .product_training import ProductTrainingService

# This creates one shared instance of the service for the whole app.
training_service = ProductTrainingService()