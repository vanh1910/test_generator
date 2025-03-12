# Exam Generator Tool

Exam Generator is a python tool for generating exam

This tool uses API from [OpenRouter](https://openrouter.ai/)

## Table of Contents
- [Installation](#installation)
- [Basic usage](#basic-usage)
- [Customizing the prompt](#customizing-the-prompt)

## Installation

**Requirements tool**: 
- python 3.8+

For Unix systems:
```bash
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

For Windows Powershell:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then, create a file `.env` at the root of the project and set variables like this:
```env
API_KEY='<YOUR_OPENROUTER_API_KEY>'
MODEL='<OPENROUTER_MODEL>'
```

**Note**: 
- `API_KEY` is required, `MODEL` is optional.
- If you don't set the `MODEL` variable, the tool will automatically use the `google/gemini-2.0-pro-exp-02-05:free` model.

## Basic usage

To run the tool, use following command:
```bash
python main.py
```

This is the output:
```yaml
dist/{timeCreated}:
  - content.txt # Response from OpenRouter API
  - qti.zip # QTI file for Canvas
  - dethi.docx # Microsoft Word File
```

## Customizing the prompt

You can modify default prompt in `prompt.txt` file to change the output content to whatever you want. 

However, you must ensure that the `content.txt` file follows the format below (assuming that option b is the correct answer):

```txt
[Number]. [Question]
a) [Option a]
*b) [Option b]
c) [Option c]
d) [Option d]
```

A correct answer always begins with a asterisk (*). Each question is separated by a blank line.

About multi-line question or multi-line answer:

```txt
|
| /* Indentation:
| Question or answer that oppucies more than 1 line 
| must have at least this indentation*/
| |
1. [Question]
| |
| [Question continued, so indentation]
| |
a) [Possible answer]
| |
| [Possible answer continued, so indentation]
| |
*b) [Correct answer]
|
...
```

For example:

```txt
1. Thuộc tính CSS nào được sử dụng để thay đổi màu chữ của một phần tử?
a) `font-color`
*b) `color`
c) `text-color`
d) `foreground-color`

2. Đoạn mã:
	```
	<ol type="A" start="3">
		<li>Item 1</li>
		<li>Item 2</li>
	</ol>
	```
	Kết quả hiển thị sẽ như thế nào?
a) 1. Item 1
	2. Item 2
b) A. Item 1
	B. Item 2
*c) C. Item 1
	D. Item 2
d) 3. Item 1
	4. Item 2
```

**Note**: code block like HTML tags should be put in backticks to ensure QTI output is correct.

### Comment in prompt:

Use `//` or `/**/` syntax to comment in your prompt.

```txt
// This line isn't included in the prompt

/*
This is also comment 
and isn't included.
*/
```

## Directory Structure

```yaml
handler:
  - apiHandler # Handler prompting and returning responses from OpenRouter API
  - convertHandler # Handler converting exam content to QTI file
  - docxHandler # Handler generating file docx
main # Entry point
test
```