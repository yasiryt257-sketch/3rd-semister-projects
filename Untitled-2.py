
import random

print("🎮 Welcome to the Number System Game!")
print("Guess the secret number between 1 and 100.")

secret_number = random.randint(1, 100)
attempts = 0

while True:
    try:
        guess = int(input("Enter your guess: "))
        attempts += 1

        if guess < 1 or guess > 100:
            print("Please enter a number between 1 and 100.")
        elif guess < secret_number:
            print("Too low! Try a bigger number.")
        elif guess > secret_number:
            print("Too high! Try a smaller number.")
        else:
            print("🎉 Congratulations! You guessed it!")
            print("Secret number:", secret_number)
            print("Attempts:", attempts)
            break

    except ValueError:
        print("Invalid input! Please enter a whole number.")

print("Thanks for playing!")
