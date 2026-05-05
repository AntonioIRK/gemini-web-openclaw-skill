# Prompt для OpenClaw: развивать Gemini Web account-session skill для OpenClaw

Ты — инженер-агент, который должен **создать новый skill для OpenClaw**.

Твоя задача — не написать исследовательский отчёт и не сделать абстрактный прототип, а **спроектировать и развивать OpenClaw skill**, который даёт OpenClaw неофициальный доступ к **реальным Gemini Web surface'ам через браузерную account session**.

## Что именно нужно получить в конце

Нужен **skill** со своей структурой, документацией, командами запуска, диагностикой и рабочим интерфейсом для OpenClaw.

Skill должен уметь:

1. использовать существующую веб-сессию Gemini пользователя;
2. выполнять normal Gemini chat flows;
3. создавать изображения и редактировать входные изображения через Gemini Web UI;
4. принимать картинки, присланные в чат, как edit inputs;
5. при необходимости запускать **Storybook workflow** в Gemini Web;
6. дожидаться завершения генерации;
7. возвращать в OpenClaw один из результатов:
   - `share_link`;
   - `pdf_path`;
   - downloaded full-size image;
   - диагностированную ошибку с debug artifacts.

## Критически важно

Не подменяй задачу.

Запрещено выдавать за результат:
- генератор книжек через официальный Gemini API;
- “storybook-like” пайплайн без обращения к Gemini Web Storybook;
- просто Playwright-скрипт без skill-обвязки;
- просто библиотеку без OpenClaw skill contract.

Нужен **именно skill для OpenClaw**, в котором базовый продуктовый контур шире Storybook.

Текущий приоритет зрелости:
- `chat-ask`
- `image-create`
- `image-edit`
- Storybook как дополнительный experimental surface

---

## Что ты должен изучить перед реализацией

Перед тем как писать код, изучи и зафиксируй выводы по следующим инженерным направлениям.

### 1. Организация неофициального Python-клиента и skill-пакета
Изучи как направление для:
- auth/session/browser login;
- client structure;
- CLI;
- skill packaging;
- exception handling;
- документацию нестабильных мест.

Нужно явно ответить:
- что из него полезно для нового skill;
- что из него нельзя переносить в Gemini Storybook;
- какие инженерные паттерны стоит повторить.

### 2. Оформление OpenClaw skill integration
Изучи как направление именно для **OpenClaw skill integration**:
- как skill оформлен;
- как описан интерфейс;
- как организован запуск;
- как работает доступ к Gemini Web;
- как организованы browser/cookie/session практики.

Нужно явно ответить:
- как на его основе оформить новый skill;
- что можно взять для auth/session;
- где нужны отдельные Storybook-специфические доработки.

### 3. Reverse-engineered доступ к Gemini Web
Изучи как направление для:
- cookies / browser session;
- file upload;
- chat/gems workflows;
- ограничения подхода.

Нужно явно ответить:
- пригоден ли этот подход как база для access layer;
- покрывает ли он Storybook напрямую или только частично;
- где понадобится UI automation.

### 4. Result/output layer для книжечных артефактов
Изучи только как направление по:
- структуре результата;
- HTML/PDF export pipeline;
- модели данных книги;
- tool contract.

Нужно явно ответить:
- что из него полезно для output/result layer;
- почему его transport/auth нельзя использовать для этой задачи.

---

## Что нужно исследовать в Gemini Web

Сначала проверяй зрелые core flows:

1. normal chat path
2. image creation path
3. image edit path, включая inbound chat images
4. full-size result download path

Отдельно исследуй Storybook как специализированный workflow.

Тебе нужно исследовать **те workflow**, которые потом будет автоматизировать skill.

Проверь:
1. как запускать Storybook:
   - через Gem "Storybook";
   - через обычный чат с trigger prompt;
2. какой путь стабильнее;
3. можно ли прикладывать файлы/изображения;
4. как выглядит состояние генерации;
5. как определяется завершение;
6. как извлекается `share_link`;
7. как делается `print/save as PDF`;
8. какие DOM-маркеры, aria-label, text anchors, URL-паттерны подходят для устойчивой автоматизации.

Если прямого низкоуровневого API не видно, не фантазируй: делай вывод, что **MVP должен быть на Playwright/UI automation**.

---

## Что именно нужно реализовать

Создай **новый skill-проект**. Предпочтительный вариант: Python skill с Playwright automation.

Пример целевой структуры:

```text
openclaw-gemini-web-skill/
├── pyproject.toml
├── README.md
├── SKILL.md
├── src/
│   └── openclaw_gemini_web/
│       ├── __init__.py
│       ├── client.py
│       ├── config.py
│       ├── models.py
│       ├── exceptions.py
│       ├── diagnostics.py
│       ├── cli.py
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── profile.py
│       │   └── login_flow.py
│       ├── web/
│       │   ├── __init__.py
│       │   ├── browser.py
│       │   ├── selectors.py
│       │   ├── storybook_runner.py
│       │   └── state_machine.py
│       ├── export/
│       │   ├── __init__.py
│       │   ├── share_link.py
│       │   └── pdf_export.py
│       └── skill/
│           ├── __init__.py
│           └── openclaw_adapter.py
└── tests/
    ├── unit/
    └── e2e/
```

