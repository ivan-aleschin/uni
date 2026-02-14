#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <algorithm>

using namespace std;
namespace fs = filesystem;

constexpr uint8_t ARCHIVE_SIGNATURE[8] = {0xBA, 0x5E, 0xBA, 0x11, 0xCA, 0xFE, 0xFF, 0x00};
constexpr uint16_t ARCHIVE_VERSION = 0x0001;

struct ArchiveHeader {
    uint8_t signature[8];
    uint16_t formatVersion;
    uint8_t compressionAlgo1;
    uint8_t compressionAlgo2;
    uint8_t protectionAlgo;
    uint32_t serviceDataSize;
    uint64_t originalDataSize;
    uint32_t fileCount;
};

static void writeLE(ofstream &out, uint8_t v) { out.write(reinterpret_cast<const char*>(&v), 1); }
static void writeLE(ofstream &out, uint16_t v) { uint8_t b[2] = { (uint8_t)(v & 0xFF), (uint8_t)((v>>8)&0xFF) }; out.write(reinterpret_cast<const char*>(b), 2); }
static void writeLE(ofstream &out, uint32_t v) { uint8_t b[4] = { (uint8_t)(v&0xFF),(uint8_t)((v>>8)&0xFF),(uint8_t)((v>>16)&0xFF),(uint8_t)((v>>24)&0xFF) }; out.write(reinterpret_cast<const char*>(b),4); }
static void writeLE(ofstream &out, uint64_t v) { uint8_t b[8]; for (int i=0;i<8;++i) b[i] = (uint8_t)((v>>(8*i))&0xFF); out.write(reinterpret_cast<const char*>(b),8); }

static bool readLE(ifstream &in, uint8_t &v) { return static_cast<bool>(in.read(reinterpret_cast<char*>(&v),1)); }
static bool readLE(ifstream &in, uint16_t &v) { uint8_t b[2]; if (!in.read(reinterpret_cast<char*>(b),2)) return false; v = (uint16_t)b[0] | ((uint16_t)b[1]<<8); return true; }
static bool readLE(ifstream &in, uint32_t &v) { uint8_t b[4]; if (!in.read(reinterpret_cast<char*>(b),4)) return false; v = (uint32_t)b[0] | ((uint32_t)b[1]<<8) | ((uint32_t)b[2]<<16) | ((uint32_t)b[3]<<24); return true; }
static bool readLE(ifstream &in, uint64_t &v) { uint8_t b[8]; if (!in.read(reinterpret_cast<char*>(b),8)) return false; v = 0; for (int i=0;i<8;++i) v |= ((uint64_t)b[i] << (8*i)); return true; }

static bool parseArchiveHeader(ifstream &in, ArchiveHeader &header) {
    if (!in.read(reinterpret_cast<char*>(header.signature), sizeof(header.signature))) return false;
    if (!readLE(in, header.formatVersion)) return false;
    if (!readLE(in, header.compressionAlgo1)) return false;
    if (!readLE(in, header.compressionAlgo2)) return false;
    if (!readLE(in, header.protectionAlgo)) return false;
    if (!readLE(in, header.serviceDataSize)) return false;
    if (!readLE(in, header.originalDataSize)) return false;
    if (!readLE(in, header.fileCount)) return false;
    return true;
}

