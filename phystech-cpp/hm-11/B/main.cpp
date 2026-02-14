#include <iostream>
#include <type_traits>

template< class T >
struct add_const;

template< class T >
struct remove_const;

template< class T >
using add_const_t    = typename add_const<T>::type;

template< class T >
using remove_const_t = typename remove_const<T>::type;

template<class T> struct add_const {
    typedef const T type;
};

template< class T > struct remove_const {
    typedef T type;
};

template<class T>
void g(const T&, std::add_const_t<T>&);

int main() {
    
    return 0;
}