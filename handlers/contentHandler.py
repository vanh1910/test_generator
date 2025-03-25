import os
import random
from pathlib import Path

import dotenv
import toml
from openai import OpenAI
from rich import print
from rich.prompt import Confirm
from toml import TomlDecodeError

from handlers.const import CONTENT_FILE

dotenv.load_dotenv()

API_KEY = os.environ.get("API_KEY")
BASE_URL = "https://openrouter.ai/api/v1/"
MODEL = os.environ.get("MODEL") or "google/gemini-2.0-pro-exp-02-05:free"


def get_prompt(prompt_dir: str):
    with open(prompt_dir, "r", encoding="utf-8") as prompt_file:
        # Read prompt content from file at prompt_dir
        prompt_content = prompt_file.read()

        # Remove comments from prompt content
        stack_comment_symbols = []
        buffer_comment_symbols = ""
        parsed_prompt_content = ""
        for index, char in enumerate(prompt_content):
            if len(stack_comment_symbols) > 0:
                if stack_comment_symbols[-1] == "//":
                    if char == "\n":
                        parsed_prompt_content += "\n"
                        stack_comment_symbols.pop()
                    continue
                elif stack_comment_symbols[-1] == "/*":
                    if (
                        char == "/"
                        and index - 1 >= 0
                        and prompt_content[index - 1] == "*"
                    ):
                        stack_comment_symbols.pop()
                    continue
                else:
                    raise SyntaxError(
                        f"Invalid comment syntax: {stack_comment_symbols[-1]}"
                    )
            if char == "/":
                if buffer_comment_symbols == "/":
                    stack_comment_symbols.append("//")
                    buffer_comment_symbols = ""
                elif buffer_comment_symbols == "":
                    buffer_comment_symbols = "/"
                else:
                    raise BufferError(
                        f"Invalid comment syntax in buffer: {buffer_comment_symbols}"
                    )
            elif char == "*":
                if buffer_comment_symbols == "/":
                    stack_comment_symbols.append("/*")
                    buffer_comment_symbols = ""
                elif buffer_comment_symbols == "":
                    parsed_prompt_content += char
                else:
                    raise BufferError(
                        f"Invalid comment syntax in buffer: {buffer_comment_symbols}"
                    )
            else:
                if buffer_comment_symbols == "/":
                    parsed_prompt_content += buffer_comment_symbols
                    parsed_prompt_content += char
                    buffer_comment_symbols = ""
                elif buffer_comment_symbols == "":
                    parsed_prompt_content += char
                else:
                    raise BufferError(
                        f"Invalid comment syntax in buffer: {buffer_comment_symbols}"
                    )

    return parsed_prompt_content


def toml_to_dict(content_toml: str):
    lines = content_toml.splitlines()
    if lines[0] == "```toml" and lines[-1] == "```":
        content_dict = toml.loads("\n".join(lines[1:-1]))
    else:
        content_dict = toml.loads(content_toml)
    return content_dict


def dict_to_qti_compatible(content_dict: dict, shuffle: bool):
    def _get_indented_multiline_str(s: str):
        lines = [line.strip() for line in s.splitlines()]
        result = lines[0]
        for line in lines[1:]:
            result += f"\n        {line}"  # Should be enough
        return result

    content = ""
    problems = [value for _, value in sorted(content_dict.items())]
    if shuffle:
        random.shuffle(problems)

    for i, problem in enumerate(problems):
        content += f"{i + 1}. {_get_indented_multiline_str(problem['question'])}\n"
        for j, choice in enumerate(problem["choices"]):
            choice_prefix = (
                f"{'*' if j == problem['correct_index'] else ''}{chr(ord('a') + j)})"
            )
            content += f"{choice_prefix} {_get_indented_multiline_str(choice)}\n"
        content += "\n"

    return content


