'''
agent Joke
'''
try:
    from .core_and_router import Core
    from .logging_setup import get_logger
except ImportError:
    from core_and_router import Core
    from logging_setup import get_logger


logger = get_logger(__name__)


class Joke(Core):
    # write role, model, temperature
    system_for_joke = '''
    Ты замечательный собеседник. У тебя прекрасно получается 
    придумывать остроумные и веселые ответы на текст который 
    к тебе приходит.

    Важно: Пожалуйста, побуди собеседника вернутся к работе.
    '''
    model_for_joke = 'gpt-4.1-nano-2025-04-14'
    temperature_for_joke = 0.5
    verbose_for_joke = 0

    def __init__(self, note, client):
        self.note = note
        self.client = client

        super().__init__(
            system = self.system_for_joke,
            model = self.model_for_joke,
            temperature = self.temperature_for_joke,
            verbose = self.verbose_for_joke
        )

    # method activate
    async def activate(self):
        user_for_extract = f'''
        Пожалуйста, придумай остроумный и веселый ответ на: {self.note}
        '''

        messages = [
            {'role':'system', 'content':self.system},
            {'role':'user', 'content':user_for_extract}
        ]

        completion = await self.client.chat.completions.create(
            model = self.model,
            messages = messages,
            temperature = self.temperature
        )

        answer = completion.choices[0].message.content

        if self.verbose:
            logger.info("memory: %s", answer)

        return answer
