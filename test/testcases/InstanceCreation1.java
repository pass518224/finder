class Calculator{
    public Calculator(){
    }

    public int calculate(int a, int b){
        return a+b;
    }
} 

class InstanceCreation1{

    public static void main (String [] args)
    {
        Calculator origin = new Calculator();
        Calculator newone = new Calculator(){

            public int calculate(int a, int b){
                return a*b;
            }
        };
        System.out.println("origin: (5,10) = ");
        System.out.println(origin.calculate(5,10));
        System.out.println("newone: (5,10) = ");
        System.out.println(newone.calculate(5,10));
    }

} 

