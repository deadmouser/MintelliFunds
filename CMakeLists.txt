cmake_minimum_required(VERSION 3.12)
project(FinancialInferenceServer)

# Set C++ standard
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find LibTorch
set(CMAKE_PREFIX_PATH "${CMAKE_CURRENT_SOURCE_DIR}/libtorch")
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")

# Find pthreads for multithreading
find_package(Threads REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Create executable for the inference server
add_executable(financial_inference_server
    src/main.cpp
    src/inference_server.cpp
    src/model_loader.cpp
)

# Link libraries
target_link_libraries(financial_inference_server 
    "${TORCH_LIBRARIES}"
    Threads::Threads
)

# Set properties for relocatable binaries
set_property(TARGET financial_inference_server PROPERTY CXX_STANDARD 14)

# Copy LibTorch libraries to build directory (for easier deployment)
if (MSVC)
    file(GLOB TORCH_DLLS "${TORCH_INSTALL_PREFIX}/lib/*.dll")
    add_custom_command(TARGET financial_inference_server
                       POST_BUILD
                       COMMAND ${CMAKE_COMMAND} -E copy_if_different
                       ${TORCH_DLLS}
                       $<TARGET_FILE_DIR:financial_inference_server>)
endif (MSVC)

# Enable optimizations in Release mode
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")