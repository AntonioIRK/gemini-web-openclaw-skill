# Спецификация Gemini Web account-session skill для OpenClaw

> **Важно:** этот документ начинался как Storybook-first MVP spec.
> Текущий продуктовый scope шире.
> Сейчас repo нужно понимать как **Gemini Web account-session skill** с тремя основными surface-областями:
>
> - `chat-ask`
> - `image-create` / `image-edit`
> - Storybook как дополнительный специализированный workflow

## 1. Назначение документа

Этот документ описывает **требования к Gemini Web skill для OpenClaw**, который должен дать агенту OpenClaw неофициальный доступ к реальным web-account surface'ам Gemini через браузерную учётку.

Документ намеренно сфокусирован не на абстрактном “коннекторе”, а на полном lifecycle skill:
- что агент должен изучить;
- какой skill он должен создать;
- какой интерфейс skill обязан предоставить;
- как skill должен быть устроен внутри;
- по каким критериям задача считается выполненной.

---

## 2. Цель

Создать **skill для OpenClaw**, который позволяет из OpenClaw работать с реальными Gemini Web surface'ами через account-session automation.

Приоритетные сценарии сейчас:

- normal Gemini chat requests через `chat-ask`
- создание изображений через `image-create`
- редактирование входных изображений через `image-edit`, в том числе картинок, присланных в Telegram
- запуск Storybook workflow как дополнительного специализированного режима

Storybook остаётся важной частью scope, но больше не является единственным или главным определением продукта.

Для Storybook skill должен уметь получать один из результатов:

- `share_link` на созданную книгу;
- `pdf_path` к локально сохранённому PDF;
- диагностированную ошибку с debug artifacts.

Ключевое требование: skill должен обращаться **к реальным Gemini Web workflow** через браузерную account session, а не подменять их отдельным API-key integration path.

---

## 3. Что является успехом

Результат считается успешным только если выполнены все условия:

1. создан отдельный skill-проект;
2. skill имеет документацию установки и использования;
3. skill имеет явный входной и выходной контракт;
4. skill умеет использовать существующую web session Gemini;
5. skill умеет запускать chat/image workflows Gemini Web;
6. skill умеет принимать и редактировать входные изображения;
7. skill умеет ждать завершения генерации и возвращать результат;
8. при Storybook-запусках умеет вернуть `share_link` или `pdf_path`;
9. при сбоях сохраняются диагностические артефакты;
10. есть хотя бы один рабочий e2e сценарий;
11. есть отчёт по изученным инженерным направлениям и их применению.

Если на выходе получается просто скрипт, библиотека или API-клиент без skill-обвязки для OpenClaw, задача **не выполнена**.

---

## 4. Non-goals

Следующие результаты не считаются выполнением этой спецификации:

- Gemini Developer API wrapper вместо браузерной account-session automation;
- "storybook-like" инструмент без обращения к реальному Storybook;
- Playwright-скрипт без упаковки в skill;
- исследовательский документ без реализованного skill;
- общий reverse-engineered Gemini SDK без фокуса на Storybook;
- инструменты обхода CAPTCHA, 2FA, device checks, anti-bot.

---

## 5. Что агент обязан изучить

Перед реализацией skill агент обязан изучить четыре инженерных направления и явно описать выводы.

### 5.1 Организация неофициального клиента

Изучить как направление по:
- структуре неофициального клиента;
- auth/session организации;
- CLI;
- skill-friendly packaging;
- диагностике;
- handling нестабильных внутренних API.

Агент обязан зафиксировать:
- что переносится в новый skill;
- что не переносится;
- какие паттерны повторить.

### 5.2 Оформление skill для OpenClaw/ClawHub

Изучить как направление по:
- оформлению skill для OpenClaw/ClawHub;
- структуре skill-манифеста и документации;
- способу запуска;
- способу работы с Gemini Web;
- auth/cookie/browser practices.

Агент обязан зафиксировать:
- как новый skill должен быть оформлен;
- какие подходы можно взять для auth/session;
- какие Storybook-специфические части надо сделать отдельно.

### 5.3 Reverse-engineered доступ к Gemini Web

Изучить как направление по:
- reverse-engineered доступу к Gemini Web;
- использованию browser cookies;
- file upload;
- чату и Gems;
- ограничениям этого подхода.

Агент обязан зафиксировать:
- можно ли использовать это как access layer;
- покрывает ли оно Storybook напрямую;
- где неизбежен UI automation.

### 5.4 Result/output layer для книжечных артефактов

