import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from threading import Thread

class ChatApp:
    def __init__(self, root):
        """Инициализация главного окна приложения"""
        self.root = root
        self.root.title("AI Study Assistant (Ollama)")  # Изменено название для студенческого ассистента
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Инициализация модели LLM через Ollama
        # TODO: Можно добавить выбор модели из списка доступных
        self.model = OllamaLLM(model="qwen3:1.7b")
        self.setup_prompt_template()
        
        # Цветовая схема в стиле Telegram
        self.bg_color = "#f5f5f5"      # Фоновый цвет
        self.user_bg = "#e3f2fd"       # Цвет сообщений пользователя
        self.ai_bg = "#ffffff"         # Цвет сообщений ИИ
        self.text_color = "#212121"    # Цвет текста
        self.accent_color = "#0088cc"  # Акцентный цвет (кнопки)
        
        self.setup_ui()
        
    def setup_prompt_template(self):
        """
        Настройка шаблона промпта для модели.
        ИЗМЕНЕНО: теперь ассистент помогает студентам с учебой
        """
        template = '''
        You are an AI assistant designed to help students with their studies.
        Your tasks include:
        - Explaining complex concepts in simple terms
        - Helping with homework and assignments
        - Providing study resources and references
        - Answering questions about various subjects
        
        Here is some relevant context: {study_materials}
        
        Student's question: {question}
        
        Please provide a clear, detailed answer with examples where appropriate.
        If the question relates to specific subjects (math, physics, programming etc.),
        tailor your response accordingly. /no_think
        '''
        self.prompt = ChatPromptTemplate.from_template(template)
        
        # TODO: Реализовать retriever для поиска по учебным материалам
        # Пример для реализации:
        # from langchain_community.vectorstores import Chroma
        # from langchain_community.embeddings import OllamaEmbeddings
        # self.embeddings = OllamaEmbeddings(model="qwen3:1.7b")
        # self.vectorstore = Chroma(embedding_function=self.embeddings)
        # self.retriever = self.vectorstore.as_retriever()
        
    def setup_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Основной контейнер
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # История чата (прокручиваемое текстовое поле)
        self.chat_history = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,           # Перенос по словам
            width=70,               # Ширина в символах
            height=25,              # Высота в строках
            font=("Segoe UI", 11),  # Шрифт
            bg=self.bg_color,       # Фоновый цвет
            fg=self.text_color,     # Цвет текста
            padx=10, pady=10,      # Отступы
            state='disabled'       # Запрет прямого редактирования
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True)
        
        # Панель ввода сообщений
        input_frame = tk.Frame(main_frame, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Текстовое поле для ввода сообщения
        self.user_input = tk.Text(
            input_frame,
            height=3,               # Высота в строках
            font=("Segoe UI", 11),  # Шрифт
            bg="white",             # Фон
            fg=self.text_color,     # Цвет текста
            padx=10, pady=10        # Отступы
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        # Обработка нажатия Enter (без Shift)
        self.user_input.bind("<Return>", self.send_message_event)
        
        # Кнопка отправки сообщения
        send_btn = tk.Button(
            input_frame,
            text="➤",                     # Символ отправки
            font=("Segoe UI", 12, "bold"), # Шрифт
            bg=self.accent_color,          # Цвет фона
            fg="white",                    # Цвет текста
            activebackground=self.accent_color,  # Цвет при нажатии
            activeforeground="white",
            borderwidth=0,                # Без рамки
            command=self.send_message      # Обработчик
        )
        send_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Кнопка загрузки файлов (конспектов, учебных материалов)
        upload_btn = tk.Button(
            input_frame,
            text="📁",                    # Иконка файла
            font=("Segoe UI", 12),
            bg=self.bg_color,
            fg=self.accent_color,
            activebackground=self.bg_color,
            activeforeground=self.accent_color,
            borderwidth=0,
            command=self.upload_file      # Обработчик загрузки
        )
        upload_btn.pack(side=tk.RIGHT, padx=(0, 5))
    
    def upload_file(self):
        """
        Загрузка учебных материалов (конспектов, лекций)
        TODO: Добавить обработку разных форматов (PDF, DOCX)
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                # Добавляем содержимое в поле ввода
                self.user_input.insert(tk.END, f"\n[File content]\n{content[:1000]}...")
                # Показываем информацию о загрузке в чате
                self.add_message("user", f"Uploaded study material: {file_path}\nContent preview: {content[:200]}...")
                
                # TODO: Добавить загрузку в векторную базу для поиска
                # self.vectorstore.add_texts([content])
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")
    
    def send_message_event(self, event):
        """
        Обработчик нажатия Enter в поле ввода.
        Отправляет сообщение только если нажат чистый Enter (без Shift)
        """
        if event.state == 0 and event.keysym == "Return":
            self.send_message()
            return "break"  # Предотвращаем перенос строки
    
    def send_message(self):
        """Основная функция отправки сообщения"""
        message = self.user_input.get("1.0", tk.END).strip()
        if not message:
            return  # Игнорируем пустые сообщения
            
        # Добавляем сообщение в историю чата
        self.add_message("user", message)
        # Очищаем поле ввода
        self.user_input.delete("1.0", tk.END)
        
        # Запускаем получение ответа в отдельном потоке,
        # чтобы не блокировать интерфейс
        Thread(target=self.get_ai_response, args=(message,)).start()
    
    def get_ai_response(self, question):
        """
        Получение ответа от ИИ-модели.
        TODO: Реализовать потоковый вывод для плавного появления текста
        """
        try:
            # Временная заглушка - здесь должен быть поиск по материалам
            # TODO: Заменить на вызов retriever.invoke(question)
            study_materials = "Relevant study materials will appear here..."
            
            # Создаем цепочку: промпт -> модель
            chain = self.prompt | self.model
            
            # Получаем ответ от модели
            response = chain.invoke({
                'study_materials': study_materials,
                'question': question
            })
            
            # TODO: Вместо этого блока реализовать потоковый вывод:
            # response_stream = chain.stream({'study_materials': study_materials, 'question': question})
            # for chunk in response_stream:
            #     self.update_message("ai", chunk)
            
            # Показываем ответ в чате
            self.add_message("ai", response)
                
        except Exception as e:
            # В случае ошибки показываем сообщение в чате
            self.add_message("system", f"Error: {str(e)}")
    
    def add_message(self, sender, message):
        """
        Добавление сообщения в историю чата с форматированием
        :param sender: 'user', 'ai' или 'system'
        :param message: текст сообщения
        """
        # Разблокируем поле для редактирования
        self.chat_history.config(state='normal')
        
        # Настраиваем стили для разных отправителей
        if sender == "user":
            bg = self.user_bg      # Цвет фона сообщений пользователя
            prefix = "You: "       # Префикс для пользователя
        elif sender == "ai":
            bg = self.ai_bg        # Цвет фона сообщений ИИ
            prefix = "Assistant: " # Префикс для ИИ (изменено)
        else:
            bg = self.bg_color     # Системные сообщения
            prefix = "System: "
        
        # Настраиваем теги для форматирования
        self.chat_history.tag_config(
            sender, 
            background=bg, 
            lmargin1=10,  # Отступ слева первой строки
            lmargin2=10,  # Отступ слева последующих строк
            rmargin=10    # Отступ справа
        )
        
        # Добавляем префикс и сообщение с соответствующими тегами
        self.chat_history.insert(tk.END, prefix, sender+"_prefix")
        self.chat_history.insert(tk.END, message + "\n\n", sender)
        
        # Блокируем поле от редактирования
        self.chat_history.config(state='disabled')
        # Прокручиваем до конца
        self.chat_history.see(tk.END)

if __name__ == "__main__":
    # Создаем главное окно и запускаем приложение
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()