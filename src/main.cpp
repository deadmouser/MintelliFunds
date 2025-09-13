#include "inference_server.h"
#include <iostream>
#include <signal.h>
#include <cstdlib>

// Global server instance for signal handling
InferenceServer* g_server = nullptr;

void signal_handler(int signal) {
    std::cout << "\nReceived signal " << signal << ". Shutting down server..." << std::endl;
    if (g_server) {
        g_server->stop();
    }
    exit(0);
}

void print_usage(const char* program_name) {
    std::cout << "Usage: " << program_name << " [options]" << std::endl;
    std::cout << "Options:" << std::endl;
    std::cout << "  --model <path>    Path to TorchScript model file (default: financial_model.pt)" << std::endl;
    std::cout << "  --port <port>     Port to listen on (default: 8888)" << std::endl;
    std::cout << "  --help            Show this help message" << std::endl;
}

int main(int argc, char* argv[]) {
    std::string model_path = "financial_model.pt";
    int port = 8888;
    
    // Parse command line arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        
        if (arg == "--help" || arg == "-h") {
            print_usage(argv[0]);
            return 0;
        } else if (arg == "--model" && i + 1 < argc) {
            model_path = argv[++i];
        } else if (arg == "--port" && i + 1 < argc) {
            port = std::atoi(argv[++i]);
        } else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            print_usage(argv[0]);
            return 1;
        }
    }
    
    // Validate arguments
    if (port <= 0 || port > 65535) {
        std::cerr << "Invalid port number: " << port << std::endl;
        return 1;
    }
    
    std::cout << "=== Financial AI Inference Server ===" << std::endl;
    std::cout << "Model: " << model_path << std::endl;
    std::cout << "Port: " << port << std::endl;
    std::cout << "=====================================" << std::endl;
    
    // Set up signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    try {
        // Create and initialize server
        InferenceServer server(model_path, port);
        g_server = &server;
        
        if (!server.initialize()) {
            std::cerr << "Failed to initialize server" << std::endl;
            return 1;
        }
        
        std::cout << "\nServer started successfully!" << std::endl;
        std::cout << "To test the server, send a POST request to http://localhost:" << port << std::endl;
        std::cout << "Example payload: {\"features\": [1.0, 2.0, 3.0, ...]}" << std::endl;
        std::cout << "\nPress Ctrl+C to stop the server.\n" << std::endl;
        
        // Run server (blocks until stopped)
        server.run();
        
    } catch (const std::exception& e) {
        std::cerr << "Server error: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}