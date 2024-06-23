// Basic Heap overflow example. Resource: https://cwe.mitre.org/data/definitions/122.html
#define BUFSIZE 32
int main(int argc, char **argv)
{
    int x = 5;
    char *buf = malloc(BUFSIZE);
    int *buf2;
    *buf2 = malloc(BUFSIZE);
    strcpy(buf, argv[1]);
}