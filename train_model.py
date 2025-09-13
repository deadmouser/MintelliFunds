"""
Advanced Training Pipeline for Financial AI Model

Features:
- Multi-task learning with synthetic target generation
- Data augmentation and validation
- Early stopping and learning rate scheduling
- Model checkpointing and TorchScript export
- Training metrics and visualization
"""

import json
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from typing import Dict, List, Tuple, Any
import random
from loguru import logger

# Import our modules
from model import FinancialAdvisorModel
from data_preprocessing import AdvancedDataPreprocessor, UserPermissions


class FinancialDataset(Dataset):
    """Custom Dataset for financial data"""
    
    def __init__(self, data: List[Dict], preprocessor: AdvancedDataPreprocessor, 
                 permissions: UserPermissions, augment: bool = False):
        self.data = data
        self.preprocessor = preprocessor
        self.permissions = permissions
        self.augment = augment
        self.features = []
        self.targets = []
        
        logger.info(f"Processing {len(data)} samples...")
        self._process_data()
        
    def _process_data(self):
        """Process raw data into features and synthetic targets"""
        for record in self.data:
            # Extract features
            features, metadata = self.preprocessor.preprocess_single_record(record, self.permissions)
            
            # Generate synthetic targets for multi-task learning
            targets = self._generate_targets(record)
            
            self.features.append(features)
            self.targets.append(targets)
        
        # Convert to tensors
        self.features = torch.FloatTensor(self.features)
        self.targets = {key: torch.FloatTensor([t[key] for t in self.targets]) 
                       for key in self.targets[0].keys()}
        
        logger.info(f"Generated {len(self.features)} training samples")
    
    def _generate_targets(self, record: Dict) -> Dict[str, float]:
        """Generate synthetic training targets from financial data"""
        # Calculate derived metrics for training
        total_assets = sum(record['assets'].values())
        total_liabilities = sum(record['liabilities'].values())
        net_worth = total_assets - total_liabilities
        income = record['transactions']['income']
        expenses = record['transactions']['expenses']
        credit_score = record['credit_score']['score']
        
        # Target 1: Savings prediction (monthly savings rate)
        monthly_savings = max(0, income - expenses) / 12 if income > 0 else 0
        savings_rate = monthly_savings / max(income / 12, 1)  # Normalize by monthly income
        
        # Target 2: Anomaly score (0 = normal, 1 = anomalous)
        # Detect anomalies based on unusual ratios
        debt_to_income = total_liabilities / max(income, 1)
        expense_to_income = expenses / max(income, 1)
        anomaly_score = min(1.0, max(0.0, 
            (debt_to_income - 0.5) * 2 +  # High debt
            (expense_to_income - 0.8) * 5  # High expenses
        ))
        
        # Target 3: Risk assessment (5 categories: very_low, low, medium, high, very_high)
        risk_factors = []
        risk_factors.append(1.0 if debt_to_income > 0.4 else 0.0)  # High debt ratio
        risk_factors.append(1.0 if expense_to_income > 0.9 else 0.0)  # Living paycheck to paycheck
        risk_factors.append(1.0 if credit_score < 650 else 0.0)  # Poor credit
        risk_factors.append(1.0 if total_assets < income * 0.5 else 0.0)  # Low assets
        risk_factors.append(1.0 if record['assets']['cash'] < expenses * 0.1 else 0.0)  # Low emergency fund
        
        # Target 4: Investment recommendations (10 categories)
        investment_profile = [0.0] * 10
        age_proxy = min(9, max(0, int((net_worth / max(income, 1)) * 2)))  # Rough age estimation
        risk_tolerance = 9 - sum(risk_factors)  # Higher risk tolerance = lower risk factors
        investment_profile[min(9, max(0, age_proxy))] = 1.0
        
        # Target 5: Debt optimization (3 strategies: aggressive, moderate, conservative)
        if debt_to_income > 0.5:
            debt_strategy = [1.0, 0.0, 0.0]  # Aggressive
        elif debt_to_income > 0.2:
            debt_strategy = [0.0, 1.0, 0.0]  # Moderate
        else:
            debt_strategy = [0.0, 0.0, 1.0]  # Conservative
            
        return {
            'savings_prediction': savings_rate,
            'anomaly_score': anomaly_score,
            'risk_assessment': risk_factors,
            'investment_recommendations': investment_profile,
            'debt_optimization': debt_strategy
        }
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        features = self.features[idx]
        
        # Data augmentation during training
        if self.augment and random.random() < 0.3:
            # Add small noise to features (±5%)
            noise = torch.randn_like(features) * 0.05
            features = features + noise
            features = torch.clamp(features, 0, float('inf'))  # Keep positive values positive
        
        targets = {key: values[idx] for key, values in self.targets.items()}
        return features, targets


