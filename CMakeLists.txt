cmake_minimum_required(VERSION 3.21)
project(CandlehearthRentDim VERSION 0.1.0 LANGUAGES CXX)
find_package(CommonLibSSE CONFIG REQUIRED)
# Explicit zero padding avoids CommonLib default-constructing unused versions as 1.0.0.
set(SUPPORTED_RUNTIMES 1.7.104.0)
foreach(i RANGE 1 15)
    list(APPEND SUPPORTED_RUNTIMES 0.0.0.0)
endforeach()
add_commonlibsse_plugin(${PROJECT_NAME}
    AUTHOR "kxgcayh"
    STRUCT_DEPENDENT
    COMPATIBLE_RUNTIMES ${SUPPORTED_RUNTIMES}
    SOURCES src/main.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_23)
target_precompile_headers(${PROJECT_NAME} PRIVATE src/PCH.h)
