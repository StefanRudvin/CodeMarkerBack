#include <iostream>
#include <cstdlib>
#include <ctime>
using namespace std;

int main()
{
    int firstNumber, secondNumber;
   
    srand (time(NULL));
    firstNumber = rand() % 100 + 1;
    secondNumber = rand() % 100 + 1;

    cout << firstNumber << " " << secondNumber << endl;

    return 0;
}