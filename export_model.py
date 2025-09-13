#!/usr/bin/env python3
"""
Export the trained model to TorchScript format for C++ inference
"""

import torch
from loguru import logger
from model import FinancialAdvisorModel

def export_model():
    """Export the best trained model to TorchScript format"""
    logger.info("🔄 Loading best model checkpoint...")
    
    # Load the best model checkpoint
    try:
        checkpoint = torch.load('models/best_model.pth', map_location='cpu', weights_only=False)
        logger.info(f"Loaded checkpoint from epoch {checkpoint['epoch']} with val loss: {checkpoint['val_loss']:.6f}")
    except FileNotFoundError:
        logger.error("No checkpoint found at models/best_model.pth")
        return False
    
    # Initialize model with same architecture
    model = FinancialAdvisorModel(input_size=16)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    logger.info(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Export to TorchScript using scripting (supports dict outputs)
    logger.info("📦 Exporting model to TorchScript format...")
    try:
        scripted_model = torch.jit.script(model)
        scripted_model.save('financial_model.pt')
        logger.info("✅ TorchScript model saved to financial_model.pt")
        
        # Also save the final PyTorch checkpoint for future use
        torch.save({
            'model_state_dict': model.state_dict(),
            'input_size': 16,
            'epoch': checkpoint['epoch'],
            'val_loss': checkpoint['val_loss']
        }, 'financial_model_final.pth')
        logger.info("✅ Final PyTorch checkpoint saved to financial_model_final.pth")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to export TorchScript model: {e}")
        return False

if __name__ == "__main__":
    success = export_model()
    if success:
        logger.info("🎉 Model export completed successfully!")
    else:
        logger.error("❌ Model export failed!")
        exit(1)