#include <stdio.h>
#include <string.h>
int main()
{
    char name[32];
    int age[4];
    char nationality[16];

    printf ("Enter your name: ");    
    scanf ("%s %d %s", name, age, nationality);
    printf ("%s\n", name);
    printf("%d\n", strlen(name));
    return 0;
}