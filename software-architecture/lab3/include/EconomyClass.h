#pragma once

#include "Section.h"
#include <vector>
#include <utility>  // pair

class EconomyClass : public Section {
public:
    EconomyClass();
    void offloadExcessBaggage(int& excess, std::vector<std::pair<std::string, int>>& removed);
};

