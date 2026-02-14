#include <iostream>
#include <type_traits>

template <typename>
struct is_function : std::false_type{};

template <typename f, typename ... types >
struct is_function< f(types...) >: std::true_type{};

template <typename f, typename ... types >
struct is_function< f(types...) const > : std::true_type{};

template <typename f, typename ... types >
struct is_function< f(types...)& > : std::true_type{};

template <typename f, typename ... types >
struct is_function< f(types...) const & > : std::true_type{};

template <typename f>
inline const bool is_function_v = is_function <f> ::value;

int main() {
    std::cout << std::boolalpha;
    std::cout << is_function_v <int(double, char) const >;

    return 0;
}