class MultiTaskLoss(nn.Module):
    """Multi-task loss with dynamic weighting"""
    
    def __init__(self):
        super().__init__()
        self.mse = nn.MSELoss()
        self.bce = nn.BCEWithLogitsLoss()
        self.ce = nn.CrossEntropyLoss()
        
        # Learnable loss weights
        self.weights = nn.Parameter(torch.ones(5))
        
    def forward(self, predictions, targets):
        # Savings prediction (regression)
        savings_loss = self.mse(predictions['savings_prediction'].squeeze(), 
                               targets['savings_prediction'])
        
        # Anomaly score (binary classification)
        anomaly_loss = self.bce(predictions['anomaly_score'].squeeze(), 
                               targets['anomaly_score'])
        
        # Risk assessment (multi-label classification)
        risk_loss = self.bce(predictions['risk_assessment'], 
                            targets['risk_assessment'])
        
        # Investment recommendations (multi-class classification)
        investment_loss = self.ce(predictions['investment_recommendations'],
                                 targets['investment_recommendations'].argmax(dim=1))
        
        # Debt optimization (multi-class classification)
        debt_loss = self.ce(predictions['debt_optimization'],
                           targets['debt_optimization'].argmax(dim=1))
        
        # Weighted combination
        losses = torch.stack([savings_loss, anomaly_loss, risk_loss, investment_loss, debt_loss])
        weights = torch.softmax(self.weights, dim=0)  # Normalize weights
        
        total_loss = (weights * losses).sum()
        
        return {
            'total_loss': total_loss,
            'savings_loss': savings_loss,
            'anomaly_loss': anomaly_loss,
            'risk_loss': risk_loss,
            'investment_loss': investment_loss,
            'debt_loss': debt_loss,
            'weights': weights
        }


