#include "model_loader.h"
#include <iostream>
#include <exception>

ModelLoader::ModelLoader(const std::string& model_path) 
    : model_path_(model_path), loaded_(false), input_size_(16) {
}

ModelLoader::~ModelLoader() {
}

bool ModelLoader::load() {
    try {
        std::cout << "Loading TorchScript model from: " << model_path_ << std::endl;
        
        // Deserialize the ScriptModule from a file using torch::jit::load().
        model_ = torch::jit::load(model_path_);
        model_.eval();
        
        loaded_ = true;
        std::cout << "Model loaded successfully!" << std::endl;
        
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "Error loading model: " << e.what() << std::endl;
        loaded_ = false;
        return false;
    }
}

bool ModelLoader::is_loaded() const {
    return loaded_;
}

torch::Dict<std::string, torch::Tensor> ModelLoader::predict(const torch::Tensor& input_tensor) {
    if (!loaded_) {
        throw std::runtime_error("Model not loaded");
    }
    
    try {
        // Set tensor to eval mode (no gradients)
        torch::NoGradGuard no_grad;
        
        // Create inputs vector for the model
        std::vector<torch::jit::IValue> inputs;
        inputs.push_back(input_tensor);
        
        // Execute the model and get the output
        auto output = model_.forward(inputs);
        
        // The output should be a dictionary (GenericDict in TorchScript)
        auto output_dict = output.toGenericDict();
        
        // Convert to torch::Dict<std::string, torch::Tensor>
        torch::Dict<std::string, torch::Tensor> result;
        
        for (auto& item : output_dict) {
            std::string key = item.key().toStringRef();
            torch::Tensor value = item.value().toTensor();
            result.insert(key, value);
        }
        
        return result;
        
    } catch (const std::exception& e) {
        std::cerr << "Error during inference: " << e.what() << std::endl;
        throw;
    }
}