bool encodeDirectory(const fs::path& inputPath, const fs::path& outputPath) {
    ofstream outputFile(outputPath, ios::binary);
    if (!outputFile) {
        cerr << "Ошибка: не удалось открыть выходной файл: " << outputPath << endl;
        return false;
    }

    vector<pair<fs::path, bool>> items; // stored relative path -> isDirectory
    uint32_t fileCount = 0;
    uint64_t totalSize = 0;

    try {
        for (const auto& entry : fs::recursive_directory_iterator(inputPath)) {
            bool isDir = entry.is_directory();
            // relInside = path relative to the inputPath (so files directly inside inputPath get "a.txt")
            fs::path relInside = fs::relative(entry.path(), inputPath);
            // storedRelative should include top-level directory name: inputPath.filename() / relInside
            fs::path storedRelative;
            if (relInside.empty()) {
                // unlikely for recursive_directory_iterator, but guard anyway
                storedRelative = inputPath.filename();
            } else {
                storedRelative = inputPath.filename() / relInside;
            }
            items.emplace_back(storedRelative, isDir);
            ++fileCount;
            if (!isDir) {
                try {
                    uint64_t sz = fs::file_size(entry.path());
                    totalSize += sz;
                } catch (const fs::filesystem_error& e) {
                    cerr << "Ошибка: не удалось получить размер файла " << entry.path() << " : " << e.what() << endl;
                    return false;
                }
            }
        }
    } catch (const fs::filesystem_error& e) {
        cerr << "Ошибка при обходе директории: " << e.what() << endl;
        return false;
    }

    sort(items.begin(), items.end(), [](const pair<fs::path,bool>& a, const pair<fs::path,bool>& b){
        return a.first.generic_string() < b.first.generic_string();
    });

    // Header
    outputFile.write(reinterpret_cast<const char*>(ARCHIVE_SIGNATURE), sizeof(ARCHIVE_SIGNATURE));
    writeLE(outputFile, ARCHIVE_VERSION);
    writeLE(outputFile, static_cast<uint8_t>(0));
    writeLE(outputFile, static_cast<uint8_t>(0));
    writeLE(outputFile, static_cast<uint8_t>(0));
    writeLE(outputFile, static_cast<uint32_t>(0));
    writeLE(outputFile, totalSize);
    writeLE(outputFile, fileCount);

    // Write entries. To read file data we need the actual file path on disk.
    for (const auto& p : items) {
        const fs::path storedRel = p.first;
        bool isDirectory = p.second;
        string pathStr = storedRel.generic_string();
        uint32_t pathLen = static_cast<uint32_t>(pathStr.size());
        uint64_t fsize = 0;

        // To get the real file contents and size, reconstruct original absolute path
        // storedRel is inputPath.filename()/rest, so to get disk file: inputPath / rest
        fs::path rest;
        // If storedRel starts with inputPath.filename(), remove it to get rest
        if (storedRel.empty()) {
            rest.clear();
        } else {
            // storedRel = topDir / relInside
            auto it = storedRel.begin();
            // skip first component (top-level dir)
            ++it;
            for (; it != storedRel.end(); ++it) rest /= *it;
        }

        fs::path diskPath = inputPath / rest; // if rest empty, diskPath == inputPath

        if (!isDirectory) {
            try {
                fsize = fs::file_size(diskPath);
            } catch (const fs::filesystem_error& e) {
                cerr << "Ошибка: не удалось получить размер файла для записи данных: " << diskPath << " : " << e.what() << endl;
                return false;
            }
        }

        writeLE(outputFile, pathLen);
        writeLE(outputFile, fsize);
        writeLE(outputFile, static_cast<uint8_t>(isDirectory ? 1 : 0));
        outputFile.write(pathStr.c_str(), static_cast<std::streamsize>(pathLen));

        if (!isDirectory) {
            ifstream inFile(diskPath, ios::binary);
            if (!inFile) {
                cerr << "Ошибка: не удалось открыть файл для чтения: " << diskPath << endl;
                return false;
            }
            const size_t chunkSize = 1 << 20;
            uint64_t remaining = fsize;
            vector<char> buf(static_cast<size_t>(min<uint64_t>(chunkSize, remaining)));
            while (remaining) {
                size_t toRead = static_cast<size_t>(min<uint64_t>(chunkSize, remaining));
                inFile.read(buf.data(), static_cast<std::streamsize>(toRead));
                outputFile.write(buf.data(), static_cast<std::streamsize>(toRead));
                remaining -= toRead;
            }
        }
    }

    return true;
}

