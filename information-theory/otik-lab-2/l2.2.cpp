#include <iostream>
#include <fstream>
#include <iomanip>
#include <map>
#include <vector>
#include <algorithm>
#include <string>
#include <sstream>
#include <locale>
#include <codecvt>
#include <cmath>
#include <filesystem>

using namespace std;

// UTF-8 to UTF-32 conversion (C++11). May throw on invalid sequences.
static u32string utf8_to_utf32(const string& str) {
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;
    return conv.from_bytes(str);
}

static int utf8_length_of_codepoint(char32_t cp) {
    if (cp <= 0x7F) return 1;
    if (cp <= 0x7FF) return 2;
    if (cp <= 0xFFFF) return 3;
    return 4;
}

template <typename Container>
double printStats(const Container& container, size_t count) {
    double iSum = 0.0;
    if (count == 0) {
        cout << "Empty file or no symbols read." << "\n";
        return 0.0;
    }
    cout << left << setw(12) << "UNICODE" << right << setw(12) << "COUNT" << setw(16) << "P" << setw(18) << "I [bit]" << "\n";
    cout << string(58, '-') << "\n";
    for (auto it = container.begin(); it != container.end(); ++it) {
        char32_t key = it->first;
        size_t cnt = it->second;
        double pIt = 0.0;
        double iIt = 0.0;
        bool has = (cnt > 0);
        if (has && count > 0) {
            pIt = static_cast<double>(cnt) / static_cast<double>(count);
            iIt = -log2(pIt);
        }
        // Print Unicode codepoint in hex
        stringstream ss;
        ss << "U+" << uppercase << hex << setw(6) << setfill('0') << (uint32_t)key;
        string codeHex = ss.str();
        cout << left << setw(12) << codeHex;
        cout << right << setw(10) << cnt;
        {
            stringstream ps;
            ps << fixed << setprecision(6) << pIt;
            cout << setw(16) << ps.str();
        }
        if (has) {
            stringstream is;
            is << fixed << setprecision(6) << iIt;
            cout << setw(14) << is.str() << "\n";
            iSum += iIt * static_cast<double>(cnt);
        } else {
            cout << setw(14) << "N/A" << "\n";
        }
    }
    return iSum;
}

void printAddStats(double iSumBits, size_t count, size_t alphabetSize, size_t symbolSize) {
    double fracISum = iSumBits - floor(iSumBits);
    cout << "\n";
    cout << fixed << setprecision(2);
    cout << "L(Q) [bit] = " << (count * 8ULL) << "\n";
    cout << "I(Q) [bit] = " << iSumBits << "\n";
    cout << "{I(Q) [bit]} = " << scientific << fracISum << "\n\n";
    double iSumOctetsExact = iSumBits / 8.0;
    size_t LqOctets = count;
    size_t E_octets = static_cast<size_t>(ceil(iSumOctetsExact));
    cout.unsetf(ios::floatfield);
    cout << fixed << setprecision(2);
    cout << "L(Q) [octet] = " << LqOctets << "\n";
    cout << "I(Q) [octet] = " << (iSumBits / 8.0) << "\n";
    cout << "E [octet] = " << E_octets << "\n";
    // Archive length: 8 bytes for alphabet size + |A1| * (symbolSize + 8)
    cout << "Archive length (UTF-32 symbols) [octet] = " << (8 + alphabetSize * (symbolSize + 8)) << "\n";
}

void analyze(const string& fileName) {
    cout << "Trying to open file: " << std::filesystem::absolute(fileName) << endl;
    ifstream file(fileName, ios::binary);
    if (!file) {
        cerr << "Cannot open file: " << fileName << "\n";
        return;
    }
    // Read whole file as string
    string fileContent((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());

    u32string u32text;
    try {
        u32text = utf8_to_utf32(fileContent);
    } catch (const std::range_error& e) {
        cerr << "UTF-8 conversion error: invalid UTF-8 sequence in file.\n";
        return;
    } catch (...) {
        cerr << "UTF-8 conversion error.\n";
        return;
    }

    map<char32_t, size_t> freqMap;
    size_t count = 0;
    for (char32_t ch : u32text) {
        freqMap[ch]++;
        ++count;
    }

    // Print sorted by Unicode codepoint
    cout << "-- Statistics sorted by Unicode codepoint --\n";
    double iSumBits = printStats(freqMap, count);

    // Print sorted by frequency
    vector<pair<char32_t, size_t>> sortedByFreq(freqMap.begin(), freqMap.end());
    sort(sortedByFreq.begin(), sortedByFreq.end(),
         [](const pair<char32_t, size_t>& a, const pair<char32_t, size_t>& b) {
             if (a.second != b.second) return a.second > b.second;
             return a.first < b.first;
         });
    cout << "\n-- Statistics sorted by decreasing frequency --\n";
    printStats(sortedByFreq, count);

    // For archive: symbolSize = 4 (UTF-32), alphabetSize = freqMap.size()
    size_t alphabetSize = freqMap.size();
    printAddStats(iSumBits, count, alphabetSize, 4);

    // Additionally compute archive length if symbols stored in UTF-8 (variable length)
    size_t sum_symbol_bytes_utf8 = 0;
    for (const auto& kv : freqMap) {
        char32_t cp = kv.first;
        sum_symbol_bytes_utf8 += static_cast<size_t>(utf8_length_of_codepoint(cp));
    }
    size_t archive_utf8 = 8 + sum_symbol_bytes_utf8 + 8 * alphabetSize;
    cout << "Archive length (UTF-8 symbols) [octet] = " << archive_utf8 << "\n";
    cout << "Full Unicode freq table [octet] = " << (8 + 0x110000ULL * 8ULL) << "\n";
}

int main(int argc, char** argv) {
    string fileName = "C:/Dev/Workspace/otik-lab-2/src/utf8.txt"; // default
    if (argc >= 2) fileName = argv[1];
    analyze(fileName);
    return 0;
}