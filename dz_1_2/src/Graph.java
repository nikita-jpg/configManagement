public class Graph {
    static String result="digraph G{\n";
    private static String mains = "";
    private static String depend = "";

    public static void reStart(String text)
    {
        result = "digraph G{\n";
    }
    public static void add(String a,String b)
    {

        if(!mains.contains(b) && !depend.contains(b)){
            result+=  "\"" + a + "\"" + " -> " + "\"" + b + "\"" + ";\n";
        }

        if(!mains.contains(a))
            mains+=a;

        if(!depend.contains(b))
            depend+=b;

    }
    public static void close()
    {
        result+="}";
    }
    public static void showGraph()
    {
        System.out.println(result);
    }

    public static boolean containDep(String dep)
    {
        return depend.contains(dep);
    }
}
