#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void vulnerable_function()
{
    char *buffer = malloc(12);
    for (int i = 0; i < 30; i++)
    {
        buffer[i] = 'b';
    }

    char buffer2[16];
    int j = 0;
    while (j < 45)
    {
        buffer2[j] = 'b';
        j++;
    }
}

int main(int argc, char *argv[])
{
    vulnerable_function(argv[1]);
    return 0;
}
