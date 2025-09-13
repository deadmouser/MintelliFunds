#ifndef MODEL_LOADER_H
#define MODEL_LOADER_H

#include <torch/torch.h>
#include <torch/script.h>
#include <string>
#include <memory>

/**
 * ModelLoader class for loading and managing TorchScript models
 */
class ModelLoader {
public:
    /**
     * Constructor
     * @param model_path Path to the TorchScript model file
     */
    explicit ModelLoader(const std::string& model_path);
    
    /**
     * Destructor
     */
    ~ModelLoader();
    
    /**
     * Load the TorchScript model
     * @return true if successful, false otherwise
     */
    bool load();
    
    /**
     * Check if model is loaded
     * @return true if model is loaded, false otherwise
     */
    bool is_loaded() const;
    
    /**
     * Run inference on input data
     * @param input_tensor Input tensor with shape [batch_size, input_size]
     * @return Dictionary of output tensors
     */
    torch::Dict<std::string, torch::Tensor> predict(const torch::Tensor& input_tensor);
    
    /**
     * Get input size of the model
     * @return Input size
     */
    int get_input_size() const { return input_size_; }
    
private:
    std::string model_path_;
    torch::jit::script::Module model_;
    bool loaded_;
    int input_size_;
    
    // Disable copy constructor and assignment operator
    ModelLoader(const ModelLoader&) = delete;
    ModelLoader& operator=(const ModelLoader&) = delete;
};

#endif // MODEL_LOADER_H