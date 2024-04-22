#include <stdio.h>
int main(){
    char last_name[22];
    printf ("Enter your last name: ");
    
    scanf ("%21s", last_name);
    if(strlen(last_name) > 20){
        printf("caught you hacker");
        return -1;
    }
    return 0;
}