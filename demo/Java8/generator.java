import java.util.Scanner;
import java.util.Random;

class sample_generator {
    public static void main(String args[]) {
        int x, y;
        Random rand = new Random();
        x = rand.nextInt(50) + 1;
        y = rand.nextInt(50) + 1;
        System.out.println(x + " " + y);
    }
}
