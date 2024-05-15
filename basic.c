#include <stdio.h>
int main(){
    char last_name[18];
    char greetings[] = "Hello World!";
    printf ("Enter your last name: ");
    
    scanf ("%17s", last_name);
    if(strlen(last_name) > 20){
        printf("caught you hacker");
        return -1;
    }
    return 0;
}