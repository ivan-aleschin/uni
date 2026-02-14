#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <cstring>
#include <filesystem>

using namespace std;

constexpr uint8_t ARCHIVE_SIGNATURE[8] = {0xBA, 0x5E, 0xBA, 0x11, 0xCA, 0xFE, 0xFF, 0x00};
constexpr uint16_t ARCHIVE_VERSION = 0x0001;

struct ArchiveHeader {
    uint8_t signature[8];
    uint16_t formatVersion;
    uint8_t compressionAlgo1;
    uint8_t compressionAlgo2;
    uint8_t protectionAlgo;
    uint32_t serviceDataSize;
    uint64_t originalFileSize;
};

bool encodeFile(const filesystem::path& inputPath, const filesystem::path& outputPath) {
    ifstream inputFile(inputPath, ios::binary);
    ofstream outputFile(outputPath, ios::binary);

    uint64_t fileSize = filesystem::file_size(inputPath);

    ArchiveHeader header;
    memcpy(header.signature, ARCHIVE_SIGNATURE, sizeof(ARCHIVE_SIGNATURE));
    header.formatVersion = ARCHIVE_VERSION;
    header.compressionAlgo1 = 0; // Без сжатия
    header.compressionAlgo2 = 0; // Без сжатия
    header.protectionAlgo = 0;   // Без защиты
    header.serviceDataSize = 0;  // Нет служебных данных
    header.originalFileSize = fileSize;

    outputFile.write(reinterpret_cast<const char*>(&header), sizeof(header));

    vector<char> buffer(fileSize);
    inputFile.read(buffer.data(), fileSize);
    outputFile.write(buffer.data(), fileSize);

    return true;
}

bool decodeFile(const filesystem::path& inputPath, const filesystem::path& outputPath) {
    ifstream inputFile(inputPath, ios::binary);

    ArchiveHeader header;
    inputFile.read(reinterpret_cast<char*>(&header), sizeof(header));

    if (memcmp(header.signature, ARCHIVE_SIGNATURE, sizeof(ARCHIVE_SIGNATURE)) != 0) {
        cerr << "Ошибка: Неверная сигнатура архива" << endl;
        return false;
    }

    if (header.formatVersion != ARCHIVE_VERSION) {
        cerr << "Ошибка: Неподдерживаемая версия формата " << header.formatVersion << endl;
        return false;
    }

    if (header.serviceDataSize > 0) {
        inputFile.seekg(header.serviceDataSize, ios::cur);
    }

    ofstream outputFile(outputPath, ios::binary);

    vector<char> buffer(header.originalFileSize);
    inputFile.read(buffer.data(), header.originalFileSize);

    outputFile.write(buffer.data(), header.originalFileSize);
    
    return true;
}

int main(int argc, char* argv[]) {
    try {
        string mode = argv[1];
        filesystem::path inputPath = argv[2];
        filesystem::path outputPath = argv[3];

        if (mode == "encode") {
            if (!encodeFile(inputPath, outputPath)) {
                return 1;
            }
        } else if (mode == "decode") {
            if (!decodeFile(inputPath, outputPath)) {
                return 1;
            }
        }
    } catch (const exception& e) {
        cerr << "Ошибка: " << e.what() << endl;
        return 1;
    }

    return 0;
}