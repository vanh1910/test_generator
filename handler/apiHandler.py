from openai import OpenAI
import os
import dotenv

dotenv.load_dotenv()

API_KEY = os.environ.get('API_KEY')
BASE_URL = 'https://openrouter.ai/api/v1/'
MODEL = 'google/gemini-2.0-pro-exp-02-05:free'

def get_prompt():
	# Read prompt content from file prompt.txt
	prompt_file = open('prompt.txt', 'r',encoding="utf-8")
	prompt_content = prompt_file.read()
	prompt_file.close()

	return prompt_content

def get_exam_content(path: str):
	client = OpenAI(
		api_key=API_KEY,
		base_url=BASE_URL
	)
	
	response = client.chat.completions.create(
		model=MODEL,
		messages=[
			{"role": "user", "content": get_prompt()}
		]
	)
	content = response.choices[0].message.content
	
	# Save response from OpenRouter API to file content.txt
	log_name = "content.txt"
	log = open(f"{path}/{log_name}", "w+",encoding="utf-8")

	log.write(content)

	log.close()

	return content