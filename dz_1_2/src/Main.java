import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.select.Elements;

import java.io.*;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

public class Main {

    public static final String urlStr = "https://pypi.org/simple/";
    private static int deep = 5;
    private static List<String> files = new ArrayList<>();
    public static void main(String args[])
    {

        String inputString;
        Link[] links;
        Link chosenLink = null;
        LinkedHashMap<String,String> dependences;
        System.out.print("Введите название нужного пакета:");
        inputString = new Scanner(System.in).nextLine();

        try {
            links = downloadHtml(inputString);//Получили список версий для нужного пакета
            if(links!=null && links.length!=0) 
                chosenLink = choiceVersion(links);//Выбрали нужную версию
            else
                System.out.println();
            
            dependences = getDependences(chosenLink.getUrl(),chosenLink.getName());//Получаем зависимости для данной версии;
            rec(inputString,dependences,2);//Рекурсивная функция по поиску зависимостей
            Graph.close();
            Graph.showGraph();
            delete();//Чистим память

        } catch (IOException e) {
            e.printStackTrace();
        }

    }


    private static Link[] downloadHtml(String packageName) {
        try {
            //Получаем html
            Document doc;
            doc = Jsoup.connect(urlStr+packageName+"/").get();

            //Распарсиваем html
            Elements elements = doc.select("a:contains(.whl)");


            Link[] links = new Link[elements.size()];
            for (int i=0;i<links.length;i++)
                links[i] = new Link();

            //Сохраняем названия пакетов и ссылки для них
            for(int i =0;i<elements.size();i++)
            {
                links[i].setIndex(i+1);
                links[i].setName(elements.get(i).text());
                links[i].setUrl(new URL(elements.get(i).attr("href")));
                Pattern pattern = Pattern.compile("-\\w+\\.\\w+\\.\\w+|-\\w+\\.\\w+|-\\w+");
                Matcher matcher = pattern.matcher(elements.get(i).text());
                if(matcher.find())
                    links[i].setVersion(elements.get(i).text().substring(matcher.start()+1,matcher.end()));
                else
                    links[i].setVersion("");
            }
            return links;
        } catch (IOException e) {
            return null;
        }
    }

    private static Link choiceVersion(Link[] links) {

        //Выводим список доступных для загрузки пакетов
        for(int i=0;i<links.length;i++)
            System.out.println(links[i].getIndex()+")"+links[i].getName().substring(0,links[i].getName().length()-4));

        System.out.print("Введите номер необходимого пакета:");
        int number = new Scanner(System.in).nextInt();
        return links[number-1];
    }

    private static LinkedHashMap<String,String> getDependences(URL url, String fileName) {

        fileName = fileName+".zip";
        LinkedHashMap<String,String> map = new LinkedHashMap<>();
        String patternNameStr = "\\s[\\S&&[^\\[;]]+";
        String patternVersionStr = "\\([.+&&[^a-z]]\\)";
        Pattern patternName = Pattern.compile(patternNameStr);
        Pattern patternVersion = Pattern.compile(patternVersionStr);
        Matcher matcherName;
        Matcher matcherVersion;
        URLConnection urlConnection;

        try {
            //Скачиваем файл
            urlConnection = url.openConnection();
            InputStream inputStream = urlConnection.getInputStream();

            //Сохраняем файл как архив
            File file = new File(fileName);
            files.add(fileName);
            FileOutputStream fileOutputStream = new FileOutputStream(file);
            fileOutputStream.write(inputStream.readAllBytes());
            fileOutputStream.close();

            //Открываем наш файл как архив
            ZipFile zipFile = new ZipFile(fileName);

            //Ищем файл "METADATA"
            for( Enumeration<? extends ZipEntry> iter = zipFile.entries();iter.hasMoreElements();)
            {
                ZipEntry zipEntry = iter.nextElement();
                if(zipEntry.getName().contains("METADATA"))
                {
                    InputStream inputStream1 = zipFile.getInputStream(zipEntry);
                    BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream1));
                    String string;

                    //Сохраняем данные о зависимостях в map
                    while ((string=bufferedReader.readLine())!=null)
                    {
                        if(string.contains("Requires-Dist"))
                        {
                            matcherName = patternName.matcher(string);
                            matcherVersion = patternVersion.matcher(string);

                            String name = "";
                            String version = "";

                            matcherName.find();
                            name = string.substring(matcherName.start()+1,matcherName.end());
                            if(matcherVersion.find())
                                version = string.substring(matcherVersion.start()+1,matcherVersion.end()-1);

                            map.put(name,version);
                        }
                    }
                    return map;
                }
            }
        } catch (IOException e) {
            return map;
        }


        return map;
    }

    private static void rec(String main,LinkedHashMap<String,String> dependences,int curDeep) throws IOException {

        if(curDeep>deep)
            return;

        Set set = dependences.entrySet();
        Iterator iterator = set.iterator();
        List<String> arr = new ArrayList<>();


        Link[] links;
        Link chosenLink;
        LinkedHashMap<String,String> dependencesNew;

        while (iterator.hasNext())
        {
            String dep = ((Map.Entry) iterator.next()).getKey().toString();
            if(!Graph.containDep(dep))
            {
                Graph.add(main, dep);
                arr.add(dep);

                links = downloadHtml(dep);
                if(links!= null && links.length!=0)
                {
                    chosenLink = chosenLink(links,dependences.get(dep));
                    if(chosenLink != null)
                    {
                        dependencesNew = getDependences(chosenLink.getUrl(),chosenLink.getName());
                        if(dependencesNew.size()!=0)
                            rec(dep,dependencesNew,curDeep+1);
                    }
                }
            }
        }
        return;
    }

    private static Link chosenLink(Link[] links, String version)
    {

        if(version.equals(""))
            return links[links.length-1];

        String[][] arr;//Вид: [i][0]:Логическое выражение, [i][1]:Версия
        Pattern logPattern = Pattern.compile("\\D+\\d");
        Matcher logMather;

        String[] expressions = version.split(",");
        arr = new String[expressions.length][2];

        //Распарсиваем version и заполняем arr
        for(int j=0;j<expressions.length;j++)
        {
            logMather = logPattern.matcher(expressions[j]);
            logMather.find();
            arr[j][0] = expressions[j].substring(logMather.start(),logMather.end()-1);
            arr[j][1] = expressions[j].substring(logMather.end()-1);
        }

        //Ищем подходящую версию
        for(int i = links.length-1;0<=i;i--)
        {
            for(int j=0;j<arr.length;j++)
            {
                if(compareString(links[i].getVersion(),arr[j][1],arr[j][0]))
                    return links[i];
            }
        }
        return null;

    }
    private static boolean compareString(String a,String b,String log)
    {
        log = log.replace('~','!');

        switch (log)
        {
            case ">":
                if(a.compareTo(b)>0)
                    return true;
                break;

            case "<":
                if(a.compareTo(b)<0)
                    return true;
                break;

            case "=":
                if(a.compareTo(b) == 0)
                    return true;
                break;

            case ">=":
                if(a.compareTo(b)>=0)
                    return true;
                break;

            case "<=":
                if(a.compareTo(b)<=0)
                    return true;
                break;

            case "!>":
                if(a.compareTo(b)<=0)
                    return true;
                break;

            case "!<":
                if(a.compareTo(b)>=0)
                    return true;
                break;

            case "!=":
                if(a.compareTo(b)!=0)
                    return true;
                break;

            default:
                return false;
        }

        return false;
    }

    private static void delete()
    {
        File file;
        for (int i=0;i<files.size();i++)
        {
            file = new File(files.get(i));
            file.delete();
        }
    }

}
