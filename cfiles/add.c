

int add_function(int num1, int num2, int num3, int num4, int num5)
{
    if (num1>5)
    {
        for (int i = 0; i < num1; i++)
        {
            num2++;
            num3++;
            num4++; 
            num5++;
        }
        return num5;
    }
    
    else if (num1<5)
    {
        for (int i = 0; i < num1; i++)
        {
            num2--;
            num3--;
            num4--; 
            num5--;
        }
        return num5;
    }

    else {
        return  num1 +  num2 +  num3 + num4 + num5;
    }
        
}

int main ()

{
    int a = 5;
    int b = 2;
    int c = 3; 
    int d = 4;
    int f = 1;
    add_function(a,b,c,d,f);
}