class FinancialTrainer:
    """Advanced trainer for financial AI model"""
    
    def __init__(self, model: FinancialAdvisorModel, device: str = 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.criterion = MultiTaskLoss().to(device)
        self.optimizer = optim.AdamW(
            list(model.parameters()) + list(self.criterion.parameters()),
            lr=0.001, weight_decay=1e-5
        )
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.7, patience=10
        )
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'learning_rates': [],
            'epoch_times': []
        }
        
        # Early stopping
        self.best_val_loss = float('inf')
        self.patience = 20
        self.patience_counter = 0
        
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        epoch_losses = []
        
        for batch_idx, (features, targets) in enumerate(train_loader):
            features = features.to(self.device)
            targets = {k: v.to(self.device) for k, v in targets.items()}
            
            self.optimizer.zero_grad()
            predictions = self.model(features)
            loss_dict = self.criterion(predictions, targets)
            
            loss_dict['total_loss'].backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            epoch_losses.append(loss_dict['total_loss'].item())
            
            if batch_idx % 50 == 0:
                logger.info(f"Batch {batch_idx}/{len(train_loader)}, Loss: {loss_dict['total_loss'].item():.4f}")
        
        return {'train_loss': np.mean(epoch_losses)}
    
    def validate_epoch(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate for one epoch"""
        self.model.eval()
        epoch_losses = []
        
        with torch.no_grad():
            for features, targets in val_loader:
                features = features.to(self.device)
                targets = {k: v.to(self.device) for k, v in targets.items()}
                
                predictions = self.model(features)
                loss_dict = self.criterion(predictions, targets)
                epoch_losses.append(loss_dict['total_loss'].item())
        
        return {'val_loss': np.mean(epoch_losses)}
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader, 
              num_epochs: int = 100, save_path: str = 'models') -> Dict[str, Any]:
        """Full training loop"""
        os.makedirs(save_path, exist_ok=True)
        
        logger.info(f"Starting training for {num_epochs} epochs")
        
        for epoch in range(num_epochs):
            epoch_start = datetime.now()
            
            # Training
            train_metrics = self.train_epoch(train_loader)
            
            # Validation
            val_metrics = self.validate_epoch(val_loader)
            
            # Learning rate scheduling
            self.scheduler.step(val_metrics['val_loss'])
            
            # Update history
            self.history['train_loss'].append(train_metrics['train_loss'])
            self.history['val_loss'].append(val_metrics['val_loss'])
            self.history['learning_rates'].append(self.optimizer.param_groups[0]['lr'])
            self.history['epoch_times'].append((datetime.now() - epoch_start).total_seconds())
            
            logger.info(f"Epoch {epoch+1}/{num_epochs} - "
                       f"Train Loss: {train_metrics['train_loss']:.4f}, "
                       f"Val Loss: {val_metrics['val_loss']:.4f}, "
                       f"LR: {self.optimizer.param_groups[0]['lr']:.6f}")
            
            # Early stopping and checkpointing
            if val_metrics['val_loss'] < self.best_val_loss:
                self.best_val_loss = val_metrics['val_loss']
                self.patience_counter = 0
                
                # Save best model
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'val_loss': val_metrics['val_loss'],
                    'history': self.history
                }, os.path.join(save_path, 'best_model.pth'))
                
                logger.info(f"New best model saved (Val Loss: {val_metrics['val_loss']:.4f})")
                
            else:
                self.patience_counter += 1
                if self.patience_counter >= self.patience:
                    logger.info(f"Early stopping triggered after {epoch+1} epochs")
                    break
        
        # Load best model
        checkpoint = torch.load(os.path.join(save_path, 'best_model.pth'), weights_only=False)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        return self.history
    
    def export_torchscript(self, save_path: str):
        """Export model to TorchScript format for C++ inference"""
        self.model.eval()
        
        # Use TorchScript scripting to support dict outputs from forward
        scripted_model = torch.jit.script(self.model)
        
        # Save TorchScript model
        scripted_model.save(save_path)
        logger.info(f"TorchScript model saved to {save_path}")
        
        return scripted_model


def plot_training_history(history: Dict[str, List], save_path: str = 'training_plots.png'):
    """Plot training history"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Loss curves
    axes[0, 0].plot(history['train_loss'], label='Train Loss', alpha=0.8)
    axes[0, 0].plot(history['val_loss'], label='Val Loss', alpha=0.8)
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].set_title('Training and Validation Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Learning rate
    axes[0, 1].plot(history['learning_rates'], color='orange')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Learning Rate')
    axes[0, 1].set_title('Learning Rate Schedule')
    axes[0, 1].set_yscale('log')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Epoch times
    axes[1, 0].plot(history['epoch_times'], color='green')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('Time (seconds)')
    axes[1, 0].set_title('Training Time per Epoch')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Loss difference
    loss_diff = np.array(history['val_loss']) - np.array(history['train_loss'])
    axes[1, 1].plot(loss_diff, color='red')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('Val Loss - Train Loss')
    axes[1, 1].set_title('Overfitting Monitor')
    axes[1, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    logger.info(f"Training plots saved to {save_path}")


def main():
    """Main training function"""
    logger.info("🚀 Starting Financial AI Model Training")
    
    # Set random seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)
    
    # Device setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    
    # Load data
    logger.info("Loading training data...")
    with open('data.json', 'r') as f:
        data = json.load(f)
    
    logger.info(f"Loaded {len(data)} financial records")
    
    # Initialize preprocessor
    preprocessor = AdvancedDataPreprocessor()
    permissions = UserPermissions()  # Full permissions for training
    
    # Train/validation split
    train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)
    logger.info(f"Train samples: {len(train_data)}, Val samples: {len(val_data)}")
    
    # Create datasets
    train_dataset = FinancialDataset(train_data, preprocessor, permissions, augment=True)
    val_dataset = FinancialDataset(val_data, preprocessor, permissions, augment=False)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False, num_workers=2)
    
    # Initialize model
    model = FinancialAdvisorModel(input_size=16)
    logger.info(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Initialize trainer
    trainer = FinancialTrainer(model, device)
    
    # Train model
    logger.info("Starting model training...")
    history = trainer.train(train_loader, val_loader, num_epochs=100)
    
    # Plot training history
    plot_training_history(history, 'training_plots.png')
    
    # Export TorchScript model for C++ inference
    logger.info("Exporting TorchScript model...")
    trainer.export_torchscript('financial_model.pt')
    
    # Save final model state
    torch.save({
        'model_state_dict': model.state_dict(),
        'history': history,
        'model_config': {
            'input_size': 16,
            'architecture': 'FinancialAdvisorModel',
            'training_samples': len(train_data),
            'validation_samples': len(val_data)
        }
    }, 'financial_model_final.pth')
    
    logger.info("🎉 Training completed successfully!")
    logger.info(f"Best validation loss: {trainer.best_val_loss:.4f}")
    logger.info("Files generated:")
    logger.info("  - financial_model.pt (TorchScript for C++)")
    logger.info("  - financial_model_final.pth (PyTorch checkpoint)")
    logger.info("  - training_plots.png (Training visualizations)")


if __name__ == "__main__":
    main()