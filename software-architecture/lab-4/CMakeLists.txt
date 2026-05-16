cmake_minimum_required(VERSION 3.16)
project(proxy_image_editor LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)

add_executable(${PROJECT_NAME}
    src/main.cpp
    src/Canvas.cpp
    src/ImageProxy.cpp
    src/RealImage.cpp
    include/Image.h
    include/Canvas.h
    include/ImageProxy.h
    include/RealImage.h
)

target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Core Qt6::Gui Qt6::Widgets)