def get_exam_content(mode: str, path: str, prefer_llm: bool, shuffle: bool):
    content_dir = f"{path}/{CONTENT_FILE}"

    if mode == "manual":
        print(
            (
                "[blue]│   └── [/blue]"
                f"[green]Nội dung đề thi định dạng QTI-compatible sẽ được đọc từ: [white]{content_dir}[/white][/green]"
            )
        )

        with open(content_dir, "r", encoding="utf-8") as log:
            return log.read()

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    if mode == "generated_qti":
        # _bqn: i'm not maintaining this
        content = ""

        for prompt_dir in sorted(Path("prompts").iterdir()):
            prompt_name = prompt_dir.stem

            print(
                (
                    "[blue]│   ├── [/blue]"
                    f"[green]Đang xử lí prompt [white]{prompt_name}[/white]...[/green]"
                )
            )

            log_dir = f"{path}/logs/{prompt_name}.txt"
            content_curr = ""

            do_let_llm_generate_content = prefer_llm or Confirm.ask(
                f"[yellow]Bạn có muốn để [white]{MODEL}[/white] sinh nội dung của [white]{log_dir}[/white]?[/yellow]"
            )

            if do_let_llm_generate_content:
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": get_prompt(prompt_dir)}],
                )
                content_curr = response.choices[0].message.content
                assert content_curr is not None

                with open(log_dir, "w+", encoding="utf-8") as log:
                    log.write(content_curr)
            else:
                with open(log_dir, "r", encoding="utf-8") as log:
                    content_curr = log.read()

            content += f"{content_curr}\n"

            print(
                (
                    "[blue]│   │   └── [/blue]"
                    + f"[green]Đã đọc nội dung đề thi được sinh bởi prompt [white]{prompt_name}[/white] thành công.[/green]"
                )
            )

        with open(content_dir, "w+", encoding="utf-8") as log:
            log.write(content)

    if mode == "generated_toml":
        content_dict = {}

        for prompt_dir in sorted(Path("prompts").iterdir()):
            prompt_name = prompt_dir.stem

            print(
                (
                    "[blue]│   ├── [/blue]"
                    f"[yellow]Đang xử lí prompt [white]{prompt_name}[/white]..."
                )
            )

            log_dir = f"{path}/logs/{prompt_name}.toml"
            content_curr_dict = {}

            n_attempts = 0
            succeeded = False
            while not succeeded:
                n_attempts += 1

                print(
                    (
                        "[blue]│   │   ├── [/blue]"
                        f"[yellow]Lần chạy #{n_attempts}...[/yellow]"
                    )
                )

                do_let_llm_generate_content = prefer_llm or Confirm.ask(
                    f"[yellow]Bạn có muốn để [white]{MODEL}[/white] sinh nội dung của [white]{log_dir}[/white]?[/yellow]"
                )

                try:
                    if do_let_llm_generate_content:
                        response = client.chat.completions.create(
                            model=MODEL,
                            messages=[
                                {"role": "user", "content": get_prompt(prompt_dir)}
                            ],
                        )
                        content_curr_raw = response.choices[0].message.content
                        assert content_curr_raw is not None

                        with open(log_dir, "w+", encoding="utf-8") as log:
                            log.write(content_curr_raw)
                    else:
                        with open(log_dir, "r", encoding="utf-8") as log:
                            content_curr_raw = log.read()
                    content_curr_dict = toml_to_dict(content_curr_raw)
                    succeeded = True

                except TomlDecodeError as error_msg:
                    print(
                        (
                            "[blue]│   │   │   ├── [/blue]"
                            f"[red]Thông báo lỗi: [/red]"
                            f"[white]{error_msg}[/white]"
                        )
                    )
                    print(
                        (
                            "[blue]│   │   │   ├── [/blue]"
                            f"[red]Xin hãy kiểm tra nội dung đề thi định dạng TOML đã được tạo ở: [/red]"
                            f"[white]{log_dir}[/white]"
                        )
                    )
                    print(
                        (
                            "[blue]│   │   │   └── [/blue]"
                            "[yellow]Đang thử lại...[/yellow]"
                        )
                    )

                except FileNotFoundError as error_msg:
                    print(
                        (
                            "[blue]│   │   │   ├── [/blue]"
                            f"[red]Thông báo lỗi: [/red]"
                            f"[white]{error_msg}[/white]"
                        )
                    )
                    print(
                        (
                            "[blue]│   │   │   ├── [/blue]"
                            f"[red]Xin hãy đảm bảo rằng tồn tại nội dung đề thi định dạng TOML ở: [/red]"
                            f"[white]{log_dir}[/white]"
                        )
                    )
                    print(
                        (
                            "[blue]│   │   │   └── [/blue]"
                            "[yellow]Đang thử lại...[/yellow]"
                        )
                    )

            content_dict.update(
                {
                    f"{prompt_name}_{key}": value
                    for key, value in content_curr_dict.items()
                }
            )

            print(
                (
                    "[blue]│   │   └── [/blue]"
                    + f"[green]Đã đọc nội dung đề thi được sinh bởi prompt [white]{prompt_name}[/white] thành công.[/green]"
                )
            )

        with open(content_dir, "w+", encoding="utf-8") as log:
            log.write(dict_to_qti_compatible(content_dict, shuffle))

    print(
        (
            "[blue]│   └── [/blue]"
            + "[green]Đã tạo nội dung đề thi định dạng QTI-compatible thành công: [/green]"
            + f"[white]{content_dir}[/white]"
        )
    )

    with open(content_dir, "r", encoding="utf-8") as log:
        return log.read()
