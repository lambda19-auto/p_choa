import tracemalloc
from os import getenv

from dotenv import find_dotenv, load_dotenv

try:
    from .accounting import Accounting
    from .analyze import Analyze
    from .ask import Ask
    from .core_and_router import Router
    from .joke import Joke
    from .openrouter_client import OpenRouterClient
except ImportError:
    from accounting import Accounting
    from analyze import Analyze
    from ask import Ask
    from core_and_router import Router
    from joke import Joke
    from openrouter_client import OpenRouterClient
tracemalloc.start()


# create class ChoaAI
class ChoaAI():

    def __init__(self):
        load_dotenv(find_dotenv())
        OPEN_ROUTER_API_KEY = getenv('OPENROUTER_API_KEY')
        self.client = OpenRouterClient(api_key=OPEN_ROUTER_API_KEY)
        self.user_context = {}

    # method ai-finance
    async def neuro_finansist(self, user_id: int, note: str):
        if user_id not in self.user_context:
            self.user_context[user_id] = ''

        router = Router(note, self.user_context[user_id], self.client)
        output = await router.activate()
        self.user_context[user_id] += note

        if 'accounting' in output:
            accounting = Accounting(note, self.user_context[user_id], self.client)
            out_answer, was_written = await accounting.activate()

            if was_written == True:
                self.user_context[user_id] = ''
                return {'module': 'accounting',
                        'text': 'Спасибо, внесла операцию в журнал'}
            else:
                ask = Ask(out_answer, self.client)
                questions = await ask.activate()
                self.user_context[user_id] += questions
                return {'module': 'ask',
                        'text': questions}
            
        elif 'analyze' in output:
            analyze = Analyze(self.client)
            out_answer = await analyze.activate()
            self.user_context[user_id] = ''

            return {'module': 'analyze',
                    'text': out_answer}
        
        elif 'error' in output:
            joke = Joke(note, self.client)
            out_answer = await joke.activate()
            self.user_context[user_id] = ''
            return {'module': 'error',
                    'text': out_answer}
        else:
            return {'module': 'error router',
                    'text': 'Error router'}
