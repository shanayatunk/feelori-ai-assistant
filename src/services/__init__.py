from .product_training import ProductTrainingService

# This creates a single, shared instance of the service
# that your entire application will use.
training_service = ProductTrainingService()