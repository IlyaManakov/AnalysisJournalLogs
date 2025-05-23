# AnalysisJournalLogs

Этот скрипт анализирует логи и формирует отчеты по обработчикам (handlers) и их статусам (INFO, ERROR и т.д.).

## Добавление нового типа отчета

Чтобы добавить новый тип отчета, нужно выполнить следующие шаги:

1. **Добавить название отчета в список `list_report`**  
   В функции `create_parser()` добавьте новое название отчета в список `list_report`:
   ```python
   list_report = ['handlers', 'handlers-split', 'new-report-name']
   ```

2. **Реализовать логику обработки нового отчета**  
   В функции `process_args()` добавьте новый блок условия для обработки вашего отчета:
   ```python
   elif args.report == 'new-report-name':
       # Ваша логика обработки нового отчета
       pass
   ```

3. **При необходимости создать новые вспомогательные функции**  
   Если для нового отчета требуется особая обработка данных, создайте новые функции аналогично `read_log()` или `merge_dict()`.

4. **Реализовать вывод результатов**  
   Можно использовать существующую функцию `result_out()` или создать новую, если требуется другой формат вывода.

## Существующие отчеты

- `handlers` - объединенный отчет по всем файлам
- `handlers-split` - отдельные отчеты для каждого файла

## Использование

```bash
python script.py file1.log file2.log --report handlers
```

## Структура кода

Основные компоненты:
- `create_parser()` - настройка аргументов командной строки
- `read_log()` - чтение и первичная обработка лог-файла
- `merge_dict()` - объединение данных из нескольких файлов
- `result_out()` - форматированный вывод результатов
- `process_args()` - основная логика обработки отчетов

Глобальная переменная `rows` определяет форматирование вывода и список поддерживаемых статусов.
