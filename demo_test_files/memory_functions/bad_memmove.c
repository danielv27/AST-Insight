static void bad_memmove()
{
    int *source = malloc(10);
    int *dest = malloc(9);
    memmove(dest, source, 10 * sizeof(int));
}