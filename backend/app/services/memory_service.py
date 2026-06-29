from collections import defaultdict


class MemoryService:

    def __init__(self):

        self.memory = defaultdict(list)

    def add_message(

        self,

        user_id: int,

        role: str,

        content: str,

    ):

        self.memory[user_id].append(

            {

                "role": role,

                "content": content,

            }

        )

        if len(self.memory[user_id]) > 10:

            self.memory[user_id] = (
                self.memory[user_id][-10:]
            )

    def get_history(

        self,

        user_id: int,

    ):

        return self.memory[user_id]

    def clear_history(

        self,

        user_id: int,

    ):

        self.memory[user_id] = []