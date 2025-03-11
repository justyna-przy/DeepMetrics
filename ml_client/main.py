import time
from metric_aggregator_sdk.aggregator_api import AggregatorAPI
from model_training import train_model, MLDevice

def main():
    aggregator = AggregatorAPI(
        guid="87d05269-f12a-45e9-9b98-4868eef4b5c6",
        name="Model Training Aggregator",
        logger=None  
    )
    
    ml_device = MLDevice("MNIST Training Device")
    
    # Register the device with the aggregator.
    aggregator.register_device(ml_device)
    
    # Start the aggregator thread.
    aggregator.start()
    
    try:
        # Start training; after each epoch metrics will be sent manually.
        train_model(aggregator, ml_device)
    except KeyboardInterrupt:
        print("Training interrupted by user.")
    finally:
        aggregator.stop()
        print("Aggregator stopped.")

if __name__ == "__main__":
    main()