---

## Обязательный skill contract

Skill должен поддерживать multi-mode contract.

Базовая unified форма:

```json
{
  "mode": "chat-ask | image-create | image-edit | create",
  "prompt": "string",
  "files": ["optional file paths"],
  "return_mode": "share_link | pdf",
  "output_path": "optional",
  "timeout_seconds": 300,
  "debug": false
}
```

Для Storybook `create` skill должен принимать такие входные параметры:

```json
{
  "prompt": "string",
  "files": ["optional file paths"],
  "return_mode": "share_link | pdf",
  "output_path": "optional",
  "timeout_seconds": 300,
  "debug": false
}
```

Unified result shape должен уметь представлять text, image и Storybook outcomes.

Для Storybook `create` skill должен возвращать такой результат:

```json
{
  "status": "success | error",
  "share_link": "optional string",
  "pdf_path": "optional string",
  "title": "optional string",
  "debug_artifacts_path": "optional string",
  "error_code": "optional string",
  "error_message": "optional string"
}
```

---

## Обязательные команды и режимы

Реализуй минимум:

```bash
gemini-web-skill login
gemini-web-skill doctor
gemini-web-skill debug-open
gemini-web-skill inspect-home
gemini-web-skill chat-ask --prompt "Summarize this topic in 3 bullets"
gemini-web-skill image-create --prompt "A friendly robot watering a tiny garden"
gemini-web-skill image-edit --file ./image.png --prompt "Add a realistic UFO in the sky"
gemini-web-skill create --prompt "..." --return-mode share_link
gemini-web-skill create --prompt "..." --file ./image.png --return-mode pdf --output ./book.pdf
```

Если в экосистеме OpenClaw нужен иной формат команды или иной manifest — адаптируй под него, но не убирай эти сценарии.

---

## Архитектурный приоритет

### Фаза 1 — обязательная
Сделай рабочий MVP через:
- browser session / persistent profile;
- Playwright;
- chat/image UI automation;
- full-size image delivery;
- Storybook UI automation как дополнительный режим.

### Фаза 2 — только после MVP
Исследуй network layer:
- какие запросы уходят;
- можно ли стабильнее получить часть результата без DOM automation;
- стоит ли переносить часть логики ниже UI.

Не делай Phase 2 вместо Phase 1.

---

## Что нужно обязательно добавить в skill

### 1. Диагностика
При сбое сохраняй:
- screenshot;
- HTML snapshot;
- console logs;
- по возможности network trace;
- информацию о текущем шаге state machine.

### 2. Ошибки
Добавь отдельные исключения и коды ошибок:
- `LoginRequiredError`
- `StorybookNotAvailableError`
- `PromptSubmissionError`
- `UploadFailedError`
- `GenerationTimeoutError`
- `ShareLinkNotFoundError`
- `PdfExportFailedError`

### 3. Документация
Нужно подготовить:
- `README.md` — как запускать проект локально;
- `SKILL.md` — как устанавливать и использовать skill в OpenClaw;
- раздел `Known limitations`;
- раздел `Recovery / troubleshooting`.

---

## Что считается завершением задачи

Работа завершена только если есть все пункты:

1. создан новый skill-проект;
2. есть код skill-а;
3. есть документация установки и запуска;
4. есть чёткий skill contract;
5. есть минимум один e2e сценарий для mature core:
   - `chat-ask` или image flow;
   - дождаться результата;
   - вернуть текст или full-size image;
6. есть дополнительный Storybook e2e или честно зафиксированный experimental status;
7. есть диагностические артефакты при ошибке;
8. есть список известных ограничений;
9. есть краткий отчёт, что было изучено в инженерных направлениях и что из них реально использовано.

---

## Формат твоего итогового ответа

Итоговый ответ должен быть структурирован строго так:

1. `Что было изучено`
2. `Что взято в новый skill`
3. `Что отвергнуто и почему`
4. `Структура нового skill`
5. `Реализованный skill contract`
6. `Ключевые модули`
7. `Как запускать`
8. `Как подключать в OpenClaw`
9. `Что уже работает`
10. `Что пока нестабильно`
11. `Какие следующие шаги`

---

## Правила работы

- Не задавай лишних уточняющих вопросов.
- Если есть неоднозначность, выбирай самый практичный вариант.
- Не уходи в длинную аналитику без кода.
- После каждого крупного этапа показывай короткий прогресс:
  - что изучено;
  - что реализовано;
  - что сломалось;
  - что будет следующим шагом.
- Если всё не удаётся завершить полностью, всё равно выдай максимум рабочего результата: код, структуру, частичный MVP, список блокеров.

Начинай с анализа референсных репозиториев именно под задачу **создания нового OpenClaw skill**, затем переходи к MVP-реализации.
