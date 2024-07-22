int main()
{
    char name[32];
    printf ("Enter your name: ");    
    scanf ("%s %d", name);
    printf ("%s\n", name);
    printf("%d\n", strlen(name));
    return 0;
}