'''
base class and agent Router
'''
# создаем базовый класс для остальных
class Core:

    # конструктор для данных
    def __init__(self, system, model, temperature, verbose):
        self.system = system
        self.model = model
        self.temperature = temperature
        self.verbose = verbose


# создаем class router
class Router(Core):
    # определяем роль, версию и температуру модели для router
    system_for_router = '''
    Ты — великолепный сотрудник финансового отдела торговой компании "Фэмили". 
    Компания занимается реализацией одежды, игрушек и закусками. У тебя 
    отлично получается выбирать к какой модели следует обратиться для 
    эффективной работы. \n\n

    Ты выбираешь одну из трех моделей: 'accounting', 'analyze', 'error'. 
    Пожалуйста, при выборе моделей учитывай контекст диалога. 
    \n\n

    Выбирай модель по следующим правилам:

    - Если сообщение — это ответ или отчет → выбери 'accounting'.
    - Если сообщение — это запрос на аналитическую записку → выбери 'analyze'.
    - Если сообщение бессмысленное → выбери 'error'

    Важно: твой ответ должен быть только одной строкой, содержащей имя модели.
    '''
    model_for_router = 'gpt-4.1-nano-2025-04-14'
    temperature_for_router = 0
    verbose_for_router = 0


    # собираем все данные
    def __init__(self, note, summary, client):
        self.note = note
        self.summary = summary
        self.client = client

        # запрашиваем данные у родительского класса
        super().__init__(
            system = self.system_for_router,
            model = self.model_for_router,
            temperature = self.temperature_for_router,
            verbose = self.verbose_for_router
        )


    # пишем функцию активации
    async def activate(self):
        user_for_router = f'''
        Пожалуйста, давай действовать последовательно: \n
        Шаг 1: Ознакомся с контекстом диалога. \n
        Шаг 2: Проанализируй сообщение сотрудника. \n
        Шаг 3: На основе Шаг 1 и Шаг 2 напиши одну модель для ответа сотрудникам. \n\n

        Сообщение клиента: {self.note} \n\n
        Контекст диалога: {self.summary} \n\n
        Ответ:
        '''

        messages = [
            {'role':'system', 'content':self.system},
            {'role':'user', 'content':user_for_router}
        ]

        completion = await self.client.chat.completions.create(
            model = self.model,
            messages = messages,
            temperature = self.temperature
        )

        answer = completion.choices[0].message.content

        if self.verbose:
            print('\n router: \n', answer)

        return answer