Изучить только как направление по:
- модели результата;
- HTML/PDF output;
- структуре истории;
- внешнему tool contract.

Агент обязан зафиксировать:
- что из него годится для output layer;
- почему auth/transport из него не подходит.

---

## 6. Ключевой инженерный вывод, который должен лечь в основу skill

MVP и текущий основной продукт должны быть построены на **UI automation вокруг реальной Gemini web account session**, а не на догадках о приватном backend API.

Причина:
- mature value здесь идёт из web-account surface, особенно chat/image flows;
- Storybook тоже UI-driven workflow;
- важны не только запрос и ответ, но и реальные web действия: загрузка файлов, ожидание генерации, скачивание полноразмерного результата, а для Storybook ещё и `share_link` / `print/save as PDF`.

Следовательно, первая рабочая версия skill должна использовать:
- browser session или persistent browser profile;
- Playwright;
- state machine по шагам Storybook workflow.

Исследование network layer допустимо только как вторая фаза после рабочего MVP.

---

## 7. Область ответственности skill

Skill должен закрывать следующие зоны:

1. **Session/Auth**
2. **Chat and image workflow execution**
3. **Storybook workflow execution**
4. **Artifact extraction**
5. **Diagnostics and recovery**
6. **OpenClaw adapter layer**
7. **CLI / local testing layer**

---

## 8. Функциональные требования

### FR-1. Инициализация и reuse сессии

Skill должен уметь:
- использовать уже существующую browser session;
- использовать persistent profile directory;
- запускать браузер для ручного логина, если это необходимо один раз;
- переиспользовать session state на следующих запусках.

### FR-2. Обнаружение доступных Gemini surface'ов

Skill должен уметь определить:
- доступен ли normal Gemini chat path;
- доступен ли image generation path;
- доступен ли image edit path;
- доступен ли Storybook в аккаунте, если нужен специализированный запуск;
- доступен ли Storybook как Gem;
- можно ли вызвать Storybook через trigger prompt в обычном чате.

### FR-3. Отправка prompt и файлов

Skill должен уметь:
- отправлять текстовый prompt;
- прикладывать один или несколько файлов/изображений;
- проверять, что UI принял запрос.

### FR-4. Ожидание завершения

Skill должен:
- различать состояния `idle`, `submitting`, `generating`, `completed`, `failed`, `timed_out`;
- поддерживать configurable timeout;
- при таймауте сохранять diagnostics.

### FR-5. Получение результата

Skill должен поддерживать несколько результатных surface'ов:
- текстовый ответ для `chat-ask`
- downloaded full-size image для `image-create` и `image-edit`
- `share_link` или `pdf` для Storybook create

Допустимо дополнительно возвращать:
- `title`
- `preview metadata`
- `debug_artifacts_path`

### FR-6. Возврат structured result

Skill обязан возвращать структурированный результат в OpenClaw.

Пример успешного результата для Storybook:

```json
{
  "status": "success",
  "share_link": "https://...",
  "pdf_path": null,
  "title": "Moon Fox Bedtime Story",
  "debug_artifacts_path": "/tmp/storybook-run-123",
  "error_code": null,
  "error_message": null
}
```

Пример ошибки для Storybook:

```json
{
  "status": "error",
  "share_link": null,
  "pdf_path": null,
  "title": null,
  "debug_artifacts_path": "/tmp/storybook-run-124",
  "error_code": "STORYBOOK_NOT_AVAILABLE",
  "error_message": "Storybook entrypoint was not found in the current Gemini account"
}
```

---

## 9. Нефункциональные требования

### NFR-1. Диагностируемость

При существенной ошибке skill должен сохранять:
- screenshot;
- HTML snapshot;
- console logs;
- network trace, если доступно;
- текущий шаг state machine.

### NFR-2. Минимизация хрупкости

Селекторы не должны быть построены только на одном CSS path.
Нужно использовать комбинацию:
- role-based selectors;
- aria-label;
- visible text anchors;
- fallback selectors.

### NFR-3. Безопасность

Skill не должен:
- обходить CAPTCHA;
- обходить 2FA;
- подменять device integrity checks;
- использовать сомнительные anti-detection хаки;
- извлекать чужие cookies скрытно.

### NFR-4. Управляемость

Skill должен иметь отдельные команды для:
- login;
- doctor/diagnostics;
- debug-open;
- inspect-home;
- chat-ask;
- image-create;
- image-edit;
- create.

### NFR-5. Воспроизводимость

При одинаковом состоянии аккаунта и одинаковом способе запуска skill должен демонстрировать воспроизводимый workflow, даже если само содержимое книги творчески варьируется.

