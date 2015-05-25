class Speaker{

    public Speaker(){
    }

    public String content(){
        return "i'm original string'";
    }

    public String toString(){
        return this.content().toString();
    }
} 

class InstanceCreation2{

    private Speaker op = new Speaker();
    private Speaker sp = new Speaker(){
        public String content(){
            return "new content";
        }
    };

    public static void main (String [] args)
    {
        InstanceCreation2 ic = new InstanceCreation2();
        System.out.println("original speaker: " + ic.op.toString());
        System.out.println("rewrited speaker: " + ic.sp.toString());
    }

} 

