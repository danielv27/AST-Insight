// Basic Heap overflow example. Resource: https://cwe.mitre.org/data/definitions/122.html
#define BUFSIZE 256
int main(int argc, char **argv)
{
    int x = 5;
    int *num;
    char *buf = malloc(BUFSIZE);
    *buf2 = malloc(BUFSIZE);
    strcpy(buf, argv[1]);
}