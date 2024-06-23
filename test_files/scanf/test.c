#include <stdio.h>

int fn1(int number){
    if(number == 1){
        return 1;
    }
    return 0;
}

int fn2(int number){
    if(number == 2){
        return 1;
    }
    return 0;
}

int main() {
    int buf[256];

    buf[1] = 10;
    // int number = 2;
    // int x = fn1(number);
    // int y = fn2(number);
    // if(x || y){
        printf("Hellow World\n");
    // } else {
        printf("Goodbye World\n");
    // }
    return 0;
}
