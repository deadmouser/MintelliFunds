#ifndef INFERENCE_SERVER_H
#define INFERENCE_SERVER_H

#include "model_loader.h"
#include <string>
#include <memory>
#include <vector>
#include <thread>
#include <atomic>

/**
 * InferenceServer class for serving financial model predictions
 */
class InferenceServer {
public:
    /**
     * Constructor
     * @param model_path Path to the TorchScript model file
     * @param port Port to listen on
     */
    InferenceServer(const std::string& model_path, int port = 8888);
    
    /**
     * Destructor
     */
    ~InferenceServer();
    
    /**
     * Initialize the server and load the model
     * @return true if successful, false otherwise
     */
    bool initialize();
    
    /**
     * Start the server (blocking call)
     */
    void run();
    
    /**
     * Stop the server
     */
    void stop();
    
    /**
     * Process inference request
     * @param input_data Vector of feature values (size must match model input)
     * @return JSON string with predictions
     */
    std::string process_inference(const std::vector<float>& input_data);
    
private:
    std::unique_ptr<ModelLoader> model_loader_;
    int port_;
    std::atomic<bool> running_;
    std::thread server_thread_;
    
    /**
     * Handle client connection (simple TCP server)
     * @param client_socket Client socket file descriptor
     */
    void handle_client(int client_socket);
    
    /**
     * Convert model output to JSON string
     * @param outputs Dictionary of output tensors
     * @return JSON string representation
     */
    std::string outputs_to_json(const torch::Dict<std::string, torch::Tensor>& outputs);
    
    /**
     * Parse input JSON to feature vector
     * @param json_str Input JSON string
     * @return Vector of feature values
     */
    std::vector<float> parse_input_json(const std::string& json_str);
    
    // Disable copy constructor and assignment operator
    InferenceServer(const InferenceServer&) = delete;
    InferenceServer& operator=(const InferenceServer&) = delete;
};

#endif // INFERENCE_SERVER_H