#include<stdio.h>
#include <stdlib.h>
#include <time.h>
int main()
{
    int a,b;
   
    srand (time(NULL));
    a = rand() % 100 + 1;
    b = rand() % 100 + 1;

    printf("%d %d\n", a, b);

    return 0;
}