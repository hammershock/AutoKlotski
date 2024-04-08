cmake_minimum_required(VERSION 3.5)
project(klotski_module)

set(CMAKE_CXX_STANDARD 17)

# 找到pybind11
find_package(pybind11 REQUIRED)

# 添加模块
pybind11_add_module(klotski_module klotski_bindings.cpp Klotski.cpp State.cpp)

# 如果你的项目使用了特定的include目录
include_directories(${PROJECT_SOURCE_DIR})

# 设置编译器优化标志
if(MSVC)
    # 对于MSVC，使用/O2进行最大优化
    target_compile_options(klotski_module PRIVATE /O2)
else()
    # 对于GCC或Clang，启用高级优化和指令集支持
    target_compile_options(klotski_module PRIVATE -O3 -funroll-loops -mavx2 -mbmi -mbmi2 -mlzcnt -mpopcnt)
endif()

