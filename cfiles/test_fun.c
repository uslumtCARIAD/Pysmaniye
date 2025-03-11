// C program to Find the Factorial Using for Loop

// do bigger functions with 25 vars
// 
int factorial(int num) {
    if (num == 1)
    {
        return 1;
    }
    return num * factorial(num - 1);
}
//int factorial2(int num) { return (num==1) ? 1 : num*factorial2(num-1); }


int main() {
    int N = 5;
    int fact = factorial(N);
    //printf("Factorial of %d is %d", N, fact);
    return 0;
}