---

## 10. Исследовательские задачи, которые skill-agent обязан выполнить

До начала или параллельно с реализацией агент должен исследовать:

### R-1. Mature core entrypoints
- normal chat path;
- image generation path;
- image edit path;
- thread reuse behavior;
- full-size image download path.

### R-2. Storybook entrypoints
- вход через Gem;
- вход через обычный чат;
- сравнить стабильность.

### R-3. UI markers
- элементы запуска;
- поле ввода;
- upload entrypoint;
- статус генерации;
- готовый результат;
- share action;
- print/PDF action.

### R-4. Session behavior
- какой тип persistent profile работает устойчиво;
- как понять, что login истёк;
- как безопасно инициировать ручной login.

### R-5. Export behavior
- как стабильно получать share link;
- как делать PDF export;
- где возможны race conditions.

### R-6. Optional network inspection
- какие запросы уходят при запуске Storybook;
- можно ли часть сигналов брать из сети, не из DOM;
- стоит ли выносить часть логики ниже UI.

---

## 11. Предлагаемая структура нового skill

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
│       ├── storage.py
│       ├── cli.py
│       ├── auth/
│       │   ├── __init__.py
│       │   ├── profile.py
│       │   └── login_flow.py
│       ├── web/
│       │   ├── __init__.py
│       │   ├── browser.py
│       │   ├── selectors.py
│       │   ├── state_machine.py
│       │   └── storybook_runner.py
│       ├── export/
│       │   ├── __init__.py
│       │   ├── share_link.py
│       │   └── pdf_export.py
│       └── skill/
│           ├── __init__.py
│           ├── manifest.py
│           └── openclaw_adapter.py
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

## 12. Внутренние модули и их ответственность

### `client.py`
Публичный Python API для запуска workflow из CLI или skill-adapter.

### `config.py`
Конфигурация путей, timeouts, browser profile, debug flags.

### `models.py`
Модели:
- `GeminiWebRequest`
- `GeminiWebResult`
- `RunDiagnostics`
- `WorkflowState`

Допустимы transitional aliases для Storybook-специфичных моделей, если они не выдаются за главный продуктовый contract.

### `exceptions.py`
Typed exceptions и error mapping.

### `diagnostics.py`
Сохранение screenshots, HTML, logs, trace artifacts.

### `auth/profile.py`
Работа с persistent browser profile и путями к session storage.

### `auth/login_flow.py`
Ручной login flow и проверки валидности сессии.

### `web/browser.py`
Запуск Playwright context/page.

### `web/selectors.py`
Централизованное описание primary/fallback selectors.

### `web/state_machine.py`
Состояния выполнения:
- `INIT`
- `OPENING_GEMINI`
- `CHECKING_LOGIN`
- `LOCATING_TARGET_SURFACE`
- `UPLOADING_FILES`
- `SUBMITTING_PROMPT`
- `WAITING_FOR_GENERATION`
- `DOWNLOADING_FINAL_IMAGE`
- `EXTRACTING_SHARE_LINK`
- `EXPORTING_PDF`
- `COMPLETED`
- `FAILED`

### `web/storybook_runner.py`
Transitional специализированный runner для Storybook workflow.

Основная продуктовая orchestration-логика skill не должна описываться так, будто весь repo сводится только к нему.

### `export/share_link.py`
Получение и валидация share link.

### `export/pdf_export.py`
PDF export через print/save-as-PDF flow.

### `skill/openclaw_adapter.py`
Skill-facing adapter: принимает вход OpenClaw, вызывает client, отдаёт structured result.

### `skill/manifest.py`
Описание skill-а, параметров, примеров использования.

---

## 13. Skill contract

Skill должен поддерживать multi-mode contract.

### 13.0 Unified input shape

```json
{
  "mode": "chat-ask | image-create | image-edit | create",
  "prompt": "string",
  "files": ["optional file paths"],
  "return_mode": "share_link | pdf",
  "output_path": "optional path",
  "timeout_seconds": 300,
  "debug": false
}
```

Unified result shape должен уметь представлять text, image и Storybook outcomes.

### 13.1 Входные параметры

```json
{
  "prompt": "string",
  "files": ["optional file paths"],
  "return_mode": "share_link | pdf",
  "output_path": "optional path",
  "timeout_seconds": 300,
  "debug": false
}
```

### 13.2 Выходной результат

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

### 13.3 Ошибки