bool decodeDirectory_from_stream(ifstream &inputFile, const ArchiveHeader &header, const fs::path &outputPath) {
    fs::create_directories(outputPath);
    for (uint32_t i = 0; i < header.fileCount; ++i) {
        uint32_t pathLen;
        uint64_t fileSize;
        uint8_t isDirectory;
        if (!readLE(inputFile, pathLen)) { cerr << "Ошибка чтения pathLen" << endl; return false; }
        if (!readLE(inputFile, fileSize)) { cerr << "Ошибка чтения fileSize" << endl; return false; }
        if (!readLE(inputFile, isDirectory)) { cerr << "Ошибка чтения isDirectory" << endl; return false; }

        if (pathLen == 0) { cerr << "Ошибка: нулевая длина пути" << endl; return false; }
        if (pathLen > 10*1024*1024) { cerr << "Ошибка: подозрительно длинный путь" << endl; return false; }

        vector<char> pathBuf(pathLen);
        if (!inputFile.read(pathBuf.data(), static_cast<std::streamsize>(pathLen))) { cerr << "Ошибка чтения пути" << endl; return false; }
        string relativePathStr(pathBuf.data(), pathLen);
        fs::path fullPath = outputPath / fs::path(relativePathStr);

        if (isDirectory) {
            fs::create_directories(fullPath);
        } else {
            fs::create_directories(fullPath.parent_path());
            ofstream outFile(fullPath, ios::binary);
            if (!outFile) { cerr << "Ошибка: не удалось создать файл: " << fullPath << endl; return false; }
            if (fileSize > 0) {
                const size_t chunkSize = 1 << 20;
                uint64_t remaining = fileSize;
                vector<char> buf(static_cast<size_t>(min<uint64_t>(chunkSize, remaining)));
                while (remaining) {
                    size_t toRead = static_cast<size_t>(min<uint64_t>(chunkSize, remaining));
                    if (!inputFile.read(buf.data(), static_cast<std::streamsize>(toRead))) { cerr << "Ошибка чтения данных файла" << endl; return false; }
                    outFile.write(buf.data(), static_cast<std::streamsize>(toRead));
                    remaining -= toRead;
                }
            }
        }
    }
    return true;
}

bool encodeFile(const fs::path& inputPath, const fs::path& outputPath) {
    ifstream inputFile(inputPath, ios::binary);
    ofstream outputFile(outputPath, ios::binary);

    if (!inputFile) { cerr << "Ошибка: не удалось открыть входной файл: " << inputPath << endl; return false; }
    if (!outputFile) { cerr << "Ошибка: не удалось открыть выходной файл: " << outputPath << endl; return false; }

    uint64_t fileSize;
    try { fileSize = fs::file_size(inputPath); }
    catch (const fs::filesystem_error& e) { cerr << "Ошибка: не удалось получить размер входного файла: " << e.what() << endl; return false; }

    outputFile.write(reinterpret_cast<const char*>(ARCHIVE_SIGNATURE), sizeof(ARCHIVE_SIGNATURE));
    writeLE(outputFile, ARCHIVE_VERSION);
    writeLE(outputFile, static_cast<uint8_t>(0));
    writeLE(outputFile, static_cast<uint8_t>(0));
    writeLE(outputFile, static_cast<uint8_t>(0));
    writeLE(outputFile, static_cast<uint32_t>(0));
    writeLE(outputFile, fileSize);
    writeLE(outputFile, static_cast<uint32_t>(1));

    string filename = inputPath.filename().generic_string();
    uint32_t pathLen = static_cast<uint32_t>(filename.size());
    writeLE(outputFile, pathLen);
    writeLE(outputFile, fileSize);
    writeLE(outputFile, static_cast<uint8_t>(0));
    outputFile.write(filename.c_str(), static_cast<std::streamsize>(pathLen));

    const size_t chunkSize = 1 << 20;
    uint64_t remaining = fileSize;
    vector<char> buf(static_cast<size_t>(min<uint64_t>(chunkSize, remaining)));
    ifstream inFile(inputPath, ios::binary);
    while (remaining) {
        size_t toRead = static_cast<size_t>(min<uint64_t>(chunkSize, remaining));
        inFile.read(buf.data(), static_cast<std::streamsize>(toRead));
        outputFile.write(buf.data(), static_cast<std::streamsize>(toRead));
        remaining -= toRead;
    }

    return true;
}

