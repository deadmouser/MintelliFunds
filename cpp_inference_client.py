#!/usr/bin/env python3
"""
Python client for the C++ inference server
"""

import json
import socket
import subprocess
import time
import threading
import requests
from typing import List, Dict, Optional
from loguru import logger
import atexit


class CppInferenceClient:
    """Client for communicating with the C++ inference server"""
    
    def __init__(self, model_path: str = "financial_model.pt", port: int = 8888, auto_start: bool = True):
        self.model_path = model_path
        self.port = port
        self.server_process: Optional[subprocess.Popen] = None
        self.auto_start = auto_start
        self.base_url = f"http://localhost:{port}"
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
        
        if auto_start:
            self.start_server()
    
    def start_server(self) -> bool:
        """Start the C++ inference server in a subprocess"""
        try:
            if self.is_server_running():
                logger.info(f"Server already running on port {self.port}")
                return True
            
            logger.info("Starting C++ inference server...")
            
            # Start the C++ server
            self.server_process = subprocess.Popen([
                "./build/financial_inference_server",
                "--model", self.model_path,
                "--port", str(self.port)
            ], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )
            
            # Give the server time to start
            time.sleep(2)
            
            # Check if server is running
            if self.is_server_running():
                logger.info(f"✅ C++ inference server started on port {self.port}")
                return True
            else:
                logger.error("Failed to start C++ inference server")
                if self.server_process:
                    stdout, stderr = self.server_process.communicate(timeout=1)
                    logger.error(f"Server stdout: {stdout}")
                    logger.error(f"Server stderr: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the C++ inference server"""
        if self.server_process:
            logger.info("Stopping C++ inference server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
                self.server_process.wait()
            self.server_process = None
            logger.info("C++ inference server stopped")
    
    def cleanup(self):
        """Cleanup method called on exit"""
        self.stop_server()
    
    def is_server_running(self) -> bool:
        """Check if the server is running and responding"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', self.port))
                return result == 0
        except:
            return False
    
    def predict(self, features: List[float]) -> Dict:
        """
        Send prediction request to C++ server
        
        Args:
            features: List of 16 feature values
            
        Returns:
            Dictionary with prediction results
        """
        if len(features) != 16:
            raise ValueError(f"Expected 16 features, got {len(features)}")
        
        if not self.is_server_running():
            if self.auto_start:
                logger.info("Server not running, attempting to start...")
                if not self.start_server():
                    raise RuntimeError("Failed to start C++ inference server")
            else:
                raise RuntimeError("C++ inference server is not running")
        
        try:
            # Prepare request payload
            payload = {"features": features}
            
            # Send HTTP POST request
            response = requests.post(
                self.base_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Server returned status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise RuntimeError(f"Failed to communicate with C++ server: {e}")
    
    def health_check(self) -> bool:
        """Check if the server is healthy by making a test prediction"""
        try:
            # Test with dummy data
            dummy_features = [1.0] * 16
            result = self.predict(dummy_features)
            return isinstance(result, dict) and len(result) > 0
        except:
            return False


class CppInferenceManager:
    """Manager for the C++ inference client with connection pooling"""
    
    def __init__(self, model_path: str = "financial_model.pt", port: int = 8888):
        self.model_path = model_path
        self.port = port
        self.client: Optional[CppInferenceClient] = None
        self._lock = threading.Lock()
    
    def get_client(self) -> CppInferenceClient:
        """Get or create a client instance (thread-safe)"""
        with self._lock:
            if self.client is None:
                self.client = CppInferenceClient(self.model_path, self.port, auto_start=True)
            return self.client
    
    def predict(self, features: List[float]) -> Dict:
        """Thread-safe prediction method"""
        client = self.get_client()
        return client.predict(features)
    
    def shutdown(self):
        """Shutdown the manager and stop the server"""
        with self._lock:
            if self.client:
                self.client.stop_server()
                self.client = None


# Global instance for easy access
_global_manager: Optional[CppInferenceManager] = None

def get_global_inference_manager() -> CppInferenceManager:
    """Get the global inference manager (singleton pattern)"""
    global _global_manager
    if _global_manager is None:
        _global_manager = CppInferenceManager()
    return _global_manager

def predict_with_cpp(features: List[float]) -> Dict:
    """Convenience function for making predictions"""
    manager = get_global_inference_manager()
    return manager.predict(features)


if __name__ == "__main__":
    # Test the client
    logger.info("Testing C++ inference client...")
    
    client = CppInferenceClient()
    
    # Test with dummy financial data
    test_features = [
        10000.0,  # cash
        50000.0,  # bank_balances
        200000.0, # property
        15000.0,  # loans
        2000.0,   # credit_card_debt
        60000.0,  # income
        45000.0,  # expenses
        5000.0,   # transfers
        12000.0,  # epf_contributions
        6000.0,   # employer_match
        150000.0, # current_balance
        720.0,    # credit_score
        2.0,      # credit_rating (encoded)
        25000.0,  # stocks
        15000.0,  # mutual_funds
        10000.0   # bonds
    ]
    
    try:
        logger.info("Making test prediction...")
        result = client.predict(test_features)
        logger.info(f"Prediction result: {json.dumps(result, indent=2)}")
        
        logger.info("Health check...")
        is_healthy = client.health_check()
        logger.info(f"Server healthy: {is_healthy}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
    
    finally:
        client.stop_server()
        logger.info("Test completed")