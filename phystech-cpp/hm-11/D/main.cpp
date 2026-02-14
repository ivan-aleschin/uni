#include <type_traits>
#include <iostream>


namespace detail {
    void* voidify(const volatile void* ptr) noexcept { return const_cast<void*>(ptr); }
}

template<class T>
typename std::enable_if<std::is_trivially_default_constructible<T>::value>::type
construct(T*) {
    std::cout << "Default constructing trivially default constructible T\n";
}

template<class T>
typename std::enable_if<!std::is_trivially_default_constructible<T>::value>::type
construct(T* p) {
    std::cout << "Default constructing non-trivially default constructible T\n";
    ::new(detail::voidify(p)) T;
}

int main() {
    std::aligned_union_t<0,int,std::string> u;

    construct(reinterpret_cast<int*>(&u));

    return 0;
}