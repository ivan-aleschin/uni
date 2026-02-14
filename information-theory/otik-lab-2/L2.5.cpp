#include <map>
#include <iostream>
#include <string>
#include <fstream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <algorithm>

using namespace std;

bool isValidCharacter(unsigned int code_point, size_t number_of_bytes) {
    // overlong checks
    if (number_of_bytes == 2 && code_point < 0x80) return false;
    if (number_of_bytes == 3 && code_point < 0x800) return false;
    if (number_of_bytes == 4 && code_point < 0x10000) return false;
    if (code_point > 0x10FFFF) return false;

    // allow control characters (if needed by task), but exclude surrogates and noncharacters
    if (code_point >= 0xD800 && code_point <= 0xDFFF) return false;
    if (code_point >= 0xF0000 && code_point <= 0xFFFFD) return false;
    if (code_point >= 0x100000 && code_point <= 0x10FFFD) return false;

    // Accept other code points (including C0/C1 controls if present)
    return true;
}

void printStats(const map<pair<unsigned int, unsigned int>, size_t>& pairCount,
                const map<unsigned int, size_t>& singleCount,
                int firstSymbol, size_t char_count) {
    double markovInfo = 0.0;

    // contribution of first symbol (unconditional). Use empirical probability if available.
    if (firstSymbol != -1 && char_count > 0) {
        auto it = singleCount.find(static_cast<unsigned int>(firstSymbol));
        if (it != singleCount.end()) {
            double p_first = static_cast<double>(it->second) / static_cast<double>(char_count);
            if (p_first > 0.0) {
                markovInfo += -log2(p_first);
            }
        }
    }

    cout << fixed << setprecision(6);
    for (const auto& entry : pairCount) {
        unsigned int aj = entry.first.first;
        unsigned int ak = entry.first.second;
        size_t count_ajak = entry.second;
        auto it_aj = singleCount.find(aj);
        size_t count_aj_star = (it_aj != singleCount.end()) ? it_aj->second : 0;

        if (count_aj_star > 0 && count_ajak > 0) {
            double p_cond = static_cast<double>(count_ajak) / static_cast<double>(count_aj_star);
            if (p_cond > 0.0) {
                markovInfo += static_cast<double>(count_ajak) * (-log2(p_cond));
            }

            // Print conditional probability info
            stringstream ss_aj, ss_ak;
            ss_aj << "U+" << uppercase << hex << setw(6) << setfill('0') << aj;
            ss_ak << "U+" << uppercase << hex << setw(6) << setfill('0') << ak;
            cout << ss_ak.str() << " | " << ss_aj.str() << " : p = " << dec << fixed << setprecision(6) << p_cond
                 << "   count(" << dec << count_ajak << ")\n";
        }
    }

    cout << fixed << setprecision(6);
    cout << "I_CM1(Q) [bit] = " << markovInfo << "\n";
    cout << "I_CM1(Q) [octet] = " << (markovInfo / 8.0) << "\n";
}

void analyze(string fileName) {
    ifstream file(fileName, ios::binary);
    if (!file) {
        cerr << "Cannot open file: " << fileName << "\n";
        return;
    }

    map<unsigned int, size_t> singleCount;
    map<pair<unsigned int, unsigned int>, size_t> pairCount;
    size_t char_count = 0;
    int firstSymbol = -1;
    int previousSymbol = -1;

    size_t bytes_left = 0;
    unsigned int current_code = 0;
    size_t expected_bytes = 0;

    char byte;
    while (file.read(&byte, 1)) {
        unsigned char ubyte = static_cast<unsigned char>(byte);

        if (bytes_left == 0) {
            // start of new character
            if (ubyte < 0x80) {
                current_code = ubyte;
                expected_bytes = 1;
                bytes_left = 0;
            } else if (ubyte >= 0xC0 && ubyte < 0xE0) {
                current_code = ubyte & 0x1F;
                expected_bytes = 2;
                bytes_left = 1;
            } else if (ubyte >= 0xE0 && ubyte < 0xF0) {
                current_code = ubyte & 0x0F;
                expected_bytes = 3;
                bytes_left = 2;
            } else if (ubyte >= 0xF0 && ubyte < 0xF8) {
                current_code = ubyte & 0x07;
                expected_bytes = 4;
                bytes_left = 3;
            } else {
                // invalid leading byte, skip
                bytes_left = 0;
                expected_bytes = 0;
                current_code = 0;
                continue;
            }
        } else {
            // continuation byte
            if ((ubyte & 0xC0) != 0x80) {
                // invalid continuation, reset state
                bytes_left = 0;
                expected_bytes = 0;
                current_code = 0;
                continue;
            }
            current_code = (current_code << 6) | (ubyte & 0x3F);
            bytes_left--;
        }

        if (bytes_left == 0) {
            // complete code point in current_code
            if (isValidCharacter(current_code, expected_bytes)) {
                if (firstSymbol == -1) {
                    firstSymbol = static_cast<int>(current_code);
                }
                singleCount[current_code]++;
                ++char_count;
                if (previousSymbol != -1) {
                    pairCount[make_pair(static_cast<unsigned int>(previousSymbol), current_code)]++;
                }
                previousSymbol = static_cast<int>(current_code);
            }
            // reset for next code point
            current_code = 0;
            expected_bytes = 0;
        }
    }

    // Exclude last symbol from singleCount (it has no outgoing bigram)
    if (previousSymbol != -1) {
        auto it = singleCount.find(static_cast<unsigned int>(previousSymbol));
        if (it != singleCount.end() && it->second > 0) {
            it->second--;
            if (char_count > 0) --char_count;
        }
    }

    if (char_count == 0) {
        cout << "No valid Unicode symbols found in file.\n";
        return;
    }

    printStats(pairCount, singleCount, firstSymbol, char_count);
}

int main(int argc, char** argv) {
    string fileName = "C:/Dev/Workspace/otik-lab-2/src/utf8.txt";
    if (argc >= 2) fileName = argv[1];
    analyze(fileName);
    return 0;
}