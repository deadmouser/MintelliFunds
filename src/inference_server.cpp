#include "inference_server.h"
#include <iostream>
#include <sstream>
#include <iomanip>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <cstring>
#include <regex>

InferenceServer::InferenceServer(const std::string& model_path, int port)
    : model_loader_(std::make_unique<ModelLoader>(model_path)), port_(port), running_(false) {
}

InferenceServer::~InferenceServer() {
    stop();
}

bool InferenceServer::initialize() {
    std::cout << "Initializing inference server..." << std::endl;
    
    if (!model_loader_->load()) {
        std::cerr << "Failed to load model" << std::endl;
        return false;
    }
    
    std::cout << "Server initialized successfully on port " << port_ << std::endl;
    return true;
}

void InferenceServer::run() {
    running_ = true;
    
    // Create socket
    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket < 0) {
        std::cerr << "Error creating socket" << std::endl;
        return;
    }
    
    // Allow socket reuse
    int opt = 1;
    setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    // Configure server address
    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port_);
    
    // Bind socket
    if (bind(server_socket, (sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "Error binding socket" << std::endl;
        close(server_socket);
        return;
    }
    
    // Listen for connections
    if (listen(server_socket, 10) < 0) {
        std::cerr << "Error listening on socket" << std::endl;
        close(server_socket);
        return;
    }
    
    std::cout << "Server listening on port " << port_ << std::endl;
    
    // Accept and handle connections
    while (running_) {
        sockaddr_in client_addr{};
        socklen_t client_addr_len = sizeof(client_addr);
        
        int client_socket = accept(server_socket, (sockaddr*)&client_addr, &client_addr_len);
        if (client_socket < 0) {
            if (running_) {
                std::cerr << "Error accepting connection" << std::endl;
            }
            continue;
        }
        
        // Handle client in a separate thread
        std::thread client_thread(&InferenceServer::handle_client, this, client_socket);
        client_thread.detach();
    }
    
    close(server_socket);
    std::cout << "Server stopped" << std::endl;
}

void InferenceServer::stop() {
    running_ = false;
}

void InferenceServer::handle_client(int client_socket) {
    try {
        // Read request from client
        char buffer[4096];
        int bytes_read = recv(client_socket, buffer, sizeof(buffer) - 1, 0);
        
        if (bytes_read <= 0) {
            close(client_socket);
            return;
        }
        
        buffer[bytes_read] = '\0';
        std::string request(buffer);
        
        std::cout << "Received request: " << request.substr(0, 100) << "..." << std::endl;
        
        // Simple HTTP parsing - extract JSON from POST body
        std::string json_body;
        size_t body_start = request.find("\r\n\r\n");
        if (body_start != std::string::npos) {
            json_body = request.substr(body_start + 4);
        } else {
            // Direct JSON request (not HTTP)
            json_body = request;
        }
        
        // Process inference request
        std::vector<float> input_data = parse_input_json(json_body);
        std::string response = process_inference(input_data);
        
        // Send HTTP response
        std::string http_response = "HTTP/1.1 200 OK\r\n";
        http_response += "Content-Type: application/json\r\n";
        http_response += "Content-Length: " + std::to_string(response.length()) + "\r\n";
        http_response += "Access-Control-Allow-Origin: *\r\n";
        http_response += "\r\n";
        http_response += response;
        
        send(client_socket, http_response.c_str(), http_response.length(), 0);
        
    } catch (const std::exception& e) {
        std::cerr << "Error handling client: " << e.what() << std::endl;
        
        // Send error response
        std::string error_response = R"({"error": ")" + std::string(e.what()) + R"("})";
        std::string http_error = "HTTP/1.1 500 Internal Server Error\r\n";
        http_error += "Content-Type: application/json\r\n";
        http_error += "Content-Length: " + std::to_string(error_response.length()) + "\r\n";
        http_error += "\r\n";
        http_error += error_response;
        
        send(client_socket, http_error.c_str(), http_error.length(), 0);
    }
    
    close(client_socket);
}

std::string InferenceServer::process_inference(const std::vector<float>& input_data) {
    if (input_data.size() != model_loader_->get_input_size()) {
        throw std::runtime_error("Input size mismatch. Expected " + 
                                std::to_string(model_loader_->get_input_size()) + 
                                " but got " + std::to_string(input_data.size()));
    }
    
    // Convert input to tensor
    torch::Tensor input_tensor = torch::from_blob(
        const_cast<float*>(input_data.data()), 
        {1, static_cast<long>(input_data.size())}, 
        torch::kFloat
    ).clone();
    
    // Run inference
    auto outputs = model_loader_->predict(input_tensor);
    
    // Convert outputs to JSON
    return outputs_to_json(outputs);
}

std::string InferenceServer::outputs_to_json(const torch::Dict<std::string, torch::Tensor>& outputs) {
    std::ostringstream json;
    json << "{";
    
    bool first = true;
    for (const auto& item : outputs) {
        if (!first) json << ",";
        first = false;
        
        json << "\"" << item.key() << "\":[";
        
        auto tensor = item.value();
        auto accessor = tensor.accessor<float, 2>(); // Assuming 2D tensors [batch, features]
        
        for (int i = 0; i < accessor.size(1); ++i) {
            if (i > 0) json << ",";
            json << std::fixed << std::setprecision(6) << accessor[0][i];
        }
        
        json << "]";
    }
    
    json << "}";
    return json.str();
}

std::vector<float> InferenceServer::parse_input_json(const std::string& json_str) {
    std::vector<float> result;
    
    // Simple JSON parsing for array of numbers
    // Look for "features": [1.0, 2.0, ...] pattern
    std::regex features_regex(R"("features"\s*:\s*\[([^\]]+)\])");
    std::smatch match;
    
    if (std::regex_search(json_str, match, features_regex)) {
        std::string numbers_str = match[1].str();
        
        // Parse numbers
        std::regex number_regex(R"([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)");
        std::sregex_iterator iter(numbers_str.begin(), numbers_str.end(), number_regex);
        std::sregex_iterator end;
        
        while (iter != end) {
            result.push_back(std::stof(iter->str()));
            ++iter;
        }
    } else {
        // If no "features" key, try to parse as simple array
        std::regex number_regex(R"([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)");
        std::sregex_iterator iter(json_str.begin(), json_str.end(), number_regex);
        std::sregex_iterator end;
        
        while (iter != end) {
            result.push_back(std::stof(iter->str()));
            ++iter;
        }
    }
    
    return result;
}