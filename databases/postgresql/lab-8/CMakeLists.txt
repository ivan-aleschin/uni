cmake_minimum_required(VERSION 3.20)
project(database_lab8)

set(CMAKE_CXX_STANDARD 17)

# Путь к PostgreSQL
set(POSTGRESQL_PATH "C:/Program Files/PostgreSQL/17")

# Добавляем пути к заголовочным файлам и библиотекам
include_directories("${POSTGRESQL_PATH}/include")
link_directories("${POSTGRESQL_PATH}/lib")

add_executable(database_lab8 main.cpp)

# Линкуем библиотеку libpq
target_link_libraries(database_lab8 pq)
