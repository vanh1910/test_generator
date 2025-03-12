from openai import OpenAI
import os
import dotenv
from handler.const import CONTENT_FILE

dotenv.load_dotenv()

API_KEY = os.environ.get('API_KEY')
BASE_URL = 'https://openrouter.ai/api/v1/'
MODEL = os.environ.get('MODEL')

if MODEL is None:
	MODEL = 'google/gemini-2.0-pro-exp-02-05:free'

def get_prompt():
	# Read prompt content from file prompt.txt
	prompt_file = open('prompt.txt', 'r',encoding='utf-8')
	prompt_content = prompt_file.read()

	# Remove comments from prompt content
	stack_comment_symbols = []
	buffer_comment_symbols = ""
	parsed_prompt_content = ""
	for index, char in enumerate(prompt_content):
		if len(stack_comment_symbols) > 0:
			if stack_comment_symbols[-1] == '//':
				if char == '\n': 
					parsed_prompt_content += '\n'
					stack_comment_symbols.pop()
				continue
			elif stack_comment_symbols[-1] == '/*':
				if char == '/' and index - 1 >= 0 and prompt_content[index - 1] == '*':
					stack_comment_symbols.pop()
				continue
			else:
				raise SyntaxError(f'Invalid comment syntax: {stack_comment_symbols[-1]}')
		if char == '/':
			if buffer_comment_symbols == '/':
				stack_comment_symbols.append("//")
				buffer_comment_symbols = ""
			elif buffer_comment_symbols == '':
				buffer_comment_symbols = "/"
			else:
				raise BufferError(f"Invalid comment syntax in buffer: {buffer_comment_symbols}")
		elif char == '*':
			if buffer_comment_symbols == '/':
				stack_comment_symbols.append("/*")
				buffer_comment_symbols = ""
			elif buffer_comment_symbols == '':
				parsed_prompt_content += char
			else:
				raise BufferError(f"Invalid comment syntax in buffer: {buffer_comment_symbols}")
		else:
			if buffer_comment_symbols == '/':
				parsed_prompt_content += buffer_comment_symbols
				parsed_prompt_content += char
				buffer_comment_symbols = ""
			elif buffer_comment_symbols == '':
				parsed_prompt_content += char
			else:
				raise BufferError(f"Invalid comment syntax in buffer: {buffer_comment_symbols}")

	prompt_file.close()

	return parsed_prompt_content

def get_exam_content(path: str):
	print(f"Model AI đang sử dụng: {MODEL}")
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
	log = open(f"{path}/{log_name}", "w+")

	log.write(content)

	log.close()