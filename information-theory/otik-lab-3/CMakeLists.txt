cmake_minimum_required(VERSION 4.0)
project(otik_lab_3)

set(CMAKE_CXX_STANDARD 20)

add_executable(otik_lab_3 main.cpp)
add_executable(task-1 L3.1.cpp)
add_executable(task-3 L3.3sp.cpp)

# Custom target to run local tests (Windows)
if (WIN32)
    add_custom_target(run_tests
        DEPENDS task-1 task-3
        COMMAND ${CMAKE_COMMAND} -E echo "Running test.bat from ${CMAKE_SOURCE_DIR}"
        COMMAND cmd /c "${CMAKE_SOURCE_DIR}\\test.bat"
        WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
        COMMENT "Builds tasks and runs test.bat"
    )
endif()
