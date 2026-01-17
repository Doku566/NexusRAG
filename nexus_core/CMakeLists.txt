cmake_minimum_required(VERSION 3.14)
project(NexusCore VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Optimization
if(MSVC)
    add_compile_options(/O2)
else()
    add_compile_options(-O3 -march=native)
endif()

find_package(Python 3.8 REQUIRED COMPONENTS Interpreter Development)

include(FetchContent)
FetchContent_Declare(
  pybind11
  URL https://github.com/pybind/pybind11/archive/v2.11.1.zip
)
FetchContent_MakeAvailable(pybind11)

include_directories(include)

pybind11_add_module(nexus_core src/bindings.cpp)
install(TARGETS nexus_core DESTINATION .)
