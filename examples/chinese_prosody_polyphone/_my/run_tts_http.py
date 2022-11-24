import requests
import argparse

api_address = "http://172.31.208.11:8081/generate"  # A100: http://172.31.208.11:8081/generate

request_payload_tmpl = {
	"text": "这是一个端到端的中文语音合成系统",
	"voice": "SSB3002",
	"format": "wav",
	"sample_rate": 22050,
	"volume": 50,
	"speech_rate": 0,
	"pitch_rate": 0,
	"energy_rate": 0,
	"enable_subtitle": False,
}


def convert_prosody_to_ssml(text):
	prosody_ssml_map = {
		' #3 ': '<break time="sp1" />',
		' #2 ': '<break time="sp0" />',
	}
	for k, v in prosody_ssml_map.items():
		text = text.replace(k, v)
	return f'<speak>{text}</speak>'


# resp = requests.post(api_address, json=request_payload)
# open("demo.wav", "wb").write(resp.content)

if __name__ == '__main__':
	import sys
	import os

	# text_file = sys.argv[1]
	# out_dir = sys.argv[2]
	
	parser = argparse.ArgumentParser()
	parser.add_argument('text_file', help='input text file')
	parser.add_argument('out_dir', help='output audio dir')
	parser.add_argument('--has_prosody', type=bool, default=True)

	args = parser.parse_args()
	
	text_file = args.text_file
	out_dir = args.out_dir
	has_prosody = args.has_prosody

	with open(text_file) as fin:
		for i, line in enumerate(fin, start=1):
			line = line.strip()

			# utt_id = f'{i:02d}'
			utt_id, text = line.split(maxsplit=1)  # has id

			if has_prosody:
				text = convert_prosody_to_ssml(text)			
			print(f'utt {utt_id} | text {text}')

			request_payload = request_payload_tmpl.copy()
			request_payload['text'] = text

			resp = requests.post(api_address, json=request_payload)

			os.makedirs(out_dir, exist_ok=True)
			with open(f"{out_dir}/{utt_id}.wav", "wb") as fp:
				fp.write(resp.content)
		# pass
	# pass
