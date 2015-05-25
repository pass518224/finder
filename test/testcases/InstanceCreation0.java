class InstanceCreation0{

    public static void main (String [] args)
    {
        System.out.println(new Speaker("hello"));
        System.out.println(new Speaker("hello"){

            public String flag(){
                return "my speaker: ";
            }
        });
    }

} 

class Speaker{
    private String sentence;
    public Speaker(String sentence){
        this.sentence = sentence;
    }

    public String flag(){
        return "original speaker: ";
    }

    public String toString(){
        return flag() + this.sentence;
    }
} 
