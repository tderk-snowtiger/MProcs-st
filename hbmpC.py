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
		print("DISCLAIMER: This works on Android and must have Termux and Termux-API installed from F-Droid and Google Text-to-Speech options set to 'Korean'")
		print()
		print("Created by tderk")
		print()
		print("'FNTCCI (H)'")
		print()

		time.sleep(.3)

		fcci = ["ga", "gya", "geo", "gyeo", "go", "gyo", "gu", "gyu", "geu", "gi", "gae", "gyae", "ge", "gye", "gwa", "gwae", "goe", "gwo", "gwe", "gwi", "gui", "kka", "kkya", "kkeo", "kkyeo", "kko", "kkyo", "kku", "kkyu", "kkeu", "kki", "kkae", "kkyae", "kke", "kkye", "kkwa", "kkwae", "kkoe", "kkwo", "kkwe", "kkwi", "kkui", "na", "nya", "neo", "nyeo", "no", "nyo", "nu", "nyu", "neu", "ni", "nae", "nyae", "ne", "nye", "nwa", "nwae", "noe", "nwo", "nwe", "nwi", "nui", "da", "dya", "deo", "dyeo", "do", "dyo", "du", "dyu", "deu", "di", "dae", "dyae", "de", "dye", "dwa", "dwae", "doe", "dwo", "dwe", "dwi", "dui", "tta", "ttya", "tteo", "ttyeo", "tto", "ttyo", "ttu", "ttyu", "tteu", "tti", "ttae", "ttyae", "tte", "ttye", "ttwa", "ttwae", "ttoe", "ttwo", "ttwe", "ttwi", "ttui", "ra", "rya", "reo", "ryeo", "ro", "ryo", "ru", "ryu", "reu", "ri", "rae", "ryae", "re", "rye", "rwa", "rwae", "roe", "rwo", "rwe", "rwi", "rui", "ma", "mya", "meo", "myeo", "mo", "myo", "mu", "myu", "meu", "mi", "mae", "myae", "me", "mye", "mwa", "mwae", "moe", "mwo", "mwe", "mwi", "mui", "ba", "bya", "beo", "byeo", "bo", "byo", "bu", "byu", "beu", "bi", "bae", "byae", "be", "bye", "bwa", "bwae", "boe", "bwo", "bwe", "bwi", "bui", "ppa", "ppya", "ppeo", "ppyeo", "ppo", "ppyo", "ppu", "ppyu", "ppeu", "ppi", "ppae", "ppyae", "ppe", "ppye", "ppwa", "ppwae", "ppoe", "ppwo", "ppwe", "ppwi", "ppui", "sa", "sya", "seo", "syeo", "so", "syo", "su", "syu", "seu", "si", "sae", "syae", "se", "sye", "swa", "swae", "soe", "swo", "swe", "swi", "sui", "ssa", "ssya", "sseo", "ssyeo", "sso", "ssyo", "ssu", "ssyu", "sseu", "ssi", "ssae", "ssyae", "sse", "ssye", "sswa", "sswae", "ssoe", "sswo", "sswe", "sswi", "ssui", "a", "ya", "eo", "yeo", "o", "yo", "u", "yu", "eu", "i", "ae", "yae", "e", "ye", "wa", "wae", "oe", "wo", "we", "wi", "ui", "ja", "jya", "jeo", "jyeo", "jo", "jyo", "ju", "jyu", "jeu", "ji", "jae", "jyae", "je", "jye", "jwa", "jwae", "joe", "jwo", "jwe", "jwi", "jui", "jja", "jjya", "jjeo", "jjyeo", "jjo", "jjyo", "jju", "jjyu", "jjeu", "jji", "jjae", "jjyae", "jje", "jjye", "jjwa", "jjwae", "jjoe", "jjwo", "jjwe", "jjwi", "jjui", "cha", "chya", "cheo", "chyeo", "cho", "chyo", "chu", "chyu", "cheu", "chi", "chae", "chyae", "che", "chye", "chwa", "chwae", "choe", "chwo", "chwe", "chwi", "chui", "ka", "kya", "keo", "kyeo", "ko", "kyo", "ku", "kyu", "keu", "ki", "kae", "kyae", "ke", "kye", "kwa", "kwae", "koe", "kwo", "kwe", "kwi", "kui", "ta", "tya", "teo", "tyeo", "to", "tyo", "tu", "tyu", "teu", "ti", "tae", "tyae", "te", "tye", "twa", "twae", "toe", "two", "twe", "twi", "tui", "pa", "pya", "peo", "pyeo", "po", "pyo", "pu", "pyu", "peu", "pi", "pae", "pyae", "pe", "pye", "pwa", "pwae", "poe", "pwo", "pwe", "pwi", "pui", "ha", "hya", "heo", "hyeo", "ho", "hyo", "hu", "hyu", "heu", "hi", "hae", "hyae", "he", "hye", "hwa", "hwae", "hoe", "hwo", "hwe", "hwi", "hui", ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
		
		maroon = "^m^"

		nano = (fcci)

		s = open("hbmp.txt", "a", buffering=1)

		ct = datetime.datetime.now()

		monitor = "hbmp-start:"
		print(monitor, ct)
		print(monitor, ct, file=s)
		print()
		print("*this saves to hbmp.txt*")
		print()
		print(file=s)

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
			print(maroon, random_letters, sitch, result_text, ctm, file=s)

			speak(result_text)

			print()
			print(file=s)
	        
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

		s.close()

	bmp()

if __name__ == "__main__":
	main()