Skill должен использовать как минимум такие коды ошибок:
- `LOGIN_REQUIRED`
- `STORYBOOK_NOT_AVAILABLE`
- `PROMPT_SUBMISSION_FAILED`
- `UPLOAD_FAILED`
- `GENERATION_TIMEOUT`
- `SHARE_LINK_NOT_FOUND`
- `PDF_EXPORT_FAILED`
- `UNKNOWN_RUNTIME_ERROR`

---

## 14. CLI contract

Минимальный CLI:

```bash
gemini-web-skill login
gemini-web-skill doctor
gemini-web-skill debug-open
gemini-web-skill inspect-home
gemini-web-skill chat-ask --prompt "Summarize this topic in 3 bullets"
gemini-web-skill image-create --prompt "A friendly robot watering a tiny garden"
gemini-web-skill image-edit --file ./image.png --prompt "Add a realistic UFO in the sky"
gemini-web-skill create --prompt "Tell a bedtime story about a robot fox" --return-mode share_link
gemini-web-skill create --prompt "Create a storybook from this child photo" --file ./child.png --return-mode pdf --output ./storybook.pdf
```

Названия могут быть адаптированы, если OpenClaw skill ecosystem требует другой стиль, но сценарии должны сохраниться.

---

## 15. План реализации

### Phase 0. Repo study
Сдать краткий отчёт:
- что изучено;
- что будет использовано;
- что отвергнуто.

### Phase 1. Skill scaffold
Создать проект, конфиг, CLI, manifest, базовые модели и exceptions.

### Phase 2. Auth/session
Сделать persistent profile, login command, session validation.

### Phase 3. Mature core UI automation MVP
Реализовать:
- open Gemini;
- normal chat path;
- image generation path;
- image edit path;
- full-size image delivery.

### Phase 4. Storybook UI automation MVP
Реализовать:
- locate Storybook;
- submit prompt;
- wait;
- get share link.

### Phase 5. PDF export
Добавить print/save-as-PDF flow.

### Phase 6. Diagnostics hardening
Добавить trace, screenshots, HTML dumps, rich errors.

### Phase 7. Optional network inspection
Проверить, можно ли часть логики сделать стабильнее.

---

## 16. Тестирование

### Unit tests
- config parsing;
- result model validation;
- selector fallback resolution;
- error mapping.

### Integration tests
- session validation;
- browser startup;
- diagnostics persistence.

### E2E tests
Минимум один e2e для mature core:
1. вызвать skill;
2. выполнить `chat-ask` или image flow;
3. дождаться результата;
4. получить текст или full-size image.

Дополнительно желателен Storybook e2e на `share_link` или `pdf_path`.

Дополнительно желателен e2e на ошибку login/session expired.

---

## 17. Диагностика и recovery

При ошибке должны сохраняться:
- `screenshot.png`
- `page.html`
- `console.log`
- `trace.zip` или аналог
- `state.json`

Нужно описать в документации:
- как повторно пройти login;
- как посмотреть debug artifacts;
- как понять, что сломался DOM;
- как понять, что Storybook недоступен в аккаунте.

---

## 18. Известные риски

1. Storybook может быть недоступен не во всех аккаунтах.
2. DOM и aria-label могут меняться.
3. Share flow может меняться по шагам.
4. PDF export может зависеть от локального browser/runtime окружения.
5. Session reuse может ломаться после logout, device change или re-verification.

Skill должен не скрывать эти риски, а явно документировать их.

---

## 19. Критерии приёмки

Skill принимается только если:
- оформлен как новый проект;
- имеет `README.md` и `SKILL.md`;
- реализует declared skill contract;
- имеет работающий CLI;
- умеет использовать web session;
- умеет стабильно выполнять `chat-ask`, `image-create` и `image-edit` через браузерную account session;
- для Storybook умеет запустить workflow и дождаться результата, если этот surface заявлен как доступный;
- для Storybook умеет вернуть `share_link` или `pdf_path`;
- умеет сохранять diagnostics;
- содержит список ограничений и recovery steps;
- содержит отчёт по применению изученных референсов.

---

## 20. Формат итоговой сдачи агентом

Итоговая сдача должна содержать:

1. `Что было изучено`
2. `Какие выводы сделаны`
3. `Как спроектирован новый skill`
4. `Структура файлов`
5. `Skill contract`
6. `Ключевые модули`
7. `Инструкция запуска`
8. `Инструкция подключения в OpenClaw`
9. `Что уже работает`
10. `Что пока нестабильно`
11. `Какие ограничения остались`
12. `Что делать дальше`

Этот формат обязателен, чтобы было видно не только код, но и то, что агент действительно создал **новый OpenClaw skill**, а не просто исследовал тему.
