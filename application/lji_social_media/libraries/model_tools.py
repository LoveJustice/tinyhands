import joblib
import datetime
import uuid


def generate_unique_filename(prefix="model", extension="pkl"):
    """
    Generate a unique filename using a prefix and extension.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    random_string = uuid.uuid4().hex[:6]
    filename = f"{prefix}_{timestamp}_{random_string}.{extension}"
    return filename


def save_model(model, filename):
    """
    Save the trained model to disk.
    """
    joblib.dump(model, filename)
    print(f"Model saved as {filename}")


def load_model(filename):
    """
    Load a saved model from disk.
    """
    model = joblib.load(filename)
    print(f"Model loaded from {filename}")
    return model
