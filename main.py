from handler import get_exam_content, create_exam_document, convert_to_QTI
from handler.const import DOCX_FILE, CONTENT_FILE, QTI_FILE
from datetime import datetime
import os
from enum import Enum

class Task(Enum):
	CONTENT = 1 # task get content from model ai
	QTI = 2 # task convert content.txt to QTI file
	DOCX = 3 # task convert content.txt to docx file

def uncomplete_run_detection() -> tuple[str, list[Task]]:
	path = './dist'
	if not os.path.exists(path):
		return ("", [])

	children: list[str] = []

	for entry in os.listdir(path):
		try:
			datetime.strptime(entry, '%Y%m%d_%H%M%S')
			children.append(entry)
		except:
			continue

	children.sort(key=lambda child: datetime.strptime(child, '%Y%m%d_%H%M%S'))

	latest_run = children[-1]
	task_to_complete = {Task.CONTENT, Task.QTI, Task.DOCX}

	for entry in os.listdir(os.path.join(path, latest_run)):
		if entry == CONTENT_FILE:
			task_to_complete.remove(Task.CONTENT)
		elif entry == QTI_FILE:
			task_to_complete.remove(Task.QTI)
		elif entry == DOCX_FILE:
			task_to_complete.remove(Task.DOCX)
	
	if len(task_to_complete) > 0:
		user_decision = input("The previous run doesn't seem to have finished yet, do you want to continue it? (y/n): ")
		if user_decision.lower() == 'y' or user_decision.lower() == 'yes':
			return (f"{path}/{latest_run}", list(task_to_complete))
		else:
			print("The new run is creating...")
			return ("", [])
	else:
		return ("", [])

def main():
	# Check if user want to re-run the previous uncompleted run
	uncompleted_tasks = uncomplete_run_detection()

	path, tasks_to_run = uncompleted_tasks
	if len(tasks_to_run) == 0:
		path = f"./dist/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
		if not os.path.exists(path):
			os.makedirs(path)
		tasks_to_run.extend([Task.CONTENT, Task.QTI, Task.DOCX])

	if Task.CONTENT in tasks_to_run:
		# Get exam content from API
		print("Đang tạo nội dung đề thi...")
		get_exam_content(path)
	
	content_file = open(f"{path}/{CONTENT_FILE}", "r", encoding="utf-8")
	exam_content = content_file.read()
	content_file.close()

	if Task.QTI in tasks_to_run:
		# Create QTI file
		print("Đang tạo tài liệu QTI...")
		convert_to_QTI(path, exam_content)

	if Task.DOCX in tasks_to_run:
		# Create document
		print("Đang tạo tài liệu docx...")
		create_exam_document(path, exam_content)

if __name__ == "__main__":
	main()