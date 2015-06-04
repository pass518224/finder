class Printer{
    public Printer(){
    }

    public void print(String str){
        System.out.println(str);
    }
}
class Machine{
    public Printer from;
    public Machine(){
        this.from = new Printer();
    }
} 
public final class Keyword0 {
    public static void main (String [] args)
    {
        Machine m = new Machine();
        m.from.print("haha");
    }
}
