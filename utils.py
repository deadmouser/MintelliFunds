import torch

def save_model(model, path):
    """
    Saves a PyTorch model to a file.

    Args:
        model (torch.nn.Module): The model to save.
        path (str): The path to save the model to.
    """
    torch.save(model.state_dict(), path)
    print(f"Model saved to {path}")

def load_model(model, path):
    """
    Loads a PyTorch model from a file.

    Args:
        model (torch.nn.Module): The model architecture.
        path (str): The path to the saved model.

    Returns:
        torch.nn.Module: The loaded model.
    """
    model.load_state_dict(torch.load(path))
    print(f"Model loaded from {path}")
    return model
