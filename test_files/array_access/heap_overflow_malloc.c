#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void vulnerable_function(const char *input) 
{
    char *buffer = (char *)malloc(12);
    
    for(int i = 0; i < 30; i++)
    {
        buffer[i - 5] = 'b';
    }


    char *buffer2 = (char *)malloc(15);
    int j = 0;
    while(j < 45){
        buffer2[j - 5] = 'b';
        j++;
    }
}

int main(int argc, char *argv[]) {
    vulnerable_function(argv[1]);
    return 0;
}