bool decodeFile_from_stream(ifstream &inputFile, const ArchiveHeader &header, const fs::path &outputPath) {
    uint32_t pathLen;
    uint64_t fileSize;
    uint8_t isDirectory;
    if (!readLE(inputFile, pathLen)) { cerr << "Ошибка чтения pathLen" << endl; return false; }
    if (!readLE(inputFile, fileSize)) { cerr << "Ошибка чтения fileSize" << endl; return false; }
    if (!readLE(inputFile, isDirectory)) { cerr << "Ошибка чтения isDirectory" << endl; return false; }

    if (pathLen == 0) { cerr << "Ошибка: нулевая длина пути" << endl; return false; }
    vector<char> pathBuf(pathLen);
    if (!inputFile.read(pathBuf.data(), static_cast<std::streamsize>(pathLen))) { cerr << "Ошибка чтения пути" << endl; return false; }

    ofstream outFile(outputPath, ios::binary);
    if (!outFile) { cerr << "Ошибка: не удалось создать файл: " << outputPath << endl; return false; }

    uint64_t remaining = fileSize;
    const size_t chunkSize = 1 << 20;
    vector<char> buf(static_cast<size_t>(min<uint64_t>(chunkSize, remaining)));
    while (remaining) {
        size_t toRead = static_cast<size_t>(min<uint64_t>(chunkSize, remaining));
        if (!inputFile.read(buf.data(), static_cast<std::streamsize>(toRead))) { cerr << "Ошибка чтения данных файла" << endl; return false; }
        outFile.write(buf.data(), static_cast<std::streamsize>(toRead));
        remaining -= toRead;
    }

    return true;
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        cerr << "Использование: " << argv[0] << " <encode|decode> <input> <output>" << endl;
        return 1;
    }

    try {
        string mode = argv[1];
        fs::path inputPath = argv[2];
        fs::path outputPath = argv[3];

        if (mode == "encode") {
            if (fs::is_directory(inputPath)) {
                if (!encodeDirectory(inputPath, outputPath)) return 1;
                cout << "Директория успешно заархивирована" << endl;
            } else {
                if (!encodeFile(inputPath, outputPath)) return 1;
                cout << "Файл успешно заархивирован" << endl;
            }
        } else if (mode == "decode") {
            ifstream inFile(inputPath, ios::binary);
            if (!inFile) { cerr << "Ошибка: не удалось открыть архив: " << inputPath << endl; return 1; }

            ArchiveHeader header{};
            if (!parseArchiveHeader(inFile, header)) { cerr << "Ошибка: не удалось прочитать заголовок архива" << endl; return 1; }

            if (memcmp(header.signature, ARCHIVE_SIGNATURE, sizeof(ARCHIVE_SIGNATURE)) != 0) {
                cerr << "Ошибка: Неверная сигнатура архива" << endl;
                return 1;
            }
            if (header.formatVersion != ARCHIVE_VERSION) {
                cerr << "Ошибка: Неподдерживаемая версия формата " << header.formatVersion << endl;
                return 1;
            }

            if (header.fileCount > 1 || fs::is_directory(outputPath)) {
                if (!decodeDirectory_from_stream(inFile, header, outputPath)) return 1;
                cout << "Архив с директорией успешно распакован" << endl;
            } else {
                if (!decodeFile_from_stream(inFile, header, outputPath)) return 1;
                cout << "Архив с файлом успешно распакован" << endl;
            }
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