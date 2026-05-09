from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectorBundle:
    storybook_entry_texts: tuple[str, ...] = (
        "Storybook",
        "storybook",
        "Создай storybook",
        "Create a storybook",
    )
    prompt_input_labels: tuple[str, ...] = (
        "Введите запрос для Gemini",
        "Спросите Gemini о чем-нибудь",
        "Спросите Gemini",
        "Ask Gemini",
        "Message Gemini",
        "Prompt",
    )
    prompt_input_selectors: tuple[str, ...] = (
        'textarea[placeholder*="Gemini"]',
        'textarea',
        'rich-textarea .ql-editor',
        'div.ql-editor',
        '[contenteditable="true"]',
        '[role="textbox"]',
        '[aria-label*="Gemini"]',
        '.textarea-container textarea',
    )
    send_button_labels: tuple[str, ...] = (
        "Отправить сообщение",
        "Отправить",
        "Send message",
        "Send",
    )
    send_button_selectors: tuple[str, ...] = (
        'button[aria-label*="Отправ"]',
        'button[aria-label*="Send"]',
        'mat-icon.send-icon',
        '.send-icon',
        '[data-test-id="send-button"]',
        'button.send-button',
    )
    generating_texts: tuple[str, ...] = (
        "Создаю",
        "Генерирую",
        "Gemini набирает ответ",
        "Gemini is typing",
        "Creating",
        "Generating",
        "Working",
    )
    error_13_texts: tuple[str, ...] = (
        "Something went wrong (13)",
        "Что-то пошло не так (13)",
        "Что-то пошло не так. (13)",
    )
    generic_error_texts: tuple[str, ...] = (
        "Something went wrong",
        "Что-то пошло не так",
    )
    share_texts: tuple[str, ...] = (
        "Поделиться книгой",
        "Поделиться чатом",
        "Share book",
        "Share chat",
        "Copy link",
        "Get link",
        "Скопировать",
        "Скопировать ссылку",
    )
    share_action_texts: tuple[str, ...] = (
        "Скопировать ссылку",
        "Copy link",
        "Get link",
        "Поделиться книгой",
        "Share book",
    )
