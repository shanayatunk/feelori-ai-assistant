from .product_training import ProductTrainingService

# Create a single, shared instance of the training service
# that the entire application will use.
training_service = ProductTrainingService()