#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <cstring>
#include <filesystem>

using namespace std;

constexpr uint8_t ARCHIVE_SIGNATURE[6] = {0xBA, 0x5E, 0xBA, 0x11, 0xCA, 0xFE};
constexpr uint16_t ARCHIVE_VERSION = 0x0000;

struct ArchiveHeader {
    uint8_t signature[6];
    uint16_t formatVersion;
    uint64_t originalFileSize;
};

// Helper to write little-endian integers explicitly
static void writeLE(ofstream &out, uint16_t v) {
    uint8_t buf[2];
    buf[0] = static_cast<uint8_t>(v & 0xFF);
    buf[1] = static_cast<uint8_t>((v >> 8) & 0xFF);
    out.write(reinterpret_cast<const char*>(buf), 2);
}
static void writeLE(ofstream &out, uint64_t v) {
    uint8_t buf[8];
    for (int i = 0; i < 8; ++i) buf[i] = static_cast<uint8_t>((v >> (8 * i)) & 0xFF);
    out.write(reinterpret_cast<const char*>(buf), 8);
}
static bool readLE(ifstream &in, uint16_t &v) {
    uint8_t buf[2];
    if (!in.read(reinterpret_cast<char*>(buf), 2)) return false;
    v = static_cast<uint16_t>(buf[0]) | (static_cast<uint16_t>(buf[1]) << 8);
    return true;
}
static bool readLE(ifstream &in, uint64_t &v) {
    uint8_t buf[8];
    if (!in.read(reinterpret_cast<char*>(buf), 8)) return false;
    v = 0;
    for (int i = 0; i < 8; ++i) v |= (static_cast<uint64_t>(buf[i]) << (8 * i));
    return true;
}

bool encodeFile(const filesystem::path& inputPath, const filesystem::path& outputPath) {
    ifstream inputFile(inputPath, ios::binary);
    ofstream outputFile(outputPath, ios::binary);

    if (!inputFile) {
        cerr << "Ошибка: не удалось открыть входной файл: " << inputPath << endl;
        return false;
    }
    if (!outputFile) {
        cerr << "Ошибка: не удалось открыть выходной файл: " << outputPath << endl;
        return false;
    }

    uint64_t fileSize = filesystem::file_size(inputPath);

    // Write header fields explicitly to avoid struct padding issues
    outputFile.write(reinterpret_cast<const char*>(ARCHIVE_SIGNATURE), sizeof(ARCHIVE_SIGNATURE));
    writeLE(outputFile, ARCHIVE_VERSION);
    writeLE(outputFile, fileSize);

    vector<char> buffer(static_cast<size_t>(fileSize));
    inputFile.read(buffer.data(), static_cast<streamsize>(fileSize));
    outputFile.write(buffer.data(), static_cast<streamsize>(fileSize));

    return true;
}

bool decodeFile(const filesystem::path& inputPath, const filesystem::path& outputPath) {
    ifstream inputFile(inputPath, ios::binary);
    if (!inputFile) {
        cerr << "Ошибка: не удалось открыть входной файл: " << inputPath << endl;
        return false;
    }

    uint8_t sig[6];
    if (!inputFile.read(reinterpret_cast<char*>(sig), sizeof(sig))) {
        cerr << "Ошибка: не удалось прочитать сигнатуру" << endl;
        return false;
    }
    if (memcmp(sig, ARCHIVE_SIGNATURE, sizeof(ARCHIVE_SIGNATURE)) != 0) {
        cerr << "Ошибка: Неверная сигнатура архива" << endl;
        return false;
    }

    uint16_t ver;
    if (!readLE(inputFile, ver)) {
        cerr << "Ошибка: не удалось прочитать версию" << endl;
        return false;
    }
    if (ver != ARCHIVE_VERSION) {
        cerr << "Ошибка: Неподдерживаемая версия формата " << ver << endl;
        return false;
    }

    uint64_t originalSize;
    if (!readLE(inputFile, originalSize)) {
        cerr << "Ошибка: не удалось прочитать размер исходного файла" << endl;
        return false;
    }

    ofstream outputFile(outputPath, ios::binary);
    if (!outputFile) {
        cerr << "Ошибка: не удалось создать выходной файл: " << outputPath << endl;
        return false;
    }

    vector<char> buffer(static_cast<size_t>(originalSize));
    inputFile.read(buffer.data(), static_cast<streamsize>(originalSize));
    outputFile.write(buffer.data(), static_cast<streamsize>(originalSize));

    return true;
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        cerr << "Использование: " << argv[0] << " <encode|decode> <input> <output>" << endl;
        return 1;
    }

    try {
        string mode = argv[1];
        filesystem::path inputPath = argv[2];
        filesystem::path outputPath = argv[3];

        if (mode == "encode") {
            if (!encodeFile(inputPath, outputPath)) {
                return 1;
            }
            cout << "Файл успешно заархивирован" << endl;
        } else if (mode == "decode") {
            if (!decodeFile(inputPath, outputPath)) {
                return 1;
            }
            cout << "Файл успешно распакован" << endl;
        } else {
            cerr << "Неизвестный режим: " << mode << endl;
            return 1;
        }
    } catch (const exception& e) {
        cerr << "Ошибка: " << e.what() << endl;
        return 1;
    }

    return 0;
}