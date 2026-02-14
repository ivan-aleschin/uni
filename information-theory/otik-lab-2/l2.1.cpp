#include <map>
#include <iostream>
#include <string>
#include <fstream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <algorithm>
#include <sstream>
#include <filesystem>

using namespace std;

template <typename Container>
double printStats(const Container& container, size_t count) {
    double iSum = 0.0;

    if (count == 0) {
        cout << "Empty file or no bytes read." << "\n";
        return 0.0;
    }

    // header
    cout << left << setw(8) << "BYTE" << right << setw(12) << "COUNT" << setw(16) << "P" << setw(18) << "I [bit]" << "\n";
    cout << string(54, '-') << "\n";

    for (auto it = container.begin(); it != container.end(); ++it) {
        unsigned int key = static_cast<unsigned int>(it->first) & 0xFFu;
        size_t cnt = it->second;

        double pIt = 0.0;
        double iIt = 0.0;
        bool has = (cnt > 0);
        if (has && count > 0) {
            pIt = static_cast<double>(cnt) / static_cast<double>(count);
            // safe: pIt > 0
            iIt = -log2(pIt);
        }

        // format byte as two-digit hex (use stringstream to avoid changing cout flags)
        stringstream ss;
        ss << uppercase << hex << setw(2) << setfill('0') << (key);
        string byteHex = ss.str();

        // Print byte
        cout << "0x" << left << setw(6) << setfill(' ') << byteHex;

        // Print count
        cout << right << setw(10) << cnt;

        // Print probability
        {
            stringstream ps;
            ps << fixed << setprecision(6) << pIt;
            cout << setw(16) << ps.str();
        }

        // Print information (I) or N/A if count == 0
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

void printAddStats(double iSumBits, size_t count) {
    if (count == 0) {
        cout << "\nNo additional stats for empty file.\n";
        return;
    }

    // fractional part of I(Q) in bits
    double fracISum = iSumBits - floor(iSumBits);

    cout << "\n";

    // L(Q) in bits is count * 8
    unsigned long long LqBits = static_cast<unsigned long long>(count) * 8ULL;

    // Print with requested formatting
    // I(Q) [bit] with two decimals
    cout << fixed << setprecision(2);
    cout << "n (length in symbols) = " << count << "\n";
    cout << "L(Q) [bit] = " << LqBits << "\n";
    cout << "I(Q) [bit] = " << iSumBits << "\n";

    // fractional part in exponential form
    cout << scientific << setprecision(6);
    cout << "{I(Q) [bit]} = " << fracISum << "\n\n";

    // Reset to fixed for octet outputs with 2 decimals
    cout << fixed << setprecision(2);
    double iSumOctetsExact = iSumBits / 8.0;
    size_t LqOctets = count; // for byte-symbol model n is bytes
    size_t E_octets = static_cast<size_t>(ceil(iSumOctetsExact));

    cout << "L(Q) [octet] = " << LqOctets << "\n";
    cout << "I(Q) [octet] = " << iSumOctetsExact << "\n";
    cout << "E [octet] = " << E_octets << "\n";
    cout << "G64 [octet] = " << (E_octets + 256 * 8) << "\n";
    cout << "G8 [octet] = " << (E_octets + 256 * 1) << "\n";

    // restore cout flags to default state
    cout.unsetf(ios::floatfield);
    cout << setprecision(6);
}

void analyze(const string& fileName) {
    cout << "Trying to open file: " << std::filesystem::absolute(fileName) << endl;

    ifstream file(fileName, ios::binary);
    map<unsigned int, size_t> freqMap;
    size_t count = 0;

    // Initialize full 256-byte alphabet with zero counts so the alphabet-sorted table contains all bytes
    for (unsigned int b = 0; b < 256; ++b) {
        freqMap[b] = 0;
    }

    if (!file) {
        cerr << "Cannot open file: " << fileName << "\n";
        return;
    }

    char byte;
    while (file.read(&byte, 1)) {
        unsigned int intByte = static_cast<unsigned char>(byte);
        freqMap[intByte]++;
        ++count;
    }

    cout << "\nTotal bytes read (n) = " << count << "\n\n";

    // Print sorted by byte value
    cout << "-- Statistics sorted by byte value --\n";
    double iSumBits = printStats(freqMap, count);

    // Now print sorted by frequency
    vector<pair<unsigned int, size_t>> sortedByFreq(freqMap.begin(), freqMap.end());
    sort(sortedByFreq.begin(), sortedByFreq.end(),
         [](const pair<unsigned int, size_t>& a, const pair<unsigned int, size_t>& b) {
             if (a.second != b.second) return a.second > b.second;
             return a.first < b.first;
         });

    cout << "\n-- Statistics sorted by decreasing frequency --\n";
    printStats(sortedByFreq, count);

    printAddStats(iSumBits, count);
}

int main(int argc, char** argv) {
    string fileName = "C:/Dev/Workspace/otik-lab-2/src/utf8.txt"; // default
    if (argc >= 2) fileName = argv[1];

    analyze(fileName);
    return 0;
}