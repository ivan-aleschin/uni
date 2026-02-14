#include <map>
#include <iostream>
#include <string>
#include <fstream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <algorithm>

using namespace std;

void printStats(const map<pair<unsigned int, unsigned int>, size_t>& pairCount,
                const map<unsigned int, size_t>& singleCount) {
    double markovInfo = 0.0;

    for (auto it = pairCount.begin(); it != pairCount.end(); ++it) {
        unsigned int aj = it->first.first;
        unsigned int ak = it->first.second;
        size_t count_ajak = it->second;
        auto it_aj = singleCount.find(aj);
        size_t count_aj_star = (it_aj != singleCount.end()) ? it_aj->second : 0;

        if (count_aj_star > 0) {
            double p_cond = static_cast<double>(count_ajak) / static_cast<double>(count_aj_star);
            if (p_cond > 0.0) {
                markovInfo += static_cast<double>(count_ajak) * (-log2(p_cond));
            }

            cout << hex << setw(2) << setfill('0') << uppercase;
            cout << "p(" << ak << "|" << aj << ") = " << dec << fixed << setprecision(6) << p_cond << "   ";
            cout << "count(" << aj << "," << ak << ") = " << dec << count_ajak << "\n";
        }
    }

    cout.unsetf(ios::floatfield);
    cout << fixed << setprecision(6);
    cout << "I_CM1(Q) [bit] = " << markovInfo << "\n";
    cout << "I_CM1(Q) [octet] = " << (markovInfo / 8.0) << "\n";
}

void analyze(const string& fileName) {

    ifstream file(fileName, ios::binary);
    if (!file) {
        cerr << "Cannot open file: " << fileName << "\n";
        return;
    }

    map<pair<unsigned int, unsigned int>, size_t> pairCount;
    map<unsigned int, size_t> singleCount;
    int previousByte = -1;
    size_t char_count = 0;

    char byte;
    while (file.read(&byte, 1)) {
        unsigned int uByte = static_cast<unsigned char>(byte); // FIX: correct unsigned conversion
        singleCount[uByte]++;
        ++char_count;
        if (previousByte != -1) {
            pairCount[make_pair(static_cast<unsigned int>(previousByte), uByte)]++;
        }
        previousByte = static_cast<int>(uByte);
    }

    // Exclude last symbol from singleCount (it has no outgoing bigram)
    if (previousByte != -1) {
        auto it = singleCount.find(static_cast<unsigned int>(previousByte));
        if (it != singleCount.end() && it->second > 0) {
            it->second--;
            if (char_count > 0) --char_count;
        }
    }

    printStats(pairCount, singleCount);
}

int main(int argc, char** argv) {
    string fileName = "C:/Dev/Workspace/otik-lab-2/src/utf8.txt";
    if (argc >= 2) fileName = argv[1];
    analyze(fileName);
    return 0;
}