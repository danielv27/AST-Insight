#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void vulnerable_function(const char *input) {
    // Allocate memory for a 16-byte buffer on the heap
    char *buffer = (char *)malloc(16);

    buffer[19] = 'b';

    for(int i = 0; i < 30; i++){
        buffer[i] = 'b';
    }

    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return;
    }

    // Copy input data to buffer using memcpy, without checking the length of the input
    memcpy(buffer, input, strlen(input) + 1);

    // Print the buffer content
    printf("Buffer content: %s\n", buffer);

    // Free the allocated memory
    free(buffer);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <input>\n", argv[0]);
        return 1;
    }

    // Call the vulnerable function with user-provided input
    vulnerable_function(argv[1]);

    return 0;
}
