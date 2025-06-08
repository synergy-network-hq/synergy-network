import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.io.IOException;

public class PrimeSieve {

    public static void main(String[] args) {
        int N = 1000;
        boolean[] isPrime = new boolean[N];

        // a) Create a Boolean array with all elements initialized to true.
        for (int i = 0; i < N; i++) {
            isPrime[i] = true;
        }

        // Ignore array elements 0 and 1.
        if (N > 0) isPrime[0] = false;
        if (N > 1) isPrime[1] = false;

        // b) Starting with array index 2, determine whether a given element is true.
        for (int p = 2; p * p < N; p++) {
            // If isPrime[p] is true, then it is a prime
            if (isPrime[p]) {
                // Update all multiples of p
                for (int i = p * p; i < N; i += p) {
                    isPrime[i] = false;
                }
            }
        }

        int primeCount = 0;
        try (PrintWriter outputFile = new PrintWriter("primes.txt")) {
            for (int i = 2; i < N; i++) {
                if (isPrime[i]) {
                    outputFile.println(i + " is prime.");
                    primeCount++;
                }
            }
            outputFile.println(); // Empty line
            outputFile.println(primeCount + " primes found.");
        } catch (FileNotFoundException exception) {
            System.out.println("File Not Found");
        } catch (IOException exception) {
            System.out.println("An error occurred while writing to the file.");
        }
    }
}
