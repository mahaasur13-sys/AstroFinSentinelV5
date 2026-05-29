import os, sys, subprocess, re
from openai import OpenAI

api_key = os.getenv("VSELM_API_KEY")
if not api_key:
    print("❌ Переменная VSELM_API_KEY не установлена")
    sys.exit(1)

client = OpenAI(api_key=api_key, base_url="https://api.vsellm.ru/v1")

TICKETS_FILE = "docs/tickets.md"
PROGRESS_FILE = "progress.md"
INSTRUCTIONS_FILE = "RALPH_INSTRUCTIONS.md"

def read_file(path):
    with open(path) as f: return f.read()
def write_file(path, content):
    with open(path, "w") as f: f.write(content)
def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

tickets = read_file(TICKETS_FILE)
progress = read_file(PROGRESS_FILE)
instructions = read_file(INSTRUCTIONS_FILE) if os.path.exists(INSTRUCTIONS_FILE) else ""

match = re.search(r"^- \[ \] (.+?)$", tickets, re.MULTILINE)
if not match:
    print("✅ Все задачи выполнены!")
    sys.exit(0)
task = match.group(1)
print(f"🎯 Задача: {task}")

prompt = f"""{instructions}

Сейчас ты выполняешь задачу:
"{task}"

Содержимое docs/tickets.md:
{tickets}

Содержимое progress.md:
{progress}

Выполни эту задачу: напиши код, тесты, обнови документацию.
После завершения запусти `pytest` и `flake8 orchestration/`.
Если тесты пройдены, сделай коммит с сообщением "feat: {task}".
Выведи краткий отчёт."""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
)
answer = response.choices[0].message.content
print(f"🤖 Ответ модели:\n{answer}")

print("🚦 Запускаем pytest...")
test_result = run("pytest")
print(test_result.stdout[-500:])

print("🧹 Запускаем flake8 orchestration/...")
lint_result = run("flake8 orchestration/")
if lint_result.returncode != 0:
    print(lint_result.stdout)

if test_result.returncode == 0:
    print("✅ Тесты пройдены, коммитим.")
    run("git add -A")
    run(f'git commit -m "feat: {task}"')
    tickets_updated = tickets.replace(f"- [ ] {task}", f"- [x] {task} ✅")
    write_file(TICKETS_FILE, tickets_updated)
    entry = f"\n## {task}\n- Статус: выполнено\n- Коммит: последний\n"
    with open(PROGRESS_FILE, "a") as pf:
        pf.write(entry)
    print("📌 Прогресс обновлён.")
else:
    print("❌ Тесты упали, задача не выполнена.")
