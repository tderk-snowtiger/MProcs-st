import random
import time
import datetime
import string
import threading
import subprocess
import platform
import os

def main():

	def bmp():

		def speak(text):
			try:
				if platform.system() == "Windows":
					subprocess.run(["termux-tts-speak", text], check=True)
				else:
					subprocess.run(["termux-tts-speak", text], check=True)

			except FileNotFoundError:
				print()
				print("X")

			except subprocess.CalledProcessError as e:
				print(f"Text-to-speech error: {e}")

		time.sleep(.3)

		print()
		print("DISCLAIMER: This works on Android and must have Termux and Termux-API installed from F-Droid and Google Text-to-Speech options set to 'Japanese'")
		print()
		print("Created by tderk")
		print()
		print("'FNTCCI (J)'")
		print()

		time.sleep(.3)

		fcci = ["a", "i", "u", "e", "o", "ka", "ki", "ku", "ke", "ko", "kya", "kyu", "kyo", "ga", "gi", "gu", "ge", "go", "gya", "gyu", "gyo", "sa", "shi", "su", "se", "so", "sha", "shu", "sho", "za", "ji", "zu", "ze", "zo", "ja", "ju", "jo", "ta", "chi", "tsu", "te", "to", "cha", "chu", "cho", "da", "de", "do", "na", "ni", "nu", "ne", "no", "nya", "nyu", "nyo", "ha", "hi", "fu", "he", "ho", "hya", "hyu", "hyo", "ba", "bi", "bu", "be", "bo", "bya", "byu", "byo", "pa", "pi", "pu", "pe", "po", "pya", "pyu", "pyo", "ma", "mi", "mu", "me", "mo", "mya", "myu", "myo", "ya", "yu", "yo", "ra", "ri", "ru", "re", "ro", "rya", "ryu", "ryo", "wa", "wo", "n", ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']

		maroon = "^m^"

		nano = (fcci)

		ct = datetime.datetime.now()

		monitor = "xjbmp-start:"
		print(monitor, ct)
		print()

		def generate_random_result():

			ctm = datetime.datetime.now()

			def generate_random_letters():
				random1 = random.choice(string.ascii_letters)
				random2 = random.choice(string.ascii_letters)
				random3 = random.choice(string.ascii_letters)
				letters = [random1, random2, random3]
				return letters

			random_letters = generate_random_letters()

			sitch  = (round(random.random()*9999,4))

			cci = random.sample(nano, random.randint(1,10))

			result_text = "".join(cci)

			print(maroon, random_letters, sitch, result_text, ctm)

			speak(result_text)

			print()
	        
		def main_loop():
			while True:
				time.sleep(random.randint(0,6))
				integer = (round(random.random()*18))
				if integer > 10:
					if random.choice([True, False]):
						generate_random_result()

		try:
			main_loop()
		except KeyboardInterrupt:
			print("\nStopped by user.")

	bmp()

if __name__ == "__main__":
	main()