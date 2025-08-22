import pandas as pd
import re
import os

def process_whatsapp_chat(input_file_path: str) -> None:
    """
    Обрабатывает файл чата WhatsApp, парсит сообщения с датой, временем и отправителем,
    фильтрует сообщения без медиафайлов, сохраняет результат в Excel.

    Объединяет строки (добавляет к предыдущему сообщению без переноса) только для сообщений,
    которые идут после появления ключевого слова "План работ".

    :param input_file_path: Путь к исходному текстовому файлу с чатом WhatsApp.
    """
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    data = []
    pattern = r'(\d{2}\.\d{2}\.\d{4}, \d{2}:\d{2}) - (.*?): (.*)'
    last_entry = None
    plan_works_started = False  # флаг, что встретили "План работ"

    for line in lines:
        line = line.strip('\n\r')
        if not line.strip():
            continue

        match = re.match(pattern, line)
        if match:
            if last_entry:
                data.append(last_entry)
            date_time = match.group(1)
            sender = match.group(2)
            message = match.group(3)

            # Проверяем появление ключевого слова "План работ" в сообщении
            if 'План работ' in message:
                plan_works_started = True

            last_entry = [date_time, sender, message]
        else:
            # Если ключевое слово уже встретилось, объединяем строки
            if plan_works_started and last_entry:
                last_entry[2] += ' ' + line.strip()
            else:
                pass

    if last_entry:
        data.append(last_entry)

    df = pd.DataFrame(data, columns=['DateTime', 'Sender', 'Message'])

    # Фильтруем записи без <Без медиафайлов>
    df_filtered = df[~df['Message'].str.contains('<Без медиафайлов>', na=False)]

    # Убираем столбец Sender, индексируем по дате
    df_filtered.index = pd.to_datetime(df_filtered['DateTime'], dayfirst=True)
    df_filtered = df_filtered.drop(['DateTime', 'Sender'], axis=1)

    # Формируем имя выходного файла на основе имени входного
    base_name = os.path.splitext(input_file_path)[0]
    output_file_path = base_name + '.xlsx'

    df_filtered.to_excel(output_file_path)
    print(f"Файл сохранён: {output_file_path}")


if __name__ == "__main__":
    input_path = r"C:\Users\Andrei\Desktop\WhatsApp.txt"
    process_whatsapp_chat(input_path)
