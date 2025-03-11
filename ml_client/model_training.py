import time
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss, accuracy_score
from sklearn.linear_model import SGDClassifier

from metric_aggregator_sdk.dto_models import DeviceSnapshot
from metric_aggregator_sdk.device import Device

class MLDevice(Device):
    """
    A simple device for the ML client. We won't rely on automatic collection;
    instead, we manually send snapshots to the aggregator after each epoch.
    """
    def __init__(self, name: str):
        super().__init__(name)

    def handle_command(self, command: str):
        """
        Respond to commands ["stop", "start", "restart"], or any others.
        """
        print(f"[MLDevice] '{self.name}' received command: {command}")
        if command == "stop":
            print("[MLDevice] Stopping training (demo).")
        elif command == "start":
            print("[MLDevice] Starting training (demo).")
        elif command == "restart":
            print("[MLDevice] Restarting training (demo).")
        else:
            print("[MLDevice] Unknown command.")

    def collect_metrics(self):
        """
        Not used in this manual demo, but required by the abstract base class.
        """
        return DeviceSnapshot(device_name=self.name, metrics={})

def train_model(aggregator, device: MLDevice):
    """
    Trains a simple classifier on the digits dataset, sending metrics manually after each epoch.
    We'll use SGDClassifier with a small learning rate and partial_fit for multiple epochs.
    """
    # Load digits dataset (like MNIST but 8x8).
    digits = load_digits()
    X, y = digits.data, digits.target
    # Simple normalization.
    X = X / 16.0
    
    # Split into training and validation sets.
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # We'll do incremental learning with SGDClassifier.
    model = SGDClassifier(
        loss="log_loss",
        penalty="l2",
        alpha=1e-4,             # regularization strength
        learning_rate="constant",
        eta0=0.001,            # small "learning rate"
        max_iter=1,            # one pass per .partial_fit() call
        shuffle=False,         # keep it deterministic for demo
        random_state=42
    )

    # We need to provide the list of classes when using partial_fit.
    classes = np.unique(y)
    
    epochs = 20
    for epoch in range(1, epochs + 1):
        print(f"\n[Training] Epoch {epoch} starting...")

        # partial_fit updates the model in-place for one pass over the data.
        model.partial_fit(X_train, y_train, classes=classes)

        # Evaluate training and validation sets.
        train_preds = model.predict(X_train)
        val_preds   = model.predict(X_val)
        
        # For log_loss we need probability estimates.
        train_probs = model.predict_proba(X_train)
        val_probs   = model.predict_proba(X_val)
        
        train_loss = log_loss(y_train, train_probs)
        val_loss   = log_loss(y_val,   val_probs)
        train_acc  = accuracy_score(y_train, train_preds)
        val_acc    = accuracy_score(y_val,   val_preds)
        
        print(f"Epoch {epoch} - "
              f"Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, "
              f"Train Acc: {train_acc:.4f}, Val Acc: {val_acc:.4f}")
        
        # Prepare and send metrics snapshot.
        metrics = {
            "Training Loss": train_loss,
            "Validation Loss": val_loss,
            "Training Accuracy": train_acc,
            "Validation Accuracy": val_acc
        }
        snapshot = DeviceSnapshot(device_name=device.name, metrics=metrics)
        aggregator.add_snapshot(snapshot)
        
        # Simulate time between epochs.
        time.sleep(2)
